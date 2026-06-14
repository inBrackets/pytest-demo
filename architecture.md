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
| Browser               | Chromium; headless controlled by `BROWSER_HEADLESS` in `.env`; `--headed` CLI flag also works |
| Parallelism           | pytest-xdist from day one; function-scoped browser fixtures                       |
| Test data             | Pydantic model factories (builder classmethods with sensible defaults)            |
| UI auth               | Session storage snapshot fixture — login once per session, reuse across tests     |
| conftest layout       | Root `conftest.py` + one per feature folder                                       |
| Test structure        | `pytest` classes (`class TestXxx:`) — not `unittest.TestCase`                     |
| Failure artefacts     | Screenshot + Playwright trace captured automatically and attached to Allure       |
| Flaky test retry      | pytest-rerunfailures, 1 retry by default (configurable in `pyproject.toml`)       |
| Test markers          | `smoke`, `ui`, `api`, `slow`, `flaky`, `visual` — registered in `pyproject.toml` |
| Type annotations      | Type hints throughout; mypy strict mode enforced (`[tool.mypy] strict = true`)    |
| Logging               | Python `logging` module; `log_cli = true`; logs attached to Allure for every test |
| Response validation   | `BaseApiClient._validated()` wraps every `model_validate()`; attaches raw JSON to Allure on `ValidationError` |
| Flaky test detection  | `pytest_runtest_logreport` hook labels Allure results and prints terminal summary for tests that pass after `--reruns` |
| Visual regression     | Playwright `to_be_visible()` checks on key UI elements; failures write PNGs to `output/screenshots/` |

---

## Project Structure

### Source / test separation — mandatory convention

**Source code and test code live in separate top-level directories.**
`tests/` contains only `conftest.py` files and `test_*.py` files — no page objects, no API
clients, no models. All framework source (page objects, API clients, models, config) lives
in the feature packages at the project root. pytest discovers tests exclusively from `tests/`
(`testpaths = ["tests"]` in `pyproject.toml`), while `pythonpath = ["."]` makes every
top-level package importable from test files.

**All generated output goes under `output/`.** Allure results, the generated HTML report,
and per-worker log files are written to subdirectories of `output/` — never to the project
root or to `tests/`. The paths are set to absolute locations in `pytest_configure` so they
are correct regardless of the working directory (PyCharm, terminal, CI all produce the same
layout). `output/` is fully gitignored; only the empty `.gitkeep` markers are committed.

```
pytest-demo/
├── pyproject.toml              # uv / pytest / allure / dependency config
├── .env                        # local secrets and overrides (gitignored)
├── .env.example                # template checked into source control
├── .gitignore                  # excludes output/, .env, .venv/, __pycache__/
├── architecture.md             # this file
├── conftest.py                 # root fixtures + hooks (see Fixture Design)
│
├── output/                     # ALL generated artifacts — gitignored
│   ├── allure-results/         # raw JSON/attachment files written during test run
│   │   └── .gitkeep
│   ├── allure-report/          # generated HTML report (allure generate …)
│   ├── screenshots/            # failure screenshots written by _save_screenshot (created on demand)
│   └── logs/
│       ├── .gitkeep
│       └── test.log            # debug log; test_gw0.log … under xdist
│
├── core/                       # framework internals — no tests here
│   ├── base_page.py            # abstract BasePage
│   ├── base_api_client.py      # abstract BaseApiClient (Generic[T])
│   ├── ae_base_client.py       # AE-specific REST base (thin wrapper over BaseApiClient)
│   ├── ae_models.py            # shared AE response models (AeBaseResponse, AeMessageResponse)
│   ├── exceptions.py           # ApiError
│   ├── config.py               # Settings (Pydantic BaseSettings)
│   └── state_validators.py     # StateValidator — reusable UI and URL assertion helpers
│
├── models/
│   └── base_model.py           # AppBaseModel — shared alias + camelCase config
│
├── users/                      # JSONPlaceholder /users + AE login/register UI
│   ├── api/user_client.py      # UserApiClient(BaseApiClient)
│   ├── models/user_model.py    # CreateUserRequest, UserResponse
│   └── pages/
│       ├── login_page.py       # LoginPage(BasePage)
│       └── signup_page.py      # SignupPage(BasePage)
│
├── posts/                      # JSONPlaceholder /posts
│   ├── api/post_client.py      # PostApiClient(BaseApiClient)
│   └── models/post_model.py    # CreatePostRequest, PostResponse
│
├── products/                   # AE product catalogue UI
│   └── pages/
│       ├── home_page.py        # HomePage(BasePage)
│       ├── product_page.py     # ProductPage(BasePage)
│       ├── product_detail_page.py
│       └── cart_page.py        # CartPage(BasePage)
│
├── checkout/
│   └── pages/
│       ├── checkout_page.py    # CheckoutPage(BasePage)
│       └── payment_page.py     # PaymentPage(BasePage)
│
├── contact/
│   └── pages/contact_page.py  # ContactPage(BasePage)
│
├── ae_account/                 # AE REST account API
│   ├── api/ae_account_client.py
│   └── models/ae_account_model.py
│
├── ae_products/                # AE REST products API
│   ├── api/ae_products_client.py
│   └── models/ae_products_model.py
│
└── tests/                      # TEST SOURCE ONLY — no framework code here
    ├── users/
    │   ├── conftest.py
    │   ├── test_user_api.py
    │   ├── test_login_ui.py
    │   └── test_register_ui.py
    ├── posts/
    │   ├── conftest.py
    │   └── test_post_api.py
    ├── products/
    │   ├── conftest.py
    │   ├── test_product_ui.py
    │   ├── test_product_detail_ui.py
    │   ├── test_cart_ui.py
    │   ├── test_categories_brands_ui.py
    │   ├── test_subscription_ui.py
    │   └── test_product_visual.py      # visual regression snapshot tests
    ├── home/
    │   ├── conftest.py
    │   └── test_home_ui.py
    ├── checkout/
    │   ├── conftest.py
    │   ├── helpers.py              # non-fixture helpers shared across checkout tests
    │   └── test_checkout_ui.py
    ├── contact/
    │   ├── conftest.py
    │   └── test_contact_ui.py
    ├── ae_account/
    │   ├── conftest.py
    │   └── test_ae_account_api.py
    └── ae_products/
        ├── conftest.py
        └── test_ae_products_api.py
```

