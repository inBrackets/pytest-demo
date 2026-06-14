import contextlib
import logging
import os
import uuid
from pathlib import Path
from typing import Any, Callable, Generator

import allure
import pytest
from filelock import FileLock
from playwright.sync_api import APIRequestContext, Browser, BrowserContext, Page, Playwright

from ae_account.api.ae_account_client import AeAccountClient
from ae_account.models.ae_account_model import AeCreateAccountRequest
from core.config import Settings
from products.pages.home_page import HomePage
from users.pages.login_page import LoginPage

_logger = logging.getLogger(__name__)

_TEST_PASSWORD = "Test1234!"
_rerun_nodeids: set[str] = set()
_passed_after_retry: set[str] = set()


def pytest_configure(config: pytest.Config) -> None:
    output_dir = config.rootpath / "output"
    allure_dir = output_dir / "allure-results"
    logs_dir = output_dir / "logs"
    allure_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(config.option, "allure_report_dir"):
        config.option.allure_report_dir = str(allure_dir)

    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    log_name = f"test_{worker_id}.log" if worker_id else "test.log"
    config.option.log_file = str(logs_dir / log_name)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return
    if report.outcome == "rerun":
        _rerun_nodeids.add(report.nodeid)
    elif report.passed and report.nodeid in _rerun_nodeids:
        _rerun_nodeids.discard(report.nodeid)
        _passed_after_retry.add(report.nodeid)
        with contextlib.suppress(Exception):
            allure.dynamic.label("flakiness", "flaky")


def pytest_terminal_summary(
    terminalreporter: Any, exitstatus: int, config: pytest.Config
) -> None:
    if not _passed_after_retry:
        return
    terminalreporter.write_sep("-", "tests that passed after retry (flaky)")
    for nodeid in sorted(_passed_after_retry):
        terminalreporter.write_line(f"  FLAKY: {nodeid}")


class ResourceRegistry:
    """LIFO cleanup registry — guarantees all registered resources are deleted even on cascade failures."""

    def __init__(self) -> None:
        self._resources: list[tuple[str, str, Callable[[], None]]] = []
        self._logger = logging.getLogger(__name__)

    def register(
        self, resource_type: str, resource_id: str, cleanup: Callable[[], None]
    ) -> None:
        self._resources.append((resource_type, resource_id, cleanup))
        self._logger.debug("Registered %s %s for cleanup", resource_type, resource_id)

    def cleanup_all(self) -> None:
        for resource_type, resource_id, cleanup in reversed(self._resources):
            try:
                cleanup()
                self._logger.debug("Cleaned up %s %s", resource_type, resource_id)
            except Exception as exc:
                self._logger.warning(
                    "Cleanup failed for %s %s: %s", resource_type, resource_id, exc
                )


@pytest.fixture
def resource_registry() -> Generator[ResourceRegistry, None, None]:
    registry = ResourceRegistry()
    yield registry
    registry.cleanup_all()


def _save_screenshot(item: pytest.Item, png: bytes) -> None:
    slug = item.nodeid.replace("/", "_").replace("::", "_").replace("[", "_").replace("]", "")
    screenshots_dir = item.config.rootpath / "output" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    (screenshots_dir / f"{slug}.png").write_bytes(png)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    rep: pytest.TestReport = yield
    setattr(item, f"rep_{rep.when}", rep)
    if rep.when == "call" and rep.failed:
        if isinstance(item, pytest.Function):
            pw_page = item.funcargs.get("page") or item.funcargs.get("unauthenticated_page")
            if isinstance(pw_page, Page):
                try:
                    png = pw_page.screenshot()
                    allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)
                    _save_screenshot(item, png)
                except Exception:
                    pass
    return rep


@pytest.fixture
def home_page(page: Page, settings: Settings) -> HomePage:
    return HomePage(page=page, settings=settings)


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: dict[str, Any], settings: Settings
) -> dict[str, Any]:
    return {**browser_type_launch_args, "headless": settings.browser_headless}


@pytest.fixture(scope="session")
def _ae_api_context(
    playwright: Playwright, settings: Settings
) -> Generator[APIRequestContext, None, None]:
    context = playwright.request.new_context(timeout=settings.api_timeout)
    yield context
    context.dispose()


