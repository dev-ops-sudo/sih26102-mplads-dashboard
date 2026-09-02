from __future__ import annotations

from datetime import date, datetime, timezone
from hashlib import sha256

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    Agency,
    Anomaly,
    FinancialTransaction,
    Inspection,
    Milestone,
    Project,
    ProjectMedia,
    SourceDocument,
    TimelineEvent,
)
from app.services.duplicate_detector import refresh_duplicate_relationships
from app.services.risk_engine import recompute_all_risks


AGENCIES = [
    ("Delhi PWD", 22, 41, 76, 68),
    ("Zilla Parishad Pune", 14, 29, 64, 72),
    ("BBMP", 18, 12, 38, 81),
    ("UP Rural Engineering", 31, 35, 72, 64),
    ("Greater Chennai Corporation", 16, 5, 24, 91),
    ("Assam PHED", 19, 26, 52, 76),
]


PROJECTS = [
    {
        "id": "MP-102-DEL-014",
        "title": "Smart Community Health Centre Upgrade",
        "state": "Delhi",
        "district": "New Delhi",
        "constituency": "New Delhi",
        "city": "New Delhi",
        "type": "Health",
        "agency": "Delhi PWD",
        "status": "Flagged",
        "risk": "Critical",
        "budget_cr": 8.6,
        "spent_cr": 7.9,
        "progress": 54,
        "sanctioned_date": "2025-10-14",
        "expected_completion": "2026-11-20",
        "last_inspection": "2026-08-22",
        "latitude": 28.61,
        "longitude": 77.20,
        "risk_score": 87,
        "summary": "Spend is high compared with physical progress and inspection notes show procurement variance.",
        "anomalies": ["Cost anomaly", "Delay", "Financial mismatch"],
    },
    {
        "id": "MP-102-MH-081",
        "title": "Rural School Digital Lab Cluster",
        "state": "Maharashtra",
        "district": "Pune",
        "constituency": "Baramati",
        "city": "Baramati",
        "type": "Education",
        "agency": "Zilla Parishad Pune",
        "status": "Delayed",
        "risk": "High",
        "budget_cr": 5.2,
        "spent_cr": 3.9,
        "progress": 48,
        "sanctioned_date": "2025-07-02",
        "expected_completion": "2026-10-05",
        "last_inspection": "2026-08-18",
        "latitude": 18.15,
        "longitude": 74.58,
        "risk_score": 73,
        "summary": "Milestone slippage detected across three schools with similar work descriptions nearby.",
        "anomalies": ["Delay"],
    },
    {
        "id": "MP-102-KA-029",
        "title": "Lakefront Solar Lighting and CCTV",
        "state": "Karnataka",
        "district": "Bengaluru Urban",
        "constituency": "Bangalore South",
        "city": "Bengaluru",
        "type": "Urban Development",
        "agency": "BBMP",
        "status": "On Track",
        "risk": "Medium",
        "budget_cr": 3.4,
        "spent_cr": 1.8,
        "progress": 61,
        "sanctioned_date": "2026-01-12",
        "expected_completion": "2026-12-16",
        "last_inspection": "2026-08-24",
        "latitude": 12.97,
        "longitude": 77.59,
        "risk_score": 42,
        "summary": "Project is broadly on schedule, with vendor invoice clustering requiring routine review.",
        "anomalies": ["Minor procurement variance"],
    },
    {
        "id": "MP-102-UP-117",
        "title": "Primary Road Drainage Reconstruction",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "constituency": "Varanasi",
        "city": "Varanasi",
        "type": "Roads",
        "agency": "UP Rural Engineering",
        "status": "Flagged",
        "risk": "High",
        "budget_cr": 11.8,
        "spent_cr": 8.4,
        "progress": 43,
        "sanctioned_date": "2025-05-19",
        "expected_completion": "2026-09-30",
        "last_inspection": "2026-08-20",
        "latitude": 25.32,
        "longitude": 82.97,
        "risk_score": 79,
        "summary": "Repeated drainage work appears in adjacent wards while current site has weak progress evidence.",
        "anomalies": ["Cost anomaly", "Delay"],
    },
    {
        "id": "MP-102-UP-118",
        "title": "Primary Ward Road and Drainage Rehabilitation",
        "state": "Uttar Pradesh",
        "district": "Varanasi",
        "constituency": "Varanasi",
        "city": "Varanasi",
        "type": "Roads",
        "agency": "UP Rural Engineering",
        "status": "Delayed",
        "risk": "High",
        "budget_cr": 10.9,
        "spent_cr": 7.1,
        "progress": 41,
        "sanctioned_date": "2025-06-11",
        "expected_completion": "2026-10-20",
        "last_inspection": "2026-08-11",
        "latitude": 25.30,
        "longitude": 82.99,
        "risk_score": 75,
        "summary": "A nearby drainage package shares agency, scope language, location, and sanction period.",
        "anomalies": ["Delay"],
    },
    {
        "id": "MP-102-TN-044",
        "title": "Anganwadi Nutrition Centre Modernisation",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "constituency": "Chennai South",
        "city": "Chennai",
        "type": "Social Welfare",
        "agency": "Greater Chennai Corporation",
        "status": "Completed",
        "risk": "Low",
        "budget_cr": 2.2,
        "spent_cr": 2.1,
        "progress": 100,
        "sanctioned_date": "2025-12-03",
        "expected_completion": "2026-07-14",
        "last_inspection": "2026-08-06",
        "latitude": 13.08,
        "longitude": 80.27,
        "risk_score": 18,
        "summary": "Work completed with matching image, inspection, and expenditure evidence.",
        "anomalies": [],
    },
    {
        "id": "MP-102-AS-032",
        "title": "Flood-Resilient Drinking Water Points",
        "state": "Assam",
        "district": "Dibrugarh",
        "constituency": "Dibrugarh",
        "city": "Dibrugarh",
        "type": "Water",
        "agency": "Assam PHED",
        "status": "Delayed",
        "risk": "Medium",
        "budget_cr": 4.8,
        "spent_cr": 2.7,
        "progress": 52,
        "sanctioned_date": "2025-11-28",
        "expected_completion": "2026-12-01",
        "last_inspection": "2026-08-12",
        "latitude": 27.47,
        "longitude": 94.91,
        "risk_score": 55,
        "summary": "Monsoon disruption explains part of the slippage; early warning remains active.",
        "anomalies": ["Delay"],
    },
]


