# Framework Architecture

## Overview

This is a Python e2e test automation framework covering both REST API and browser UI testing.
It uses pytest as the runner with no BDD/Gherkin layers — tests are plain Python classes.
The design prioritises extensibility: adding a new API backend requires one new subclass, one new conftest, and one line added to `testpaths` — no changes to existing framework code.

---

## Technology Stack

| Dimension             | Decision                                                                          |
|-----------------------|-----------------------------------------------------------------------------------|
| Package manager       | uv                                                                                |
| Test runner           | pytest                                                                            |
| HTTP / browser client | Playwright `APIRequestContext` (single dependency, shared browser context)        |
| Data serialisation    | Pydantic v2 (domain models + `BaseSettings` for config)                           |
| Config management     | `pydantic-settings` + `.env` files                                                |
| Reporting             | allure-pytest + Allure CLI                                                        |
| UI target             | https://automationexercise.com                                                    |
| API target            | https://jsonplaceholder.typicode.com/                                             |
| Folder layout         | Feature-based                                                                     |
| Browser               | Chromium; headless by default; `--headed` CLI flag to override                    |
| Parallelism           | pytest-xdist from day one; function-scoped browser fixtures                       |
| Test data             | Pydantic model factories (builder classmethods with sensible defaults)            |
| UI auth               | Session storage snapshot fixture — login once per session, reuse across tests     |
| conftest layout       | Root `conftest.py` + one per feature folder                                       |
| Test structure        | `pytest` classes (`class TestXxx:`) — not `unittest.TestCase`                     |
| Failure artefacts     | Screenshot + Playwright trace captured automatically and attached to Allure       |
| Flaky test retry      | pytest-rerunfailures, 1 retry by default (configurable in `pyproject.toml`)       |
| Test markers          | `smoke`, `ui`, `api` — registered in `pyproject.toml`                            |
| Type annotations      | Type hints throughout; no mypy enforcement                                        |
| Logging               | Python `logging` module; `log_cli = true`; logs attached to Allure for every test |
| Response validation   | `BaseApiClient` always calls `model_validate()` on every response before returning |

---

## Project Structure

```
pytest-demo/
├── pyproject.toml              # uv / pytest / allure / dependency config
├── .env                        # local secrets and overrides (gitignored)
├── .env.example                # template checked into source control
├── .gitignore                  # excludes .env, allure-results/, logs/, __pycache__/, .venv/
├── logs/
│   └── .gitkeep                # ensures logs/ exists; pytest needs it for log_file
├── architecture.md             # this file
├── conftest.py                 # settings, auth_state, browser_context, page, api_context,
│                                 # trace_path, attach_trace_on_failure, makereport hook,
│                                 # pytest_configure (per-worker log_file under xdist)
│
├── core/                       # framework internals — no tests here
│   ├── __init__.py
│   ├── base_page.py            # abstract BasePage
│   ├── base_api_client.py      # abstract BaseApiClient (Generic[T])
│   ├── exceptions.py           # ApiError
│   └── config.py               # Settings (Pydantic BaseSettings singleton)
│
├── models/                     # shared Pydantic base
│   ├── __init__.py
│   └── base_model.py           # AppBaseModel — shared model config
│
├── users/                      # JSONPlaceholder /users + AE account/login
│   ├── __init__.py
│   ├── conftest.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user_model.py       # CreateUserRequest, UserResponse
│   ├── api/
│   │   ├── __init__.py
│   │   └── user_client.py      # UserApiClient(BaseApiClient)
│   ├── pages/
│   │   ├── __init__.py
│   │   └── login_page.py       # LoginPage(BasePage)
│   └── tests/
│       ├── __init__.py
│       ├── test_user_api.py
│       └── test_login_ui.py
│
├── posts/                      # JSONPlaceholder /posts
│   ├── __init__.py
│   ├── conftest.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── post_model.py       # CreatePostRequest, PostResponse
│   ├── api/
│   │   ├── __init__.py
│   │   └── post_client.py      # PostApiClient(BaseApiClient)
│   └── tests/
│       ├── __init__.py
│       └── test_post_api.py
│
└── products/                   # automationexercise.com product catalogue
    ├── __init__.py
    ├── conftest.py
    ├── pages/
    │   ├── __init__.py
    │   ├── home_page.py        # HomePage(BasePage)
    │   └── product_page.py     # ProductPage(BasePage)
    └── tests/
        ├── __init__.py
        └── test_product_ui.py
```

