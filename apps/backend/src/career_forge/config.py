from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"
    database_url: str = (
        "postgresql+psycopg://careerforge:careerforge@localhost:5432/careerforge"
    )
    env: str = "production"
    debug: bool = False
    log_dir: str = "logs"
    diagnosis_interview_model: str = "gpt-4.1-nano"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def local_file_logging(self) -> bool:
        return self.debug or self.env.lower() == "local"


settings = Settings()
