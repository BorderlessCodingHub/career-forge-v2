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

    # Cost instrumentation (CAR-6) — hard stop pool + per-user forge cap
    monthly_api_budget_brl: float = 500.0
    forge_cap_per_user_month: int = 2
    cost_p95_brl_per_run: float = 1.0  # stub until CAR-7 measures real P95
    cost_buffer_factor: float = 1.10

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
