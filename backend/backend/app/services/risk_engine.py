from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.models import (
    Alert,
    Anomaly,
    DuplicateRelationship,
    Prediction,
    Project,
    RiskAssessment,
    RiskContribution,
)


RISK_MODEL_VERSION = "risk-rules-v1.0"


def clamp(value: float) -> int:
    return max(0, min(100, round(value)))


def risk_level(score: int) -> str:
    if score >= 80:
        return "Critical"
    if score >= 65:
        return "High"
    if score >= 35:
        return "Medium"
    return "Low"


def severity_for_score(score: int) -> str:
    return risk_level(score)


def latest_duplicate_score(session: Session, project_id: str) -> int:
    value = session.scalar(
        select(func.max(DuplicateRelationship.similarity_score)).where(
            or_(
                DuplicateRelationship.project_a_id == project_id,
                DuplicateRelationship.project_b_id == project_id,
            )
        )
    )
    return int(value or 0)


def build_contributions(session: Session, project: Project) -> list[dict[str, int | str]]:
    spend_progress_gap = max(0, project.utilization - project.progress)
    cost_score = clamp(18 + spend_progress_gap * 2.1)

    today = date.today()
    overdue_days = max(0, (today - project.expected_completion).days)
    schedule_base = 78 if project.status in {"Delayed", "Flagged"} else 24
    schedule_score = clamp(schedule_base + min(overdue_days, 180) / 4)

    inspection_age = max(0, (today - project.last_inspection).days)
    open_anomaly_count = sum(anomaly.status == "open" for anomaly in project.anomalies)
    evidence_score = clamp(18 + min(inspection_age, 150) * 0.45 + open_anomaly_count * 8)
    duplicate_score = latest_duplicate_score(session, project.id)
    agency_score = project.agency_record.risk_score if project.agency_record else 40

    return [
        {
            "label": "Cost variance",
            "weight": 30,
            "score": cost_score,
            "explanation": f"Financial utilization is {project.utilization}% against {project.progress}% physical progress.",
        },
        {
            "label": "Schedule slippage",
            "weight": 25,
            "score": schedule_score,
            "explanation": "Milestone status, completion date, and current progress are evaluated together.",
        },
        {
            "label": "Evidence confidence",
            "weight": 20,
            "score": evidence_score,
            "explanation": f"Latest recorded inspection is {inspection_age} days old and evidence gaps are included.",
        },
        {
            "label": "Duplicate similarity",
            "weight": 15,
            "score": duplicate_score,
            "explanation": "Nearby works are compared using title, type, agency, location, and sanction period.",
        },
        {
            "label": "Agency history",
            "weight": 10,
            "score": agency_score,
            "explanation": "The implementing agency's completion rate and delay history are included.",
        },
    ]


def upsert_anomaly(
    session: Session,
    project: Project,
    anomaly_type: str,
    score: int,
    explanation: str,
) -> None:
    anomaly_id = f"AUTO-{project.id}-{anomaly_type.lower().replace(' ', '-')}"
    anomaly = session.get(Anomaly, anomaly_id)
    if anomaly is None:
        anomaly = Anomaly(id=anomaly_id, project_id=project.id, type=anomaly_type)
        session.add(anomaly)
    anomaly.score = score
    anomaly.severity = severity_for_score(score)
    anomaly.explanation = explanation
    anomaly.evidence_json = [
        {"type": "project", "id": project.id},
        {"type": "model", "id": RISK_MODEL_VERSION},
    ]
    anomaly.model_version = RISK_MODEL_VERSION
    anomaly.status = "open"


