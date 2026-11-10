"""Phase 9: idempotent first-run bootstrap for reference data, sample cranes, and the first admin."""

from sqlalchemy.orm import Session

from ..auth import ROLE_ADMIN, get_password_hash
from ..config import BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_PASSWORD, SEED_SAMPLE_DATA
from ..database import engine
from ..models import User
from ..services.admin_service import record_admin_action
from .seed_data import seed_reference_data, seed_sample_cranes

MIN_BOOTSTRAP_PASSWORD_LENGTH = 12


# Create the first admin only when configured and absent; never touches an existing account.
def bootstrap_admin(db: Session) -> bool:
    """Return True when a new admin was created."""
    if not BOOTSTRAP_ADMIN_EMAIL or not BOOTSTRAP_ADMIN_PASSWORD:
        return False
    if len(BOOTSTRAP_ADMIN_PASSWORD) < MIN_BOOTSTRAP_PASSWORD_LENGTH:
        raise RuntimeError(
            f"BOOTSTRAP_ADMIN_PASSWORD must be at least {MIN_BOOTSTRAP_PASSWORD_LENGTH} characters"
        )

    email = BOOTSTRAP_ADMIN_EMAIL.strip().lower()
    if db.query(User).filter(User.email == email).first():
        return False

    admin = User(
        email=email,
        full_name="Bootstrap Admin",
        password_hash=get_password_hash(BOOTSTRAP_ADMIN_PASSWORD),
        role=ROLE_ADMIN,
        is_active=True,
    )
    db.add(admin)
    db.flush()
    record_admin_action(db, admin, "user.bootstrapped", "user", admin.id, f"Bootstrapped admin account {admin.email}")
    db.commit()
    return True


# Run every bootstrap step; safe to run repeatedly (local startup, ECS one-off task, manual).
def run_bootstrap() -> None:
    with Session(engine) as db:
        reference_added = seed_reference_data(db)
        cranes_added = seed_sample_cranes(db) if SEED_SAMPLE_DATA else 0
        admin_created = bootstrap_admin(db)
    print(
        f"bootstrap: reference_data_added={reference_added} "
        f"cranes_added={cranes_added} admin_created={admin_created}",
        flush=True,
    )


if __name__ == "__main__":
    run_bootstrap()