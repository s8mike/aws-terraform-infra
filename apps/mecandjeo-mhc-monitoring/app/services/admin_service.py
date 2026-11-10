# Phase 6: shared helpers for auditable administrative configuration changes.
from sqlalchemy.orm import Session

from ..models import AuditLog, User


# Persist a concise record of every user, crane, or reference-data change.
def record_admin_action(
    db: Session,
    actor: User,
    action: str,
    entity_type: str,
    entity_id: int,
    description: str,
) -> None:
    db.add(
        AuditLog(
            actor_id=actor.id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
        )
    )
