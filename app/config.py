from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ShieldPack"
    app_version: str = "0.2.0"
    debug: bool = True
    hibp_api_key: str = ""
    enable_email_check: bool = False
    request_timeout: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
