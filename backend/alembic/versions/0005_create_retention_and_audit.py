"""create_retention_and_audit

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Create retention_policy table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS retention_policy (
            policy_id              SERIAL PRIMARY KEY,
            school_id              INTEGER NOT NULL REFERENCES school(school_id) ON DELETE RESTRICT,
            scope                  VARCHAR(50) NOT NULL CHECK (scope IN ('telemetry_events', 'trips', 'audit_logs')),
            default_days           INTEGER NOT NULL CHECK (default_days > 0),
            min_days               INTEGER NOT NULL CHECK (min_days > 0),
            max_days               INTEGER NOT NULL CHECK (max_days >= min_days),
            school_override_days   INTEGER,
            purge_enabled          BOOLEAN NOT NULL DEFAULT TRUE,
            updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            
            CONSTRAINT uq_retention_school_scope UNIQUE (school_id, scope),
            CONSTRAINT chk_retention_override_bounds CHECK (
                school_override_days IS NULL OR 
                (school_override_days >= min_days AND school_override_days <= max_days)
            )
        );

        -- Dynamically seed default retention policies for the default school
        DO $$
        DECLARE
            v_school_id INTEGER;
        BEGIN
            SELECT school_id INTO v_school_id FROM school WHERE LOWER(school_code) = 'default' LIMIT 1;
            IF v_school_id IS NOT NULL THEN
                INSERT INTO retention_policy (school_id, scope, default_days, min_days, max_days, purge_enabled)
                VALUES 
                    (v_school_id, 'telemetry_events', 30,  7,  90,  TRUE),
                    (v_school_id, 'trips',            365, 90, 730, TRUE),
                    (v_school_id, 'audit_logs',        365, 90, 1095, TRUE)
                ON CONFLICT (school_id, scope) DO NOTHING;
            END IF;
        END $$;
    """))

    # 2. Create audit_log table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS audit_log (
            log_id         BIGSERIAL PRIMARY KEY,
            school_id      INTEGER REFERENCES school(school_id) ON DELETE SET NULL,
            actor_type     VARCHAR(20)  NOT NULL CHECK (actor_type IN ('admin', 'parent', 'driver', 'system')),
            actor_id       INTEGER,
            actor_username VARCHAR(255),
            action         VARCHAR(100) NOT NULL,
            target_table   VARCHAR(100),
            target_id      BIGINT,
            detail         JSONB,
            ip_address     INET,
            occurred_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        CREATE INDEX IF NOT EXISTS idx_audit_school_time ON audit_log (school_id, occurred_at DESC);
        CREATE INDEX IF NOT EXISTS idx_audit_actor       ON audit_log (actor_type, actor_id, occurred_at DESC);
        CREATE INDEX IF NOT EXISTS idx_audit_action      ON audit_log (action, occurred_at DESC);
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        DROP TABLE IF EXISTS audit_log CASCADE;
        DROP TABLE IF EXISTS retention_policy CASCADE;
    """))