### `.env.example` content

```dotenv
# --- Required (no defaults — missing values raise ValidationError at startup) ---
AE_USERNAME=your_email@example.com
AE_PASSWORD=your_password

# --- Optional overrides (defaults shown) ---
API_BASE_URL=https://jsonplaceholder.typicode.com
UI_BASE_URL=https://automationexercise.com
BROWSER_TIMEOUT=30000
API_TIMEOUT=10000
```

Copy to `.env` and fill in credentials before running any UI tests.

---

## OOP Design and SOLID Principles

### `core/base_api_client.py` — Abstraction, Open/Closed, Liskov, Dependency Inversion

`BaseApiClient` is generic over its response model type `T` so the compiler can
infer the return type of every HTTP helper without casts in subclasses.

```
BaseApiClient(ABC, Generic[T])
  ├── __init__(context: APIRequestContext, settings: Settings)
  │     stores _context and _settings; both encapsulated (single underscore)
  ├── base_url (abstract property)   ← subclass reads self._settings or returns a constant
  ├── endpoint (abstract property)   ← subclass declares its resource path
  ├── _response_model: type[T]       ← subclass sets this as a CLASS variable (see below)
  │
  │   Protected HTTP helpers — construct full URL from base_url + endpoint + resource_id:
  ├── _get(resource_id: int | str, params=None) → T
  ├── _get_many(params=None) → list[T]
  ├── _post(payload: AppBaseModel) → T
  ├── _put(resource_id: int | str, payload: AppBaseModel) → T
  ├── _patch(resource_id: int | str, payload: AppBaseModel) → T
  └── _delete(resource_id: int | str) → None

# Subclass must set _response_model as a class variable.
# Generic[T] is erased at runtime — the type cannot be inferred automatically.
# Subclasses expose a domain-specific PUBLIC API; tests never call _get/_post directly.
class UserApiClient(BaseApiClient[UserResponse]):
    endpoint = "/users"
    _response_model = UserResponse        # ← required; drives model_validate in base

    @property
    def base_url(self) -> str:
        return self._settings.api_base_url

    # Public domain API — wraps the protected HTTP helpers:
    def get(self, user_id: int) -> UserResponse:
        return self._get(user_id)

    def get_all(self) -> list[UserResponse]:
        return self._get_many()

    def create(self, payload: CreateUserRequest) -> UserResponse:
        return self._post(payload)

    def update(self, user_id: int, payload: CreateUserRequest) -> UserResponse:
        return self._put(user_id, payload)

    def delete(self, user_id: int) -> None:
        self._delete(user_id)

# PostApiClient follows the same pattern.
class PostApiClient(BaseApiClient[PostResponse]):
    endpoint = "/posts"
    _response_model = PostResponse

    @property
    def base_url(self) -> str:
        return self._settings.api_base_url

    def get(self, post_id: int) -> PostResponse: ...
    def get_all(self) -> list[PostResponse]: ...
    def create(self, payload: CreatePostRequest) -> PostResponse: ...
    def update(self, post_id: int, payload: CreatePostRequest) -> PostResponse: ...
    def delete(self, post_id: int) -> None: ...
```

`base_url` is an abstract property so each subclass explicitly declares where it reads
the URL from — either `self._settings` for configurable targets or a class constant for
fixed third-party URLs (see extensibility recipe).

**Extensibility:** to target a new backend (e.g. `reqres.in`), subclass `BaseApiClient`,
override `base_url` and `endpoint`. No existing framework code changes — only a one-line
addition to `testpaths` in `pyproject.toml` (see extensibility recipe).

Every `_get` / `_post` / `_put` / `_patch` method (single-object response):
1. Logs the request at DEBUG level.
2. Executes the Playwright API call. Write methods (`_post`, `_put`, `_patch`) serialize
   the payload with `payload.model_dump(by_alias=True)` to produce camelCase keys
   (`userId`, not `user_id`) as required by the API. Plain `model_dump()` would send
   snake_case keys and silently fail on any real backend.
3. Raises `ApiError` (see below) on non-2xx status codes.
4. Calls `self._response_model.model_validate(response.json())` and returns the result.

