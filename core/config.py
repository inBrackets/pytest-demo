from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_base_url: str = "https://jsonplaceholder.typicode.com"
    ui_base_url: str = "https://automationexercise.com"
    browser_timeout: int = 30_000
    api_timeout: int = 10_000
    ae_username: str
    ae_password: SecretStr

    model_config = SettingsConfigDict(env_file=".env")