### `.env.example` content

```dotenv
# --- Required (no defaults — missing values raise ValidationError at startup) ---
AE_USERNAME=your_email@example.com
AE_PASSWORD=your_password

# --- Optional overrides (defaults shown) ---
API_BASE_URL=https://jsonplaceholder.typicode.com
UI_BASE_URL=https://automationexercise.com
BROWSER_HEADLESS=true    # set to false to open a visible browser window
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
# Both base_url and endpoint are abstract properties — concrete clients must
# implement them as @property methods, not plain class attributes. Assigning a
# class attribute over an abstract property is a mypy strict [override] error.
# Subclasses expose a domain-specific PUBLIC API; tests never call _get/_post directly.
class UserApiClient(BaseApiClient[UserResponse]):
    _response_model = UserResponse        # ← required; drives model_validate in base

    @property
    def base_url(self) -> str:
        return self._settings.api_base_url

    @property
    def endpoint(self) -> str:
        return "/users"

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
    _response_model = PostResponse

    @property
    def base_url(self) -> str:
        return self._settings.api_base_url

    @property
    def endpoint(self) -> str:
        return "/posts"

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
3. Raises `ApiError` on non-2xx status codes **and attaches the raw response body to Allure**
   as a `TEXT` attachment named `error-response-{status}`. This means every API failure in
   the Allure report includes the full error payload for post-mortem analysis without
   needing to reproduce the failure.
4. Calls `self._validated(response.json())` and returns the result. `_validated` is a
   thin wrapper around `model_validate` that catches `ValidationError`, attaches the raw JSON
   to Allure as `schema-validation-failure`, then re-raises. This surfaces the actual
   response body when the API returns an unexpected shape.

Step 3 must precede step 4: a non-2xx body (e.g. `{}` from a 404) would fail
`model_validate` with a Pydantic `ValidationError` before `ApiError` is ever raised,
making `pytest.raises(ApiError)` unreachable.

`_get_many` (list response) differs at step 4 — a JSON array cannot be passed to
`model_validate` on a single-item model. The implementation calls `_validated` per element:
```python
return [self._validated(item) for item in response.json()]
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

### `core/ae_base_client.py` and `core/ae_models.py` — AE-specific REST layer

The automationexercise.com API does not follow standard HTTP semantics: every endpoint
returns HTTP 200 regardless of success or failure and embeds the real status code in the
JSON body as `responseCode`. `AeBaseClient` is a separate base class from `BaseApiClient`
that handles this quirk.

```
AeBaseClient (ABC)
  ├── __init__(context: APIRequestContext, settings: Settings)
  ├── _base_url → str       ← reads settings.ae_api_base_url; not an abstract property
  ├── _get(path, params)  → dict[str, Any]
  ├── _post(path, form)   → dict[str, Any]   # form=None sends an empty form body
  ├── _put(path, form)    → dict[str, Any]
  └── _delete(path, form) → dict[str, Any]
```

All helpers return raw `dict[str, Any]`. Each concrete method in the client subclass
calls `SomeModel.model_validate(raw)` explicitly, which keeps the return type visible
in the public API signature rather than hidden in a generic base.

**Shared AE response models** live in `core/ae_models.py` — not in domain model files:

```python
# core/ae_models.py
class AeBaseResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    response_code: int = Field(alias="responseCode")

class AeMessageResponse(AeBaseResponse):
    message: str
```

`AeBaseResponse` and `AeMessageResponse` are shared across both `ae_account` and
`ae_products`. Domain model files (`ae_account/models/`, `ae_products/models/`) import
`AeBaseResponse` from `core.ae_models` for inheritance and define their own
feature-specific response types there. Client files (`ae_account/api/`, `ae_products/api/`)
import `AeMessageResponse` directly from `core.ae_models` — not through the domain model
re-export — keeping the import chain unambiguous.

```python
# ae_account/api/ae_account_client.py — correct import pattern
from ae_account.models.ae_account_model import AeCreateAccountRequest, AeUserDetailResponse
from core.ae_models import AeMessageResponse   # shared type from core, not re-exported
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
  ├── current_url → str              ← public read-only view of the browser's current URL
  │     tests assert on this instead of accessing _page.url directly
  ├── is_loaded() → None (abstract)
  │     subclass calls expect(locator).to_be_visible() on a stable landmark element.
  │     Playwright's built-in retry+timeout handles the wait — do not use time.sleep().
  │     Raises AssertionError/TimeoutError if the element never appears; navigate() propagates it.
  └── _click_and_navigate(locator, target_url) → None
        clicks the locator, waits for domcontentloaded, falls back to goto() if the URL
        didn't change, then always calls _dismiss_consent_banner() regardless of which
        navigation path was taken.
```

