# Comprehensive Implementation Plan & Engineering Roadmap
**Project Name:** School Transport Management System (STMS)
**Document Version:** 1.0 (Enterprise Strategy)
**Date:** July 2026
**Author:** Lead Software Architect 

---

## 1. Project Management Methodology
The transition from STMS v1.0 to v2.0 will be managed using an Agile Scrum framework. The project is divided into two-week Sprints, with daily stand-ups, sprint planning, and retrospective rituals. 

### 1.1 Team Resource Allocation
* **1x Lead Architect / Tech Lead:** Oversees system design, code reviews, and database migration.
* **2x Backend Engineers (Python/FastAPI):** Focuses on REST API development and WebSocket implementations.
* **1x Frontend Engineer (CustomTkinter/React):** Focuses on mapping components and payment modals.
* **1x DevOps Engineer:** Focuses on AWS IoT infrastructure, Redis caching, and CI/CD pipelines.

---

## 2. Work Breakdown Structure (WBS)

### Sprint 1: Foundation & Security Hardening (Weeks 1 - 2)
**Goal:** Migrate data persistence and secure the application layer.

* **Task 1.1: Database Migration to PostgreSQL**
  * Spin up Amazon RDS PostgreSQL instance.
  * Map SQLite schemas to SQLAlchemy ORM models.
  * Write ETL (Extract, Transform, Load) script to port existing v1.0 data to RDS.
  * *Deliverable:* `db_migration.py` and updated `database.py` connecting via `psycopg2`.
* **Task 1.2: Password Hashing Protocol**
  * Integrate `passlib` and `bcrypt`.
  * Update `create_schema.py` to hash the default admin password.
  * Script a one-time migration to hash all existing plaintext passwords in `admin` and `parent` tables.
* **Task 1.3: REST API Foundation**
  * Initialize FastAPI project structure (`/api/v1/routes`, `/api/v1/controllers`).
  * Generate JWT (JSON Web Token) authentication endpoints for login handshakes.

### Sprint 2: WebSockets & IoT Infrastructure (Weeks 3 - 4)
**Goal:** Build the plumbing for real-time tracking.

* **Task 2.1: Message Broker Setup**
  * Provision AWS Elasticache (Redis) cluster.
  * Configure AWS IoT Core to receive MQTT payloads from OBD-II devices.
* **Task 2.2: Payload Parser Service**
  * Build a Python daemon that subscribes to MQTT, validates lat/long coordinates, and updates Redis keys (`bus_location:{bus_id}`).
* **Task 2.3: WebSocket Broadcaster**
  * Create FastAPI WebSocket endpoints (`/ws/bus/{bus_id}`).
  * Implement Redis Pub/Sub so the FastAPI server can broadcast location changes to connected parent clients instantly.

### Sprint 3: Client-Side Mapping (Weeks 5 - 6)
**Goal:** Show parents where the bus is.

* **Task 3.1: TkinterMapView Integration**
  * Embed `tkintermapview` into the `ParentDashboard` UI.
  * Create a map marker representing the assigned bus.
* **Task 3.2: Async Client Architecture**
  * Implement `asyncio` within the CustomTkinter event loop to maintain open WebSocket connections without freezing the UI thread.
* **Task 3.3: Visualizing Routes**
  * Draw polylines on the map representing the planned route, and overlay the bus's live location.

### Sprint 4: Fintech & Fee Management (Weeks 7 - 8)
**Goal:** Collect money.

* **Task 4.1: Stripe API Integration**
  * Register Stripe merchant account.
  * Create backend endpoints to generate Stripe PaymentIntents.
* **Task 4.2: Fee Schedule Schema**
  * Add tables: `fee_schedules`, `payments`, `invoices`.
  * Define logic to break a $1,000 annual fee into 10 x $100 monthly installments.
* **Task 4.3: Payment UI Modals**
  * Build "Pay Now" popups in the Parent Dashboard.
  * Integrate Stripe Checkout (or webview capture) to securely process credit cards without STMS holding PCI compliance burden.
  * Setup webhooks to listen for `payment_intent.succeeded` and update the `fee_status` to 'Paid' instantly.

### Sprint 5: Admin Finance & Reporting (Weeks 9 - 10)
**Goal:** Empower the Admin with accounting tools.

* **Task 5.1: Accounting Dashboard**
  * Add a "Finance" tab to the Admin Dashboard.
  * Display MRR (Monthly Recurring Revenue), YTD Collected, and Outstanding Balances.
* **Task 5.2: Overdue Automation**
  * Write a CRON job that runs daily at 00:00 UTC.
  * Identify parents with missed installment dates and trigger email/SMS warnings (via Twilio/SendGrid).

### Sprint 6: UAT & Deployment (Weeks 11 - 12)
**Goal:** Go Live safely.

* **Task 6.1: End-to-End (E2E) Testing**
  * Run simulated IoT data through the entire pipeline to verify map markers update correctly under load.
  * Conduct penetration testing on the payment gateway.
* **Task 6.2: Executable Compilation**
  * Use PyInstaller and Inno Setup to create a standard Windows installer (`STMS_v2.0_Setup.exe`).
* **Task 6.3: Pilot Rollout**
  * Deploy to 5 buses and 200 parents. Gather feedback, monitor server metrics (Datadog/NewRelic).

---

## 3. Git Strategy & CI/CD
* **Branching Model:** GitFlow. `main` strictly holds production code. `develop` holds the next sprint's release. Features are branched off `develop` (e.g., `feature/stripe-integration`).
* **CI Validation:** GitHub Actions triggers on every PR to `develop`.
  * Runs `pytest` suite.
  * Runs `black` for PEP8 formatting compliance.
  * Runs `bandit` to scan for security vulnerabilities (like hardcoded secrets).
* **CD Pipeline:** Merging to `main` triggers Docker builds for the backend API, pushing images to Amazon ECR, and orchestrating rolling updates to Amazon ECS via Terraform.
