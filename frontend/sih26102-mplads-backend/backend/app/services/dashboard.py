from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Agency,
    Alert,
    Anomaly,
    DuplicateRelationship,
    Prediction,
    Project,
    ProjectMedia,
    RiskAssessment,
    TimelineEvent,
)
from app.services.risk_engine import recompute_project_risk
from app.services.serializers import alert_dict, duplicate_dict, duplicates_for_project, project_dict


def project_query():
    return select(Project).options(selectinload(Project.anomalies), selectinload(Project.agency_record))


def dashboard_summary(session: Session, statement=None) -> dict:
    statement = statement if statement is not None else project_query()
    projects = list(session.scalars(statement.order_by(Project.risk_score.desc())))
    project_ids = [project.id for project in projects]
    agency_names = sorted({project.agency for project in projects})
    alerts = list(
        session.scalars(
            select(Alert)
            .where(Alert.acknowledged.is_(False), Alert.project_id.in_(project_ids))
            .order_by(Alert.created_at.desc())
            .limit(12)
        )
    )
    agencies = list(
        session.scalars(
            select(Agency).where(Agency.name.in_(agency_names)).order_by(Agency.risk_score.desc()).limit(8)
        )
    )
    predictions = list(
        session.scalars(
            select(Prediction)
            .where(Prediction.project_id.in_(project_ids))
            .order_by(Prediction.probability.desc())
            .limit(8)
        )
    )

    avg_progress = round(sum(project.progress for project in projects) / max(1, len(projects)))
    avg_utilization = round(sum(project.utilization for project in projects) / max(1, len(projects)))
    high_risk = sum(project.risk in {"High", "Critical"} for project in projects)
    duplicate_count = session.scalar(
        select(func.count(DuplicateRelationship.id)).where(
            (DuplicateRelationship.project_a_id.in_(project_ids))
            | (DuplicateRelationship.project_b_id.in_(project_ids))
        )
    ) or 0

    factors = [0.32, 0.48, 0.63, 0.76, 0.89, 1.0]
    month_labels = ["Mar", "Apr", "May", "Jun", "Jul", "Aug"]
    monthly_trend = [
        {
            "month": month,
            "spend": round(avg_utilization * factor),
            "progress": round(avg_progress * min(1, factor + 0.06)),
            "alerts": round(len(alerts) * factor + index * 2),
        }
        for index, (month, factor) in enumerate(zip(month_labels, factors, strict=True))
    ]

    sector_values: dict[str, list[int]] = {}
    for project in projects:
        sector_values.setdefault(project.type, []).append(project.risk_score)
    sector_risk = [
        {"sector": sector.replace("Urban Development", "Urban"), "risk": round(sum(values) / len(values))}
        for sector, values in sorted(sector_values.items(), key=lambda item: sum(item[1]) / len(item[1]), reverse=True)
    ]

    changed_since_login = [
        f"{len(alerts)} unacknowledged project alerts are in the national review queue.",
        f"{high_risk} works are currently classified High or Critical risk.",
        f"{duplicate_count} duplicate-work relationships require evidence review.",
        f"Average physical progress is {avg_progress}% against {avg_utilization}% financial utilization.",
    ]
    situation_brief = (
        f"National monitoring currently covers {len(projects)} demonstration works. "
        f"The immediate review priority is {high_risk} High or Critical risk projects, with particular attention "
        "to financial-progress mismatches, delayed milestones, and nearby similar sanctions."
    )

    return {
        "projects": [project_dict(project) for project in projects],
        "alerts": [alert_dict(alert) for alert in alerts],
        "agencies": [
            {
                "name": agency.name,
                "projects": agency.projects_count,
                "avg_delay_days": agency.avg_delay_days,
                "risk_score": agency.risk_score,
                "completion_rate": agency.completion_rate,
            }
            for agency in agencies
        ],
        "predictions": [
            {
                "id": prediction.id,
                "title": prediction.title,
                "probability": prediction.probability,
                "impact": prediction.impact,
                "project_id": prediction.project_id,
                "recommendation": prediction.recommendation,
            }
            for prediction in predictions
        ],
        "monthly_trend": monthly_trend,
        "sector_risk": sector_risk,
        "changed_since_login": changed_since_login,
        "situation_brief": situation_brief,
        "generated_at": datetime.now(timezone.utc),
    }


def project_intelligence(session: Session, project: Project) -> dict:
    assessment = session.scalar(
        select(RiskAssessment)
        .options(selectinload(RiskAssessment.contributions))
        .where(RiskAssessment.project_id == project.id)
        .order_by(desc(RiskAssessment.generated_at))
        .limit(1)
    )
    if assessment is None:
        assessment = recompute_project_risk(session, project)
        session.commit()
        session.refresh(assessment)

    anomalies = list(
        session.scalars(
            select(Anomaly).where(Anomaly.project_id == project.id).order_by(Anomaly.score.desc())
        )
    )
    predictions = list(
        session.scalars(
            select(Prediction).where(Prediction.project_id == project.id).order_by(Prediction.probability.desc())
        )
    )
    timeline = list(
        session.scalars(
            select(TimelineEvent).where(TimelineEvent.project_id == project.id).order_by(TimelineEvent.date)
        )
    )
    media = list(
        session.scalars(
            select(ProjectMedia).where(ProjectMedia.project_id == project.id).order_by(ProjectMedia.captured_at)
        )
    )
    duplicate_relationships = duplicates_for_project(session, project.id)

    return {
        "project_id": project.id,
        "risk_score": assessment.score,
        "risk_contributions": [
            {
                "label": contribution.label,
                "weight": contribution.weight,
                "score": contribution.score,
                "explanation": contribution.explanation,
            }
            for contribution in assessment.contributions
        ],
        "anomalies": [
            {
                "id": anomaly.id,
                "project_id": anomaly.project_id,
                "type": anomaly.type,
                "score": anomaly.score,
                "severity": anomaly.severity,
                "explanation": anomaly.explanation,
                "evidence": anomaly.evidence_json,
                "model_version": anomaly.model_version,
                "status": anomaly.status,
            }
            for anomaly in anomalies
        ],
        "predictions": [
            {
                "id": prediction.id,
                "title": prediction.title,
                "probability": prediction.probability,
                "impact": prediction.impact,
                "project_id": prediction.project_id,
                "recommendation": prediction.recommendation,
            }
            for prediction in predictions
        ],
        "timeline": [
            {"date": event.date, "title": event.title, "state": event.state, "detail": event.detail}
            for event in timeline
        ],
        "media": [
            {
                "id": item.id,
                "stage": item.stage,
                "url": item.public_url,
                "captured_at": item.captured_at,
                "geo_match_score": item.geo_match_score,
                "progress_confidence": item.progress_confidence,
            }
            for item in media
        ],
        "duplicate_relationships": [duplicate_dict(session, item) for item in duplicate_relationships],
    }