#### Locator fields — mandatory convention

Every locator used by a page object **must be declared as a `@property` on the class**, not
constructed inline inside the method that uses it. This keeps selectors in one place,
makes them reusable across methods, and makes selector changes a one-line edit.

```python
class LoginPage(BasePage):
    @property
    def url(self) -> str:
        return f"{self._settings.ui_base_url}/login"

    # Locators — one @property per distinct element
    @property
    def _login_email(self):
        return self._page.locator("input[data-qa='login-email']")

    @property
    def _login_password(self):
        return self._page.locator("input[data-qa='login-password']")

    @property
    def _login_button(self):
        return self._page.locator("button[data-qa='login-button']")

    @property
    def _login_error(self):
        return self._page.locator("p:has-text('Your email or password is incorrect!')")

    # Actions — use locator properties, never re-construct the locator here
    def is_loaded(self) -> None:
        expect(self._login_email).to_be_visible()

    def login(self, username: str, password: str) -> None:
        self._login_email.fill(username)
        self._login_password.fill(password)
        self._login_button.click()

    def get_error_message(self) -> str:
        return self._login_error.inner_text()
```

Locators that depend on a method parameter (e.g. `a[href='#Men']` where "Men" is passed
in) cannot be extracted as fixed properties — they remain inline in the method body. All
*static* locators must be properties.

Playwright `Locator` objects are lazy — they hold only the selector string and a reference
to `_page`. Each property access constructs a new `Locator` instance; there is no DOM
query until the locator is acted on. `@property` is therefore safe and correct: no
memoisation is needed, and the locator reflects the current page state on every use.

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
  ├── api_base_url: str        = "https://jsonplaceholder.typicode.com"
  ├── ui_base_url: str         = "https://automationexercise.com"
  ├── browser_headless: bool   = True    ← False opens a visible browser window
  ├── browser_timeout: int     = 30_000  ← ms; passed to context.set_default_timeout()
  ├── api_timeout: int         = 10_000  ← ms; passed to APIRequestContext timeout option
  ├── ae_username: str                   ← required; no default — must be set in .env
  ├── ae_password: SecretStr             ← required; no default — SecretStr hides it from logs
  └── model_config = SettingsConfigDict(env_file=".env")
```

`ae_username` and `ae_password` have no defaults intentionally. Pydantic raises a clear
`ValidationError: field required` at fixture setup time if either is missing from `.env`,
rather than silently passing empty credentials to the login page and producing a confusing
UI failure deep inside the test run.

`browser_headless` is read from `.env` as `BROWSER_HEADLESS=false` to show the browser
during local development. The `browser_type_launch_args` session fixture injects this
value into pytest-playwright's launch arguments. The `--headed` CLI flag also works and
takes precedence (pytest-playwright merges it with the fixture args).

Tests receive `Settings` via fixture injection; they never read `os.environ` directly.
`browser_context` applies `context.set_default_timeout(settings.browser_timeout)` after creation.
`api_context` passes `timeout=settings.api_timeout` to `new_context(...)`.

---

## Fixture Design

### pytest-playwright fixture layering

`pytest-playwright` already provides `playwright`, `browser`, `browser_context`, and `page`
fixtures. Our root `conftest.py` **overrides** `browser_context` and `page` (same names) to
inject auth state and start tracing, and adds `browser_type_launch_args` to wire the
`BROWSER_HEADLESS` setting into the browser launch. The built-in `playwright` and low-level
`browser` fixtures are used as-is; we do not redeclare them.

```python
# Injects the BROWSER_HEADLESS setting into playwright's launch arguments.
# The spread **browser_type_launch_args preserves any other flags already present
# (e.g. --headed CLI flag, slow_mo, etc.) so both mechanisms work together.
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args: dict, settings: Settings) -> dict:
    return {**browser_type_launch_args, "headless": settings.browser_headless}
```

### Root `conftest.py` (parallel-safe with pytest-xdist)

```python
@pytest.fixture(scope="session")
def settings() -> Settings:
    return Settings()

# live_account: session-scoped account created once via the AE REST API and
# deleted in teardown.  All authenticated UI tests share it; the actual
# credentials never appear in Settings or test code.
@pytest.fixture(scope="session")
def live_account(_ae_api_context, settings) -> Generator[dict[str, str], None, None]:
    yield from _account_lifecycle(AeAccountClient(context=_ae_api_context, settings=settings))

# temp_account: function-scoped — a fresh account per test.  Used by tests
# that mutate or delete the account (so they don't interfere with live_account).
@pytest.fixture
def temp_account(api_context, settings) -> Generator[dict[str, str], None, None]:
    yield from _account_lifecycle(AeAccountClient(context=api_context, settings=settings))

# Module-level constant — one place to change the shared test password.
_TEST_PASSWORD = "Test1234!"

# _account_lifecycle: helper (not a fixture) that creates an account before
# yield and deletes it in a try/finally so cleanup always runs even if the
# test itself deletes the account first.
def _account_lifecycle(client):
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

