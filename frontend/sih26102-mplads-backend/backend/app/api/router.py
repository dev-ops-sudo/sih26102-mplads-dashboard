from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import desc, false, or_, select
from sqlalchemy.orm import Session, selectinload

from app.auth import Principal, get_current_user, get_scoped_db, require_roles
from app.config import settings
from app.models import (
    Agency,
    Alert,
    Anomaly,
    DuplicateRelationship,
    FinancialTransaction,
    IngestionRun,
    Inspection,
    InvestigationMessage,
    Prediction,
    Project,
    ProjectMedia,
    RiskAssessment,
    TimelineEvent,
)
from app.schemas import (
    AgencyOut,
    AlertOut,
    AnomalyOut,
    CompleteUploadRequest,
    DashboardSummaryOut,
    DuplicateRelationshipOut,
    FinancialTransactionOut,
    IngestionRequest,
    IngestionResponse,
    InspectionCreate,
    InspectionOut,
    InvestigationRequest,
    InvestigationResponse,
    JobResponse,
    PredictionOut,
    PresignUploadRequest,
    PresignUploadResponse,
    ProjectIntelligenceOut,
    ProjectMediaOut,
    ProjectOut,
    RiskAssessmentOut,
    TimelineEventOut,
)
from app.services.audit import record_audit
from app.services.dashboard import dashboard_summary, project_intelligence, project_query
from app.services.duplicate_detector import refresh_duplicate_relationships
from app.services.investigation import answer_question
from app.services.media_intelligence import analyze_media
from app.services.risk_engine import recompute_all_risks, recompute_project_risk
from app.services.serializers import alert_dict, duplicate_dict, project_dict
from app.services.storage import upload_service


router = APIRouter()


def scoped_projects(statement, user: Principal):
    if "NationalAdmin" in user.roles or "Auditor" in user.roles:
        return statement
    if user.district:
        return statement.where(Project.district == user.district)
    if user.state:
        return statement.where(Project.state == user.state)
    return statement.where(false())


def enforce_project_scope(project: Project, user: Principal) -> None:
    if user.roles.intersection({"NationalAdmin", "Auditor"}):
        return
    if user.district and project.district == user.district:
        return
    if user.state and project.state == user.state:
        return
    raise HTTPException(status_code=404, detail="Project not found")


@router.get("/dashboard/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(
    session: Session = Depends(get_scoped_db), user: Principal = Depends(get_current_user)
):
    return dashboard_summary(session, scoped_projects(project_query(), user))


@router.get("/projects", response_model=list[ProjectOut])
def list_projects(
    states: list[str] | None = Query(default=None),
    districts: list[str] | None = Query(default=None),
    constituencies: list[str] | None = Query(default=None),
    types: list[str] | None = Query(default=None),
    statuses: list[str] | None = Query(default=None),
    risks: list[str] | None = Query(default=None),
    search: str | None = None,
    limit: int = Query(default=250, ge=1, le=1000),
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    statement = scoped_projects(project_query(), user)
    if states:
        statement = statement.where(Project.state.in_(states))
    if districts:
        statement = statement.where(or_(Project.district.in_(districts), Project.city.in_(districts)))
    if constituencies:
        statement = statement.where(Project.constituency.in_(constituencies))
    if types:
        statement = statement.where(Project.type.in_(types))
    if statuses:
        statement = statement.where(Project.status.in_(statuses))
    if risks:
        statement = statement.where(Project.risk.in_(risks))
    if search:
        pattern = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Project.title.ilike(pattern),
                Project.district.ilike(pattern),
                Project.constituency.ilike(pattern),
                Project.agency.ilike(pattern),
            )
        )
    projects = list(session.scalars(statement.order_by(Project.risk_score.desc()).limit(limit)))
    return [project_dict(project) for project in projects]


@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.scalar(project_query().where(Project.id == project_id))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    return project_dict(project)


