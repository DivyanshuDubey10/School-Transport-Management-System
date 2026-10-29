import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import {
  Users, Bus, Map, UserCircle,
  ArrowRight,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getDashboard } from '../../api/dashboard'
import { KpiCard } from '../../components/ui/Card'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { Button } from '../../components/ui/Button'

const PIE_COLORS = ['#10B981', '#EF4444']

export default function Dashboard() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  if (isLoading) return <LoadingSpinner />
  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        Failed to load dashboard data. Please try again.
      </div>
    )
  }

  const { stats, route_occupancy, fee_status } = data
  const pieData = [
    { name: 'Paid', value: fee_status.paid },
    { name: 'Pending', value: fee_status.pending },
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Overview of your school transport system
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Total Students"
          value={stats.total_students}
          icon={<Users size={22} className="text-sky-500" />}
          iconBg="bg-sky-50"
        />
        <KpiCard
          title="Active Buses"
          value={stats.active_buses}
          icon={<Bus size={22} className="text-purple-500" />}
          iconBg="bg-purple-50"
        />
        <KpiCard
          title="Designated Routes"
          value={stats.designated_routes}
          icon={<Map size={22} className="text-emerald-500" />}
          iconBg="bg-emerald-50"
        />
        <KpiCard
          title="Total Parents"
          value={stats.total_parents}
          icon={<UserCircle size={22} className="text-amber-500" />}
          iconBg="bg-amber-50"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Bar Chart */}
        <div className="xl:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-1">Route Occupancy</h2>
          <p className="text-xs text-slate-400 mb-5">Students vs capacity per route</p>
          {route_occupancy.length === 0 ? (
            <div className="flex items-center justify-center h-48 text-slate-400 text-sm">
              No route data available
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={route_occupancy} barGap={4}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" />
                <XAxis
                  dataKey="route_name"
                  tick={{ fontSize: 11, fill: '#94A3B8' }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0', fontSize: 12 }}
                />
                <Bar dataKey="students" name="Students" fill="#38BDF8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="capacity" name="Capacity" fill="#E2E8F0" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Pie Chart */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-1">Fee Status</h2>
          <p className="text-xs text-slate-400 mb-2">Paid vs Pending students</p>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="45%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={3}
                dataKey="value"
              >
                {pieData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={PIE_COLORS[index]} />
                ))}
              </Pie>
              <Legend iconType="circle" iconSize={10} wrapperStyle={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ borderRadius: 8, border: '1px solid #E2E8F0', fontSize: 12 }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {[
            { label: 'Manage Students', path: '/admin/students', color: 'text-sky-600 bg-sky-50' },
            { label: 'Manage Parents', path: '/admin/parents', color: 'text-purple-600 bg-purple-50' },
            { label: 'Manage Buses', path: '/admin/buses', color: 'text-amber-600 bg-amber-50' },
            { label: 'Manage Routes', path: '/admin/routes', color: 'text-emerald-600 bg-emerald-50' },
            { label: 'View Attendance', path: '/admin/attendance', color: 'text-blue-600 bg-blue-50' },
            { label: 'Transport Requests', path: '/admin/requests', color: 'text-rose-600 bg-rose-50' },
          ].map(({ label, path, color }) => (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={[
                'flex flex-col items-center justify-center gap-2 p-4 rounded-xl font-medium text-xs transition-all hover:scale-105 hover:shadow-sm',
                color,
              ].join(' ')}
            >
              <ArrowRight size={18} />
              {label}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
