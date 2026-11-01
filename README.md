# 🚌 School Transport Management System (NeoYatra)

A full-stack web application built to manage school bus transport, student routes, attendance, and live bus location tracking.

I built this project using **React + TypeScript** for the frontend and **FastAPI + PostgreSQL** for the backend as part of my BCA coursework / portfolio.

---

## 💡 Why I Made This

In many schools, managing bus routes, tracking student attendance, and updating parents about bus locations is either done on paper or with complicated phone calls. 

I wanted to make a clean, modern web app where:
1. **Admins** can manage students, parents, buses, routes, and view everything on a dashboard.
2. **Parents** can see their child's bus details, fee balance, and track the bus live on an interactive map.
3. **Drivers** can mark daily student attendance (present/absent) and start a live trip that broadcasts the bus's location.

---

## ✨ Features

### 1. 🔐 User Roles & Login
- Single login screen with automatic redirection based on role:
  - **Admin** (`admin / admin123`)
  - **Parent** (`parent1 / password123`)
  - **Driver** (login with bus username & password)
- Secure password hashing using `bcrypt` and session tokens using `JWT`.

### 2. 📍 Live Bus Tracking (Free OpenStreetMap & Leaflet)
- No paid Google Maps API keys required — uses free OpenStreetMap and Leaflet.
- **Admin Fleet Map**: View all school buses on the city map in real-time.
- **Parent View**: Parents can click "Live Track Bus" to see where the bus currently is and watch it approach their designated pickup stop.
- **Driver Trip Mode**: Drivers can click "Start Trip" to broadcast their live location (supports real GPS or an automatic simulator for testing on a laptop).

### 3. 👨‍🎓 Student & Route Management
- Add, edit, and delete student records.
- Link each student to their parent and an assigned bus route.
- Track transport fee payments (Paid vs. Pending).

### 4. 📅 Attendance Tracker
- Drivers can mark students as **Present** or **Absent** when they board the bus.
- Bulk "Mark All Present" button for busy mornings.
- Parents can view their child's attendance history.

### 5. 🔄 Pickup Change Requests
- Parents can submit an online request if they need their child picked up from a different stop.
- Admins can approve or reject requests with one click.

---

## 🛠️ Tech Stack Used

- **Frontend**:
  - React 18 with TypeScript
  - Vite (fast build tool)
  - Tailwind CSS (styling)
  - Leaflet + OpenStreetMap (interactive maps)
  - TanStack Query (API data fetching & caching)
  - Recharts (dashboard charts)
  - Lucide Icons
- **Backend**:
  - Python 3
  - FastAPI (REST API framework)
  - Uvicorn (ASGI web server)
  - PostgreSQL with `psycopg2`
  - JWT (`python-jose`) & `bcrypt` for authentication
- **Database**:
  - PostgreSQL (8 tables: `admin`, `parent`, `route`, `bus`, `student`, `attendance`, `transport_change_request`, `user_settings`)

---

## 📁 Project Structure

```text
Transport-management/
├── backend/                  # FastAPI backend
│   ├── routers/              # API endpoints (auth, students, buses, tracking, etc.)
│   ├── middleware/           # JWT authentication middleware
│   ├── database.py           # PostgreSQL connection & auto-table creation
│   ├── dal.py                # Data Access Layer (SQL queries)
│   ├── security.py           # Password hashing & JWT helpers
│   ├── reset_db.py           # Helper script to reset database to clean state
│   ├── main.py               # FastAPI entry point
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Sample backend environment variables
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── api/              # Axios API functions (auth, students, tracking, etc.)
│   │   ├── components/       # Reusable UI components (Sidebar, TopBar, Table, Map, etc.)
│   │   ├── pages/            # Pages for Admin, Parent, and Driver portals
│   │   ├── hooks/            # Custom React hooks (useAuth)
│   │   └── App.tsx           # Main router & layout setup
│   ├── package.json          # Node dependencies
│   └── vite.config.ts        # Vite configuration & code splitting
└── README.md
```

---

## 🚀 How to Run Locally

### Prerequisites
- Node.js (v18+)
- Python (3.10+)
- PostgreSQL installed and running locally

---

### Step 1: Backend Setup

1. Open a terminal and navigate to the backend folder:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   py -m pip install -r requirements.txt
   ```

3. Create your `.env` file in the `backend/` folder:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```
   Update the DB password to match your local PostgreSQL password.

4. Start the FastAPI server:
   ```bash
   py -m uvicorn main:app --reload --port 8000
   ```
   - The backend will start on: `http://localhost:8000`
   - You can view the automatic Swagger API documentation at: `http://localhost:8000/docs`
   - *Note: On first startup, the tables and default admin account (`admin` / `admin123`) are created automatically!*

---

### Step 2: Frontend Setup

1. Open a second terminal and navigate to the frontend folder:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   - Open your browser at: `http://localhost:5173`

---

## 🔑 Login Credentials

| Role | Username | Password |
|---|---|---|
| **Admin** | `admin` | `admin123` |
| **Parent** | `parent1` | `password123` |
| **Driver** | Created during bus registration | (set in the bus form) |

---

## 📝 Notes & Future Improvements
- [x] Full CRUD for students, buses, routes, and parents
- [x] JWT authentication for all 3 portals
- [x] Live GPS tracking with Leaflet map
- [ ] Push notifications to mobile for bus arrival alerts
- [ ] Automatic SMS alerts to parents

*Made by a BCA student interested in full-stack development.*
