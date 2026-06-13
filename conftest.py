import os
import uuid
from pathlib import Path
from typing import Generator

import allure
import pytest
from filelock import FileLock
from playwright.sync_api import Browser, BrowserContext, Page

from core.config import Settings
from users.pages.login_page import LoginPage


def pytest_configure(config: pytest.Config) -> None:
    output_dir = Path(config.rootdir) / "output"
    allure_dir = output_dir / "allure-results"
    logs_dir = output_dir / "logs"
    allure_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(config.option, "allure_report_dir"):
        config.option.allure_report_dir = str(allure_dir)

    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    log_name = f"test_{worker_id}.log" if worker_id else "test.log"
    config.option.log_file = str(logs_dir / log_name)


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    rep = yield
    setattr(item, f"rep_{rep.when}", rep)
    return rep


@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()


@pytest.fixture(scope="session")
def auth_state(
    browser: Browser,
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
                    username=settings.ae_username,
                    password=settings.ae_password.get_secret_value(),
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
) -> BrowserContext:
    context = browser.new_context(storage_state=str(auth_state))
    context.set_default_timeout(settings.browser_timeout)
    context.tracing.start(screenshots=True, snapshots=True)
    yield context
    context.tracing.stop(path=str(trace_path))
    context.close()


@pytest.fixture
def page(browser_context: BrowserContext, request: pytest.FixtureRequest) -> Page:
    pw_page = browser_context.new_page()
    yield pw_page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        try:
            allure.attach(
                pw_page.screenshot(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
    pw_page.close()


@pytest.fixture
def unauthenticated_page(browser: Browser, settings: Settings, tmp_path: Path, request):
    context = browser.new_context()
    context.set_default_timeout(settings.browser_timeout)
    trace_zip = tmp_path / "trace.zip"
    context.tracing.start(screenshots=True, snapshots=True)
    pw_page = context.new_page()
    yield pw_page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        try:
            allure.attach(
                pw_page.screenshot(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
        context.tracing.stop(path=str(trace_zip))
        allure.attach.file(str(trace_zip), name="trace", attachment_type=allure.attachment_type.ZIP)
    else:
        context.tracing.stop()
    pw_page.close()
    context.close()


@pytest.fixture
def disposable_credentials(api_context, settings) -> Generator[dict, None, None]:
    """Generate a unique account, yield credentials, delete via API in teardown."""
    from ae_account.api.ae_account_client import AeAccountClient
    email = f"pytest_{uuid.uuid4().hex[:8]}@test.com"
    creds = {"name": "Pytest User", "email": email, "password": "Test1234!"}
    yield creds
    try:
        AeAccountClient(api_context, settings).delete_account(
            email=creds["email"], password=creds["password"]
        )
    except Exception:
        pass


@pytest.fixture
def api_context(playwright, settings: Settings):
    context = playwright.request.new_context(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
    )
    yield context
    context.dispose()


@pytest.fixture(autouse=True)
def attach_trace_on_failure(request: pytest.FixtureRequest, trace_path: Path) -> None:
    yield
    if not (getattr(request.node, "rep_call", None) and request.node.rep_call.failed):
        return
    if trace_path.exists():
        allure.attach.file(
            str(trace_path),
            name="trace",
            attachment_type=allure.attachment_type.ZIP,
        )
