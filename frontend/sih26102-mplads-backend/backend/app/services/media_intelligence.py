from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Anomaly, Project, ProjectMedia
from app.services.risk_engine import clamp, risk_level


def coordinate_distance_km(first_lat: float, first_lon: float, second_lat: float, second_lon: float) -> float:
    earth_radius_km = 6371.0
    lat_delta = radians(second_lat - first_lat)
    lon_delta = radians(second_lon - first_lon)
    first_latitude = radians(first_lat)
    second_latitude = radians(second_lat)
    value = sin(lat_delta / 2) ** 2 + cos(first_latitude) * cos(second_latitude) * sin(lon_delta / 2) ** 2
    return 2 * earth_radius_km * asin(sqrt(value))


def analyze_media(session: Session, media_id: int) -> dict[str, int | bool]:
    media = session.get(ProjectMedia, media_id)
    if media is None:
        raise ValueError("Evidence record not found")
    project = session.get(Project, media.project_id)
    if project is None:
        raise ValueError("Project not found")

    if media.latitude is not None and media.longitude is not None:
        distance = coordinate_distance_km(
            project.latitude,
            project.longitude,
            media.latitude,
            media.longitude,
        )
        media.geo_match_score = clamp(100 - distance * 12)
    else:
        media.geo_match_score = 50

    stage_confidence = {
        "before": 92,
        "during": max(35, 100 - abs(project.progress - 55)),
        "after": 88 if project.status == "Completed" else 55,
        "document": 70,
    }
    media.progress_confidence = stage_confidence.get(media.stage, 50)

    duplicate_found = False
    if media.sha256:
        duplicate = session.scalar(
            select(ProjectMedia).where(ProjectMedia.sha256 == media.sha256, ProjectMedia.id != media.id).limit(1)
        )
        if duplicate:
            duplicate_found = True
            media.progress_confidence = max(10, media.progress_confidence - 35)
            anomaly_id = f"AUTO-{project.id}-reused-evidence"
            anomaly = session.get(Anomaly, anomaly_id)
            if anomaly is None:
                anomaly = Anomaly(id=anomaly_id, project_id=project.id, type="Reused image evidence")
                session.add(anomaly)
            anomaly.score = 82
            anomaly.severity = risk_level(anomaly.score)
            anomaly.explanation = f"Evidence checksum matches media record {duplicate.id} from project {duplicate.project_id}."
            anomaly.evidence_json = [
                {"type": "media", "id": str(media.id)},
                {"type": "media", "id": str(duplicate.id)},
            ]
            anomaly.model_version = "media-rules-v1.0"
            anomaly.status = "open"

    session.commit()
    return {
        "geoMatchScore": int(media.geo_match_score or 0),
        "progressConfidence": int(media.progress_confidence or 0),
        "duplicateFound": duplicate_found,
    }

