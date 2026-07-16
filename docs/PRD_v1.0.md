# Product Requirements Document (PRD) - Extended Enterprise Edition
**Project Name:** School Transport Management System (STMS)
**Document Version:** 1.0.1 (Comprehensive Baseline)
**Date:** July 2026
**Author:** Lead Software Architect (30+ Years Exp.) & Principal Product Manager

---

## 1. Document Control
### 1.1 Revision History
| Date | Version | Description | Author |
| :--- | :--- | :--- | :--- |
| 2026-07-16 | 1.0.0 | Initial Draft | Lead Architect |
| 2026-07-16 | 1.0.1 | Comprehensive Enterprise Expansion | Lead Architect |

### 1.2 Glossary of Terms
* **STMS:** School Transport Management System.
* **CRUD:** Create, Read, Update, Delete operations.
* **IoT:** Internet of Things (referring to GPS trackers on buses).
* **FERPA:** Family Educational Rights and Privacy Act (US Data Privacy).
* **GDPR:** General Data Protection Regulation (EU Data Privacy).

---

## 2. Executive Summary
The School Transport Management System (STMS) is a paradigm-shifting, centralized application designed to orchestrate the complex logistics of school transportation. In its initial iteration (v1.0), it serves as a robust administrative backbone, replacing archaic spreadsheet-based routing with a deterministic, relational database model. It provides administrative staff with granular control over fleets, routes, and student assignments, while empowering parents with a self-service dashboard to monitor their children's logistical and financial (fee) statuses.

The ultimate vision for STMS (v2.0 and beyond) is to evolve into a full-scale real-time ecosystem. This includes sub-second latency IoT GPS tracking of fleet vehicles, dynamic route optimization using machine learning, and a fully integrated fintech layer for seamless, installment-based fee processing.

---

## 3. Market Research & Problem Statement
### 3.1 The Problem
Educational institutions currently suffer from disconnected logistical frameworks.
1. **Administrative Overhead:** Route planning is done manually. When a bus reaches capacity, re-routing takes hours of administrative labor.
2. **Parental Anxiety:** Parents lack visibility into transit times. "Where is the bus?" is the highest volume call to school front desks.
3. **Financial Leakage:** Tracking transport fees separately from tuition leads to missed payments and difficult reconciliation.

### 3.2 Competitive Landscape
Existing solutions (e.g., Zonar, Samsara) are heavily skewed towards massive enterprise fleets and are prohibitively expensive for mid-sized schools. They lack tightly coupled "Parent-Facing" portals and integrated fee management. STMS bridges this gap by focusing equally on the Administrative, Financial, and Parental experiences.

---

## 4. User Personas (Deep Dive)

### 4.1 Persona 1: "Agnes" - The Transport Administrator
* **Demographics:** 45-55 years old, highly organized, moderate technical literacy.
* **Motivations:** Wants to ensure zero child-left-behind incidents, optimize bus capacities to save fuel, and reduce angry phone calls from parents.
* **Pain Points:** Using Excel to track which student is on which bus. When a student changes address, Agnes has to manually calculate which new route they belong to.
* **Core Needs:** Bulk import tools, visual dashboard of fleet health, automated capacity warnings.

### 4.2 Persona 2: "David" - The Busy Parent
* **Demographics:** 30-45 years old, works full time, high technical literacy (expects mobile-first/modern UI).
* **Motivations:** The safety of his children. Wants to know exactly when to walk to the bus stop.
* **Pain Points:** The bus is often 10 minutes early or late due to traffic, causing David to wait in the rain or miss the bus entirely. Forgetting to send physical transport fee checks.
* **Core Needs:** Real-time visibility, automated push notifications, one-click digital payments.

### 4.3 Persona 3: "Marcus" - The Bus Driver (Future v3.0 Persona)
* **Demographics:** 50-65 years old, low technical literacy.
* **Motivations:** Wants to drive safely without being distracted by paper manifests.
* **Pain Points:** Unsure if a student is absent or just late to the stop.
* **Core Needs:** Large-button, high-contrast tablet interface showing exactly who is boarding next.

---

## 5. Detailed Functional Requirements (Epics & User Stories)

### Epic 1: Authentication & Authorization
**Description:** The system must securely authenticate users and route them to their respective role-based dashboards.