Step 3 must precede step 4: a non-2xx body (e.g. `{}` from a 404) would fail
`model_validate` with a Pydantic `ValidationError` before `ApiError` is ever raised,
making `pytest.raises(ApiError)` unreachable.

`_get_many` (list response) differs at step 4 — a JSON array cannot be passed to
`model_validate` on a single-item model. The implementation validates each element:
```python
return [self._response_model.model_validate(item) for item in response.json()]
```

`_delete` follows steps 1, 2, and 3 only — it returns `None` so there is no response
model to validate, but it still logs the request and raises `ApiError` on non-2xx.

#### `core/exceptions.py` — custom exception hierarchy

```
ApiError(RuntimeError)
  ├── status_code: int
  ├── url: str
  └── body: str          ← raw response text for debugging

# Raised by BaseApiClient on every non-2xx response.
# Tests that expect failures catch ApiError explicitly:
#   with pytest.raises(ApiError) as exc:
#       client.get(user_id=999)
#   assert exc.value.status_code == 404
```

### `core/base_page.py` — Abstraction, Liskov, Interface Segregation

```
BasePage (ABC)
  ├── __init__(page: Page, settings: Settings)
  │     stores _page and _settings; both encapsulated (single underscore)
  ├── navigate() → self
  │     calls _page.goto(self.url), then calls is_loaded() and returns self.
  │     safe for chaining: LoginPage(...).navigate().login(...) only runs after load.
  ├── url (abstract property)        ← subclass computes full URL, typically from _settings.ui_base_url
  └── is_loaded() → None (abstract)
        subclass calls expect(locator).to_be_visible() on a stable landmark element.
        Playwright's built-in retry+timeout handles the wait — do not use time.sleep().
        Raises AssertionError/TimeoutError if the element never appears; navigate() propagates it.

class LoginPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/login"

    def is_loaded(self) -> None:
        expect(self._page.locator("input[name='email']")).to_be_visible()

    def login(self, username: str, password: str) -> None: ...
    # All login selectors live here; no raw page.fill() calls outside this class

class HomePage(BasePage):
    @property
    def url(self) -> str:
        return self._settings.ui_base_url

    def is_loaded(self) -> None:
        expect(self._page.locator("h2", has_text="Features Items")).to_be_visible()

class ProductPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/products"

    def is_loaded(self) -> None:
        expect(self._page.locator("h2", has_text="All Products")).to_be_visible()
```

All page objects are substitutable where `BasePage` is expected (LSP).
Page objects are responsible only for navigation and interaction — assertions live
in test classes (Single Responsibility).

### `models/base_model.py` — Single Responsibility

```
AppBaseModel(pydantic.BaseModel)
  └── model_config: alias_generator=to_camel, populate_by_name=True
                   # to_camel imported from pydantic.alias_generators
                   # handles JSONPlaceholder camelCase fields (userId, postId, …)

UserResponse(AppBaseModel)
    id: int, name: str, username: str, email: str, ...

CreateUserRequest(AppBaseModel)
    name: str, username: str, email: str, ...

    @classmethod
    def make(cls, **overrides: Any) -> Self:
        # Merges test-appropriate defaults with any caller-supplied overrides.
        # Self (typing.Self, Python 3.12) returns the concrete subclass type correctly.
        defaults = {"name": "Test User", "username": "testuser", "email": "test@example.com"}
        return cls(**{**defaults, **overrides})
    # Usage: CreateUserRequest.make()                        → all defaults
    #        CreateUserRequest.make(name="Alice")            → only name overridden

PostResponse(AppBaseModel)
    id: int, user_id: int, title: str, body: str
    # user_id maps to JSONPlaceholder's camelCase "userId" via alias_generator

CreatePostRequest(AppBaseModel)
    user_id: int, title: str, body: str

    @classmethod
    def make(cls, **overrides: Any) -> Self: ...
```

### `core/config.py` — Dependency Inversion

```
Settings(pydantic_settings.BaseSettings)
  ├── api_base_url: str      = "https://jsonplaceholder.typicode.com"
  ├── ui_base_url: str       = "https://automationexercise.com"
  ├── browser_timeout: int   = 30_000   ← ms; passed to context.set_default_timeout()
  ├── api_timeout: int       = 10_000   ← ms; passed to APIRequestContext timeout option
  ├── ae_username: str                  ← required; no default — must be set in .env
  ├── ae_password: SecretStr            ← required; no default — SecretStr hides it from logs
  └── model_config = SettingsConfigDict(env_file=".env")
```

