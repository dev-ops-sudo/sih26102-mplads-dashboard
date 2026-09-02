from sqlalchemy.orm import Session

from app.auth import Principal
from app.models import AuditEvent


def record_audit(
    session: Session,
    actor: Principal,
    action: str,
    resource_type: str,
    resource_id: str,
    details: dict | None = None,
) -> None:
    session.add(
        AuditEvent(
            actor_id=actor.id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details_json=details or {},
        )
    )

