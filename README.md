# 🚌 NeoYatra — School Transport Management System

A production-ready full-stack web application developed using **React + Vite + TypeScript** and **FastAPI + PostgreSQL** to streamline school transport administration. The system provides dedicated web portals for Administrators, Parents, and Drivers with real-time GPS & route tracking.

---

## 🌟 Key Features

### 🔐 Multi-Role Authentication
- Single unified login screen with automatic role-based routing (Admin, Parent, Driver).
- Secure JWT Bearer token authentication with bcrypt password hashing.

### 🛰️ Real-Time Live Bus Tracking (Leaflet & OpenStreetMap)
- **100% Free & Open-Source**: Zero paid external API keys (no Google Maps API bills).
- **Admin Fleet Radar**: City-wide map displaying all active buses in transit with real-time speed, heading, and route waypoints.
- **Parent Live View**: Modal with real-time bus marker tracking towards the student's designated pickup stop.
- **Driver Navigation & Simulator**: Live trip broadcasting with device GPS or smooth simulated motion along route stops.

### 📊 Admin Portal
- **Dashboard Overview**: KPI statistics, Route Occupancy charts, Fee collection metrics, and Quick Actions.
- **Live Fleet Map**: Real-time tracking command center for all school transport vehicles.
- **Student Management**: Full CRUD operations, route allocations, parent linkages, and fee tracking.
- **Parent Management**: Register parent accounts, home pickup points, and emergency contacts.
- **Bus Fleet Management**: Register transport vehicles, seat capacities, driver credentials, and route links.
- **Route Management**: Create and manage travel corridors across city sectors.
- **Attendance Logs**: Real-time review of daily bus boarding records marked by drivers.
- **Transport Change Requests**: Review and approve/reject pickup point change requests.

### 👨‍👩‍👧 Parent Portal
- **Children Transport Hub**: Assigned bus number, driver contact, designated pickup stop, and fee balance status.
- **Live Track Bus**: One-click real-time map showing the child's bus progressing along the route.
- **Boarding Logs**: Detailed attendance history and boarding percentage.
- **Pickup Change Requests**: Submit online requests to change designated bus stops.

### 🚍 Driver Portal
- **Route Student List**: View students allocated to the driver's bus with one-click **Present** / **Absent** boarding buttons.
- **Route Navigation & Tracking**: Start/stop active trips, broadcast live location, and inspect ordered stop sequence.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Leaflet, TanStack Query, Recharts, Lucide Icons |
| **Backend** | FastAPI, Python 3, Uvicorn, psycopg2-binary, python-jose (JWT), bcrypt |
| **Database** | PostgreSQL (`stms_db` or cloud connection string) |
| **Tooling** | npm, Git |

---

## 🚀 Running Locally

### 1. Backend Setup
```bash
cd backend
# Install dependencies
py -m pip install -r requirements.txt

# Start FastAPI server
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
- API is running at: `http://localhost:8000`
- Interactive API Swagger docs: `http://localhost:8000/docs`
- On first boot, tables and the default administrator account are automatically initialized.

### 2. Frontend Setup
```bash
cd frontend
# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
- Web application is running at: `http://localhost:5173`

---

## 🔑 Default Credentials

| Portal | Username | Password |
|---|---|---|
| **Admin** | `admin` | `admin123` |
| **Parent** | `parent1` | `password123` |
| **Driver** | Created during bus registration | (as set in bus form) |

---

## 🌐 Production Deployment

### Backend (Railway / Render / Fly.io)
1. Point to the `backend/` directory as the root.
2. Set Environment Variables:
   - `DATABASE_URL`: Connection URL from your PostgreSQL provider (Supabase / Neon / Railway).
   - `JWT_SECRET`: A secure random string (32+ characters).
   - `ALLOWED_ORIGINS`: Your live frontend domain (e.g. `https://your-app.vercel.app`).
3. Start Command: `uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}`

### Frontend (Vercel / Netlify)
1. Point to the `frontend/` directory as the root.
2. Build Command: `npm run build`
3. Output Directory: `dist`
4. Set Environment Variable:
   - `VITE_API_URL`: Your deployed FastAPI backend URL + `/api/v1` (e.g. `https://your-api.onrender.com/api/v1`).
