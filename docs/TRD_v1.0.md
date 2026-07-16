# Technical Requirements Document (TRD)
**Project Name:** School Transport Management System (STMS)
**Document Version:** 1.0 
**Date:** July 2026
**Author:** Lead Software Architect (30+ Years Exp.)

---

## 1. System Architecture Overview
The architecture for STMS v1.0 follows a fat-client, 2-tier architectural pattern. The presentation and business logic layers are tightly coupled within the Python application, communicating directly with an embedded data tier.

### 1.1 Core Components
* **Application Runtime:** Python 3.10+ virtual environment.
* **UI Framework:** `customtkinter` (wraps standard `tkinter` to provide hardware-accelerated, modern UI elements that scale effectively on High-DPI monitors).
* **Data Access Layer:** Direct SQL execution via Python's native `sqlite3` module.

### 1.2 C4 Context Model (Current vs Future)
**Current (v1.0):**
`[Admin/Parent User] -> (Desktop Application) -> (Local SQLite DB)`

**Future (v2.0 Networked Model):**
`[Parent Mobile App / Web] -> (REST/GraphQL API - FastAPI) -> (PostgreSQL Cluster)`
`[Admin Desktop App] --------> (REST/GraphQL API - FastAPI) -> (PostgreSQL Cluster)`
`[Bus IoT GPS Tracker] ------> (MQTT Broker) ----------------> (Redis Cache) -> (PostgreSQL)`

---

## 2. Detailed Database Schema (Data Dictionary)

The foundational database `database.db` uses SQLite and enforces strict foreign key constraints.

### 2.1 Table: `admin`
Stores root-level administrative users.
* `admin_id` [INTEGER] - Primary Key, Auto Increment.
* `USERNAME` [TEXT] - Not Null, Unique constraint. Max length 50.
* `password` [TEXT] - Not Null. *(Note: v1.0 stores plaintext; v1.5 mandates bcrypt hashes of 60 chars).*
* `full_name` [TEXT] - Not Null. Used for UI greetings.

### 2.2 Table: `parent`
Stores guardian profiles and portal login credentials.
* `parent_id` [INTEGER] - Primary Key, Auto Increment.
* `parent_name` [TEXT] - Not Null, Unique.
* `phone` [NUMBER] - Not Null, Unique. Used for SMS notifications in v2.0.
* `address` [TEXT] - Not Null. Residential address for route calculation.
* `pickup_point` [TEXT] - Not Null, Default `''`. The designated geographical stop.
* `username` [TEXT] - Not Null. Parent Portal login.
* `password` [TEXT] - Not Null.

### 2.3 Table: `route`
Defines logical paths taken by fleet vehicles.
* `route_id` [INTEGER] - Primary Key, Auto Increment.
* `route_name` [TEXT] - Not Null. (e.g., "Northside Morning Express").

### 2.4 Table: `bus`
Represents physical fleet assets.
* `bus_id` [INTEGER] - Primary Key, Auto Increment.
* `bus_number` [TEXT] - Not Null, Unique. The physical decal number on the bus.
* `driver_name` [TEXT] - Not Null.
* `driver_phone` [TEXT] - Not Null, Unique. Emergency contact for the admin.
* `capacity` [INTEGER] - Not Null. The maximum legal seating capacity of the vehicle.
* `route_id` [INTEGER] - Foreign Key referencing `route(route_id)`. Defines which path this bus runs.

### 2.5 Table: `student`
The core entity tying passengers, guardians, and logistics together.
* `student_id` [INTEGER] - Primary Key, Auto Increment.
* `student_name` [TEXT] - Not Null.
* `student_class` [TEXT] - Not Null. Used for sorting/filtering.
* `parent_id` [INTEGER] - Not Null. Foreign Key referencing `parent(parent_id)`.
* `route_id` [INTEGER] - Not Null. Foreign Key referencing `route(route_id)`. (Note: The bus is inferred by joining route to bus).
* `fee_status` [TEXT] - Not Null. (Enum values expected: 'Paid', 'Pending').

---

## 3. Detailed User & Component Flows

### 3.1 Authentication Handshake & State Management
When `main.py` is executed:
1. `ctk.set_appearance_mode("Dark")` initializes the UI context globally.
2. `LoginWindow` is instantiated.
3. User enters credentials and clicks login.
4. `login()` method queries `admin` table. If false, queries `parent` table.
5. If match found in `parent`:
   * `parent_id` is extracted from the tuple.
   * `self.window.withdraw()` hides the login UI without destroying the Tcl/Tk interpreter.
   * `ParentDashboard(parent_id, master=self.window)` is instantiated as a `CTkToplevel`.
6. When `ParentDashboard` is closed via the `X` button or `Logout` button, `master.deiconify()` restores the login window.

### 3.2 Dynamic Data Fetching Strategy (Parent Dashboard)
The system leverages complex SQL JOINs to flatten relational data into UI-ready tuples.
```sql
SELECT s.student_name, s.student_class, b.bus_number, b.driver_name, 
       b.driver_phone, r.route_name, s.fee_status, p.pickup_point
FROM student s
JOIN parent p ON s.parent_id = p.parent_id
LEFT JOIN route r ON s.route_id = r.route_id
LEFT JOIN bus b ON r.route_id = b.route_id
WHERE s.parent_id = ?
```
* **Performance Note:** `LEFT JOIN` is utilized intentionally so that if a student is temporarily unassigned from a route, the UI does not crash or omit the child completely.

---

## 4. Hardware Integration Topology (Future v2.0)
To achieve Live GPS tracking, the following technical topology will be engineered:
1. **IoT Edge:** CalAmp or similar OBD-II GPS trackers installed in buses.
2. **Ingestion Layer:** Devices ping NMEA coordinate sentences over TCP/UDP every 3 seconds to an AWS IoT Core / MQTT Broker.
3. **Processing:** AWS Lambda triggers parse the payloads, filter out GPS bounce anomalies, and update a highly available Redis cache with the latest `[bus_id, lat, long, timestamp]`.
4. **Client Delivery:** The STMS backend maintains an open WebSocket connection with Parent Dashboards. When Redis receives an update for `bus_id = X`, it broadcasts the delta to all WebSocket clients subscribed to `bus_id = X`.

---

## 5. Security & Disaster Recovery
### 5.1 Vulnerability Management
* **SQL Injection:** Current v1.0 uses parameterized queries (e.g., `WHERE USERNAME = ?`) which mitigates 99% of SQLi attacks. Dynamic SQL string concatenation must be strictly prohibited in all code reviews.
* **Secret Management:** Hardcoded credentials do not exist in the source code; the database is initialized with a default `admin/admin123` via `create_schema.py` which MUST be rotated upon first production deployment.

### 5.2 Backup Strategy (RPO & RTO)
* **Recovery Point Objective (RPO):** 24 Hours.
* **Recovery Time Objective (RTO):** 1 Hour.
* **Mechanism:** A scheduled cron job (Linux) or Task Scheduler (Windows) executing `sqlite3 database.db ".backup 'database_backup_date.db'"` nightly. Backups must be synced to an off-site S3 bucket or equivalent secure cloud storage.
