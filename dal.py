import sqlite3
import database
from typing import List, Dict, Any, Optional, Tuple

class DAL:
    def __init__(self):
        # We will open a new connection for each DAL method call
        # or we could manage a pool, but for SQLite, creating connections is cheap.
        pass

    def _get_connection(self):
        return database.connect_database()

    # --- Auth & Users ---
    def get_admin_by_username(self, username: str) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin WHERE USERNAME = ?", (username,))
            return cursor.fetchone()
        finally:
            conn.close()

    def get_parent_by_username(self, username: str) -> Optional[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM parent WHERE username = ?", (username,))
            return cursor.fetchone()
        finally:
            conn.close()
            
    # --- Dashboard Stats ---
    def get_dashboard_stats(self) -> Dict[str, int]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM student")
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

    def get_parent_dashboard_students(self, parent_id: int) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # PRD: Select Child Name, Class, Fee Paid, Fee Balance, Bus Number, Driver Name, Driver Contact, Route, and Pickup Point.
            cursor.execute('''
                SELECT s.student_name, s.student_class, s.fee_paid, s.fee_balance, b.bus_number, 
                       b.driver_name, b.driver_phone, r.route_name, p.pickup_point
                FROM student s
                JOIN parent p ON s.parent_id = p.parent_id
                LEFT JOIN route r ON s.route_id = r.route_id
                LEFT JOIN bus b ON r.route_id = b.route_id
                WHERE s.parent_id = ?
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
                       s.parent_id, p.phone, p.address, b.bus_id, s.route_id, s.fee_paid, s.fee_balance 
                FROM student s 
                JOIN parent p ON s.parent_id = p.parent_id 
                LEFT JOIN bus b ON s.route_id = b.route_id
            '''
            if search_query:
                query += " WHERE s.student_name LIKE ? OR s.student_class LIKE ?"
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
                (student_name, student_class, parent_id, route_id, fee_status, fee_paid, fee_balance)
                VALUES (?, ?, ?, ?, 'Active', ?, ?)
                """,
                (student_name, student_class, parent_id, route_id, fee_paid, fee_balance)
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
            # Find the bus for this route
            cursor.execute("SELECT bus_id, capacity FROM bus WHERE route_id = ?", (route_id,))
            bus_row = cursor.fetchone()
            if not bus_row:
                return False, 0, 0 # No bus assigned, capacity check passes or fails? Let's say it passes, or maybe it's limitless.
            
            bus_id, capacity = bus_row
            
            # Count students on this route
            cursor.execute("SELECT COUNT(*) FROM student WHERE route_id = ?", (route_id,))
            current_students = cursor.fetchone()[0]
            
            is_full = current_students >= capacity
            return is_full, current_students, capacity
        finally:
            conn.close()

    def delete_student(self, student_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student WHERE student_id = ?", (student_id,))
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
                SET student_name = ?, student_class = ?, parent_id = ?, route_id = ?, fee_paid = ?, fee_balance = ?
                WHERE student_id = ?
                """,
                (name, class_name, parent_id, route_id, fee_paid, fee_balance, student_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Parent Management ---
    def get_all_parents(self, search_query: str = "") -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT parent_id, parent_name, phone, address, pickup_point, username, password FROM parent"
            if search_query:
                query += " WHERE parent_name LIKE ? OR username LIKE ? OR phone LIKE ?"
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
                VALUES (?, ?, ?, ?, ?, ?)
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
            # Also delete students linked to this parent to maintain referential integrity if not cascaded
            cursor.execute("DELETE FROM student WHERE parent_id = ?", (parent_id,))
            cursor.execute("DELETE FROM parent WHERE parent_id = ?", (parent_id,))
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
                SET parent_name = ?, phone = ?, address = ?, pickup_point = ?, username = ?
                WHERE parent_id = ?
                """,
                (name, phone, address, pickup_point, username, parent_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Bus Management ---
    def get_all_buses(self) -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT b.bus_id, b.bus_number, b.driver_name, b.driver_phone, b.capacity, b.route_id, r.route_name FROM bus b LEFT JOIN route r ON b.route_id = r.route_id")
            return cursor.fetchall()
        finally:
            conn.close()

    def add_bus(self, bus_number: str, driver_name: str, driver_phone: str, capacity: int, route_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO bus (bus_number, driver_name, driver_phone, capacity, route_id)
                VALUES (?, ?, ?, ?, ?)
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
            cursor.execute("DELETE FROM bus WHERE bus_id = ?", (bus_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    # --- Route Management ---
    def get_all_routes(self, search_query: str = "") -> List[Tuple]:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "SELECT route_id, route_name FROM route"
            if search_query:
                query += " WHERE route_name LIKE ?"
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
            cursor.execute("INSERT INTO route (route_name) VALUES (?)", (route_name,))
            conn.commit()
            return True
        finally:
            conn.close()
            
    def delete_route(self, route_id: int) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bus WHERE route_id = ?", (route_id,))
            cursor.execute("DELETE FROM student WHERE route_id = ?", (route_id,))
            cursor.execute("DELETE FROM route WHERE route_id = ?", (route_id,))
            conn.commit()
            return True
        finally:
            conn.close()

    def update_route(self, route_id: int, route_name: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE route SET route_name = ? WHERE route_id = ?",
                (route_name, route_id)
            )
            conn.commit()
            return True
        finally:
            conn.close()

# Global singleton for DAL
db_dal = DAL()
