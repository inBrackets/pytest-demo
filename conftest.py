import os
from pathlib import Path

import allure
import pytest
from filelock import FileLock
from playwright.sync_api import Browser, BrowserContext, Page

from core.config import Settings
from users.pages.login_page import LoginPage


def pytest_configure(config: pytest.Config) -> None:
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id:
        config.option.log_file = f"logs/test_{worker_id}.log"


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
        allure.attach(
            pw_page.screenshot(full_page=True),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
    pw_page.close()


@pytest.fixture
def api_context(playwright, settings: Settings):
    context = playwright.request.new_context(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
    )
    yield context
    context.dispose()


@pytest.fixture(autouse=True)
def attach_trace_on_failure(request: pytest.FixtureRequest) -> None:
    yield
    if not (getattr(request.node, "rep_call", None) and request.node.rep_call.failed):
        return
    if "trace_path" in request.fixturenames:
        tp: Path = request.getfixturevalue("trace_path")
        if tp.exists():
            allure.attach.file(
                str(tp),
                name="trace",
                attachment_type=allure.attachment_type.ZIP,
            )
