from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Alert, DuplicateRelationship, Project


def project_dict(project: Project) -> dict:
    anomaly_types = sorted({anomaly.type for anomaly in project.anomalies if anomaly.status == "open"})
    return {
        "id": project.id,
        "title": project.title,
        "state": project.state,
        "district": project.district,
        "constituency": project.constituency,
        "city": project.city,
        "type": project.type,
        "agency": project.agency,
        "status": project.status,
        "risk": project.risk,
        "budget_cr": project.budget_cr,
        "spent_cr": project.spent_cr,
        "utilization": project.utilization,
        "progress": project.progress,
        "sanctioned_date": project.sanctioned_date,
        "expected_completion": project.expected_completion,
        "last_inspection": project.last_inspection,
        "latitude": project.latitude,
        "longitude": project.longitude,
        "risk_score": project.risk_score,
        "anomaly_types": anomaly_types,
        "summary": project.summary,
    }


def relative_time(value: datetime) -> str:
    now = datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    seconds = max(0, int((now - value).total_seconds()))
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60} min ago"
    if seconds < 86400:
        return f"{seconds // 3600} hr ago"
    return f"{seconds // 86400} d ago"


def alert_dict(alert: Alert) -> dict:
    return {
        "id": alert.id,
        "project_id": alert.project_id,
        "title": alert.title,
        "district": alert.district,
        "severity": alert.severity,
        "time": relative_time(alert.updated_at),
        "description": alert.description,
        "acknowledged": alert.acknowledged,
        "created_at": alert.created_at,
    }


def duplicate_dict(session: Session, relationship: DuplicateRelationship) -> dict:
    first = session.get(Project, relationship.project_a_id)
    second = session.get(Project, relationship.project_b_id)
    return {
        "id": relationship.id,
        "project_a_id": relationship.project_a_id,
        "project_b_id": relationship.project_b_id,
        "project_a_title": first.title if first else relationship.project_a_id,
        "project_b_title": second.title if second else relationship.project_b_id,
        "similarity_score": relationship.similarity_score,
        "distance_km": relationship.distance_km,
        "reasons": relationship.reasons,
        "status": relationship.status,
    }


def duplicates_for_project(session: Session, project_id: str) -> list[DuplicateRelationship]:
    return list(
        session.scalars(
            select(DuplicateRelationship)
            .where(
                or_(
                    DuplicateRelationship.project_a_id == project_id,
                    DuplicateRelationship.project_b_id == project_id,
                )
            )
            .order_by(DuplicateRelationship.similarity_score.desc())
        )
    )
