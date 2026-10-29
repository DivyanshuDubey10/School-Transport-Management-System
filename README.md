# 🚌 NeoYatra — School Transport Management System

A modern full-stack web application developed using **React + Vite + TypeScript** and **FastAPI + PostgreSQL** to streamline school transport administration. The system provides dedicated web portals for Administrators, Parents, and Drivers.

---

## 🌟 Key Features

### 🔐 Multi-Role Authentication
- Single unified login screen with automatic redirection based on user role (Admin, Parent, Driver).
- Secure JWT Bearer token authentication with bcrypt password hashing.

### 📊 Admin Portal
- **Dashboard Overview**: Live KPI statistics (Total Students, Active Fleet, Designated Routes, Total Parents), Route Occupancy bar chart, and Fee distribution pie chart.
- **Student Management**: Full CRUD operations, route allocations, parent linkages, and fee tracking.
- **Parent Management**: Register parent accounts, manage designated home pickup points, and track emergency contacts.
- **Bus Fleet Management**: Register transport vehicles, assign drivers with login credentials, set seat capacities, and link routes.
- **Route Management**: Add, update, and manage travel paths across city and suburban sectors.
- **Daily Attendance Logs**: Real-time review of bus boarding records marked by drivers.
- **Transport Change Requests**: Review and approve/reject pickup point change requests submitted by parents.

### 👨‍👩‍👧 Parent Portal
- **Children Overview**: Cards displaying each child's assigned bus number, driver name, direct phone call link, designated pickup/drop stop, and fee balance status.
- **Boarding Logs**: Detailed attendance history and attendance percentage per student for the last 30 recorded trips.
- **Fleet Schedule**: Searchable directory of all operational school buses and travel routes.
- **Pickup Change Requests**: Submit online requests to change a child's designated bus stop.

### 🚍 Driver Portal
- **Route Student List**: View students allocated to the driver's bus with one-click **Present** and **Absent** boarding buttons, plus a **Mark All Present** bulk action.
- **Route Itinerary Map**: Ordered sequence of designated pickup stops showing which students board at each location with parent contact numbers.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts, Lucide Icons |
| **Backend** | FastAPI, Python 3, Uvicorn, python-jose (JWT), bcrypt, psycopg2 |
| **Database** | PostgreSQL (`stms_db`) |
| **Tooling** | npm, Git |

---

## 🚀 Getting Started

### 1. Database Setup & Seeding
Ensure PostgreSQL is running, then run the seeder:
```bash
py seed.py
```

### 2. Running Locally

**Terminal 1 — Backend:**
```bash
cd backend
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
# API running at: http://localhost:8000
# Interactive API docs: http://localhost:8000/docs
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
# Web application running at: http://localhost:5173
```

---

## 🔑 Default Credentials

| Portal | Username | Password |
|---|---|---|
| **Admin** | `admin` | `admin123` |
| **Parent** | `parent1` | `password123` |
| **Driver** | `driver1` (or custom created in Bus Management) | (as set in bus form) |
