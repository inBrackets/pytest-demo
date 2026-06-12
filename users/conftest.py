from pathlib import Path

import allure
import pytest

from users.api.user_client import UserApiClient
from users.pages.login_page import LoginPage


@pytest.fixture
def user_client(api_context, settings) -> UserApiClient:
    return UserApiClient(context=api_context, settings=settings)


@pytest.fixture
def login_page(page, settings) -> LoginPage:
    return LoginPage(page=page, settings=settings)


@pytest.fixture
def unauthenticated_page(browser, settings, tmp_path: Path, request):
    context = browser.new_context()
    context.set_default_timeout(settings.browser_timeout)
    trace_zip = tmp_path / "trace.zip"
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    yield page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        allure.attach(
            page.screenshot(full_page=True),
            name="screenshot",
            attachment_type=allure.attachment_type.PNG,
        )
        context.tracing.stop(path=str(trace_zip))
        allure.attach.file(
            str(trace_zip),
            name="trace",
            attachment_type=allure.attachment_type.ZIP,
        )
    else:
        context.tracing.stop()
    page.close()
    context.close()
