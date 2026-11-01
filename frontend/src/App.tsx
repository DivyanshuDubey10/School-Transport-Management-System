import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { useAuth } from './hooks/useAuth'

// Layouts
import AdminLayout from './components/layout/AdminLayout'
import ParentLayout from './components/layout/ParentLayout'
import DriverLayout from './components/layout/DriverLayout'

// Pages
import Login from './pages/Login'
import Dashboard from './pages/admin/Dashboard'
import Students from './pages/admin/Students'
import Parents from './pages/admin/Parents'
import Buses from './pages/admin/Buses'
import AdminRoutes from './pages/admin/Routes'
import Attendance from './pages/admin/Attendance'
import Requests from './pages/admin/Requests'
import FleetMap from './pages/admin/FleetMap'
import ParentDashboard from './pages/parent/ParentDashboard'
import ParentAttendance from './pages/parent/ParentAttendance'
import ParentSchedule from './pages/parent/ParentSchedule'
import DriverStudents from './pages/driver/DriverStudents'
import DriverRouteMap from './pages/driver/DriverRouteMap'
import { ToastProvider } from './components/ui/Toast'

function RequireAuth({
  children,
  role,
}: {
  children: JSX.Element
  role: string
}) {
  const { user, token } = useAuth()
  if (!token || !user) return <Navigate to="/login" replace />
  if (user.user_type !== role) return <Navigate to="/login" replace />
  return children
}

function AppRoutes() {
  const { user, token } = useAuth()

  const defaultRedirect = () => {
    if (!token || !user) return '/login'
    if (user.user_type === 'admin') return '/admin/dashboard'
    if (user.user_type === 'parent') return '/parent/dashboard'
    if (user.user_type === 'driver') return '/driver/students'
    return '/login'
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      {/* Admin Routes */}
      <Route
        path="/admin"
        element={
          <RequireAuth role="admin">
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="students" element={<Students />} />
        <Route path="parents" element={<Parents />} />
        <Route path="buses" element={<Buses />} />
        <Route path="routes" element={<AdminRoutes />} />
        <Route path="attendance" element={<Attendance />} />
        <Route path="requests" element={<Requests />} />
        <Route path="live-map" element={<FleetMap />} />
      </Route>

      {/* Parent Routes */}
      <Route
        path="/parent"
        element={
          <RequireAuth role="parent">
            <ParentLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="dashboard" replace />} />
        <Route path="dashboard" element={<ParentDashboard />} />
        <Route path="attendance" element={<ParentAttendance />} />
        <Route path="schedule" element={<ParentSchedule />} />
      </Route>

      {/* Driver Routes */}
      <Route
        path="/driver"
        element={
          <RequireAuth role="driver">
            <DriverLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="students" replace />} />
        <Route path="students" element={<DriverStudents />} />
        <Route path="route-map" element={<DriverRouteMap />} />
      </Route>

      {/* Root redirect */}
      <Route path="/" element={<Navigate to={defaultRedirect()} replace />} />
      <Route path="*" element={<Navigate to={defaultRedirect()} replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <ToastProvider>
          <AppRoutes />
        </ToastProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
