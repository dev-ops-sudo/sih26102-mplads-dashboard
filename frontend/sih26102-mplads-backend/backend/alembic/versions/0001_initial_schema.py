"""Create the initial MPLADS intelligence schema.

Revision ID: 0001
Revises:
Create Date: 2026-09-01
"""
from alembic import op
from sqlalchemy import text

from app import models  # noqa: F401
from app.db import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        bind.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=bind)
    if bind.dialect.name == "postgresql":
        bind.execute(text("CREATE INDEX IF NOT EXISTS ix_projects_location_gist ON projects USING GIST (location)"))
        bind.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_source_documents_embedding_hnsw "
                "ON source_documents USING hnsw (embedding vector_cosine_ops)"
            )
        )


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())

