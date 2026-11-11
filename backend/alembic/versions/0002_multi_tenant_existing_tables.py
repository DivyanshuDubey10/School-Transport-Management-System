"""multi_tenant_existing_tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, Sequence[str], None] = '0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()

    # Step 1: Preflight validation
    conn.execute(sa.text("""
        DO $$
        DECLARE
            v_school_id INTEGER;
            v_orphan_count INTEGER;
            v_dup_count INTEGER;
        BEGIN
            -- Check default school exists
            SELECT school_id INTO v_school_id 
            FROM school 
            WHERE LOWER(school_code) = 'default' 
            LIMIT 1;

            IF v_school_id IS NULL THEN
                RAISE EXCEPTION 'Preflight check failed: Target default school anchor not found.';
            END IF;

            -- Check orphaned students
            SELECT COUNT(*) INTO v_orphan_count
            FROM student s
            LEFT JOIN parent p ON s.parent_id = p.parent_id
            WHERE p.parent_id IS NULL;

            IF v_orphan_count > 0 THEN
                RAISE EXCEPTION 'Preflight check failed: % orphaned students found without valid parents.', v_orphan_count;
            END IF;

            -- Check duplicate parent usernames
            SELECT COUNT(*) INTO v_dup_count
            FROM (
                SELECT LOWER(username) FROM parent GROUP BY LOWER(username) HAVING COUNT(*) > 1
            ) dup;

            IF v_dup_count > 0 THEN
                RAISE EXCEPTION 'Preflight check failed: Duplicate parent usernames detected in existing data.';
            END IF;
        END $$;
    """))

    # Step 2: Add school_id column to existing 8 tables
    tables = [
        "admin", "parent", "route", "bus", "student",
        "transport_change_request", "attendance", "user_settings"
    ]
    for table in tables:
        conn.execute(sa.text(f"""
            ALTER TABLE {table}
            ADD COLUMN IF NOT EXISTS school_id INTEGER
            REFERENCES school(school_id) ON DELETE RESTRICT;
        """))

    # Step 3: Dynamic backfill of school_id using resolved ID from school_code='default'
    conn.execute(sa.text("""
        DO $$
        DECLARE
            v_school_id INTEGER;
        BEGIN
            SELECT school_id INTO v_school_id 
            FROM school 
            WHERE LOWER(school_code) = 'default' 
            LIMIT 1;

            UPDATE admin                    SET school_id = v_school_id WHERE school_id IS NULL;
            UPDATE parent                   SET school_id = v_school_id WHERE school_id IS NULL;
            UPDATE route                    SET school_id = v_school_id WHERE school_id IS NULL;
            UPDATE bus                      SET school_id = v_school_id WHERE school_id IS NULL;
            UPDATE student                  SET school_id = v_school_id WHERE school_id IS NULL;
            UPDATE transport_change_request SET school_id = v_school_id WHERE school_id IS NULL;
            UPDATE attendance               SET school_id = v_school_id WHERE school_id IS NULL;
            UPDATE user_settings            SET school_id = v_school_id WHERE school_id IS NULL;
        END $$;
    """))

    # Step 4: Enforce NOT NULL and set DEFAULT on school_id for legacy compatibility
    conn.execute(sa.text("""
        DO $$
        DECLARE
            v_school_id INTEGER;
        BEGIN
            SELECT school_id INTO v_school_id 
            FROM school 
            WHERE LOWER(school_code) = 'default' 
            LIMIT 1;

            EXECUTE 'ALTER TABLE admin                    ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
            EXECUTE 'ALTER TABLE parent                   ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
            EXECUTE 'ALTER TABLE route                    ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
            EXECUTE 'ALTER TABLE bus                      ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
            EXECUTE 'ALTER TABLE student                  ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
            EXECUTE 'ALTER TABLE transport_change_request ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
            EXECUTE 'ALTER TABLE attendance               ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
            EXECUTE 'ALTER TABLE user_settings            ALTER COLUMN school_id SET DEFAULT ' || v_school_id || ';';
        END $$;
    """))

    for table in tables:
        conn.execute(sa.text(f"ALTER TABLE {table} ALTER COLUMN school_id SET NOT NULL;"))

    # Step 5: Establish composite unique constraints on parent tables
    conn.execute(sa.text("""
        ALTER TABLE parent  ADD CONSTRAINT uq_parent_school_id   UNIQUE (school_id, parent_id);
        ALTER TABLE route   ADD CONSTRAINT uq_route_school_id    UNIQUE (school_id, route_id);
        ALTER TABLE bus     ADD CONSTRAINT uq_bus_school_id      UNIQUE (school_id, bus_id);
        ALTER TABLE student ADD CONSTRAINT uq_student_school_id  UNIQUE (school_id, student_id);
    """))

    # Step 6: Dynamically drop existing single-column FKs
    conn.execute(sa.text("""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT tc.table_name, tc.constraint_name
                FROM information_schema.table_constraints tc
                WHERE tc.table_schema = 'public'
                  AND tc.constraint_type = 'FOREIGN KEY'
                  AND tc.table_name IN ('bus', 'student', 'transport_change_request', 'attendance')
                  AND tc.constraint_name NOT LIKE '%_tenant'
                  AND tc.constraint_name NOT LIKE '%_school_id_fkey'
            ) LOOP
                EXECUTE 'ALTER TABLE ' || quote_ident(r.table_name) || ' DROP CONSTRAINT ' || quote_ident(r.constraint_name) || ';';
            END LOOP;
        END $$;
    """))

    # Step 7: Add composite foreign keys
    conn.execute(sa.text("""
        -- bus -> route (RESTRICT-and-detach pattern)
        ALTER TABLE bus ADD CONSTRAINT fk_bus_route_tenant
            FOREIGN KEY (school_id, route_id) REFERENCES route(school_id, route_id) ON DELETE RESTRICT;

        -- student -> parent & route
        ALTER TABLE student ADD CONSTRAINT fk_student_parent_tenant
            FOREIGN KEY (school_id, parent_id) REFERENCES parent(school_id, parent_id) ON DELETE RESTRICT;
        ALTER TABLE student ADD CONSTRAINT fk_student_route_tenant
            FOREIGN KEY (school_id, route_id) REFERENCES route(school_id, route_id) ON DELETE RESTRICT;

        -- transport_change_request -> student
        ALTER TABLE transport_change_request ADD CONSTRAINT fk_tcr_student_tenant
            FOREIGN KEY (school_id, student_id) REFERENCES student(school_id, student_id) ON DELETE CASCADE;

        -- attendance -> student & bus (Historical preservation: RESTRICT deletion)
        ALTER TABLE attendance ADD CONSTRAINT fk_attendance_student_tenant
            FOREIGN KEY (school_id, student_id) REFERENCES student(school_id, student_id) ON DELETE RESTRICT;
        ALTER TABLE attendance ADD CONSTRAINT fk_attendance_bus_tenant
            FOREIGN KEY (school_id, bus_id) REFERENCES bus(school_id, bus_id) ON DELETE RESTRICT;
    """))

    # Step 8: Replace global unique on usernames with tenant-scoped unique indexes
    conn.execute(sa.text("""
        DO $$
        DECLARE
            r RECORD;
        BEGIN
            FOR r IN (
                SELECT tc.table_name, tc.constraint_name
                FROM information_schema.table_constraints tc
                WHERE tc.table_schema = 'public'
                  AND tc.constraint_type = 'UNIQUE'
                  AND tc.table_name IN ('admin', 'parent', 'bus')
                  AND tc.constraint_name IN ('admin_username_key', 'parent_username_key', 'bus_username_key')
            ) LOOP
                EXECUTE 'ALTER TABLE ' || quote_ident(r.table_name) || ' DROP CONSTRAINT ' || quote_ident(r.constraint_name) || ';';
            END LOOP;
        END $$;
    """))

    conn.execute(sa.text("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_admin_school_username ON admin (school_id, LOWER(username));
        CREATE UNIQUE INDEX IF NOT EXISTS idx_parent_school_username ON parent (school_id, LOWER(username));
        CREATE UNIQUE INDEX IF NOT EXISTS idx_bus_school_username ON bus (school_id, LOWER(username)) WHERE username IS NOT NULL;
    """))

    # Step 9: Scope attendance and user settings uniqueness
    conn.execute(sa.text("""
        ALTER TABLE attendance DROP CONSTRAINT IF EXISTS attendance_student_id_date_key;
        ALTER TABLE attendance ADD CONSTRAINT uq_attendance_student_date UNIQUE (school_id, student_id, date);

        ALTER TABLE user_settings DROP CONSTRAINT IF EXISTS user_settings_user_type_user_id_setting_key_key;
        ALTER TABLE user_settings ADD CONSTRAINT uq_user_settings_tenant UNIQUE (school_id, user_type, user_id, setting_key);
    """))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        ALTER TABLE attendance DROP CONSTRAINT IF EXISTS uq_attendance_student_date;
        ALTER TABLE user_settings DROP CONSTRAINT IF EXISTS uq_user_settings_tenant;
        DROP INDEX IF EXISTS idx_admin_school_username;
        DROP INDEX IF EXISTS idx_parent_school_username;
        DROP INDEX IF EXISTS idx_bus_school_username;

        ALTER TABLE bus DROP CONSTRAINT IF EXISTS fk_bus_route_tenant;
        ALTER TABLE student DROP CONSTRAINT IF EXISTS fk_student_parent_tenant;
        ALTER TABLE student DROP CONSTRAINT IF EXISTS fk_student_route_tenant;
        ALTER TABLE transport_change_request DROP CONSTRAINT IF EXISTS fk_tcr_student_tenant;
        ALTER TABLE attendance DROP CONSTRAINT IF EXISTS fk_attendance_student_tenant;
        ALTER TABLE attendance DROP CONSTRAINT IF EXISTS fk_attendance_bus_tenant;

        ALTER TABLE parent  DROP CONSTRAINT IF EXISTS uq_parent_school_id;
        ALTER TABLE route   DROP CONSTRAINT IF EXISTS uq_route_school_id;
        ALTER TABLE bus     DROP CONSTRAINT IF EXISTS uq_bus_school_id;
        ALTER TABLE student DROP CONSTRAINT IF EXISTS uq_student_school_id;

        ALTER TABLE admin                    DROP COLUMN IF EXISTS school_id;
        ALTER TABLE parent                   DROP COLUMN IF EXISTS school_id;
        ALTER TABLE route                    DROP COLUMN IF EXISTS school_id;
        ALTER TABLE bus                      DROP COLUMN IF EXISTS school_id;
        ALTER TABLE student                  DROP COLUMN IF EXISTS school_id;
        ALTER TABLE transport_change_request DROP COLUMN IF EXISTS school_id;
        ALTER TABLE attendance               DROP COLUMN IF EXISTS school_id;
        ALTER TABLE user_settings            DROP COLUMN IF EXISTS school_id;
    """))