def _account_lifecycle(client: AeAccountClient) -> Generator[dict[str, str], None, None]:
    email = f"pytest_{uuid.uuid4().hex[:8]}@test.com"
    password = _TEST_PASSWORD
    client.create_account(AeCreateAccountRequest.make(email=email, password=password))
    try:
        yield {"email": email, "password": password}
    finally:
        try:
            client.delete_account(email=email, password=password)
        except Exception as exc:
            _logger.warning("Account deletion failed for %s: %s", email, exc)


@pytest.fixture(scope="session")
def live_account(
    _ae_api_context: APIRequestContext, settings: Settings
) -> Generator[dict[str, str], None, None]:
    yield from _account_lifecycle(AeAccountClient(context=_ae_api_context, settings=settings))


@pytest.fixture
def temp_account(
    api_context: APIRequestContext, settings: Settings
) -> Generator[dict[str, str], None, None]:
    yield from _account_lifecycle(AeAccountClient(context=api_context, settings=settings))


@pytest.fixture(scope="session")
def auth_state(
    browser: Browser,
    live_account: dict[str, str],
    settings: Settings,
    tmp_path_factory: pytest.TempPathFactory,
) -> Path:
    path = tmp_path_factory.getbasetemp() / "storage_state.json"
    lock = FileLock(str(path) + ".lock")
    with lock:
        if not path.exists():
            context = browser.new_context()
            try:
                pw_page = context.new_page()
                LoginPage(pw_page, settings).navigate().login(
                    username=live_account["email"],
                    password=live_account["password"],
                )
                if "/login" in pw_page.url:
                    raise RuntimeError(
                        f"Session login failed — still at {pw_page.url!r}. "
                        "All authenticated tests would receive an unauthenticated context."
                    )
                context.storage_state(path=str(path))
            finally:
                context.close()
    return path


@pytest.fixture
def trace_path(tmp_path: Path) -> Path:
    return tmp_path / "trace.zip"


@pytest.fixture
def browser_context(
    browser: Browser,
    auth_state: Path,
    trace_path: Path,
    settings: Settings,
) -> Generator[BrowserContext, None, None]:
    context = browser.new_context(storage_state=str(auth_state))
    context.set_default_timeout(settings.browser_timeout)
    context.tracing.start(screenshots=True, snapshots=True)
    yield context
    context.tracing.stop(path=str(trace_path))
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    pw_page = browser_context.new_page()
    yield pw_page
    pw_page.close()


@pytest.fixture
def unauthenticated_page(
    browser: Browser,
    settings: Settings,
    tmp_path: Path,
    request: pytest.FixtureRequest,
) -> Generator[Page, None, None]:
    context = browser.new_context()
    context.set_default_timeout(settings.browser_timeout)
    trace_zip = tmp_path / "trace.zip"
    context.tracing.start(screenshots=True, snapshots=True)
    pw_page = context.new_page()
    yield pw_page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        context.tracing.stop(path=str(trace_zip))
        allure.attach.file(  # type: ignore[no-untyped-call]
            str(trace_zip), name="trace", attachment_type=allure.attachment_type.ZIP
        )
    else:
        context.tracing.stop()
    pw_page.close()
    context.close()


@pytest.fixture
def disposable_credentials(
    api_context: APIRequestContext, settings: Settings
) -> Generator[dict[str, str], None, None]:
    email = f"pytest_{uuid.uuid4().hex[:8]}@test.com"
    creds: dict[str, str] = {"name": "Pytest User", "email": email, "password": _TEST_PASSWORD}
    yield creds
    try:
        AeAccountClient(api_context, settings).delete_account(
            email=creds["email"], password=creds["password"]
        )
    except Exception as exc:
        _logger.warning("Account deletion failed for %s: %s", creds["email"], exc)


@pytest.fixture
def api_context(
    playwright: Playwright, settings: Settings
) -> Generator[APIRequestContext, None, None]:
    context = playwright.request.new_context(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
    )
    yield context
    context.dispose()


@pytest.fixture(autouse=True)
def attach_trace_on_failure(
    request: pytest.FixtureRequest, trace_path: Path
) -> Generator[None, None, None]:
    yield
    if not (getattr(request.node, "rep_call", None) and request.node.rep_call.failed):
        return
    if trace_path.exists():
        allure.attach.file(  # type: ignore[no-untyped-call]
            str(trace_path),
            name="trace",
            attachment_type=allure.attachment_type.ZIP,
        )
