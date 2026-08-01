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
    cost_p95_brl_per_run: float = 1.10  # CAR-7 gate P95 (rounded; see docs/reports/*-cost-gate.md)
    cost_buffer_factor: float = 1.10

    # Auth scaffold (CAR-23 / ADR-003) — anon JWT; Borderless issuer in F3
    jwt_secret: str = "career-forge-dev-jwt-secret-change-me-32b+"
    jwt_anon_ttl_days: int = 90
    # CAR-26 — short-lived forge SSE stream ticket (Bearer → ?ticket=)
    jwt_stream_ticket_ttl_seconds: int = 300

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