`ae_username` and `ae_password` have no defaults intentionally. Pydantic raises a clear
`ValidationError: field required` at fixture setup time if either is missing from `.env`,
rather than silently passing empty credentials to the login page and producing a confusing
UI failure deep inside the test run.

`browser_headless` is intentionally absent from `Settings` — headless/headed mode is
controlled exclusively by pytest-playwright's native `--headed` CLI flag. Duplicating
it here would create dead config with no effect on the actual browser launch.

Tests receive `Settings` via fixture injection; they never read `os.environ` directly.
`browser_context` applies `context.set_default_timeout(settings.browser_timeout)` after creation.
`api_context` passes `timeout=settings.api_timeout` to `new_context(...)`.

---

## Fixture Design

### pytest-playwright fixture layering

`pytest-playwright` already provides `playwright`, `browser`, `browser_context`, and `page`
fixtures. Our root `conftest.py` **overrides** `browser_context` and `page` (same names) to
inject auth state and start tracing. The built-in `playwright` and low-level `browser`
fixtures are used as-is; we do not redeclare them. The `--headed` flag is provided natively
by `pytest-playwright` (`--headed` CLI option and `PLAYWRIGHT_HEADLESS` env var) so no
custom `pytest_addoption` hook is needed.

### Root `conftest.py` (parallel-safe with pytest-xdist)

```python
@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()

# auth_state: session-scoped but xdist-safe via tmp_path_factory + filelock.
# Creates its own temporary BrowserContext + Page solely to perform login,
# then saves storage state to a shared file and closes the context.
# Each xdist worker acquires a FileLock before checking if the file already
# exists; only the first worker performs the login round-trip.
# Uses LoginPage (not raw selectors) to stay consistent with the Page Object pattern.
@pytest.fixture(scope="session")
def auth_state(browser, settings, tmp_path_factory) -> Path:
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
                context.close()   # always close even if login throws
    return path

# trace_path: unique per-test temp file so parallel workers never collide.
@pytest.fixture
def trace_path(tmp_path) -> Path:
    return tmp_path / "trace.zip"

# Override pytest-playwright's browser_context to inject auth, timeouts, and tracing.
@pytest.fixture
def browser_context(browser, auth_state, trace_path, settings):
    context = browser.new_context(storage_state=auth_state)
    context.set_default_timeout(settings.browser_timeout)
    context.tracing.start(screenshots=True, snapshots=True)
    yield context
    context.tracing.stop(path=str(trace_path))   # explicit path required
    context.close()

# Override pytest-playwright's page.
# Screenshot is captured HERE — before page.close() — so the page is still open.
# This is the only correct place; a separate autouse fixture would read a closed page.
@pytest.fixture
def page(browser_context, request):
    page = browser_context.new_page()
    yield page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        allure.attach(page.screenshot(full_page=True), name="screenshot",
                      attachment_type=allure.attachment_type.PNG)
    page.close()

# api_context must be disposed after each test to release the underlying connection.
@pytest.fixture
def api_context(playwright, settings):
    context = playwright.request.new_context(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
    )
    yield context
    context.dispose()

# pytest_configure runs before any fixture.
# Without this, all xdist workers write to the same logs/test.log simultaneously —
# on Windows that causes PermissionError or interleaved/corrupted output.
def pytest_configure(config):
    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    if worker_id:
        config.option.log_file = f"logs/test_{worker_id}.log"

# hookwrapper=True is deprecated since pytest 7.2; use wrapper=True instead.
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    rep = yield
    setattr(item, f"rep_{rep.when}", rep)
    return rep

# Attaches the Playwright trace after test failure.
# Does NOT depend on browser_context or page — API tests are unaffected.
# trace_path is cheap (just a Path) and safe to check on any test.
@pytest.fixture(autouse=True)
def attach_trace_on_failure(request):
    yield
    if not (getattr(request.node, "rep_call", None) and request.node.rep_call.failed):
        return
    if "trace_path" in request.fixturenames:
        tp: Path = request.getfixturevalue("trace_path")
        if tp.exists():
            allure.attach.file(str(tp), name="trace",
                               attachment_type=allure.attachment_type.ZIP)
```

