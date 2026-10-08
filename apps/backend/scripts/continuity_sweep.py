"""Send due Continuity emails. One accepted send per quiet stretch.

Billing email is not this script and does not spend the stretch.

    PYTHONPATH=src python scripts/continuity_sweep.py
"""

from __future__ import annotations

from career_forge.db.session import SessionLocal
from career_forge.services.continuity import sweep_continuity_emails
from career_forge.services.mailer import get_mailer


def main() -> None:
    session = SessionLocal()
    try:
        sent = sweep_continuity_emails(session, mailer=get_mailer())
    finally:
        session.close()
    print(f"continuity emails accepted: {sent}")


if __name__ == "__main__":
    main()
