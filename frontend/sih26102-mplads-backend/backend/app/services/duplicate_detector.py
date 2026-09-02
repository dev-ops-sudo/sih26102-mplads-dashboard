from __future__ import annotations

from datetime import date
from difflib import SequenceMatcher
from math import asin, cos, radians, sin, sqrt

from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.models import DuplicateRelationship, Project


def haversine_km(a: Project, b: Project) -> float:
    earth_radius_km = 6371.0
    lat_delta = radians(b.latitude - a.latitude)
    lon_delta = radians(b.longitude - a.longitude)
    first_lat = radians(a.latitude)
    second_lat = radians(b.latitude)
    value = sin(lat_delta / 2) ** 2 + cos(first_lat) * cos(second_lat) * sin(lon_delta / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(value))


def normalized_similarity(first: str, second: str) -> float:
    normalize = lambda value: " ".join("".join(char.lower() if char.isalnum() else " " for char in value).split())
    return SequenceMatcher(None, normalize(first), normalize(second)).ratio()


def date_similarity(first: date, second: date) -> float:
    days = abs((first - second).days)
    return max(0.0, 1.0 - min(days, 365) / 365)


def relationship_score(first: Project, second: Project) -> tuple[int, float, list[str]]:
    text_score = normalized_similarity(first.title, second.title)
    distance = haversine_km(first, second)
    geo_score = max(0.0, 1.0 - min(distance, 50) / 50)
    type_score = 1.0 if first.type == second.type else 0.0
    agency_score = 1.0 if first.agency == second.agency else 0.0
    sanction_score = date_similarity(first.sanctioned_date, second.sanctioned_date)
    score = round(
        100
        * (
            text_score * 0.45
            + geo_score * 0.25
            + type_score * 0.15
            + agency_score * 0.10
            + sanction_score * 0.05
        )
    )

    reasons: list[str] = []
    if text_score >= 0.55:
        reasons.append("Similar project description")
    if distance <= 15:
        reasons.append("Nearby sanctioned work")
    if type_score:
        reasons.append("Same project type")
    if agency_score:
        reasons.append("Same implementing agency")
    if sanction_score >= 0.7:
        reasons.append("Overlapping sanction period")
    return score, round(distance, 2), reasons


def refresh_duplicate_relationships(session: Session, project_id: str | None = None) -> int:
    projects = list(session.scalars(select(Project).order_by(Project.id)))
    if project_id:
        session.execute(
            delete(DuplicateRelationship).where(
                or_(
                    DuplicateRelationship.project_a_id == project_id,
                    DuplicateRelationship.project_b_id == project_id,
                )
            )
        )
    else:
        session.execute(delete(DuplicateRelationship))

    created = 0
    for index, first in enumerate(projects):
        for second in projects[index + 1 :]:
            if project_id and project_id not in {first.id, second.id}:
                continue
            score, distance, reasons = relationship_score(first, second)
            if score < 55:
                continue
            session.add(
                DuplicateRelationship(
                    project_a_id=first.id,
                    project_b_id=second.id,
                    similarity_score=score,
                    distance_km=distance,
                    reasons=reasons,
                )
            )
            created += 1
    session.flush()
    return created

