"""create_trips_and_telemetry

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0004'
down_revision: Union[str, Sequence[str], None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # 1. Create trips table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS trips (
            trip_id                BIGSERIAL PRIMARY KEY,
            school_id              INTEGER NOT NULL,
            bus_id                 INTEGER NOT NULL,
            route_id               INTEGER,
            driver_name_snapshot   VARCHAR(255) NOT NULL,
            driver_id              INTEGER, -- NULLable for Phase 2B (driver table deferred to Phase 2C)
            started_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            ended_at               TIMESTAMPTZ,
            status                 VARCHAR(20) NOT NULL DEFAULT 'active'
                                       CHECK (status IN ('active', 'completed', 'timed_out', 'cancelled')),
            end_reason             VARCHAR(100),
            total_events           INTEGER NOT NULL DEFAULT 0,
            filtered_events        INTEGER NOT NULL DEFAULT 0,
            distance_km            NUMERIC(8,3) DEFAULT 0.0,
            duration_minutes       NUMERIC(8,1) DEFAULT 0.0,
            created_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            
            -- Composite Unique Anchors
            CONSTRAINT uq_trips_school_trip UNIQUE (school_id, trip_id),
            CONSTRAINT uq_trips_school_trip_bus UNIQUE (school_id, trip_id, bus_id),
            
            -- Composite FKs: Bus and Route must belong to the same school
            CONSTRAINT fk_trips_bus_tenant
                FOREIGN KEY (school_id, bus_id) REFERENCES bus(school_id, bus_id) ON DELETE RESTRICT,
            CONSTRAINT fk_trips_route_tenant
                FOREIGN KEY (school_id, route_id) REFERENCES route(school_id, route_id) ON DELETE RESTRICT,
                
            CONSTRAINT chk_trip_timestamps CHECK (ended_at IS NULL OR ended_at >= started_at)
        );

        -- Strictly ONE active trip per bus per school
        CREATE UNIQUE INDEX IF NOT EXISTS idx_trips_one_active_per_bus
            ON trips (school_id, bus_id) 
            WHERE status = 'active';

        CREATE INDEX IF NOT EXISTS idx_trips_school_started ON trips (school_id, started_at DESC);
        CREATE INDEX IF NOT EXISTS idx_trips_bus_started    ON trips (school_id, bus_id, started_at DESC);
    """))

    # 2. Create bus_telemetry_events table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS bus_telemetry_events (
            event_id              BIGSERIAL PRIMARY KEY,
            school_id             INTEGER NOT NULL,
            trip_id               BIGINT NOT NULL,
            bus_id                INTEGER NOT NULL,
            client_event_id       UUID NOT NULL,
            trip_sequence         INTEGER NOT NULL CHECK (trip_sequence >= 0),
            device_timestamp      TIMESTAMPTZ NOT NULL,
            server_received_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            latitude              DOUBLE PRECISION NOT NULL CHECK (latitude  BETWEEN -90  AND 90),
            longitude             DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
            altitude_m            REAL,
            accuracy_metres       REAL CHECK (accuracy_metres IS NULL OR accuracy_metres >= 0),
            gps_quality           VARCHAR(20) NOT NULL DEFAULT 'unknown'
                                      CHECK (gps_quality IN ('good', 'degraded', 'poor', 'unknown')),
            speed_kmh             REAL CHECK (speed_kmh IS NULL OR speed_kmh >= 0),
            heading_degrees       REAL CHECK (heading_degrees IS NULL OR (heading_degrees >= 0 AND heading_degrees <= 360)),
            is_out_of_order       BOOLEAN NOT NULL DEFAULT FALSE,
            is_hard_rejected      BOOLEAN NOT NULL DEFAULT FALSE,
            rejection_reason      VARCHAR(100),
            
            -- Global idempotency key per event
            CONSTRAINT uq_telemetry_client_event_id UNIQUE (client_event_id),
            
            -- 3-Column Composite FK: Guarantees event bus matches trip bus directly at relational level
            CONSTRAINT fk_telemetry_trip_bus_tenant
                FOREIGN KEY (school_id, trip_id, bus_id)
                REFERENCES trips(school_id, trip_id, bus_id)
                ON DELETE RESTRICT
                ON UPDATE RESTRICT
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_telemetry_trip_sequence 
            ON bus_telemetry_events (trip_id, trip_sequence)
            WHERE is_hard_rejected = FALSE;

        CREATE INDEX IF NOT EXISTS idx_telemetry_playback 
            ON bus_telemetry_events (trip_id, device_timestamp)
            WHERE is_hard_rejected = FALSE;

        CREATE INDEX IF NOT EXISTS idx_telemetry_school_bus 
            ON bus_telemetry_events (school_id, bus_id, server_received_at DESC);
    """))

    # 3. Create bus_live_location table
    conn.execute(sa.text("""
        CREATE TABLE IF NOT EXISTS bus_live_location (
            bus_id               INTEGER PRIMARY KEY,
            school_id            INTEGER NOT NULL,
            trip_id              BIGINT,
            latitude             DOUBLE PRECISION,
            longitude            DOUBLE PRECISION,
            accuracy_metres      REAL,
            gps_quality          VARCHAR(20),
            speed_kmh            REAL,
            heading_degrees      REAL,
            next_stop            VARCHAR(255),
            status               VARCHAR(50) NOT NULL DEFAULT 'Idle',
            device_timestamp     TIMESTAMPTZ,
            server_received_at   TIMESTAMPTZ,
            is_stale             BOOLEAN NOT NULL DEFAULT FALSE,
            last_trip_sequence   INTEGER,
            
            CONSTRAINT fk_live_location_bus_tenant
                FOREIGN KEY (school_id, bus_id) REFERENCES bus(school_id, bus_id) ON DELETE RESTRICT,
            CONSTRAINT fk_live_trip_bus_tenant
                FOREIGN KEY (school_id, trip_id, bus_id) REFERENCES trips(school_id, trip_id, bus_id) ON DELETE RESTRICT
        );

        CREATE INDEX IF NOT EXISTS idx_live_location_school ON bus_live_location (school_id, status);
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        DROP TABLE IF EXISTS bus_live_location CASCADE;
        DROP TABLE IF EXISTS bus_telemetry_events CASCADE;
        DROP TABLE IF EXISTS trips CASCADE;
    """))

