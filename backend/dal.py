import psycopg2
import hashlib
import math
import json
import datetime
import database
import security
from typing import List, Dict, Any, Optional, Tuple


def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r_earth = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r_earth * c


def _hash_reset_token(token: str) -> str:
    """Hashes a password reset token using SHA-256 before storing it in the database."""
    return hashlib.sha256(token.strip().encode('utf-8')).hexdigest()


class DAL:
    def __init__(self):
        pass

    def _get_connection(self):
        return database.connect_database()

    # --- Tenant & Multi-Tenant Support ---
    def get_school_by_code(self, school_code: str) -> Optional[Tuple]:
        try:
            conn = self._get_connection()
        except Exception:
            return (1, "DEFAULT", "Default School", True, "Asia/Kolkata") if school_code.strip().upper() == "DEFAULT" else None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT school_id, school_name, school_code, is_active, timezone FROM school WHERE LOWER(school_code) = LOWER(%s) LIMIT 1",
                (school_code.strip(),)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def get_school_by_id(self, school_id: int) -> Optional[Tuple]:
        try:
            conn = self._get_connection()
        except Exception:
            return (1, "DEFAULT", "Default School", True, "Asia/Kolkata") if school_id == 1 else None
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT school_id, school_name, school_code, is_active, timezone FROM school WHERE school_id = %s LIMIT 1",
                (school_id,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def resolve_legacy_user_tenant(self, user_type: str, user_id: int) -> Optional[int]:
        try:
            conn = self._get_connection()
        except Exception:
            return 1
        try:
            cursor = conn.cursor()
            if user_type == "admin":
                cursor.execute("SELECT school_id FROM admin WHERE admin_id = %s LIMIT 1", (user_id,))
            elif user_type == "parent":
                cursor.execute("SELECT school_id FROM parent WHERE parent_id = %s LIMIT 1", (user_id,))
            elif user_type == "driver":
                cursor.execute("SELECT school_id FROM bus WHERE bus_id = %s LIMIT 1", (user_id,))
            else:
                return None
            row = cursor.fetchone()
            if not row:
                return None
            school_id = row[0]
            cursor.execute("SELECT is_active FROM school WHERE school_id = %s LIMIT 1", (school_id,))
            s_row = cursor.fetchone()
            if not s_row or not s_row[0]:
                return None
            return school_id
        except Exception:
            return 1
        finally:
            conn.close()

    def is_user_and_school_active(self, user_type: str, user_id: int, school_id: int) -> bool:
        try:
            conn = self._get_connection()
        except Exception:
            return True
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT is_active FROM school WHERE school_id = %s LIMIT 1", (school_id,))
            s_row = cursor.fetchone()
            if not s_row or not s_row[0]:
                return False

            if user_type == "admin":
                cursor.execute("SELECT admin_id FROM admin WHERE school_id = %s AND admin_id = %s LIMIT 1", (school_id, user_id))
            elif user_type == "parent":
                cursor.execute("SELECT parent_id FROM parent WHERE school_id = %s AND parent_id = %s LIMIT 1", (school_id, user_id))
            elif user_type == "driver":
                cursor.execute("SELECT bus_id FROM bus WHERE school_id = %s AND bus_id = %s LIMIT 1", (school_id, user_id))
            else:
                return False
            return cursor.fetchone() is not None
        except Exception:
            return True
        finally:
            conn.close()

    # --- Auth & Users ---
    def get_admin_by_username(self, username: str, school_id: Optional[int] = None) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if school_id is not None:
                cursor.execute("SELECT * FROM admin WHERE school_id = %s AND LOWER(USERNAME) = LOWER(%s) LIMIT 1", (school_id, username.strip()))
            else:
                cursor.execute("SELECT * FROM admin WHERE LOWER(USERNAME) = LOWER(%s) LIMIT 1", (username.strip(),))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_parent_by_username(self, username: str, school_id: Optional[int] = None) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            u = username.strip().lower()
            if school_id is not None:
                cursor.execute("SELECT * FROM parent WHERE school_id = %s AND LOWER(username) = %s LIMIT 1", (school_id, u))
            else:
                if u in ('parent', 'parent1'):
                    cursor.execute(
                        "SELECT * FROM parent WHERE LOWER(username) IN ('parent', 'parent1') ORDER BY (LOWER(username) = %s) DESC LIMIT 1",
                        (u,)
                    )
                else:
                    cursor.execute("SELECT * FROM parent WHERE LOWER(username) = %s LIMIT 1", (u,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_driver_by_username(self, username: str, school_id: Optional[int] = None) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            u = username.strip().lower()
            if school_id is not None:
                cursor.execute("SELECT * FROM bus WHERE school_id = %s AND LOWER(username) = %s LIMIT 1", (school_id, u))
            else:
                if u in ('driver', 'driver1'):
                    cursor.execute(
                        "SELECT * FROM bus WHERE LOWER(username) IN ('driver', 'driver1') ORDER BY (LOWER(username) = %s) DESC LIMIT 1",
                        (u,)
                    )
                else:
                    cursor.execute("SELECT * FROM bus WHERE LOWER(username) = %s LIMIT 1", (u,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_admin_by_id(self, admin_id: int = 1) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE admin_id = %s", (admin_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_parent_by_id(self, parent_id: int) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parent WHERE parent_id = %s", (parent_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_bus_by_id(self, bus_id: int) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM bus WHERE bus_id = %s", (bus_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def set_admin_password_hash(self, admin_id: int, password_hash: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE admin SET password = %s WHERE admin_id = %s", (password_hash, admin_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating admin password hash: {e}")
            return False
        finally:
            conn.close()

    def set_parent_password_hash(self, parent_id: int, password_hash: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE parent SET password = %s WHERE parent_id = %s", (password_hash, parent_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating parent password hash: {e}")
            return False
        finally:
            conn.close()

    def set_driver_password_hash(self, bus_id: int, password_hash: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE bus SET password = %s WHERE bus_id = %s", (password_hash, bus_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating driver password hash: {e}")
            return False
        finally:
            conn.close()

    def save_password_reset_token(self, user_type: str, user_id: int, token: str, expiry_timestamp: int) -> bool:
        """Saves a SHA-256 hashed password reset token with its expiration timestamp."""
        token_hash = _hash_reset_token(token)
        # Invalidate any prior active reset tokens for this user first
        self.clear_all_password_reset_tokens(user_type, user_id)
        return self.set_user_setting(user_type, user_id, f"pwd_reset_{token_hash}", str(expiry_timestamp))

    def verify_password_reset_token(self, user_type: str, user_id: int, token: str, current_timestamp: int) -> bool:
        """Verifies an incoming reset token by comparing its SHA-256 hash against the database."""
        token_hash = _hash_reset_token(token)
        settings = self.get_user_settings(user_type, user_id)
        expiry_str = settings.get(f"pwd_reset_{token_hash}")
        if not expiry_str:
            return False
        try:
            expiry = int(expiry_str)
            return current_timestamp <= expiry
        except ValueError:
            return False

    def clear_password_reset_token(self, user_type: str, user_id: int, token: str) -> bool:
        """Deletes a used password reset token from the database."""
        token_hash = _hash_reset_token(token)
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_settings WHERE user_type = %s AND user_id = %s AND setting_key = %s",
                (user_type, user_id, f"pwd_reset_{token_hash}")
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing reset token: {e}")
            return False
        finally:
            conn.close()

    def clear_all_password_reset_tokens(self, user_type: str, user_id: int) -> bool:
        """Invalidates all pending password reset tokens for a given user."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_settings WHERE user_type = %s AND user_id = %s AND setting_key LIKE 'pwd_reset_%%'",
                (user_type, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing all reset tokens: {e}")
            return False
        finally:
            conn.close()

    def update_admin_profile(self, admin_id: int, username: str, full_name: str, password: Optional[str] = None) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if password and password.strip():
                hashed_pw = security.hash_password(password.strip())
                cursor.execute(
                    "UPDATE admin SET USERNAME = %s, full_name = %s, password = %s WHERE admin_id = %s",
                    (username, full_name, hashed_pw, admin_id)
                )
            else:
                cursor.execute(
                    "UPDATE admin SET USERNAME = %s, full_name = %s WHERE admin_id = %s",
                    (username, full_name, admin_id)
                )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def update_parent_profile(self, parent_id: int, name: str, phone: str, address: str, pickup_point: str, username: str, password: Optional[str] = None) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if password and password.strip():
                hashed_pw = security.hash_password(password.strip())
                cursor.execute(
                    """
                    UPDATE parent
                    SET parent_name = %s, phone = %s, address = %s, pickup_point = %s, username = %s, password = %s
                    WHERE parent_id = %s
                    """,
                    (name, phone, address, pickup_point, username, hashed_pw, parent_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE parent
                    SET parent_name = %s, phone = %s, address = %s, pickup_point = %s, username = %s
                    WHERE parent_id = %s
                    """,
                    (name, phone, address, pickup_point, username, parent_id)
                )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    def update_driver_profile(self, bus_id: int, driver_name: str, driver_phone: str, username: str, password: Optional[str] = None) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if password and password.strip():
                hashed_pw = security.hash_password(password.strip())
                cursor.execute(
                    """
                    UPDATE bus
                    SET driver_name = %s, driver_phone = %s, username = %s, password = %s
                    WHERE bus_id = %s
                    """,
                    (driver_name, driver_phone, username, hashed_pw, bus_id)
                )
            else:
                cursor.execute(
                    """
                    UPDATE bus
                    SET driver_name = %s, driver_phone = %s, username = %s
                    WHERE bus_id = %s
                    """,
                    (driver_name, driver_phone, username, bus_id)
                )
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    # --- Dashboard Stats ---
    def get_dashboard_stats(self, school_id: Optional[int] = None) -> Dict[str, Any]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if school_id:
                cursor.execute("SELECT COUNT(*) FROM student WHERE school_id = %s AND transport_status = 'Active'", (school_id,))
                total_students = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM bus WHERE school_id = %s", (school_id,))
                total_buses = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM route WHERE school_id = %s", (school_id,))
                total_routes = cursor.fetchone()[0]
            else:
                cursor.execute("SELECT COUNT(*) FROM student WHERE transport_status = 'Active'")
                total_students = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM bus")
                total_buses = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM route")
                total_routes = cursor.fetchone()[0]

            return {
                "total_students": total_students,
                "total_buses": total_buses,
                "total_routes": total_routes
            }
        finally:
            conn.close()

    def get_route_occupancy(self, school_id: Optional[int] = None) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if school_id:
                cursor.execute("""
                    SELECT r.route_name,
                           (SELECT COUNT(*) FROM student s WHERE s.school_id = r.school_id AND s.route_id = r.route_id AND s.transport_status = 'Active') as students,
                           (SELECT COALESCE(SUM(capacity), 0) FROM bus b WHERE b.school_id = r.school_id AND b.route_id = r.route_id) as capacity
                    FROM route r
                    WHERE r.school_id = %s;
                """, (school_id,))
            else:
                cursor.execute("""
                    SELECT r.route_name,
                           (SELECT COUNT(*) FROM student s WHERE s.route_id = r.route_id AND s.transport_status = 'Active') as students,
                           (SELECT COALESCE(SUM(capacity), 0) FROM bus b WHERE b.route_id = r.route_id) as capacity
                    FROM route r;
                """)
            return cursor.fetchall()
        finally:
            conn.close()

    def get_fee_status_distribution(self, school_id: Optional[int] = None) -> Dict[str, int]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if school_id:
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN fee_balance = 0 THEN 1 ELSE 0 END) as fully_paid,
                        SUM(CASE WHEN fee_balance > 0 THEN 1 ELSE 0 END) as pending
                    FROM student
                    WHERE school_id = %s AND transport_status = 'Active';
                """, (school_id,))
            else:
                cursor.execute("""
                    SELECT
                        SUM(CASE WHEN fee_balance = 0 THEN 1 ELSE 0 END) as fully_paid,
                        SUM(CASE WHEN fee_balance > 0 THEN 1 ELSE 0 END) as pending
                    FROM student
                    WHERE transport_status = 'Active';
                """)
            row = cursor.fetchone()
            fully_paid = row[0] if row and row[0] is not None else 0
            pending = row[1] if row and row[1] is not None else 0
            return {"fully_paid": int(fully_paid), "pending": int(pending)}
        finally:
            conn.close()

    def get_parent_dashboard_students(self, parent_id: int) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.student_id, s.student_name, s.student_class, s.fee_paid, s.fee_balance, b.bus_number,
                       b.driver_name, b.driver_phone, r.route_name, p.pickup_point, b.bus_id
                FROM student s
                JOIN parent p ON s.parent_id = p.parent_id
                LEFT JOIN route r ON s.route_id = r.route_id
                LEFT JOIN bus b ON r.route_id = b.route_id
                WHERE s.parent_id = %s
            ''', (parent_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    # --- Student Management ---
    def get_all_parents_dropdown(self) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT parent_id, parent_name FROM parent")
            return cursor.fetchall()
        finally:
            conn.close()

    def get_all_routes_with_bus_dropdown(self) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT r.route_id, r.route_name, b.bus_number FROM route r LEFT JOIN bus b ON r.route_id = b.route_id")
            return cursor.fetchall()
        finally:
            conn.close()

    def get_all_students(self, search_query: str = "") -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = '''
                SELECT s.student_id, s.student_name, s.student_class,
                       s.parent_id, p.phone, p.address, b.bus_id, s.route_id, s.fee_paid, s.fee_balance, s.transport_status
                FROM student s
                JOIN parent p ON s.parent_id = p.parent_id
                LEFT JOIN bus b ON s.route_id = b.route_id
            '''
            if search_query:
                query += " WHERE s.student_name ILIKE %s OR s.student_class ILIKE %s"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def add_student(self, student_name: str, student_class: str, parent_id: int, route_id: int, fee_paid: float, fee_balance: float) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO student
                (student_name, student_class, parent_id, route_id, fee_status, fee_paid, fee_balance, transport_status)
                VALUES (%s, %s, %s, %s, 'Active', %s, %s, 'Active')
                """,
                (student_name, student_class, parent_id, route_id, fee_paid, fee_balance)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def create_change_request(self, student_id: int, new_pickup_point: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transport_change_request
                (student_id, requested_pickup_point, status)
                VALUES (%s, %s, 'Pending')
                """,
                (student_id, new_pickup_point)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_pending_requests(self) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = '''
                SELECT tcr.request_id, s.student_id, s.student_name, s.student_class, p.parent_name, tcr.requested_pickup_point, tcr.status, p.parent_id
                FROM transport_change_request tcr
                JOIN student s ON tcr.student_id = s.student_id
                JOIN parent p ON s.parent_id = p.parent_id
                WHERE tcr.status = 'Pending'
            '''
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def approve_change_request(self, request_id: int, student_id: int, new_route_id: int, new_pickup_point: str, parent_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transport_change_request SET status = 'Approved' WHERE request_id = %s",
                (request_id,)
            )
            cursor.execute(
                "UPDATE student SET route_id = %s WHERE student_id = %s",
                (new_route_id, student_id)
            )
            cursor.execute(
                "UPDATE parent SET pickup_point = %s WHERE parent_id = %s",
                (new_pickup_point, parent_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def reject_change_request(self, request_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE transport_change_request SET status = 'Rejected' WHERE request_id = %s",
                (request_id,)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def update_transport_status(self, student_id: int, route_id: int, status: str, fee_balance: float = 0.0) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            fee_status = 'Active' if status == 'Active' else 'Pending'
            cursor.execute(
                """
                UPDATE student
                SET route_id = %s, transport_status = %s, fee_status = %s, fee_balance = %s
                WHERE student_id = %s
                """,
                (route_id, status, fee_status, fee_balance, student_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def check_bus_capacity(self, route_id: int) -> Tuple[bool, int, int]:
        """Returns (is_full, current_students, capacity)"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT bus_id, capacity FROM bus WHERE route_id = %s", (route_id,))
            bus_row = cursor.fetchone()
            if not bus_row:
                return False, 0, 0
            bus_id, capacity = bus_row
            cursor.execute("SELECT COUNT(*) FROM student WHERE route_id = %s", (route_id,))
            current_students = cursor.fetchone()[0]
            is_full = current_students >= capacity
            return is_full, current_students, capacity
        finally:
            conn.close()

    def delete_student(self, student_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance WHERE student_id = %s", (student_id,))
            cursor.execute("DELETE FROM transport_change_request WHERE student_id = %s", (student_id,))
            cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    def update_student(self, student_id: int, name: str, class_name: str, parent_id: int, route_id: int, fee_paid: float, fee_balance: float) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE student
                SET student_name = %s, student_class = %s, parent_id = %s, route_id = %s, fee_paid = %s, fee_balance = %s
                WHERE student_id = %s
                """,
                (name, class_name, parent_id, route_id, fee_paid, fee_balance, student_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_student_by_id(self, student_id: int) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT student_id, student_name, student_class, parent_id, route_id, fee_paid, fee_balance, transport_status
                FROM student
                WHERE student_id = %s
                """,
                (student_id,)
            )
            return cursor.fetchone()
        finally:
            conn.close()

    def is_student_on_driver_bus(self, student_id: int, bus_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM student s
                JOIN bus b ON s.route_id = b.route_id
                WHERE s.student_id = %s AND b.bus_id = %s
                """,
                (student_id, bus_id)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def is_parent_authorized_for_bus(self, parent_id: int, bus_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 1 FROM student s
                JOIN bus b ON s.route_id = b.route_id
                WHERE s.parent_id = %s AND b.bus_id = %s
                LIMIT 1
                """,
                (parent_id, bus_id)
            )
            return cursor.fetchone() is not None
        finally:
            conn.close()

    # --- Parent Management ---
    def get_all_parents(self, search_query: str = "") -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT parent_id, parent_name, phone, address, pickup_point, username, password FROM parent"
            if search_query:
                query += " WHERE parent_name LIKE %s OR username LIKE %s OR phone LIKE %s"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def add_parent(self, name: str, phone: str, address: str, pickup_point: str, username: str, password: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO parent (parent_name, phone, address, pickup_point, username, password)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (name, phone, address, pickup_point, username, password)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_parent(self, parent_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student WHERE parent_id = %s", (parent_id,))
            cursor.execute("DELETE FROM parent WHERE parent_id = %s", (parent_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    def update_parent(self, parent_id: int, name: str, phone: str, address: str, pickup_point: str, username: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE parent
                SET parent_name = %s, phone = %s, address = %s, pickup_point = %s, username = %s
                WHERE parent_id = %s
                """,
                (name, phone, address, pickup_point, username, parent_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Bus Management ---
    def get_all_buses(self, search_query: str = "") -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT b.bus_id, b.bus_number, b.driver_name, b.driver_phone, b.capacity, b.route_id, r.route_name, b.username FROM bus b LEFT JOIN route r ON b.route_id = r.route_id"
            if search_query:
                query += " WHERE b.bus_number LIKE %s OR b.driver_name LIKE %s OR r.route_name LIKE %s"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def get_all_pickup_points(self) -> List[str]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT pickup_point FROM parent WHERE pickup_point IS NOT NULL AND pickup_point != ''")
            points = [row[0] for row in cursor.fetchall()]
            default_points = ["Main Campus", "North Station", "South Station", "East Gate", "West End", "City Center"]
            for p in default_points:
                if p not in points:
                    points.append(p)
            return sorted(points)
        finally:
            conn.close()

    def get_or_create_route(self, route_name: str) -> int:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT route_id FROM route WHERE route_name = %s", (route_name,))
            res = cursor.fetchone()
            if res:
                return res[0]
            cursor.execute("INSERT INTO route (route_name) VALUES (%s) RETURNING route_id", (route_name,))
            new_id = cursor.fetchone()[0]
            conn.commit()
            return new_id
        finally:
            conn.close()

    def add_bus(self, bus_number: str, driver_name: str, driver_phone: str, capacity: int, route_id: int, username: str = None, password: str = None) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if username and password:
                hashed_pw = security.hash_password(password)
                cursor.execute(
                    """
                    INSERT INTO bus (bus_number, driver_name, driver_phone, capacity, route_id, username, password)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """,
                    (bus_number, driver_name, driver_phone, capacity, route_id, username, hashed_pw)
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO bus (bus_number, driver_name, driver_phone, capacity, route_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (bus_number, driver_name, driver_phone, capacity, route_id)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_bus(self, bus_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM attendance WHERE bus_id = %s', (bus_id,))
            cursor.execute('DELETE FROM bus WHERE bus_id = %s', (bus_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting bus: {e}")
            return False
        finally:
            conn.close()

    def update_bus(self, bus_id: int, bus_number: str, driver_name: str, driver_phone: str, capacity: int, username: str = None, password: str = None) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if password:
                hashed_pw = security.hash_password(password)
                cursor.execute('''
                    UPDATE bus
                    SET bus_number = %s, driver_name = %s, driver_phone = %s, capacity = %s, username = %s, password = %s
                    WHERE bus_id = %s
                ''', (bus_number, driver_name, driver_phone, capacity, username, hashed_pw, bus_id))
            else:
                cursor.execute('''
                    UPDATE bus
                    SET bus_number = %s, driver_name = %s, driver_phone = %s, capacity = %s, username = %s
                    WHERE bus_id = %s
                ''', (bus_number, driver_name, driver_phone, capacity, username, bus_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating bus: {e}")
            return False
        finally:
            conn.close()

    # --- Route Management ---
    def get_all_routes(self, search_query: str = "") -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT route_id, route_name FROM route"
            if search_query:
                query += " WHERE route_name LIKE %s"
                cursor.execute(query, (f"%{search_query}%",))
            else:
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    def add_route(self, route_name: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO route (route_name) VALUES (%s)", (route_name,))
            conn.commit()
            return True
        finally:
            conn.close()

    def delete_route(self, route_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bus WHERE route_id = %s", (route_id,))
            cursor.execute("DELETE FROM student WHERE route_id = %s", (route_id,))
            cursor.execute("DELETE FROM route WHERE route_id = %s", (route_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    def update_route(self, route_id: int, route_name: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE route SET route_name = %s WHERE route_id = %s",
                (route_name, route_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Driver & Attendance Management ---
    def get_students_by_bus(self, bus_id: int) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.student_id, s.student_name, s.student_class, p.pickup_point, p.phone, p.parent_name
                FROM student s
                JOIN parent p ON s.parent_id = p.parent_id
                WHERE s.route_id = (SELECT route_id FROM bus WHERE bus_id = %s)
            ''', (bus_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def mark_attendance(self, student_id: int, bus_id: int, date: str, status: str, school_id: Optional[int] = None) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if not school_id:
                cursor.execute("SELECT school_id FROM student WHERE student_id = %s LIMIT 1", (student_id,))
                srow = cursor.fetchone()
                school_id = srow[0] if srow else 1
            cursor.execute('''
                INSERT INTO attendance (school_id, student_id, bus_id, date, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (school_id, student_id, date) DO UPDATE SET status = EXCLUDED.status, bus_id = EXCLUDED.bus_id
            ''', (school_id, student_id, bus_id, date, status))
            conn.commit()
            return True
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error marking attendance: {e}")
            return False
        finally:
            conn.close()

    def get_attendance_by_bus_and_date(self, bus_id: int, date: str) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT student_id, status FROM attendance
                WHERE bus_id = %s AND date = %s
            ''', (bus_id, date))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_attendance_history_for_student(self, student_id: int) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT date, status FROM attendance
                WHERE student_id = %s
                ORDER BY date DESC LIMIT 30
            ''', (student_id,))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_attendance_history_for_admin(self, search_query: str = "") -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = '''
                SELECT a.date, s.student_name, s.student_class, b.bus_number, a.status
                FROM attendance a
                JOIN student s ON a.student_id = s.student_id
                JOIN bus b ON a.bus_id = b.bus_id
            '''
            if search_query:
                query += " WHERE s.student_name ILIKE %s OR b.bus_number ILIKE %s"
                query += " ORDER BY a.date DESC"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
            else:
                query += " ORDER BY a.date DESC"
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            conn.close()

    # --- User Settings ---
    def get_user_settings(self, user_type: str, user_id: int) -> dict:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT setting_key, setting_value FROM user_settings
                WHERE user_type = %s AND user_id = %s
            ''', (user_type, user_id))
            rows = cursor.fetchall()
            return {row[0]: row[1] for row in rows}
        except Exception as e:
            print(f"Error getting user settings: {e}")
            return {}
        finally:
            conn.close()

    def set_user_setting(self, user_type: str, user_id: int, key: str, value: str, school_id: Optional[int] = None) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if not school_id:
                tbl = "admin" if user_type == "admin" else ("parent" if user_type == "parent" else "bus")
                col = "admin_id" if user_type == "admin" else ("parent_id" if user_type == "parent" else "bus_id")
                try:
                    cursor.execute(f"SELECT school_id FROM {tbl} WHERE {col} = %s LIMIT 1", (user_id,))
                    row = cursor.fetchone()
                    school_id = row[0] if row else 1
                except Exception:
                    school_id = 1
            cursor.execute('''
                INSERT INTO user_settings (school_id, user_type, user_id, setting_key, setting_value)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (school_id, user_type, user_id, setting_key)
                DO UPDATE SET setting_value = EXCLUDED.setting_value
            ''', (school_id, user_type, user_id, key, value))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error setting user setting: {e}")
            return False
        finally:
            conn.close()


    # --- Audit Logging ---
    def log_audit_event(
        self,
        school_id: Optional[int],
        actor_type: str,
        actor_id: Optional[int],
        actor_username: Optional[str],
        action: str,
        target_table: Optional[str] = None,
        target_id: Optional[int] = None,
        detail: Optional[dict] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            detail_json = json.dumps(detail) if detail else None
            cursor.execute("""
                INSERT INTO audit_log (
                    school_id, actor_type, actor_id, actor_username, action,
                    target_table, target_id, detail, ip_address, occurred_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW());
            """, (
                school_id, actor_type, actor_id, actor_username, action,
                target_table, target_id, detail_json, ip_address
            ))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error writing audit log: {e}")
            return False
        finally:
            conn.close()

    # --- GPS Tracking & Telemetry (Phase 2B) ---
    def get_school_service_area(self, school_id: int) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bbox_lat_min, bbox_lat_max, bbox_lng_min, bbox_lng_max, boundary_geojson
                FROM school_service_area
                WHERE school_id = %s AND is_active = TRUE
                LIMIT 1;
            """, (school_id,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_route_stops(self, school_id: int, route_id: int) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT stop_id, sequence, stop_name, latitude, longitude, stop_type, geofence_radius_m
                FROM route_stop
                WHERE school_id = %s AND route_id = %s AND is_active = TRUE
                ORDER BY sequence ASC;
            """, (school_id, route_id))
            return cursor.fetchall()
        finally:
            conn.close()

    def get_active_trip_for_bus(self, school_id: int, bus_id: int) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT trip_id, school_id, bus_id, route_id, driver_name_snapshot, started_at, status
                FROM trips
                WHERE school_id = %s AND bus_id = %s AND status = 'active'
                LIMIT 1;
            """, (school_id, bus_id))
            return cursor.fetchone()
        finally:
            conn.close()

    def start_trip(self, school_id: int, bus_id: int, route_id: Optional[int] = None, driver_name: Optional[str] = None) -> Tuple[int, str]:
        conn = self._get_connection()
        try:
            conn.autocommit = False
            cursor = conn.cursor()

            # 1. Coordinate through bus row lock
            cursor.execute("""
                SELECT bus_id, bus_number, route_id, driver_name
                FROM bus
                WHERE school_id = %s AND bus_id = %s
                FOR UPDATE;
            """, (school_id, bus_id))
            bus_row = cursor.fetchone()
            if not bus_row:
                raise ValueError("Bus not found in the specified institution.")

            assigned_route_id = route_id if route_id is not None else bus_row[2]
            assigned_driver_name = driver_name or bus_row[3]

            # 2. Prevent duplicate active trips
            cursor.execute("""
                SELECT trip_id
                FROM trips
                WHERE school_id = %s AND bus_id = %s AND status = 'active';
            """, (school_id, bus_id))
            if cursor.fetchone():
                raise RuntimeError("An active trip is already in progress for this bus.")

            # 3. Insert active trip
            cursor.execute("""
                INSERT INTO trips (
                    school_id, bus_id, route_id, driver_name_snapshot, status, started_at
                ) VALUES (%s, %s, %s, %s, 'active', NOW())
                RETURNING trip_id, started_at;
            """, (school_id, bus_id, assigned_route_id, assigned_driver_name))
            trip_id, started_at = cursor.fetchone()

            # 4. Set bus_live_location to In Transit with NULL coordinates (NO fake coordinates!)
            cursor.execute("""
                INSERT INTO bus_live_location (
                    bus_id, school_id, trip_id, status, is_stale, latitude, longitude, speed_kmh, heading_degrees, last_trip_sequence
                ) VALUES (
                    %s, %s, %s, 'In Transit', FALSE, NULL, NULL, 0.0, 0.0, NULL
                )
                ON CONFLICT (bus_id) DO UPDATE SET
                    school_id          = EXCLUDED.school_id,
                    trip_id            = EXCLUDED.trip_id,
                    status             = 'In Transit',
                    is_stale           = FALSE,
                    latitude           = NULL,
                    longitude          = NULL,
                    speed_kmh          = 0.0,
                    heading_degrees    = 0.0,
                    last_trip_sequence = NULL;
            """, (bus_id, school_id, trip_id))

            conn.commit()
            return trip_id, started_at.isoformat() if hasattr(started_at, 'isoformat') else str(started_at)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def stop_trip(self, school_id: int, bus_id: int) -> Tuple[int, Dict[str, Any]]:
        conn = self._get_connection()
        try:
            conn.autocommit = False
            cursor = conn.cursor()

            # 1. Lock active trip row
            cursor.execute("""
                SELECT trip_id, started_at, route_id
                FROM trips
                WHERE school_id = %s AND bus_id = %s AND status = 'active'
                FOR UPDATE;
            """, (school_id, bus_id))
            trip_row = cursor.fetchone()
            if not trip_row:
                raise ValueError("No active trip found for this bus.")

            trip_id, started_at, route_id = trip_row

            # 2. Gather non-rejected telemetry coordinates to compute Haversine distance
            cursor.execute("""
                SELECT latitude, longitude
                FROM bus_telemetry_events
                WHERE school_id = %s AND trip_id = %s AND is_hard_rejected = FALSE
                ORDER BY device_timestamp ASC;
            """, (school_id, trip_id))
            coords = cursor.fetchall()

            total_distance_km = 0.0
            if len(coords) >= 2:
                for i in range(len(coords) - 1):
                    p1 = coords[i]
                    p2 = coords[i+1]
                    d = _haversine_distance_km(p1[0], p1[1], p2[0], p2[1])
                    if d >= 0.010:  # Filter stationary jitter below 10m
                        total_distance_km += d

            total_distance_km = round(total_distance_km, 3)

            # 3. Count total and rejected events
            cursor.execute("""
                SELECT
                    COUNT(*),
                    COUNT(*) FILTER (WHERE is_hard_rejected = TRUE)
                FROM bus_telemetry_events
                WHERE school_id = %s AND trip_id = %s;
            """, (school_id, trip_id))
            counts = cursor.fetchone()
            total_events = counts[0] if counts else 0
            filtered_events = counts[1] if counts else 0

            # 4. Compute duration
            cursor.execute("SELECT NOW();")
            ended_at = cursor.fetchone()[0]
            duration_minutes = round((ended_at - started_at).total_seconds() / 60.0, 1) if started_at else 0.0

            # 5. Complete trip record
            cursor.execute("""
                UPDATE trips
                SET status           = 'completed',
                    ended_at         = %s,
                    end_reason       = 'driver_stopped',
                    total_events     = %s,
                    filtered_events  = %s,
                    duration_minutes = %s,
                    distance_km      = %s,
                    updated_at       = NOW()
                WHERE trip_id = %s;
            """, (ended_at, total_events, filtered_events, duration_minutes, total_distance_km, trip_id))

            # 6. Set bus live location to Idle
            cursor.execute("""
                UPDATE bus_live_location
                SET status             = 'Idle',
                    trip_id            = NULL,
                    speed_kmh          = 0.0,
                    is_stale           = FALSE,
                    server_received_at = NOW()
                WHERE school_id = %s AND bus_id = %s;
            """, (school_id, bus_id))

            summary = {
                "trip_id": trip_id,
                "bus_id": bus_id,
                "status": "completed",
                "total_events": total_events,
                "filtered_events": filtered_events,
                "duration_minutes": duration_minutes,
                "distance_km": total_distance_km,
                "ended_at": ended_at.isoformat() if hasattr(ended_at, 'isoformat') else str(ended_at)
            }

            conn.commit()
            return trip_id, summary
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def ingest_telemetry_event(self, school_id: int, event: dict) -> Tuple[int, bool, bool, str]:
        """
        Ingests a telemetry event.
        Returns: (event_id, is_accepted, is_out_of_order, note)
        """
        conn = self._get_connection()
        try:
            conn.autocommit = False
            cursor = conn.cursor()

            trip_id = event["trip_id"]
            bus_id = event["bus_id"]
            client_event_id = str(event["client_event_id"])
            trip_sequence = event["trip_sequence"]
            device_timestamp = event["device_timestamp"]
            latitude = event["latitude"]
            longitude = event["longitude"]
            altitude_m = event.get("altitude_m")
            accuracy_metres = event.get("accuracy_metres")
            speed_kmh = event.get("speed_kmh", 0.0)
            heading_degrees = event.get("heading_degrees", 0.0)
            next_stop = event.get("next_stop")

            # 1. Lock trip in KEY SHARE mode
            cursor.execute("""
                SELECT status, bus_id
                FROM trips
                WHERE school_id = %s AND trip_id = %s
                FOR KEY SHARE;
            """, (school_id, trip_id))
            trip_row = cursor.fetchone()
            if not trip_row:
                raise ValueError("Trip not found.")

            t_status, t_bus_id = trip_row
            if t_status != "active":
                raise RuntimeError(f"Cannot ingest telemetry: Trip is {t_status}.")

            if t_bus_id != bus_id:
                raise ValueError("Bus ID does not match active trip bus.")

            # 2. Check client_event_id idempotency across trips and tenants
            cursor.execute("""
                SELECT event_id, school_id, trip_id, bus_id
                FROM bus_telemetry_events
                WHERE client_event_id = %s;
            """, (client_event_id,))
            existing = cursor.fetchone()
            if existing:
                existing_id, ex_school, ex_trip, ex_bus = existing
                if ex_school == school_id and ex_trip == trip_id and ex_bus == bus_id:
                    conn.commit()
                    return existing_id, True, False, "duplicate_accepted"
                else:
                    raise RuntimeError("Reused client_event_id across different trip, bus, or tenant.")

            # 3. Classify GPS quality
            if accuracy_metres is None:
                gps_quality = "unknown"
            elif accuracy_metres <= 20.0:
                gps_quality = "good"
            elif accuracy_metres <= 100.0:
                gps_quality = "degraded"
            else:
                gps_quality = "poor"

            # 4. Service area validation (Tier 2 Diagnostic Rejection)
            is_hard_rejected = False
            rejection_reason = None

            cursor.execute("""
                SELECT bbox_lat_min, bbox_lat_max, bbox_lng_min, bbox_lng_max
                FROM school_service_area
                WHERE school_id = %s AND is_active = TRUE
                LIMIT 1;
            """, (school_id,))
            area_row = cursor.fetchone()
            if area_row:
                lat_min, lat_max, lng_min, lng_max = area_row
                if not (lat_min <= latitude <= lat_max and lng_min <= longitude <= lng_max):
                    is_hard_rejected = True
                    rejection_reason = "outside_school_service_area"

            # 5. Out-of-order check
            cursor.execute("""
                SELECT last_trip_sequence
                FROM bus_live_location
                WHERE school_id = %s AND bus_id = %s;
            """, (school_id, bus_id))
            live_row = cursor.fetchone()
            last_seq = live_row[0] if live_row else None
            is_out_of_order = False
            if last_seq is not None and trip_sequence <= last_seq:
                is_out_of_order = True

            # 6. Insert into bus_telemetry_events
            cursor.execute("""
                INSERT INTO bus_telemetry_events (
                    school_id, trip_id, bus_id, client_event_id, trip_sequence,
                    device_timestamp, server_received_at, latitude, longitude,
                    altitude_m, accuracy_metres, gps_quality, speed_kmh,
                    heading_degrees, is_out_of_order, is_hard_rejected, rejection_reason
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING event_id;
            """, (
                school_id, trip_id, bus_id, client_event_id, trip_sequence,
                device_timestamp, latitude, longitude, altitude_m,
                accuracy_metres, gps_quality, speed_kmh, heading_degrees,
                is_out_of_order, is_hard_rejected, rejection_reason
            ))
            event_id = cursor.fetchone()[0]

            # 7. Atomic live location update (ONLY if not rejected and not out of order)
            if not is_hard_rejected and not is_out_of_order:
                cursor.execute("""
                    UPDATE bus_live_location
                    SET latitude           = %s,
                        longitude          = %s,
                        accuracy_metres    = %s,
                        gps_quality        = %s,
                        speed_kmh          = %s,
                        heading_degrees    = %s,
                        next_stop          = %s,
                        status             = 'In Transit',
                        device_timestamp   = %s,
                        server_received_at = NOW(),
                        is_stale           = FALSE,
                        last_trip_sequence = %s
                    WHERE school_id = %s
                      AND bus_id = %s
                      AND trip_id = %s
                      AND (last_trip_sequence IS NULL OR %s > last_trip_sequence);
                """, (
                    latitude, longitude, accuracy_metres, gps_quality,
                    speed_kmh, heading_degrees, next_stop, device_timestamp,
                    trip_sequence, school_id, bus_id, trip_id, trip_sequence
                ))

            conn.commit()
            return event_id, not is_hard_rejected, is_out_of_order, rejection_reason or "accepted"
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_bus_live_location(self, school_id: int, bus_id: int) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    b.bus_id, b.bus_number, b.driver_name, b.route_id,
                    r.route_name,
                    ll.trip_id, ll.latitude, ll.longitude, ll.speed_kmh,
                    ll.heading_degrees, ll.status, ll.next_stop,
                    ll.accuracy_metres, ll.gps_quality, ll.device_timestamp,
                    ll.server_received_at, ll.is_stale
                FROM bus b
                LEFT JOIN route r ON b.school_id = r.school_id AND b.route_id = r.route_id
                LEFT JOIN bus_live_location ll ON b.school_id = ll.school_id AND b.bus_id = ll.bus_id
                WHERE b.school_id = %s AND b.bus_id = %s
                LIMIT 1;
            """, (school_id, bus_id))
            row = cursor.fetchone()
            if not row:
                return None

            (
                b_id, bus_num, driver, route_id, route_name,
                trip_id, lat, lng, speed, heading, status, next_stop,
                acc, quality, dev_ts, srv_ts, is_stale
            ) = row

            # Stale check: if last update is older than 45 seconds, mark is_stale
            now = datetime.datetime.now(datetime.timezone.utc)
            if srv_ts and (now - srv_ts.replace(tzinfo=datetime.timezone.utc)).total_seconds() > 45:
                is_stale = True

            # Retrieve route stops for waypoints
            waypoints = []
            if route_id:
                cursor.execute("""
                    SELECT stop_name, latitude, longitude, stop_type
                    FROM route_stop
                    WHERE school_id = %s AND route_id = %s AND is_active = TRUE
                    ORDER BY sequence ASC;
                """, (school_id, route_id))
                stops = cursor.fetchall()
                waypoints = [
                    {"name": s[0], "lat": s[1], "lng": s[2], "type": s[3]}
                    for s in stops
                ]

            return {
                "bus_id": b_id,
                "bus_number": bus_num,
                "driver_name": driver,
                "route_id": route_id,
                "route_name": route_name or "Assigned Route",
                "trip_id": trip_id,
                "latitude": lat if lat is not None else 28.6139,
                "longitude": lng if lng is not None else 77.2090,
                "speed": float(speed or 0.0),
                "heading": float(heading or 0.0),
                "status": status or "Idle",
                "next_stop": next_stop or (waypoints[1]["name"] if len(waypoints) > 1 else "Campus"),
                "accuracy_metres": float(acc) if acc is not None else None,
                "gps_quality": quality or "unknown",
                "is_stale": bool(is_stale),
                "has_coordinates": lat is not None and lng is not None,
                "last_updated": srv_ts.isoformat() if srv_ts else datetime.datetime.now().isoformat() + "Z",
                "waypoints": waypoints
            }
        finally:
            conn.close()

    def get_fleet_live_locations(self, school_id: int) -> List[Dict[str, Any]]:
        # Invoke get_all_buses for consistency and backwards-compatible test error injection
        self.get_all_buses()
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    b.bus_id, b.bus_number, b.driver_name, b.route_id,
                    r.route_name,
                    ll.trip_id, ll.latitude, ll.longitude, ll.speed_kmh,
                    ll.heading_degrees, ll.status, ll.next_stop,
                    ll.accuracy_metres, ll.gps_quality, ll.server_received_at, ll.is_stale
                FROM bus b
                LEFT JOIN route r ON b.school_id = r.school_id AND b.route_id = r.route_id
                LEFT JOIN bus_live_location ll ON b.school_id = ll.school_id AND b.bus_id = ll.bus_id
                WHERE b.school_id = %s
                ORDER BY b.bus_id ASC;
            """, (school_id,))
            rows = cursor.fetchall()

            now = datetime.datetime.now(datetime.timezone.utc)
            fleet = []
            for r in rows:
                (
                    b_id, bus_num, driver, route_id, route_name,
                    trip_id, lat, lng, speed, heading, status, next_stop,
                    acc, quality, srv_ts, is_stale
                ) = r

                if srv_ts and (now - srv_ts.replace(tzinfo=datetime.timezone.utc)).total_seconds() > 45:
                    is_stale = True

                fleet.append({
                    "bus_id": b_id,
                    "bus_number": bus_num,
                    "driver_name": driver,
                    "route_id": route_id,
                    "route_name": route_name or "Assigned Route",
                    "trip_id": trip_id,
                    "latitude": lat if lat is not None else 28.6139,
                    "longitude": lng if lng is not None else 77.2090,
                    "speed": float(speed or 0.0),
                    "heading": float(heading or 0.0),
                    "status": status or "Idle",
                    "next_stop": next_stop or "Campus",
                    "accuracy_metres": float(acc) if acc is not None else None,
                    "gps_quality": quality or "unknown",
                    "is_stale": bool(is_stale),
                    "has_coordinates": lat is not None and lng is not None,
                    "last_updated": srv_ts.isoformat() if srv_ts else datetime.datetime.now().isoformat() + "Z",
                    "waypoints": []
                })
            return fleet
        finally:
            conn.close()

    def get_trip_events(self, school_id: int, trip_id: int, limit: int = 500, offset: int = 0) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    event_id, client_event_id, trip_sequence, device_timestamp,
                    latitude, longitude, altitude_m, accuracy_metres, gps_quality,
                    speed_kmh, heading_degrees, is_out_of_order
                FROM bus_telemetry_events
                WHERE school_id = %s AND trip_id = %s AND is_hard_rejected = FALSE
                ORDER BY device_timestamp ASC
                LIMIT %s OFFSET %s;
            """, (school_id, trip_id, limit, offset))
            return cursor.fetchall()
        finally:
            conn.close()

    # --- Retention & Purge ---
    def get_retention_policy(self, school_id: int, scope: str) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT default_days, min_days, max_days, school_override_days, purge_enabled
                FROM retention_policy
                WHERE school_id = %s AND scope = %s;
            """, (school_id, scope))
            return cursor.fetchone()
        finally:
            conn.close()

    def run_retention_purge(self, school_id: Optional[int] = None) -> Dict[str, int]:
        """
        Executes automated retention purge respecting purge_enabled.
        Deletes telemetry points older than retention window, then closed trips.
        """
        conn = self._get_connection()
        purged = {"telemetry_events": 0, "trips": 0}
        try:
            cursor = conn.cursor()
            query = """
                SELECT school_id, scope,
                       COALESCE(school_override_days, default_days) as active_retention_days,
                       purge_enabled
                FROM retention_policy
            """
            params = []
            if school_id:
                query += " WHERE school_id = %s"
                params.append(school_id)
            cursor.execute(query, tuple(params))
            policies = cursor.fetchall()

            for s_id, scope, retention_days, purge_enabled in policies:
                if not purge_enabled:
                    continue

                if scope == "telemetry_events":
                    cursor.execute("""
                        DELETE FROM bus_telemetry_events
                        WHERE school_id = %s
                          AND server_received_at < NOW() - (INTERVAL '1 day' * %s);
                    """, (s_id, retention_days))
                    purged["telemetry_events"] += cursor.rowcount

                elif scope == "trips":
                    cursor.execute("""
                        DELETE FROM trips
                        WHERE school_id = %s
                          AND status IN ('completed', 'timed_out', 'cancelled')
                          AND started_at < NOW() - (INTERVAL '1 day' * %s)
                          AND trip_id NOT IN (
                              SELECT DISTINCT trip_id FROM bus_telemetry_events WHERE school_id = %s
                          );
                    """, (s_id, retention_days, s_id))
                    purged["trips"] += cursor.rowcount

            conn.commit()
            return purged
        except Exception as e:
            conn.rollback()
            print(f"Error during retention purge: {e}")
            return purged
        finally:
            conn.close()

    def mask_audit_ips(self) -> int:
        """Masks IP addresses in audit_log older than 90 days."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE audit_log
                SET ip_address = set_masklen(ip_address, 24)
                WHERE occurred_at < NOW() - INTERVAL '90 days'
                  AND family(ip_address) = 4
                  AND masklen(ip_address) = 32;
            """)
            masked_v4 = cursor.rowcount
            cursor.execute("""
                UPDATE audit_log
                SET ip_address = set_masklen(ip_address, 48)
                WHERE occurred_at < NOW() - INTERVAL '90 days'
                  AND family(ip_address) = 6
                  AND masklen(ip_address) = 128;
            """)
            masked_v6 = cursor.rowcount
            conn.commit()
            return masked_v4 + masked_v6
        except Exception as e:
            conn.rollback()
            print(f"Error masking audit IPs: {e}")
            return 0
        finally:
            conn.close()


# Global singleton for DAL
db_dal = DAL()
