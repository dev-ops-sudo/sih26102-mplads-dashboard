from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def to_camel(value: str) -> str:
    first, *rest = value.split("_")
    return first + "".join(item.capitalize() for item in rest)


class APIModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel, from_attributes=True)


RiskLevel = Literal["Low", "Medium", "High", "Critical"]
ProjectStatus = Literal["On Track", "Delayed", "Flagged", "Completed"]


class ProjectOut(APIModel):
    id: str
    title: str
    state: str
    district: str
    constituency: str
    city: str
    type: str
    agency: str
    status: ProjectStatus
    risk: RiskLevel
    budget_cr: float
    spent_cr: float
    utilization: int
    progress: int
    sanctioned_date: date
    expected_completion: date
    last_inspection: date
    latitude: float
    longitude: float
    risk_score: int
    anomaly_types: list[str] = []
    summary: str


class ProjectCreate(APIModel):
    id: str
    title: str
    state: str
    district: str
    constituency: str
    city: str
    type: str
    agency: str
    status: ProjectStatus = "On Track"
    budget_cr: float = Field(gt=0)
    spent_cr: float = Field(ge=0)
    progress: int = Field(ge=0, le=100)
    sanctioned_date: date
    expected_completion: date
    last_inspection: date
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    summary: str

    @field_validator("expected_completion")
    @classmethod
    def completion_after_sanction(cls, value: date, info):
        sanctioned = info.data.get("sanctioned_date")
        if sanctioned and value < sanctioned:
            raise ValueError("expected completion must be after sanction date")
        return value


class AlertOut(APIModel):
    id: str
    project_id: str
    title: str
    district: str
    severity: RiskLevel
    time: str
    description: str
    acknowledged: bool = False
    created_at: datetime


class AgencyOut(APIModel):
    name: str
    projects: int
    avg_delay_days: int
    risk_score: int
    completion_rate: int


class RiskContributionOut(APIModel):
    label: str
    weight: int
    score: int
    explanation: str


class PredictionOut(APIModel):
    id: str
    title: str
    probability: int
    impact: Literal["Cost", "Delay", "Compliance"]
    project_id: str
    recommendation: str


class TimelineEventOut(APIModel):
    date: date
    title: str
    state: Literal["done", "active", "risk", "upcoming"]
    detail: str


class AnomalyOut(APIModel):
    id: str
    project_id: str
    type: str
    score: int
    severity: RiskLevel
    explanation: str
    evidence: list[dict[str, Any]] = []
    model_version: str
    status: str


class DuplicateRelationshipOut(APIModel):
    id: int
    project_a_id: str
    project_b_id: str
    project_a_title: str
    project_b_title: str
    similarity_score: int
    distance_km: float
    reasons: list[str]
    status: str


class ProjectMediaOut(APIModel):
    id: int
    stage: str
    url: str | None = None
    captured_at: datetime | None = None
    geo_match_score: int | None = None
    progress_confidence: int | None = None


class ProjectIntelligenceOut(APIModel):
    project_id: str
    risk_score: int
    risk_contributions: list[RiskContributionOut]
    anomalies: list[AnomalyOut]
    predictions: list[PredictionOut]
    timeline: list[TimelineEventOut]
    media: list[ProjectMediaOut]
    duplicate_relationships: list[DuplicateRelationshipOut]


class RiskAssessmentOut(APIModel):
    project_id: str
    score: int
    level: RiskLevel
    model_version: str
    generated_at: datetime
    contributions: list[RiskContributionOut]


class FinancialTransactionOut(APIModel):
    id: int
    project_id: str
    transaction_type: str
    amount_cr: float
    transaction_date: date
    reference: str
    metadata: dict[str, Any] = {}


class InspectionOut(APIModel):
    id: int
    project_id: str
    inspected_at: datetime
    officer_id: str
    physical_progress: int
    latitude: float
    longitude: float
    notes: str
    evidence_confidence: int


class MonthlyTrendPoint(APIModel):
    month: str
    spend: int
    progress: int
    alerts: int


class SectorRiskPoint(APIModel):
    sector: str
    risk: int


class DashboardSummaryOut(APIModel):
    projects: list[ProjectOut]
    alerts: list[AlertOut]
    agencies: list[AgencyOut]
    predictions: list[PredictionOut]
    monthly_trend: list[MonthlyTrendPoint]
    sector_risk: list[SectorRiskPoint]
    changed_since_login: list[str]
    situation_brief: str
    generated_at: datetime


class InvestigationRequest(APIModel):
    project_id: str
    question: str = Field(min_length=3, max_length=1200)


class EvidenceReference(APIModel):
    id: str
    label: str
    type: str


class InvestigationResponse(APIModel):
    answer: str
    evidence: list[EvidenceReference]
    provider: str


class PresignUploadRequest(APIModel):
    project_id: str
    stage: Literal["before", "during", "after", "document"]
    filename: str
    content_type: str

    @field_validator("content_type")
    @classmethod
    def supported_evidence_type(cls, value: str) -> str:
        supported = {
            "image/jpeg",
            "image/png",
            "image/webp",
            "application/pdf",
            "text/csv",
            "application/json",
        }
        if value.lower() not in supported:
            raise ValueError("unsupported evidence content type")
        return value.lower()


class PresignUploadResponse(APIModel):
    upload_url: str
    object_key: str
    method: str = "PUT"
    headers: dict[str, str] = {}


class CompleteUploadRequest(APIModel):
    project_id: str
    stage: Literal["before", "during", "after", "document"]
    object_key: str
    captured_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    sha256: str | None = None


class InspectionCreate(APIModel):
    project_id: str
    inspected_at: datetime
    physical_progress: int = Field(ge=0, le=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    notes: str = Field(min_length=3)
    evidence_confidence: int = Field(default=0, ge=0, le=100)


class IngestionRequest(APIModel):
    source_name: str
    projects: list[ProjectCreate]


class IngestionResponse(APIModel):
    run_id: str
    status: str
    records_received: int
    records_accepted: int
    errors: list[dict[str, Any]] = []


class JobResponse(APIModel):
    status: str
    task_id: str | None = None
