from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    api_base_url: str = "https://jsonplaceholder.typicode.com"
    ui_base_url: str = "https://automationexercise.com"
    browser_headless: bool = True
    browser_timeout: int = 30_000
    api_timeout: int = 10_000
    ae_api_base_url: str = "https://automationexercise.com/api"
    ae_username: str
    ae_password: SecretStr

    model_config = SettingsConfigDict(env_file=_ENV_FILE)
