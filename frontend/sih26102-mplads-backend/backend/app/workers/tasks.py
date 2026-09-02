from app.db import SessionLocal
from app.services.duplicate_detector import refresh_duplicate_relationships
from app.services.media_intelligence import analyze_media
from app.services.risk_engine import recompute_all_risks
from app.workers.celery_app import celery_app


@celery_app.task(
    name="app.workers.tasks.refresh_national_risk",
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def refresh_national_risk() -> dict[str, int]:
    with SessionLocal() as session:
        relationships = refresh_duplicate_relationships(session)
        session.commit()
        projects = recompute_all_risks(session)
    return {"projects": projects, "duplicateRelationships": relationships}


@celery_app.task(
    name="app.workers.tasks.analyze_project_media",
    autoretry_for=(ConnectionError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def analyze_project_media(media_id: int) -> dict[str, int | bool]:
    with SessionLocal() as session:
        return analyze_media(session, media_id)