# disposable_credentials: yields a name/email/password dict and deletes the
# account at teardown.  Used by tests that create an account through the UI
# (not via the API) — the teardown API call cleans up after the UI flow.
@pytest.fixture
def disposable_credentials(api_context, settings) -> Generator[dict[str, str], None, None]:
    email = f"pytest_{uuid.uuid4().hex[:8]}@test.com"
    creds = {"name": "Pytest User", "email": email, "password": _TEST_PASSWORD}
    yield creds
    try:
        AeAccountClient(api_context, settings).delete_account(
            email=creds["email"], password=creds["password"]
        )
    except Exception as exc:
        _logger.warning("Account deletion failed for %s: %s", creds["email"], exc)

# _ae_api_context: session-scoped APIRequestContext used exclusively by
# live_account.  Kept separate from the function-scoped api_context so the
# session account fixture does not force a new HTTP context for every test.
@pytest.fixture(scope="session")
def _ae_api_context(playwright, settings) -> Generator[APIRequestContext, None, None]:
    context = playwright.request.new_context(timeout=settings.api_timeout)
    yield context
    context.dispose()

# auth_state: session-scoped but xdist-safe via tmp_path_factory + filelock.
# Depends on live_account (not on settings.ae_username directly) so the
# credentials are always the same account the session fixture keeps alive.
# After login, validates that the URL changed away from /login before saving
# storage state — a missing redirect would silently give every test an
# unauthenticated context, producing confusing failures far from the cause.
@pytest.fixture(scope="session")
def auth_state(browser, live_account, settings, tmp_path_factory) -> Path:
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

# Override pytest-playwright's page. Just creates and closes the page;
# screenshot capture is handled by pytest_runtest_makereport (see below).
@pytest.fixture
def page(browser_context):
    pw_page = browser_context.new_page()
    yield pw_page
    pw_page.close()

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
# Creates output directories so they exist for every run (CI and local).
# Sets the Allure results directory and the per-worker log file path here —
# using absolute paths derived from config.rootpath so they are correct
# regardless of the working directory (PyCharm, terminal, CI).
# Without the per-worker log path, all xdist workers write to the same
# logs/test.log simultaneously → PermissionError or corrupted output on Windows.
def pytest_configure(config):
    output_dir = config.rootpath / "output"
    allure_dir = output_dir / "allure-results"
    logs_dir   = output_dir / "logs"
    allure_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if hasattr(config.option, "allure_report_dir"):
        config.option.allure_report_dir = str(allure_dir)

    worker_id = os.environ.get("PYTEST_XDIST_WORKER")
    log_name = f"test_{worker_id}.log" if worker_id else "test.log"
    config.option.log_file = str(logs_dir / log_name)

# Sets rep_call/rep_setup/rep_teardown on the item for fixture teardown checks,
# and captures a screenshot directly into the Allure test result on call-phase failure.
# Screenshot is taken here — not in the page fixture teardown — because allure-pytest
# keeps the test result open during the call phase. Attachments added in fixture teardown
# land in the fixture's container (shown only under "Tear Down"), not in the test result.
# Bytes are captured once and passed to both allure.attach and _save_screenshot to avoid
# a second Playwright call.
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    rep = yield
    setattr(item, f"rep_{rep.when}", rep)
    if rep.when == "call" and rep.failed:
        pw_page = item.funcargs.get("page") or item.funcargs.get("unauthenticated_page")
        if pw_page:
            try:
                png = pw_page.screenshot()
                allure.attach(png, name="screenshot", attachment_type=allure.attachment_type.PNG)
                _save_screenshot(item, png)
            except Exception:
                pass
    return rep

# Writes the screenshot bytes to output/screenshots/<slug>.png so failures can be
# inspected directly on disk without opening the Allure report.
def _save_screenshot(item, png: bytes) -> None:
    slug = item.nodeid.replace("/", "_").replace("::", "_").replace("[", "_").replace("]", "")
    screenshots_dir = item.config.rootpath / "output" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    (screenshots_dir / f"{slug}.png").write_bytes(png)

# Attaches the Playwright trace after test failure.
# Takes trace_path as a direct parameter (autouse pulls it in for every test).
# The exists() guard makes it a no-op for API tests and any test that did not
# start a tracing session — trace_path is just a Path object with no side effects.
@pytest.fixture(autouse=True)
def attach_trace_on_failure(request, trace_path):
    yield
    if not (getattr(request.node, "rep_call", None) and request.node.rep_call.failed):
        return
    if trace_path.exists():
        allure.attach.file(str(trace_path), name="trace",
                           attachment_type=allure.attachment_type.ZIP)
```

# unauthenticated_page lives in the ROOT conftest — it is used by tests across
# multiple feature folders (users, checkout, products) so it must be globally
# available.  It bypasses auth_state entirely: no storage_state → no session
# cookie → browser starts unauthenticated.
# Trace handling is inline (stop+attach on failure, discard on pass) because
# this fixture owns its own BrowserContext and cannot delegate to
# attach_trace_on_failure (which only covers contexts created via browser_context).
# Screenshot on failure is handled by pytest_runtest_makereport, which also
# checks item.funcargs.get("unauthenticated_page") — no duplication needed here.
@pytest.fixture
def unauthenticated_page(browser, settings, tmp_path, request):
    context = browser.new_context()   # no storage_state — fresh unauthenticated session
    context.set_default_timeout(settings.browser_timeout)
    trace_zip = tmp_path / "trace.zip"
    context.tracing.start(screenshots=True, snapshots=True)
    pw_page = context.new_page()
    yield pw_page
    if getattr(request.node, "rep_call", None) and request.node.rep_call.failed:
        context.tracing.stop(path=str(trace_zip))
        allure.attach.file(str(trace_zip), name="trace",
                           attachment_type=allure.attachment_type.ZIP)
    else:
        context.tracing.stop()   # discard trace on pass to save disk space
    pw_page.close()
    context.close()
```

