"""Add database-enforced officer scope policies.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-01
"""
from alembic import op
from sqlalchemy import text


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


PROJECT_TABLES = [
    "project_milestones",
    "financial_transactions",
    "inspections",
    "project_media",
    "anomalies",
    "risk_assessments",
    "predictions",
    "alerts",
    "timeline_events",
    "investigation_messages",
    "source_documents",
]


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    bind.execute(
        text(
            """
            DO $$
            BEGIN
              IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'mplads_runtime') THEN
                CREATE ROLE mplads_runtime NOLOGIN;
              END IF;
              EXECUTE format('GRANT mplads_runtime TO %I', current_user);
            END
            $$;
            GRANT USAGE ON SCHEMA public TO mplads_runtime;
            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO mplads_runtime;
            GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO mplads_runtime;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO mplads_runtime;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO mplads_runtime;
            """
        )
    )

    project_scope = """
        current_setting('app.is_national', true) = 'true'
        OR state = current_setting('app.user_state', true)
        OR district = current_setting('app.user_district', true)
    """
    bind.execute(text("ALTER TABLE projects ENABLE ROW LEVEL SECURITY"))
    bind.execute(text(f"CREATE POLICY projects_officer_scope ON projects USING ({project_scope}) WITH CHECK ({project_scope})"))

    for table_name in PROJECT_TABLES:
        bind.execute(text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY"))
        scope_expression = "project_id IN (SELECT id FROM projects)"
        if table_name == "source_documents":
            scope_expression += " OR (project_id IS NULL AND current_setting('app.is_national', true) = 'true')"
        bind.execute(
            text(
                f"CREATE POLICY {table_name}_officer_scope ON {table_name} "
                f"USING ({scope_expression}) WITH CHECK ({scope_expression})"
            )
        )

    bind.execute(text("ALTER TABLE risk_contributions ENABLE ROW LEVEL SECURITY"))
    bind.execute(
        text(
            "CREATE POLICY risk_contributions_officer_scope ON risk_contributions "
            "USING (assessment_id IN (SELECT id FROM risk_assessments)) "
            "WITH CHECK (assessment_id IN (SELECT id FROM risk_assessments))"
        )
    )
    bind.execute(text("ALTER TABLE duplicate_relationships ENABLE ROW LEVEL SECURITY"))
    bind.execute(
        text(
            "CREATE POLICY duplicate_relationships_officer_scope ON duplicate_relationships "
            "USING (project_a_id IN (SELECT id FROM projects) OR project_b_id IN (SELECT id FROM projects)) "
            "WITH CHECK (project_a_id IN (SELECT id FROM projects) OR project_b_id IN (SELECT id FROM projects))"
        )
    )
    bind.execute(text("ALTER TABLE audit_events ENABLE ROW LEVEL SECURITY"))
    bind.execute(
        text(
            "CREATE POLICY audit_events_read_scope ON audit_events FOR SELECT "
            "USING (current_setting('app.is_national', true) = 'true')"
        )
    )
    bind.execute(
        text(
            "CREATE POLICY audit_events_insert_scope ON audit_events FOR INSERT "
            "WITH CHECK (actor_id = current_setting('app.user_id', true) OR current_setting('app.is_national', true) = 'true')"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    bind.execute(text("DROP POLICY IF EXISTS projects_officer_scope ON projects"))
    bind.execute(text("ALTER TABLE projects DISABLE ROW LEVEL SECURITY"))
    for table_name in PROJECT_TABLES:
        bind.execute(text(f"DROP POLICY IF EXISTS {table_name}_officer_scope ON {table_name}"))
        bind.execute(text(f"ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY"))
    bind.execute(text("DROP POLICY IF EXISTS risk_contributions_officer_scope ON risk_contributions"))
    bind.execute(text("ALTER TABLE risk_contributions DISABLE ROW LEVEL SECURITY"))
    bind.execute(text("DROP POLICY IF EXISTS duplicate_relationships_officer_scope ON duplicate_relationships"))
    bind.execute(text("ALTER TABLE duplicate_relationships DISABLE ROW LEVEL SECURITY"))
    bind.execute(text("DROP POLICY IF EXISTS audit_events_read_scope ON audit_events"))
    bind.execute(text("DROP POLICY IF EXISTS audit_events_insert_scope ON audit_events"))
    bind.execute(text("ALTER TABLE audit_events DISABLE ROW LEVEL SECURITY"))
    bind.execute(text("REVOKE mplads_runtime FROM CURRENT_USER"))
    bind.execute(text("DROP ROLE IF EXISTS mplads_runtime"))
