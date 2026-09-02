from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class PointType(TypeDecorator):
    impl = Text
    cache_ok = True
    spatial_index = False

    def load_dialect_impl(self, dialect):
        if dialect is None:
            return self.impl
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Geometry("POINT", srid=4326, spatial_index=False))
        return dialect.type_descriptor(Text())


class EmbeddingType(TypeDecorator):
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect is None:
            return self.impl
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector(1536))
        return dialect.type_descriptor(JSON())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class Agency(TimestampMixin, Base):
    __tablename__ = "agencies"

    name: Mapped[str] = mapped_column(String(180), primary_key=True)
    projects_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_delay_days: Mapped[int] = mapped_column(Integer, default=0)
    risk_score: Mapped[int] = mapped_column(Integer, default=0)
    completion_rate: Mapped[int] = mapped_column(Integer, default=0)

    projects: Mapped[list[Project]] = relationship(back_populates="agency_record")


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    title: Mapped[str] = mapped_column(String(260), index=True)
    state: Mapped[str] = mapped_column(String(120), index=True)
    district: Mapped[str] = mapped_column(String(120), index=True)
    constituency: Mapped[str] = mapped_column(String(160), index=True)
    city: Mapped[str] = mapped_column(String(120), index=True)
    type: Mapped[str] = mapped_column(String(120), index=True)
    agency: Mapped[str] = mapped_column(ForeignKey("agencies.name"), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    risk: Mapped[str] = mapped_column(String(20), index=True)
    budget_cr: Mapped[float] = mapped_column(Float)
    spent_cr: Mapped[float] = mapped_column(Float)
    utilization: Mapped[int] = mapped_column(Integer)
    progress: Mapped[int] = mapped_column(Integer)
    sanctioned_date: Mapped[date] = mapped_column(Date)
    expected_completion: Mapped[date] = mapped_column(Date)
    last_inspection: Mapped[date] = mapped_column(Date)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    location: Mapped[str | None] = mapped_column(PointType(), nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    summary: Mapped[str] = mapped_column(Text)
    source_system: Mapped[str] = mapped_column(String(80), default="demo")

    agency_record: Mapped[Agency] = relationship(back_populates="projects")
    anomalies: Mapped[list[Anomaly]] = relationship(back_populates="project", cascade="all, delete-orphan")
    predictions: Mapped[list[Prediction]] = relationship(back_populates="project", cascade="all, delete-orphan")
    timeline_events: Mapped[list[TimelineEvent]] = relationship(back_populates="project", cascade="all, delete-orphan")
    media: Mapped[list[ProjectMedia]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Milestone(TimestampMixin, Base):
    __tablename__ = "project_milestones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(220))
    due_date: Mapped[date] = mapped_column(Date)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_progress: Mapped[int] = mapped_column(Integer, default=0)
    actual_progress: Mapped[int] = mapped_column(Integer, default=0)


class FinancialTransaction(TimestampMixin, Base):
    __tablename__ = "financial_transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    transaction_type: Mapped[str] = mapped_column(String(40))
    amount_cr: Mapped[float] = mapped_column(Float)
    transaction_date: Mapped[date] = mapped_column(Date)
    reference: Mapped[str] = mapped_column(String(120), unique=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class Inspection(TimestampMixin, Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    inspected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    officer_id: Mapped[str] = mapped_column(String(100))
    physical_progress: Mapped[int] = mapped_column(Integer)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(Text)
    evidence_confidence: Mapped[int] = mapped_column(Integer, default=0)


class ProjectMedia(TimestampMixin, Base):
    __tablename__ = "project_media"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    stage: Mapped[str] = mapped_column(String(20))
    object_key: Mapped[str] = mapped_column(String(500), unique=True)
    public_url: Mapped[str | None] = mapped_column(String(800), nullable=True)
    captured_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    perceptual_hash: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    geo_match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    progress_confidence: Mapped[int | None] = mapped_column(Integer, nullable=True)

    project: Mapped[Project] = relationship(back_populates="media")


class Anomaly(TimestampMixin, Base):
    __tablename__ = "anomalies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(80), index=True)
    score: Mapped[int] = mapped_column(Integer)
    severity: Mapped[str] = mapped_column(String(20), index=True)
    explanation: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(40), default="rules-v1")
    status: Mapped[str] = mapped_column(String(24), default="open")

    project: Mapped[Project] = relationship(back_populates="anomalies")


class RiskAssessment(TimestampMixin, Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    score: Mapped[int] = mapped_column(Integer)
    level: Mapped[str] = mapped_column(String(20))
    model_version: Mapped[str] = mapped_column(String(40))
    data_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    contributions: Mapped[list[RiskContribution]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class RiskContribution(Base):
    __tablename__ = "risk_contributions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("risk_assessments.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(120))
    weight: Mapped[int] = mapped_column(Integer)
    score: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text)

    assessment: Mapped[RiskAssessment] = relationship(back_populates="contributions")


class Prediction(TimestampMixin, Base):
    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(240))
    probability: Mapped[int] = mapped_column(Integer)
    impact: Mapped[str] = mapped_column(String(24))
    recommendation: Mapped[str] = mapped_column(Text)
    model_version: Mapped[str] = mapped_column(String(40), default="forecast-v1")
    horizon_days: Mapped[int] = mapped_column(Integer, default=90)

    project: Mapped[Project] = relationship(back_populates="predictions")


class DuplicateRelationship(TimestampMixin, Base):
    __tablename__ = "duplicate_relationships"
    __table_args__ = (UniqueConstraint("project_a_id", "project_b_id", name="uq_duplicate_pair"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_a_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    project_b_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    similarity_score: Mapped[int] = mapped_column(Integer)
    distance_km: Mapped[float] = mapped_column(Float)
    reasons: Mapped[list[str]] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(40), default="duplicate-v1")
    status: Mapped[str] = mapped_column(String(24), default="candidate")


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(260))
    district: Mapped[str] = mapped_column(String(120))
    severity: Mapped[str] = mapped_column(String(20), index=True)
    description: Mapped[str] = mapped_column(Text)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    acknowledged_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TimelineEvent(TimestampMixin, Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    date: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(String(220))
    state: Mapped[str] = mapped_column(String(20))
    detail: Mapped[str] = mapped_column(Text)

    project: Mapped[Project] = relationship(back_populates="timeline_events")


class InvestigationMessage(TimestampMixin, Base):
    __tablename__ = "investigation_messages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String(100), index=True)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    evidence_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    provider: Mapped[str] = mapped_column(String(40), default="mock")


class SourceDocument(TimestampMixin, Base):
    __tablename__ = "source_documents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[str | None] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(260))
    source_type: Mapped[str] = mapped_column(String(60))
    object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), unique=True)
    embedding: Mapped[list[float] | None] = mapped_column(EmbeddingType(), nullable=True)


class IngestionRun(TimestampMixin, Base):
    __tablename__ = "ingestion_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(24), index=True)
    records_received: Mapped[int] = mapped_column(Integer, default=0)
    records_accepted: Mapped[int] = mapped_column(Integer, default=0)
    errors_json: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    actor_id: Mapped[str] = mapped_column(String(100), index=True)
    action: Mapped[str] = mapped_column(String(100), index=True)
    resource_type: Mapped[str] = mapped_column(String(80), index=True)
    resource_id: Mapped[str] = mapped_column(String(100), index=True)
    details_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