Root `conftest.py` also defines `home_page` — a fixture used across both `tests/home/`
and `tests/products/`. Shared page-object fixtures belong at the root rather than in a
single feature conftest so they do not need to be duplicated:

```python
@pytest.fixture
def home_page(page: Page, settings: Settings) -> HomePage:
    return HomePage(page=page, settings=settings)
```

### Feature `conftest.py` (e.g. `tests/users/conftest.py`)

```python
@pytest.fixture
def user_client(api_context, settings) -> UserApiClient:
    return UserApiClient(context=api_context, settings=settings)
```

Feature conftests declare only fixtures — thin wrappers that construct a page object or
client with the right fixtures injected. Tests that need a `LoginPage` construct it
directly: `LoginPage(page=unauthenticated_page, settings=settings).navigate()`. Adding a
`login_page` fixture here would hide the intent and create an unused symbol whenever a
test file already builds the page inline.

Page-object fixtures that are used in more than one feature folder are defined in root
`conftest.py` (e.g. `home_page`), not duplicated across sub-conftests.

Tests that exercise the login form itself (credential validation, redirect on success,
error messaging) must start unauthenticated and use `unauthenticated_page` from the root
conftest instead of the pre-authenticated `page`.

`unauthenticated_page` bypasses `auth_state` so the session cookie is absent.
Because it owns its context, it manages its own tracing inline rather than delegating
to `attach_trace_on_failure` (which only covers contexts created via the root `browser_context`).

### Resource Cleanup Registry

`ResourceRegistry` (defined in root `conftest.py`) provides a LIFO cleanup guarantee for
tests that create multiple resources and cannot rely on a single `yield` teardown.

```python
@pytest.fixture
def resource_registry() -> Generator[ResourceRegistry, None, None]:
    registry = ResourceRegistry()
    yield registry
    registry.cleanup_all()   # runs in reverse registration order after the test
```

Usage in a test:

```python
def test_account_lifecycle(
    resource_registry: ResourceRegistry,
    ae_account_client: AeAccountClient,
) -> None:
    payload = AeCreateAccountRequest.make()
    ae_account_client.create_account(payload)

    # Register cleanup immediately after creation — before any assertion.
    resource_registry.register(
        "account",
        payload.email,
        lambda: ae_account_client.delete_account(
            email=payload.email, password=payload.password
        ),
    )

    response = ae_account_client.get_user_detail(email=payload.email)
    assert response.user.email == payload.email
    # cleanup_all() runs at teardown regardless of whether the assert passed
```

Key design decisions:
- **LIFO order** — resources are cleaned up in reverse registration order so nested
  dependencies (e.g. an order that depends on an account) are torn down correctly.
- **Exception isolation** — each cleanup call is wrapped in `try/except`; a failed
  cleanup is logged as WARNING but does not prevent subsequent cleanups from running.
- **Explicit registration** — resources must be registered immediately after creation,
  before any assertion. An assertion failure between creation and `register()` would
  leave an orphaned resource. The pattern `create → register → assert` enforces this.

`resource_registry` is function-scoped and opt-in. It is not autouse — only tests that
explicitly request it pay the overhead of the registry object.

### Test helper functions — use `helpers.py`, not `conftest.py`

Non-fixture helper functions shared within a test folder belong in a `helpers.py` module,
not in `conftest.py`. Conftest files are collected by pytest's plugin mechanism and are not
intended to be imported directly by test files. Importing from `conftest.py` works in
practice but is an antipattern that can cause double-collection issues and fragile path
coupling.

```python
# tests/checkout/helpers.py
from playwright.sync_api import Page
from core.config import Settings
from products.pages.cart_page import CartPage
from products.pages.product_page import ProductPage

def add_product_and_checkout(page: Page, settings: Settings) -> None:
    """Add first product to cart and proceed to checkout page."""
    product_pg = ProductPage(page=page, settings=settings)
    product_pg.navigate()
    product_pg.add_to_cart(index=0)
    product_pg.view_cart_from_modal()
    CartPage(page=page, settings=settings).proceed_to_checkout()

# tests/checkout/test_checkout_ui.py
from tests.checkout.helpers import add_product_and_checkout  # ← import from helpers, not conftest
```

### `core/state_validators.py` — explicit post-action assertions

`StateValidator` provides named, Allure-wrapped assertion helpers for common
post-action checks. Each method creates an `allure.step` so the assertion appears in
the report timeline with a human-readable label, and logs at INFO level for the test log.

```python
class StateValidator:
    @staticmethod
    def assert_logged_in(page: Page) -> None:
        with allure.step("Assert authenticated session is active"):
            expect(page.locator("a[href='/logout']")).to_be_visible()

    @staticmethod
    def assert_logged_out(page: Page) -> None:
        with allure.step("Assert no authenticated session"):
            expect(page.locator("a[href='/logout']")).not_to_be_visible()
            expect(page.locator("a[href='/login']")).to_be_visible()

    @staticmethod
    def assert_url_contains(page: Page, fragment: str) -> None: ...

    @staticmethod
    def assert_url_excludes(page: Page, fragment: str) -> None: ...

    @staticmethod
    def assert_text_visible(page: Page, text: str) -> None: ...
```

