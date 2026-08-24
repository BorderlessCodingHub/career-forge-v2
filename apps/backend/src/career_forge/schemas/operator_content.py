"""HTTP contracts for the Operator Content desk (CAR-79)."""

from __future__ import annotations

from pydantic import (
    AnyHttpUrl,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


class OperatorContentPatch(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    url: AnyHttpUrl | None = None
    published: bool | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("title cannot be blank")
        return value

    @model_validator(mode="after")
    def validate_patch(self) -> "OperatorContentPatch":
        if not self.model_fields_set:
            raise ValueError("at least one content field is required")
        if "title" in self.model_fields_set and self.title is None:
            raise ValueError("title cannot be null")
        if "published" in self.model_fields_set and self.published is None:
            raise ValueError("published must be boolean")
        return self


class OperatorContentSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill_id: str
    track_id: str
    title: str
    description: str | None
    url: str | None
    published: bool
    body_present: bool


class OperatorContentListResponse(BaseModel):
    skills: list[OperatorContentSkillResponse]