* **User Story 1.1:** As an Admin, I want to log in using a secure username and password so that I can access administrative controls.
  * **Acceptance Criteria:**
    * System verifies credentials against the `admin` table.
    * Invalid credentials trigger a "Invalid username or password" modal.
    * Successful login destroys the login window and instantiates the `AdminDashboard`.
* **User Story 1.2:** As a Parent, I want to log in using my provided credentials so that I can view my children's data.
  * **Acceptance Criteria:**
    * System verifies credentials against the `parent` table.
    * System greets the parent by their `parent_name`.

### Epic 2: Fleet & Route Management
**Description:** Administrative tools to define the physical assets and geographical paths.

* **User Story 2.1:** As an Admin, I want to create a new Route so that I can assign buses to it.
  * **Acceptance Criteria:** Must require a unique Route Name. Saves to `route` table.
* **User Story 2.2:** As an Admin, I want to register a new Bus with a maximum capacity so that I don't overbook a vehicle.
  * **Acceptance Criteria:** Captures Bus Number, Driver Name, Driver Phone, Capacity, and assigns to a Route.

### Epic 3: Stakeholder Management (Parents & Students)
**Description:** Managing the human element of the transport system.

* **User Story 3.1:** As an Admin, I want to register a Parent and assign them login credentials.
  * **Acceptance Criteria:** Captures Name, Phone, Address, Default Pickup Point. Automatically ensures username/phone uniqueness.
* **User Story 3.2:** As an Admin, I want to add a Student, link them to a Parent, and assign them to a Route.
  * **Acceptance Criteria:** The system must visually link the student to the parent ID. (Future: Must validate that the assigned route's bus has `current_students < capacity`).

### Epic 4: Parent Portal
**Description:** The self-service area for guardians.

* **User Story 4.1:** As a Parent, I want to see a list of all my children and their assigned transport details.
  * **Acceptance Criteria:** The dashboard dynamically generates UI cards for each child. Each card explicitly lists: Child Name, Class, Fee Status, Bus Number, Driver Name, Driver Contact, Route, and Pickup Point.

---

## 6. Non-Functional Requirements (NFRs)

### 6.1 Performance & Scalability
* **Response Time:** UI transitions must occur in < 200ms to maintain a desktop-native feel. Database queries must execute in < 50ms.
* **Concurrency (v1.0):** SQLite database is designed for a single local administrative user.
* **Concurrency (v2.0):** Migration to PostgreSQL must support up to 5,000 concurrent parent connections polling for live tracking data simultaneously.

### 6.2 Security & Compliance
* **Data Encryption at Rest:** SQLite database file must reside on an encrypted volume (BitLocker/FileVault).
* **Data Encryption in Transit (v2.0):** All API calls must be enforced over TLS 1.3 (HTTPS).
* **Password Policies (v1.5):** Implement `bcrypt` hashing with a minimum work factor of 12. Plaintext passwords are strictly prohibited in production.
* **Compliance:** The system must mask student names (e.g., displaying only initials) if requested by the school to comply with FERPA guidelines.

### 6.3 Reliability & Availability
* **Uptime:** The future web backend (v2.0) must target 99.9% uptime.
* **Offline Mode:** The desktop UI (v1.0) must gracefully handle network disconnections if the database is moved to a network drive, attempting 3 retries before failing gracefully.

### 6.4 Usability & Accessibility
* **Contrast:** The UI must adhere to WCAG 2.1 AA standards for contrast ratios (hence the dark mode implementation with white text on `#2b2b2b` backgrounds).
* **Readability:** Base font size set to Arial 12pt+, scaling appropriately on high-DPI displays (handled automatically by `customtkinter`).

---

## 7. Out of Scope for Version 1.0
* Mobile Application for iOS/Android (Deferred to v3.0).
* Automated Route Optimization using Graph Theory/Dijkstra's Algorithm (Deferred to v4.0).
* Direct communication/chat between Parents and Drivers (Security risk; deferred indefinitely).

---

## 8. Telemetry and Analytics (Future Implementation)
To understand system usage, the following telemetry should be captured in v2.0:
* **Login Frequency:** How often parents check the app (Daily active users).
* **Dwell Time:** Time spent on the live tracking map.
* **Payment Funnel Drop-off:** Percentage of parents who click "Pay Fees" but do not complete the transaction.