Usage in a test:

```python
from core.state_validators import StateValidator

def test_logout_redirects_to_login(self, page: Page, ...) -> None:
    page.locator("a[href='/logout']").click()
    StateValidator.assert_logged_out(page)
    StateValidator.assert_url_contains(page, "/login")
```

`StateValidator` methods use only Playwright `expect()` and standard assertions — they
have no dependencies on specific page objects and are usable from any test. The class
exists purely for namespace organisation; all methods are `@staticmethod`.

`tests/checkout/conftest.py` keeps only fixture definitions (`registered_page`, etc.).
`registered_page` is a regular fixture (not a generator) because it has no teardown — it
creates an account via the API, logs in, and returns the page. Account cleanup is handled
entirely by the `disposable_credentials` fixture:

```python
@pytest.fixture
def registered_page(
    unauthenticated_page: Page,
    settings: Settings,
    disposable_credentials: dict[str, str],
    api_context: APIRequestContext,
) -> Page:
    AeAccountClient(api_context, settings).create_account(
        AeCreateAccountRequest.make(
            name=disposable_credentials["name"],
            email=disposable_credentials["email"],
            password=disposable_credentials["password"],
        )
    )
    LoginPage(unauthenticated_page, settings).navigate().login(
        username=disposable_credentials["email"],
        password=disposable_credentials["password"],
    )
    return unauthenticated_page
```

Use `yield` only when the fixture has cleanup code after the yield. A fixture with nothing
after `yield` is functionally identical to `return`, but the `Generator` return type
annotation is misleading.

---

## Failure Artefacts

Two separate mechanisms handle failure capture, each timed to when its data is available:

**Screenshot** — captured inside `pytest_runtest_makereport` during the `"call"` phase,
immediately after the test body raises. The bytes are captured once and used for two
destinations: `allure.attach()` adds the image to the active test result (visible at the
top of the Allure report), and `_save_screenshot()` writes the same bytes to
`output/screenshots/<slug>.png` on disk for direct inspection without opening the report.
Capturing in fixture teardown instead would attach to the fixture's container (`afters`),
making the screenshot appear only under the collapsed "Tear Down" section — not at the
top of the report where it is most useful. `item.funcargs` still holds all live fixture
objects during the call phase so `page.screenshot()` works.

**Trace** — attached by `attach_trace_on_failure` (autouse), which runs after `browser_context`
teardown has already written `trace.zip` to `trace_path`. This ordering is safe because the
autouse fixture (no dependencies on browser fixtures) is set up before the explicitly-requested
fixtures, and therefore tears down after them (pytest LIFO).

Both rely on `request.node.rep_call.failed`, which is set by the `pytest_runtest_makereport`
hook. Without this hook the attribute is absent and both captures silently no-op.

### xdist + rerunfailures incompatibility

`pytest-xdist` (`-n auto`) and `pytest-rerunfailures` (`--reruns`) **cannot be active at
the same time** — rerunfailures explicitly disables itself under xdist. The strategy is:

- Normal development / CI fast run: `pytest -n auto` (parallel, no reruns).
- Flaky-detection / stability run: `pytest --reruns 1 --reruns-delay 2` (serial, with retries).
Run both profiles directly with `uv run`:

```
uv run pytest -n auto                      # parallel
uv run pytest --reruns 1 --reruns-delay 2  # serial with retries
```

`addopts` in `pyproject.toml` is intentionally empty — neither flag is baked in because
they are mutually exclusive. The allure results directory is set in `pytest_configure`
(not via `addopts`) so it resolves to an absolute path under `output/` regardless of
the working directory.

### Flaky Test Detection

A `pytest_runtest_logreport` hook in root `conftest.py` turns invisible retries into
observable signal in both the Allure report and the terminal.

```
test_foo FAILED  → outcome == "rerun"   → node ID added to _rerun_nodeids (scratch set)
test_foo PASSED  → node ID in scratch   → allure.dynamic.label("flakiness", "flaky")
                                        → node ID moved to _passed_after_retry (reporting set)
```

When `--reruns` is active and a test fails then passes:
- **Allure label** `flakiness=flaky` is attached to the final passing result so the report
  surface shows the test as "passed but unstable" rather than simply "passed".
- **Terminal summary** — `pytest_terminal_summary` prints a `tests that passed after retry
  (flaky)` section at the bottom of the run output listing each affected node ID.

Two module-level sets power the detection. `_rerun_nodeids` is a scratch set: IDs are
added on `"rerun"` outcome and removed when the same ID later passes. `_passed_after_retry`
is the reporting set that drives the terminal summary — it is never cleared so the summary
accurately lists every node that flaked during the session.

Tests with known, accepted instability can be tagged explicitly with `@pytest.mark.flaky`
and excluded or isolated with `-m "not flaky"`. The hook still detects them at runtime;
the marker is documentary.

`allure.dynamic.label` requires an active Allure test context. Conftest hooks have higher
pytest priority than installed plugins, so the hook fires while allure-pytest's listener
still holds the test result open. Under xdist (where tests run in worker processes),
`_rerun_nodeids` in the controller process is still populated via relayed
`pytest_runtest_logreport` events, so the terminal summary works; the Allure label call
is wrapped in `contextlib.suppress(Exception)` to degrade gracefully if the worker's
allure context is not accessible from the controller.