def seed_database(session: Session) -> None:
    if (session.scalar(select(func.count(Project.id))) or 0) > 0:
        return

    for name, project_count, delay, risk, completion in AGENCIES:
        session.add(
            Agency(
                name=name,
                projects_count=project_count,
                avg_delay_days=delay,
                risk_score=risk,
                completion_rate=completion,
            )
        )
    session.flush()

    for data in PROJECTS:
        sanctioned = date.fromisoformat(data["sanctioned_date"])
        expected = date.fromisoformat(data["expected_completion"])
        inspection_date = date.fromisoformat(data["last_inspection"])
        utilization = round(float(data["spent_cr"]) / float(data["budget_cr"]) * 100)
        project = Project(
            id=data["id"],
            title=data["title"],
            state=data["state"],
            district=data["district"],
            constituency=data["constituency"],
            city=data["city"],
            type=data["type"],
            agency=data["agency"],
            status=data["status"],
            risk=data["risk"],
            budget_cr=data["budget_cr"],
            spent_cr=data["spent_cr"],
            utilization=utilization,
            progress=data["progress"],
            sanctioned_date=sanctioned,
            expected_completion=expected,
            last_inspection=inspection_date,
            latitude=data["latitude"],
            longitude=data["longitude"],
            location=f"SRID=4326;POINT({data['longitude']} {data['latitude']})",
            risk_score=data["risk_score"],
            summary=data["summary"],
        )
        session.add(project)
        session.flush()

        for index, anomaly_type in enumerate(data["anomalies"], start=1):
            session.add(
                Anomaly(
                    id=f"SEED-{data['id']}-{index}",
                    project_id=data["id"],
                    type=anomaly_type,
                    score=min(95, int(data["risk_score"]) + index),
                    severity=data["risk"],
                    explanation=f"Seed evidence indicates {anomaly_type.lower()} requiring officer review.",
                    evidence_json=[{"type": "project", "id": data["id"]}],
                    model_version="seed-v1",
                )
            )

        timeline_rows = [
            (sanctioned, "Sanction approved", "done", "Initial project sanction recorded after district validation."),
            (inspection_date, "Latest inspection", "active", "Officer inspection evidence and progress estimate recorded."),
            (expected, "Expected completion", "upcoming", "Current sanctioned completion date."),
        ]
        for event_date, title, state, detail in timeline_rows:
            session.add(
                TimelineEvent(project_id=data["id"], date=event_date, title=title, state=state, detail=detail)
            )

        session.add(
            Milestone(
                project_id=data["id"],
                name="Current implementation milestone",
                due_date=expected,
                planned_progress=min(100, int(data["progress"]) + 15),
                actual_progress=data["progress"],
            )
        )
        session.add(
            FinancialTransaction(
                project_id=data["id"],
                transaction_type="utilization",
                amount_cr=data["spent_cr"],
                transaction_date=inspection_date,
                reference=f"UTR-{data['id']}",
                metadata_json={"source": "demo-seed"},
            )
        )
        session.add(
            Inspection(
                project_id=data["id"],
                inspected_at=datetime.combine(inspection_date, datetime.min.time(), tzinfo=timezone.utc),
                officer_id="demo-district-officer",
                physical_progress=data["progress"],
                latitude=data["latitude"],
                longitude=data["longitude"],
                notes=data["summary"],
                evidence_confidence=max(35, 100 - int(data["risk_score"]) // 2),
            )
        )
        for stage, confidence in (("before", 96), ("during", 72), ("after", 58)):
            session.add(
                ProjectMedia(
                    project_id=data["id"],
                    stage=stage,
                    object_key=f"demo/{data['id']}/{stage}.jpg",
                    geo_match_score=max(50, confidence - 4),
                    progress_confidence=confidence,
                    captured_at=datetime.combine(inspection_date, datetime.min.time(), tzinfo=timezone.utc),
                )
            )

        document_content = f"{data['title']}\n{data['summary']}\nAgency: {data['agency']}"
        session.add(
            SourceDocument(
                project_id=data["id"],
                title=f"Project brief for {data['id']}",
                source_type="project_brief",
                content=document_content,
                content_hash=sha256(document_content.encode("utf-8")).hexdigest(),
            )
        )

    session.commit()
    refresh_duplicate_relationships(session)
    session.commit()
    recompute_all_risks(session)