### Feature `conftest.py` (e.g. `users/conftest.py`)

```python
@pytest.fixture
def user_client(api_context, settings) -> UserApiClient:
    return UserApiClient(context=api_context, settings=settings)

@pytest.fixture
def login_page(page, settings) -> LoginPage:
    return LoginPage(page=page, settings=settings)

# login_page above uses the pre-authenticated `page` fixture — suitable for
# tests that verify post-login UI behaviour (e.g. account name visible in header).
#
# Tests that exercise the login flow itself (fill credentials → submit → verify)
# must start unauthenticated. Use unauthenticated_page instead.
# The fixture replicates the screenshot + trace teardown from the root `page` fixture
# so login test failures produce the same diagnostic artefacts as all other UI tests.
@pytest.fixture
def unauthenticated_page(browser, settings, tmp_path, request):
    context = browser.new_context()   # no storage_state — fresh unauthenticated session
    context.set_default_timeout(settings.browser_timeout)
    trace_zip = tmp_path / "trace.zip"
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    yield page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        allure.attach(page.screenshot(full_page=True), name="screenshot",
                      attachment_type=allure.attachment_type.PNG)
        context.tracing.stop(path=str(trace_zip))
        allure.attach.file(str(trace_zip), name="trace",
                           attachment_type=allure.attachment_type.ZIP)
    else:
        context.tracing.stop()   # discard trace on pass to save disk space
    page.close()
    context.close()
```

`unauthenticated_page` bypasses `auth_state` so the session cookie is absent.
Tests using it see the login form in its initial state, which is required for testing
credential validation, redirect-on-success, and error messaging.
Because it owns its context, it manages its own tracing inline rather than delegating
to `attach_trace_on_failure` (which only covers contexts created via the root `browser_context`).

---

## Failure Artefacts

Two separate mechanisms handle failure capture, split by a critical timing constraint:

**Screenshot** — captured inside the `page` fixture teardown, **before** `page.close()`.
A separate autouse fixture cannot do this because by the time it runs teardown, `page` has
already been closed and `page.screenshot()` would throw.

**Trace** — attached by `attach_trace_on_failure` (autouse), which runs after `browser_context`
teardown has already written `trace.zip` to `trace_path`. This ordering is safe because the
autouse fixture (no dependencies) is set up before the explicitly-requested fixtures, and
therefore tears down after them (pytest LIFO).

Both rely on `request.node.rep_call.failed`, which is set by the `pytest_runtest_makereport`
hook. Without this hook the attribute is absent and both captures silently no-op.

### xdist + rerunfailures incompatibility

`pytest-xdist` (`-n auto`) and `pytest-rerunfailures` (`--reruns`) **cannot be active at
the same time** — rerunfailures explicitly disables itself under xdist. The strategy is:

- Normal development / CI fast run: `pytest -n auto` (parallel, no reruns).
- Flaky-detection / stability run: `pytest --reruns 1 --reruns-delay 2` (serial, with retries).
- Both profiles are exposed as `uv run` scripts in `pyproject.toml`.
  Note: `[project.scripts]` expects `module:function` entry points and cannot hold shell
  commands. Use `[tool.uv.scripts]` (uv-specific, supports shell strings) instead:

```toml
[tool.pytest.ini_options]
# Neither -n auto nor --reruns in addopts — they are mutually exclusive.
addopts = "--alluredir=allure-results"

[tool.uv.scripts]
test-parallel = "pytest -n auto"
test-stable   = "pytest --reruns 1 --reruns-delay 2"
# Usage: uv run test-parallel  /  uv run test-stable
```

---

## Test Class Shape

```python
@pytest.mark.api
@pytest.mark.smoke
class TestGetUser:
    def test_returns_valid_schema(self, user_client: UserApiClient) -> None:
        user = user_client.get(user_id=1)   # validated → UserResponse inside client
        assert user.id == 1

    def test_name_is_non_empty(self, user_client: UserApiClient) -> None:
        user = user_client.get(user_id=1)
        assert user.name
```

---

## Allure Step Decoration

Every public method on `BasePage` subclasses and `BaseApiClient` subclasses should be
decorated with `@allure.step(...)` so the Allure report shows a human-readable action
timeline. The `@allure.step` decorator is additive — it does not replace logging.

