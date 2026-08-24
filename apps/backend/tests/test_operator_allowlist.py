"""Unit tests for Operator allowlist parsing (CAR-75)."""

from career_forge.services.operator_allowlist import desks_for_roles, parse_operator_allowlist


def test_parse_operator_allowlist_roles() -> None:
    mapping = parse_operator_allowlist(
        "ops@borderless.com:both,editor@borderless.com:editor,access@borderless.com:access",
    )
    assert mapping["ops@borderless.com"] == "both"
    assert mapping["editor@borderless.com"] == "editor"
    assert mapping["access@borderless.com"] == "access"


def test_parse_operator_allowlist_defaults_both() -> None:
    mapping = parse_operator_allowlist("solo@borderless.com")
    assert mapping["solo@borderless.com"] == "both"


def test_desks_for_roles() -> None:
    assert desks_for_roles("access") == ["access"]
    assert desks_for_roles("editor") == ["content"]
    assert desks_for_roles("both") == ["access", "content"]