---

## Test Class Shape

```python
@allure.feature("Users API")
@allure.story("Retrieve User by ID")
@pytest.mark.api
@pytest.mark.smoke
class TestGetUser:
    def test_returns_valid_schema(self, user_client: UserApiClient) -> None:
        user = user_client.get(user_id=1)   # validated → UserResponse inside client
        assert user.id == 1

    def test_name_is_non_empty(self, user_client: UserApiClient) -> None:
        user = user_client.get(user_id=1)
        assert user.name

    @pytest.mark.parametrize("user_id", [1, 3, 5, 7, 10])
    def test_valid_id_returns_matching_user(
        self, user_client: UserApiClient, user_id: int
    ) -> None:
        user = user_client.get(user_id=user_id)
        assert user.id == user_id
        assert user.name
        assert user.email
```

### Allure feature/story metadata

Class-level `@allure.feature` and `@allure.story` decorators are applied to every test
class. They do not affect test execution but populate Allure's **Features** and
**Stories** tree, which groups results by domain rather than by file path.

```
@allure.feature("Posts API")   → top-level grouping in the Features tab
@allure.story("Create Post")   → sub-grouping under the feature
```

`@allure.feature` / `@allure.story` are placed before pytest markers so the decorator
stack reads domain → runner concern top-to-bottom.

### Parametrized tests

`@pytest.mark.parametrize` multiplies a single test body across input variants without
duplicating test classes. Each parameter set appears as a separate node in the Allure
report and in the pytest output.

```python
@pytest.mark.parametrize("title,body", [
    ("Short", "Brief content."),
    ("A" * 80, "Body with a maximum-length title."),
    ("Unicode: café 北京", "Body content with unicode characters."),
])
def test_various_payloads_return_generated_id(
    self, post_client: PostApiClient, title: str, body: str
) -> None:
    post = post_client.create(CreatePostRequest.make(title=title, body=body))
    assert post.id > 0
    assert post.title == title
    assert post.body == body
```

Parametrize for input variety (IDs, payloads, user names) — not for assertion variety.
Each assertion should remain a separate test method so failures are isolated.
Every parametrize argument must be asserted in the test body; an argument that is passed
to the API but never verified adds no coverage.

### Asserting on the browser URL

Use `page_object.current_url` — never access `page_object._page.url` or
`page_object._settings` directly from a test. Page object internals are private by
convention (single underscore); tests that reach into them break encapsulation and
become fragile if the implementation changes.

```python
# CORRECT
home_page.go_to_test_cases()
assert "/test_cases" in home_page.current_url.split("#")[0]

# WRONG — leaks private internals
assert "/test_cases" in home_page._page.url.split("#")[0]
```

When a test needs to assert against a configured value (e.g. `ui_base_url`), request
the `settings` fixture explicitly rather than reading `page_object._settings`.

---

## Allure Step Decoration and Report Metadata

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

### Dynamic Allure attributes — flaky label and error attachments

`allure.dynamic.*` can be called anywhere inside a running test to modify the active
Allure result. The framework uses two dynamic calls automatically:

- **`allure.dynamic.label("flakiness", "flaky")`** — added by the `pytest_runtest_logreport`
  hook when a test passes after a `--reruns` retry. No per-test annotation required.
- **`allure.attach(...)`** — added by `_raise_for_status` (raw error response body on HTTP
  errors) and `_validated` (raw JSON on schema validation failure). Both attach to the
  currently active Allure step automatically.

`StateValidator` methods use `with allure.step(...)` (context manager, not decorator)
because they are static utility functions called from inside test bodies, not methods
decorated at definition time. This is the correct usage of the context manager form.

**Do not mix `@allure.step` with `with allure.step()` inside the same method.** The
decorator already wraps the entire method body in a step; adding a `with allure.step()`
block inside creates a redundant nested step in the report. Use one or the other:

```python
# CORRECT — decorator only
@allure.step("Navigate to product details for product {product_id}")
def navigate_to(self, product_id: int) -> Self:
    self._page.goto(...)
    self.is_loaded()
    return self

# WRONG — decorator + inner with creates a duplicate nested step
@allure.step("Navigate to product details for product {product_id}")
def navigate_to(self, product_id: int) -> Self:
    with allure.step(f"Navigate to /product_details/{product_id}"):  # redundant
        self._page.goto(...)
```

---

## Logging

`BaseApiClient` and `BasePage` each hold a module-level `logging.getLogger(__name__)`.
Every HTTP request/response and every `navigate()` call emits a `DEBUG` line.

pytest routes log records to three independent sinks, each with its own format key:

| Sink | Level key | Format key | Controls |
|---|---|---|---|
| Console (live) | `log_cli_level` | `log_cli_format` | Terminal output during the run |
| File | `log_file_level` | `log_file_format` | `output/logs/test.log` |
| In-memory capture | *(inherited)* | `log_format` | Allure log attachment, pytest report section |

All three format strings use `%(asctime)s` so every log line carries a timestamp.
`log_date_format` is a shared key that controls the `%(asctime)s` rendering for all sinks:

```toml
log_format      = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
log_cli_format  = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
log_file_format = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"
```

`log_format` (the in-memory sink) must be set explicitly — it is not a fallback for
`log_cli_format` or `log_file_format`. Omitting it produces Allure log attachments without
timestamps even when the other two sinks are correctly formatted.

