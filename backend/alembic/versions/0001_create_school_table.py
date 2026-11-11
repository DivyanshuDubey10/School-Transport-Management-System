"""create_school_table

Revision ID: 0001
Revises: 
Create Date: 2026-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create school root tenant table
    op.execute("""
        CREATE TABLE IF NOT EXISTS school (
            school_id        SERIAL PRIMARY KEY,
            school_name      VARCHAR(255) NOT NULL,
            school_code      VARCHAR(50)  NOT NULL,
            address          TEXT,
            contact_email    VARCHAR(255),
            contact_phone    VARCHAR(50),
            timezone         VARCHAR(100) NOT NULL DEFAULT 'Asia/Kolkata',
            is_active        BOOLEAN NOT NULL DEFAULT TRUE,
            created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)

    # 2. Case-insensitive unique index on school_code
    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_school_code_ci ON school (LOWER(school_code));
    """)

    # 3. Seed initial default school anchor dynamically
    op.execute("""
        INSERT INTO school (school_name, school_code, timezone)
        VALUES ('Default School', 'DEFAULT', 'Asia/Kolkata')
        ON CONFLICT (LOWER(school_code)) DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS school CASCADE;")

