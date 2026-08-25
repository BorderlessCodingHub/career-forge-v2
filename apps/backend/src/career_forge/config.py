from pydantic_settings import BaseSettings, SettingsConfigDict

# Source-controlled local default — never valid when ENV=production (CAR-83).
DEV_JWT_SECRET = "career-forge-dev-jwt-secret-change-me-32b+"


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
    cost_p95_brl_per_run: float = 1.3639  # F2 re-cost forge P95 (CAR-33; docs/reports/2026-08-06-cost-gate.md)
    cost_buffer_factor: float = 1.10

    # Auth scaffold (CAR-23 / ADR-003) — anon JWT; email OTP IdP in F3b (CAR-44)
    jwt_secret: str = DEV_JWT_SECRET
    jwt_anon_ttl_days: int = 90
    # CAR-26 — short-lived forge SSE stream ticket (Bearer → ?ticket=)
    jwt_stream_ticket_ttl_seconds: int = 300
    # CAR-27 — resume deep-link TTL (single-use + expiry)
    jwt_resume_ttl_days: int = 7
    # CAR-44 — email OTP (6-digit); mailer=log for local, resend|ses for prod
    otp_ttl_seconds: int = 600
    otp_rate_limit_per_email: int = 5
    otp_rate_limit_per_ip: int = 20
    otp_rate_limit_window_seconds: int = 600
    mailer_backend: str = "log"  # log | resend | ses
    mail_from: str = "Career Forge <noreply@careerforge.local>"
    resend_api_key: str = ""
    aws_ses_region: str = ""
    # CAR-45 — membership soft label (stub allowlist until Borderless HTTP is live)
    membership_backend: str = "stub"  # stub | http
    membership_stub_allowlist: str = ""  # email:base,email:psp
    borderless_members_url: str = ""  # GET {url}?email=
    borderless_members_token: str = ""
    # CAR-46/CAR-57 — Stripe entitlement before diagnosis/forge for external learners
    frontend_url: str = "http://localhost:3300/career-forge"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""
    # CAR-75 — Operator console identity (distinct from learner Email OTP)
    operator_allowlist: str = ""  # email:both,email:access,email:editor
    operator_session_ttl_hours: int = 8
    operator_cookie_name: str = "cf_operator_session"
    operator_cookie_path: str = "/career-forge/operator"

    @property
    def operator_cookie_path_resolved(self) -> str:
        """Browser path on Labs; root path in local/test so API ``/operator/*`` receives the cookie."""
        if self.env.lower() in {"local", "test"}:
            return "/"
        return self.operator_cookie_path

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


def assert_production_jwt_secret() -> None:
    """Refuse to boot production with the public default JWT secret."""
    if settings.env.lower() != "production":
        return
    if settings.jwt_secret == DEV_JWT_SECRET:
        raise RuntimeError(
            "JWT_SECRET must not equal the development default when ENV=production. "
            "Generate one with: openssl rand -base64 48"
        )