def replace_predictions(session: Session, project: Project, contributions: list[dict]) -> None:
    session.execute(delete(Prediction).where(Prediction.project_id == project.id))
    by_label = {item["label"]: int(item["score"]) for item in contributions}

    delay_probability = clamp((by_label["Schedule slippage"] * 0.7) + (100 - project.progress) * 0.3)
    cost_probability = clamp((by_label["Cost variance"] * 0.8) + project.utilization * 0.2)

    if delay_probability >= 45:
        session.add(
            Prediction(
                id=f"PR-{project.id}-DELAY",
                project_id=project.id,
                title="Likely completion delay beyond the sanctioned window",
                probability=delay_probability,
                impact="Delay",
                recommendation="Validate milestone evidence and agree a recovery schedule before the next release.",
            )
        )
    if cost_probability >= 45:
        session.add(
            Prediction(
                id=f"PR-{project.id}-COST",
                project_id=project.id,
                title="Cost overrun exposure requires early review",
                probability=cost_probability,
                impact="Cost",
                recommendation="Compare BOQ, invoices, and peer-project unit costs before approving further expenditure.",
            )
        )
    if by_label["Duplicate similarity"] >= 55:
        session.add(
            Prediction(
                id=f"PR-{project.id}-DUPLICATE",
                project_id=project.id,
                title="Duplicate sanction investigation recommended",
                probability=by_label["Duplicate similarity"],
                impact="Compliance",
                recommendation="Review the linked works, ward boundaries, BOQs, and sanction records together.",
            )
        )


def ensure_alert(session: Session, project: Project, score: int) -> None:
    alert_id = f"AUTO-RISK-{project.id}"
    if score < 65:
        existing = session.get(Alert, alert_id)
        if existing:
            session.delete(existing)
        return
    alert = session.get(Alert, alert_id)
    previous_severity = alert.severity if alert else None
    if alert is None:
        alert = Alert(id=alert_id, project_id=project.id)
        session.add(alert)
    alert.title = f"{risk_level(score)} project risk requires review"
    alert.district = project.district
    alert.severity = risk_level(score)
    alert.description = f"Explainable risk engine scored this project {score}/100 using current financial, schedule, evidence, duplicate, and agency signals."
    severity_rank = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}
    if previous_severity is None or severity_rank[alert.severity] > severity_rank.get(previous_severity, -1):
        alert.acknowledged = False
        alert.acknowledged_by = None
        alert.acknowledged_at = None


def recompute_project_risk(session: Session, project: Project) -> RiskAssessment:
    for anomaly in project.anomalies:
        if anomaly.model_version == RISK_MODEL_VERSION:
            anomaly.status = "resolved"
    contributions = build_contributions(session, project)
    score = clamp(sum(int(item["score"]) * int(item["weight"]) for item in contributions) / 100)
    level = risk_level(score)

    assessment = RiskAssessment(
        project_id=project.id,
        score=score,
        level=level,
        model_version=RISK_MODEL_VERSION,
        generated_at=datetime.now(timezone.utc),
        data_snapshot={
            "budgetCr": project.budget_cr,
            "spentCr": project.spent_cr,
            "utilization": project.utilization,
            "progress": project.progress,
            "status": project.status,
            "lastInspection": project.last_inspection.isoformat(),
        },
    )
    assessment.contributions = [
        RiskContribution(
            label=str(item["label"]),
            weight=int(item["weight"]),
            score=int(item["score"]),
            explanation=str(item["explanation"]),
        )
        for item in contributions
    ]
    session.add(assessment)

    project.risk_score = score
    project.risk = level

    by_label = {item["label"]: int(item["score"]) for item in contributions}
    if by_label["Cost variance"] >= 55:
        upsert_anomaly(session, project, "Cost anomaly", by_label["Cost variance"], contributions[0]["explanation"])
    if by_label["Schedule slippage"] >= 55:
        upsert_anomaly(session, project, "Delay", by_label["Schedule slippage"], contributions[1]["explanation"])
    if project.utilization - project.progress >= 15:
        upsert_anomaly(
            session,
            project,
            "Financial mismatch",
            clamp(50 + (project.utilization - project.progress)),
            "Financial utilization materially exceeds recorded physical progress.",
        )
    if by_label["Duplicate similarity"] >= 55:
        upsert_anomaly(
            session,
            project,
            "Possible duplicate",
            by_label["Duplicate similarity"],
            contributions[3]["explanation"],
        )

    replace_predictions(session, project, contributions)
    ensure_alert(session, project, score)
    session.flush()
    return assessment


def recompute_all_risks(session: Session) -> int:
    projects = list(session.scalars(select(Project)))
    for project in projects:
        recompute_project_risk(session, project)
    session.commit()
    return len(projects)
