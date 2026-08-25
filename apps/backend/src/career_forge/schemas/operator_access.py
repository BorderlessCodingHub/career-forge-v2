"""HTTP contracts for the Operator Access desk (CAR-77)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class OperatorAccessPatch(BaseModel):
    operator_membership_label: Literal["base", "psp"] | None = None
    billing_entitled: bool | None = None

    @model_validator(mode="after")
    def validate_patch(self) -> "OperatorAccessPatch":
        if not self.model_fields_set:
            raise ValueError("at least one access field is required")
        if "billing_entitled" in self.model_fields_set and self.billing_entitled is None:
            raise ValueError("billing_entitled must be boolean")
        return self


class OperatorLearnerAccessResponse(BaseModel):
    email: str
    operator_membership_label: Literal["base", "psp"] | None
    membership_label: str
    membership_entitled: bool
    billing_entitled: bool
    pilot_email_listed: bool
    stripe_subscription_status: str | None
    stripe_billing_locked: bool


class BillingPilotEmailCreate(BaseModel):
    email: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if (
            "@" not in normalized
            or normalized.startswith("@")
            or normalized.endswith("@")
            or len(normalized) > 255
        ):
            raise ValueError("valid email is required")
        return normalized


class BillingPilotEmailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    created_at: datetime
    created_by_operator_id: int | None


class BillingPilotEmailListResponse(BaseModel):
    emails: list[BillingPilotEmailResponse]


class OperatorCostPoolResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    year_month: str
    estimated_cost_brl: float
    budget_brl: float
    billable_runs: int
    forge_runs: int


class OperatorAccessAuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_type: str
    operator_id: int | None
    actor_email: str | None
    learner_email: str
    field: str
    before: Any = Field(validation_alias="before_value")
    after: Any = Field(validation_alias="after_value")
    action: str
    created_at: datetime


class OperatorAccessAuditListResponse(BaseModel):
    entries: list[OperatorAccessAuditResponse]