```python
# In a page object:
@allure.step("Click 'Add to cart' for product {product_name}")
def add_to_cart(self, product_name: str) -> None: ...

# In an API client:
@allure.step("GET /users/{user_id}")
def get(self, user_id: int) -> UserResponse: ...
```

Each method applies `@allure.step` explicitly. The decorator is not inheritable —
it must be applied at the point of definition in each subclass method.

---

## Logging

`BaseApiClient` and `BasePage` each hold a module-level `logging.getLogger(__name__)`.
Every HTTP request/response and every `navigate()` call emits a `DEBUG` line.
`pyproject.toml` enables `log_cli = true` so logs appear in the terminal during local runs
and are captured by pytest. `allure-pytest` attaches captured logs to every test's report
automatically — pass and fail alike — with no extra fixture code required.

---

## `pyproject.toml` Configuration Sketch

```toml
[project]
name = "pytest-demo"
requires-python = ">=3.12"
dependencies = [
    "pytest",
    "pytest-playwright",      # bundles playwright; provides browser/page fixtures
    "pydantic>=2",
    "pydantic-settings",
    "allure-pytest",
    "pytest-xdist[psutil]",   # psutil enables -n auto CPU detection
    "pytest-rerunfailures",
    "filelock",               # for xdist-safe auth_state session fixture
]

[tool.pytest.ini_options]
# -n auto and --reruns are mutually exclusive; omit both from addopts.
# Run via: uv run pytest -n auto  OR  uv run pytest --reruns 1 --reruns-delay 2
addopts       = "--alluredir=allure-results"
testpaths     = ["users", "posts", "products"]
log_cli        = true
log_cli_level  = "INFO"           # concise terminal output; avoids flood in parallel runs
log_file       = "logs/test.log"   # default; pytest_configure overrides to logs/test_gw0.log etc. under xdist
log_file_level = "DEBUG"          # full request/response detail in file for post-mortem
markers = [
    "smoke: critical-path tests",
    "api: REST API tests",
    "ui: browser UI tests",
]

[tool.uv.scripts]
test-parallel = "pytest -n auto"
test-stable   = "pytest --reruns 1 --reruns-delay 2"
# Usage: uv run test-parallel  /  uv run test-stable
```

---

## Extensibility Recipe (Open/Closed in practice)

To add a new API target (e.g. `reqres.in`):

1. Add `reqres_users/api/reqres_user_client.py`:
   ```python
   from core.base_api_client import BaseApiClient
   from reqres_users.models.reqres_user_model import CreateReqresUserRequest, ReqresUserResponse

   class ReqresUserClient(BaseApiClient[ReqresUserResponse]):
       _BASE_URL = "https://reqres.in"   # class constant — no Settings change needed
       endpoint = "/api/users"
       _response_model = ReqresUserResponse

       @property
       def base_url(self) -> str:
           return self._BASE_URL

       # Public domain API — required; tests call these, not the protected _get/_post helpers
       def get(self, user_id: int) -> ReqresUserResponse:
           return self._get(user_id)

       def get_all(self) -> list[ReqresUserResponse]:
           return self._get_many()

       def create(self, payload: CreateReqresUserRequest) -> ReqresUserResponse:
           return self._post(payload)
   ```
2. Add `reqres_users/models/reqres_user_model.py` with `ReqresUserResponse(AppBaseModel)` and `CreateReqresUserRequest(AppBaseModel)`.
3. Add `reqres_users/conftest.py` with a `reqres_user_client` fixture.
4. Write tests in `reqres_users/tests/`.

One-line change required: add `"reqres_users"` to `testpaths` in `pyproject.toml` so
pytest discovers the new tests. All framework code (`core/`, `users/`, `posts/`, `Settings`)
remains untouched.

---

## Verification Checklist

1. `uv run pytest users/tests/test_user_api.py -v` — API smoke, schema validation.
2. `uv run pytest products/tests/test_product_ui.py -v --headed` — UI smoke with visible browser.
3. `uv run pytest -n 4` — parallel run; confirms no shared-state fixture collisions.
4. `allure serve allure-results` — report renders with steps, logs, and artefacts.
5. `uv run pytest -m smoke --co -q` — confirms marker collection covers expected tests.
