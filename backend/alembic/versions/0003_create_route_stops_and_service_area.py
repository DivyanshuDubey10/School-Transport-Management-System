"""create_route_stops_and_service_area

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0003'
down_revision: Union[str, Sequence[str], None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Create route_stop table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS route_stop (
            stop_id           SERIAL PRIMARY KEY,
            school_id         INTEGER NOT NULL,
            route_id          INTEGER NOT NULL,
            sequence          SMALLINT NOT NULL CHECK (sequence > 0),
            stop_name         VARCHAR(255) NOT NULL,
            latitude          DOUBLE PRECISION NOT NULL CHECK (latitude  BETWEEN -90  AND 90),
            longitude         DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
            stop_type         VARCHAR(20) NOT NULL DEFAULT 'stop' CHECK (stop_type IN ('school', 'stop')),
            geofence_radius_m INTEGER NOT NULL DEFAULT 50 CHECK (geofence_radius_m BETWEEN 10 AND 500),
            is_active         BOOLEAN NOT NULL DEFAULT TRUE,
            
            CONSTRAINT fk_route_stop_route_tenant
                FOREIGN KEY (school_id, route_id) REFERENCES route(school_id, route_id) ON DELETE RESTRICT,
                
            CONSTRAINT uq_route_stop_sequence UNIQUE (school_id, route_id, sequence)
        );

        CREATE INDEX IF NOT EXISTS idx_route_stop_lookup ON route_stop (school_id, route_id, is_active);
    """))

    # 2. Create school_service_area table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS school_service_area (
            area_id           SERIAL PRIMARY KEY,
            school_id         INTEGER NOT NULL REFERENCES school(school_id) ON DELETE RESTRICT,
            area_name         VARCHAR(100) NOT NULL,
            bbox_lat_min      DOUBLE PRECISION NOT NULL CHECK (bbox_lat_min BETWEEN -90 AND 90),
            bbox_lat_max      DOUBLE PRECISION NOT NULL CHECK (bbox_lat_max BETWEEN -90 AND 90),
            bbox_lng_min      DOUBLE PRECISION NOT NULL CHECK (bbox_lng_min BETWEEN -180 AND 180),
            bbox_lng_max      DOUBLE PRECISION NOT NULL CHECK (bbox_lng_max BETWEEN -180 AND 180),
            boundary_geojson  JSONB,
            is_active         BOOLEAN NOT NULL DEFAULT TRUE,
            created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            
            CONSTRAINT chk_bbox_lat_order CHECK (bbox_lat_min <= bbox_lat_max),
            CONSTRAINT chk_bbox_lng_order CHECK (bbox_lng_min <= bbox_lng_max)
        );

        CREATE INDEX IF NOT EXISTS idx_service_area_lookup ON school_service_area (school_id, is_active);
    """))

    # 3. Dynamically seed default metropolitan service area for default school
    conn.execute(sa.text("""
        DO $$
        DECLARE
            v_school_id INTEGER;
        BEGIN
            SELECT school_id INTO v_school_id FROM school WHERE LOWER(school_code) = 'default' LIMIT 1;
            IF v_school_id IS NOT NULL THEN
                INSERT INTO school_service_area 
                    (school_id, area_name, bbox_lat_min, bbox_lat_max, bbox_lng_min, bbox_lng_max)
                VALUES 
                    (v_school_id, 'Default Metropolitan Area', 6.0, 37.5, 68.0, 97.5)
                ON CONFLICT DO NOTHING;
            END IF;
        END $$;
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        DROP TABLE IF EXISTS route_stop CASCADE;
        DROP TABLE IF EXISTS school_service_area CASCADE;
    """))