`allure-pytest` attaches in-memory captured logs to every test's report automatically —
pass and fail alike — with no extra fixture code required.

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
# addopts is empty — -n auto and --reruns are mutually exclusive; pass them directly.
# alluredir and log_file are set in pytest_configure (absolute paths under output/).
addopts        = ""
testpaths      = ["tests"]
pythonpath     = ["."]
log_cli        = true
log_cli_level  = "INFO"           # concise terminal output; avoids flood in parallel runs
log_file_level = "DEBUG"          # full request/response detail in file for post-mortem
# Three format keys needed — one per sink (console, file, Allure in-memory capture):
log_format      = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
log_cli_format  = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
log_file_format = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
log_date_format = "%Y-%m-%d %H:%M:%S"
markers = [
    "smoke: critical-path tests",
    "api: REST API tests",
    "ui: browser UI tests",
    "slow: long-running end-to-end flows",
]

[dependency-groups]
dev = ["mypy>=2.1.0"]

[tool.mypy]
strict = true
explicit_package_bases = true
exclude = ["\\.venv"]
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = ["allure.*", "filelock.*"]
ignore_missing_imports = true
# Run: uv run mypy conftest.py core/ models/ users/ posts/ products/ checkout/ contact/ ae_account/ ae_products/ tests/
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
       _response_model = ReqresUserResponse

       @property
       def base_url(self) -> str:
           return self._BASE_URL

       @property
       def endpoint(self) -> str:
           return "/api/users"

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

## Visual Regression Testing

`tests/products/test_product_visual.py` contains visual sanity tests tagged
`@pytest.mark.visual` so they can be excluded from normal runs with `-m "not visual"`.

These tests use `unauthenticated_page` because the pages under test (home, product
listing) are publicly accessible — no auth session is needed. Using `unauthenticated_page`
avoids the `live_account` session fixture entirely, so the visual tests do not depend on
the AE account API being reachable.

```python
@pytest.mark.ui
@pytest.mark.visual
class TestProductVisualRegression:
    def test_home_page_hero_banner(self, unauthenticated_page: Page, settings: Settings) -> None:
        HomePage(page=unauthenticated_page, settings=settings).navigate()
        expect(unauthenticated_page.locator(".item.active").first).to_be_visible()

    def test_product_listing_grid(self, unauthenticated_page: Page, settings: Settings) -> None:
        ProductPage(page=unauthenticated_page, settings=settings).navigate()
        expect(unauthenticated_page.locator(".features_items")).to_be_visible()
```

Visual tests assert element visibility rather than pixel-exact snapshots. This avoids
the baseline management overhead of `to_have_screenshot()` (committed PNG files,
`--update-snapshots` workflow, CI flakiness from rendering differences). When a visual
test fails, `pytest_runtest_makereport` captures a full-page screenshot and writes it to
`output/screenshots/<test-slug>.png` for direct inspection — no Allure report needed
to see what the page looked like at failure time.

Note on `.first` — `.item.active` matches two carousel containers on the home page.
`locator(...).first` pins the assertion to the hero carousel, avoiding Playwright's
strict-mode error for multi-match locators.

---

## CI / GitHub Actions

The workflow at `.github/workflows/ci.yml` triggers on every push and on manual dispatch.

### What the workflow does

1. Installs uv, syncs dependencies from the lockfile (`--frozen`), installs Chromium with system dependencies.
2. Runs the full test suite (`uv run pytest`) with credentials injected from GitHub Secrets.
3. Fetches the `gh-pages` branch to restore Allure's `history/` directory, which powers the trend graph.
4. Generates the HTML report with `allure generate`.
5. Deploys to GitHub Pages in three steps:
   - Full report → `/<run_number>/` (every run is preserved)
   - `history/` directory → `/history/` (shared across runs; picked up by the next run)
   - Root `index.html` → `/` (meta-refresh redirect to the latest run number)

Result: `https://<user>.github.io/<repo>/` always opens the latest report; previous runs remain browsable at `/<run_number>/`.

### One-time repository setup

1. Add two repository secrets (**Settings → Secrets → Actions**):
   - `AE_USERNAME` — automationexercise.com login email
   - `AE_PASSWORD` — automationexercise.com password
2. After the first workflow run creates the `gh-pages` branch, enable GitHub Pages (**Settings → Pages**):
   - Source: **Deploy from a branch**
   - Branch: `gh-pages` / `/ (root)`

The first run will not have trend history (no previous `gh-pages` branch). All subsequent runs will carry the Allure history forward.

---

## Verification Checklist

1. `uv run pytest tests/users/test_user_api.py -v` — API smoke, schema validation.
2. `uv run pytest tests/products/test_product_ui.py -v --headed` — UI smoke with visible browser.
3. `uv run pytest -n auto` — parallel run; confirms no shared-state fixture collisions.
4. `allure serve output/allure-results` — report renders with steps, logs, and artefacts.
5. `uv run pytest -m smoke --co -q` — confirms marker collection covers expected tests.
6. `uv run pytest --reruns 1 --reruns-delay 2 -v` — flaky detection run; check terminal summary and Allure `flakiness` label on any retry-passed test.
7. `uv run pytest -m visual` — run visual sanity tests; on failure, check `output/screenshots/` for the captured page state.
8. `uv run pytest -m "not visual"` — standard run excluding visual tests.
