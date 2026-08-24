"""Access desk domain service — learner grants and immutable audit (CAR-77)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.user import User
from career_forge.errors import ConflictError, ForbiddenError, NotFoundError
from career_forge.schemas.operator_access import OperatorAccessPatch
from career_forge.services.access_audit import append_access_audit
from career_forge.services.entitlement import stripe_subscription_is_active
from career_forge.services.membership import apply_membership_label


class LearnerNotFoundError(NotFoundError):
    pass


class StripeBillingLockedError(ConflictError):
    pass


def require_access_role(principal: OperatorPrincipal) -> None:
    if principal.desk_roles not in {"access", "both"}:
        raise ForbiddenError(
            "Access desk role required",
            code="access_desk_forbidden",
        )


def stripe_billing_locked(user: User) -> bool:
    return stripe_subscription_is_active(user.stripe_subscription_status)


def get_learner_by_email(
    session: Session,
    email: str,
    *,
    for_update: bool = False,
) -> User:
    statement = select(User).where(User.email == email.strip().lower())
    if for_update:
        statement = statement.with_for_update()
    user = session.scalar(statement)
    if user is None:
        raise LearnerNotFoundError("learner not found")
    return user


def write_operator_access(
    session: Session,
    *,
    principal: OperatorPrincipal,
    learner_email: str,
    patch: OperatorAccessPatch,
) -> User:
    require_access_role(principal)
    user = get_learner_by_email(session, learner_email, for_update=True)

    if "operator_membership_label" in patch.model_fields_set:
        operator_membership_label = patch.operator_membership_label
        before = user.operator_membership_label
        if before != operator_membership_label:
            user.operator_membership_label = operator_membership_label
            apply_membership_label(user, user.email or learner_email)
            append_access_audit(
                session,
                actor_type="operator",
                operator_id=principal.operator_id,
                actor_email=principal.email,
                user=user,
                field="operator_membership_label",
                before=before,
                after=operator_membership_label,
            )

    if "billing_entitled" in patch.model_fields_set:
        billing_entitled = patch.billing_entitled
        if billing_entitled is None:
            raise ValueError("validated billing_entitled cannot be null")
        before = bool(user.billing_entitled)
        if before != billing_entitled:
            if stripe_billing_locked(user):
                raise StripeBillingLockedError(
                    "active Stripe billing is read-only in Access desk"
                )
            user.billing_entitled = billing_entitled
            append_access_audit(
                session,
                actor_type="operator",
                operator_id=principal.operator_id,
                actor_email=principal.email,
                user=user,
                field="billing_entitled",
                before=before,
                after=billing_entitled,
            )

    session.flush()
    return user