@router.get("/projects/{project_id}/intelligence", response_model=ProjectIntelligenceOut)
def get_project_intelligence(
    project_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.scalar(
        select(Project)
        .options(selectinload(Project.anomalies), selectinload(Project.agency_record))
        .where(Project.id == project_id)
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    return project_intelligence(session, project)


@router.get("/projects/{project_id}/risk", response_model=RiskAssessmentOut)
def get_project_risk(
    project_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    assessment = session.scalar(
        select(RiskAssessment)
        .options(selectinload(RiskAssessment.contributions))
        .where(RiskAssessment.project_id == project_id)
        .order_by(desc(RiskAssessment.generated_at))
        .limit(1)
    )
    if assessment is None:
        assessment = recompute_project_risk(session, project)
        session.commit()
    return {
        "project_id": project_id,
        "score": assessment.score,
        "level": assessment.level,
        "model_version": assessment.model_version,
        "generated_at": assessment.generated_at,
        "contributions": [
            {
                "label": item.label,
                "weight": item.weight,
                "score": item.score,
                "explanation": item.explanation,
            }
            for item in assessment.contributions
        ],
    }


@router.get("/projects/{project_id}/timeline", response_model=list[TimelineEventOut])
def get_project_timeline(
    project_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    return list(
        session.scalars(
            select(TimelineEvent).where(TimelineEvent.project_id == project_id).order_by(TimelineEvent.date)
        )
    )


@router.get("/projects/{project_id}/financials", response_model=list[FinancialTransactionOut])
def get_project_financials(
    project_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    transactions = list(
        session.scalars(
            select(FinancialTransaction)
            .where(FinancialTransaction.project_id == project_id)
            .order_by(FinancialTransaction.transaction_date.desc())
        )
    )
    return [
        {
            "id": item.id,
            "project_id": item.project_id,
            "transaction_type": item.transaction_type,
            "amount_cr": item.amount_cr,
            "transaction_date": item.transaction_date,
            "reference": item.reference,
            "metadata": item.metadata_json,
        }
        for item in transactions
    ]


@router.get("/projects/{project_id}/inspections", response_model=list[InspectionOut])
def get_project_inspections(
    project_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    return list(
        session.scalars(
            select(Inspection).where(Inspection.project_id == project_id).order_by(Inspection.inspected_at.desc())
        )
    )


@router.get("/projects/{project_id}/media", response_model=list[ProjectMediaOut])
def get_project_media(
    project_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    media = list(
        session.scalars(
            select(ProjectMedia).where(ProjectMedia.project_id == project_id).order_by(ProjectMedia.captured_at)
        )
    )
    return [
        {
            "id": item.id,
            "stage": item.stage,
            "url": item.public_url,
            "captured_at": item.captured_at,
            "geo_match_score": item.geo_match_score,
            "progress_confidence": item.progress_confidence,
        }
        for item in media
    ]


@router.get("/agencies", response_model=list[AgencyOut])
def list_agencies(
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project_rows = list(session.scalars(scoped_projects(select(Project), user)))
    names = sorted({project.agency for project in project_rows})
    agencies = list(session.scalars(select(Agency).where(Agency.name.in_(names)).order_by(Agency.risk_score.desc())))
    return [
        {
            "name": agency.name,
            "projects": agency.projects_count,
            "avg_delay_days": agency.avg_delay_days,
            "risk_score": agency.risk_score,
            "completion_rate": agency.completion_rate,
        }
        for agency in agencies
    ]


@router.get("/anomalies", response_model=list[AnomalyOut])
def list_anomalies(
    project_id: str | None = None,
    severity: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    statement = scoped_projects(select(Anomaly).join(Project, Project.id == Anomaly.project_id), user)
    if project_id:
        statement = statement.where(Anomaly.project_id == project_id)
    if severity:
        statement = statement.where(Anomaly.severity == severity)
    anomalies = list(session.scalars(statement.order_by(Anomaly.score.desc()).limit(limit)))
    return [
        {
            "id": item.id,
            "project_id": item.project_id,
            "type": item.type,
            "score": item.score,
            "severity": item.severity,
            "explanation": item.explanation,
            "evidence": item.evidence_json,
            "model_version": item.model_version,
            "status": item.status,
        }
        for item in anomalies
    ]


@router.get("/predictions", response_model=list[PredictionOut])
def list_predictions(
    project_id: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    statement = scoped_projects(select(Prediction).join(Project, Project.id == Prediction.project_id), user)
    if project_id:
        statement = statement.where(Prediction.project_id == project_id)
    predictions = list(session.scalars(statement.order_by(Prediction.probability.desc()).limit(limit)))
    return predictions


@router.get("/duplicate-relationships", response_model=list[DuplicateRelationshipOut])
def list_duplicate_relationships(
    limit: int = Query(default=100, ge=1, le=500),
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project_ids = list(session.scalars(scoped_projects(select(Project.id), user)))
    statement = (
        select(DuplicateRelationship)
        .where(
            or_(
                DuplicateRelationship.project_a_id.in_(project_ids),
                DuplicateRelationship.project_b_id.in_(project_ids),
            )
        )
        .order_by(DuplicateRelationship.similarity_score.desc())
        .limit(limit)
    )
    return [duplicate_dict(session, item) for item in session.scalars(statement)]


@router.get("/geo/projects", response_model=list[ProjectOut])
def geo_projects(
    session: Session = Depends(get_scoped_db), user: Principal = Depends(get_current_user)
):
    projects = list(session.scalars(scoped_projects(project_query(), user).order_by(Project.risk_score.desc())))
    return [project_dict(project) for project in projects]


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(
    acknowledged: bool | None = None,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    statement = scoped_projects(select(Alert).join(Project, Project.id == Alert.project_id), user).order_by(Alert.created_at.desc())
    if acknowledged is not None:
        statement = statement.where(Alert.acknowledged == acknowledged)
    return [alert_dict(alert) for alert in session.scalars(statement.limit(100))]


@router.patch("/alerts/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(
    alert_id: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(require_roles("NationalAdmin", "StateOfficer", "DistrictOfficer", "Auditor")),
):
    alert = session.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    project = session.get(Project, alert.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    enforce_project_scope(project, user)
    alert.acknowledged = True
    alert.acknowledged_by = user.id
    alert.acknowledged_at = datetime.now(timezone.utc)
    record_audit(session, user, "alert.acknowledge", "alert", alert.id)
    session.commit()
    session.refresh(alert)
    return alert_dict(alert)


@router.post("/investigation/query", response_model=InvestigationResponse)
def investigate(
    payload: InvestigationRequest,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    project = session.get(Project, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    answer, evidence, provider = answer_question(session, project, payload.question)
    session.add(
        InvestigationMessage(
            project_id=project.id,
            user_id=user.id,
            question=payload.question,
            answer=answer,
            evidence_json=evidence,
            provider=provider,
        )
    )
    record_audit(session, user, "investigation.query", "project", project.id, {"provider": provider})
    session.commit()
    return {"answer": answer, "evidence": evidence, "provider": provider}


@router.post("/uploads/presign", response_model=PresignUploadResponse)
def presign_upload(
    payload: PresignUploadRequest,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(require_roles("NationalAdmin", "StateOfficer", "DistrictOfficer")),
):
    project = session.get(Project, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    return upload_service.presign(payload.project_id, payload.stage, payload.filename, payload.content_type)


@router.put("/uploads/local/{object_key:path}", status_code=status.HTTP_204_NO_CONTENT)
async def local_upload(
    object_key: str,
    request: Request,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(require_roles("NationalAdmin", "StateOfficer", "DistrictOfficer")),
):
    parts = object_key.split("/")
    if len(parts) < 4 or parts[0] != "projects":
        raise HTTPException(status_code=400, detail="Invalid evidence path")
    project = session.get(Project, parts[1])
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    try:
        target = upload_service.local_path(object_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    body = await request.body()
    if len(body) > 25 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Upload exceeds 25 MB")
    target.write_bytes(body)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/uploads/download/{object_key:path}")
def download_evidence(
    object_key: str,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(get_current_user),
):
    parts = object_key.split("/")
    if len(parts) < 4 or parts[0] != "projects":
        raise HTTPException(status_code=400, detail="Invalid evidence path")
    project = session.get(Project, parts[1])
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    if settings.storage_backend == "s3":
        return RedirectResponse(upload_service.presigned_download(object_key), status_code=307)
    path = upload_service.local_path(object_key)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Evidence file not found")
    return FileResponse(path)


@router.post("/uploads/complete")
def complete_upload(
    payload: CompleteUploadRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(require_roles("NationalAdmin", "StateOfficer", "DistrictOfficer")),
):
    project = session.get(Project, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    expected_prefix = f"projects/{project.id}/{payload.stage}/"
    if not payload.object_key.startswith(expected_prefix):
        raise HTTPException(status_code=400, detail="Evidence key does not match project and stage")
    if not upload_service.object_exists(payload.object_key):
        raise HTTPException(status_code=400, detail="Uploaded evidence object was not found")
    media = ProjectMedia(
        project_id=payload.project_id,
        stage=payload.stage,
        object_key=payload.object_key,
        public_url=upload_service.object_url(payload.object_key),
        captured_at=payload.captured_at,
        latitude=payload.latitude,
        longitude=payload.longitude,
        sha256=payload.sha256 or upload_service.local_checksum(payload.object_key),
    )
    session.add(media)
    record_audit(session, user, "evidence.upload", "project", payload.project_id, {"stage": payload.stage})
    session.commit()
    session.refresh(media)
    queue_media_analysis(background_tasks, media.id)
    return {"id": media.id, "url": media.public_url, "status": "registered"}


@router.post("/inspections", status_code=status.HTTP_201_CREATED)
def create_inspection(
    payload: InspectionCreate,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(require_roles("NationalAdmin", "StateOfficer", "DistrictOfficer")),
):
    project = session.get(Project, payload.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    enforce_project_scope(project, user)
    inspection = Inspection(
        project_id=payload.project_id,
        inspected_at=payload.inspected_at,
        officer_id=user.id,
        physical_progress=payload.physical_progress,
        latitude=payload.latitude,
        longitude=payload.longitude,
        notes=payload.notes,
        evidence_confidence=payload.evidence_confidence,
    )
    session.add(inspection)
    project.progress = payload.physical_progress
    project.last_inspection = payload.inspected_at.date()
    record_audit(session, user, "inspection.create", "project", project.id)
    recompute_project_risk(session, project)
    session.commit()
    return {"id": inspection.id, "status": "created", "riskScore": project.risk_score}


@router.post("/ingestion/import", response_model=IngestionResponse, status_code=status.HTTP_202_ACCEPTED)
def ingest_projects(
    payload: IngestionRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_scoped_db),
    user: Principal = Depends(require_roles("NationalAdmin")),
):
    run_id = f"ING-{uuid4().hex[:12].upper()}"
    run = IngestionRun(
        id=run_id,
        source_name=payload.source_name,
        status="processing",
        records_received=len(payload.projects),
        records_accepted=0,
    )
    session.add(run)
    errors: list[dict] = []
    accepted = 0
    for record in payload.projects:
        agency = session.get(Agency, record.agency)
        if agency is None:
            agency = Agency(name=record.agency)
            session.add(agency)
            session.flush()
        project = session.get(Project, record.id) or Project(id=record.id)
        project.title = record.title
        project.state = record.state
        project.district = record.district
        project.constituency = record.constituency
        project.city = record.city
        project.type = record.type
        project.agency = record.agency
        project.status = record.status
        project.risk = "Low"
        project.budget_cr = record.budget_cr
        project.spent_cr = record.spent_cr
        project.utilization = round(record.spent_cr / record.budget_cr * 100)
        project.progress = record.progress
        project.sanctioned_date = record.sanctioned_date
        project.expected_completion = record.expected_completion
        project.last_inspection = record.last_inspection
        project.latitude = record.latitude
        project.longitude = record.longitude
        project.location = f"SRID=4326;POINT({record.longitude} {record.latitude})"
        project.risk_score = 0
        project.summary = record.summary
        project.source_system = payload.source_name
        session.add(project)
        accepted += 1
    run.records_accepted = accepted
    run.errors_json = errors
    run.status = "completed"
    run.completed_at = datetime.now(timezone.utc)
    record_audit(session, user, "ingestion.import", "ingestion_run", run_id, {"accepted": accepted})
    session.commit()
    queue_national_scan(background_tasks)
    return {
        "run_id": run_id,
        "status": run.status,
        "records_received": run.records_received,
        "records_accepted": accepted,
        "errors": errors,
    }


def run_post_ingestion_scan() -> None:
    from app.db import SessionLocal

    with SessionLocal() as session:
        refresh_duplicate_relationships(session)
        session.commit()
        recompute_all_risks(session)


def run_media_analysis(media_id: int) -> None:
    from app.db import SessionLocal

    with SessionLocal() as session:
        analyze_media(session, media_id)


def queue_national_scan(background_tasks: BackgroundTasks) -> str:
    if not settings.celery_enabled:
        task_id = uuid4().hex
        background_tasks.add_task(run_post_ingestion_scan)
        return task_id
    try:
        from app.workers.tasks import refresh_national_risk

        return str(refresh_national_risk.delay().id)
    except Exception:
        task_id = uuid4().hex
        background_tasks.add_task(run_post_ingestion_scan)
        return task_id


def queue_media_analysis(background_tasks: BackgroundTasks, media_id: int) -> str:
    if not settings.celery_enabled:
        task_id = uuid4().hex
        background_tasks.add_task(run_media_analysis, media_id)
        return task_id
    try:
        from app.workers.tasks import analyze_project_media

        return str(analyze_project_media.delay(media_id).id)
    except Exception:
        task_id = uuid4().hex
        background_tasks.add_task(run_media_analysis, media_id)
        return task_id


@router.post("/admin/risk/recompute", response_model=JobResponse, status_code=status.HTTP_202_ACCEPTED)
def trigger_risk_recompute(
    background_tasks: BackgroundTasks,
    user: Principal = Depends(require_roles("NationalAdmin", "Auditor")),
):
    task_id = queue_national_scan(background_tasks)
    return {"status": "queued", "task_id": task_id}
