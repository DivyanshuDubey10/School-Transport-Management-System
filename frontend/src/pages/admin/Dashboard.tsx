import { useQuery } from '@tanstack/react-query'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts'
import {
  Users, Bus, Map, UserCircle,
  TrendingUp, Calendar, ArrowUpRight,
} from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { getDashboard } from '../../api/dashboard'
import { KpiCard } from '../../components/ui/Card'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'

const PIE_COLORS = ['#10B981', '#F97316']

const QUICK_ACTIONS = [
  { label: 'Students', path: '/admin/students', color: 'text-sky-600 bg-sky-50 border-sky-100', icon: Users },
  { label: 'Parents', path: '/admin/parents', color: 'text-purple-600 bg-purple-50 border-purple-100', icon: UserCircle },
  { label: 'Buses', path: '/admin/buses', color: 'text-amber-600 bg-amber-50 border-amber-100', icon: Bus },
  { label: 'Routes', path: '/admin/routes', color: 'text-emerald-600 bg-emerald-50 border-emerald-100', icon: Map },
  { label: 'Attendance', path: '/admin/attendance', color: 'text-blue-600 bg-blue-50 border-blue-100', icon: Calendar },
  { label: 'Requests', path: '/admin/requests', color: 'text-rose-600 bg-rose-50 border-rose-100', icon: TrendingUp },
]

export default function Dashboard() {
  const navigate = useNavigate()
  const { data, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: getDashboard,
  })

  if (isLoading) return <LoadingSpinner />
  if (error || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500 text-sm">
        Failed to load dashboard data. Please try again.
      </div>
    )
  }

  const { stats, route_occupancy, fee_status } = data
  const pieData = [
    { name: 'Paid', value: fee_status.paid },
    { name: 'Pending', value: fee_status.pending },
  ]
  const total = fee_status.paid + fee_status.pending || 1
  const paidPct = Math.round((fee_status.paid / total) * 100)

  return (
    <div className="space-y-6 page-enter">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-1">Overview</p>
          <h1 className="text-2xl font-bold text-slate-800">Dashboard</h1>
        </div>
        <div className="text-xs text-slate-400 bg-white border border-slate-100 rounded-xl px-3 py-1.5 shadow-sm">
          {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <KpiCard
          title="Total Students"
          value={stats.total_students}
          icon={<Users size={20} className="text-sky-500" />}
          iconBg="bg-sky-50"
          subtitle="Enrolled in transport"
        />
        <KpiCard
          title="Active Buses"
          value={stats.active_buses}
          icon={<Bus size={20} className="text-purple-500" />}
          iconBg="bg-purple-50"
          subtitle="On assigned routes"
        />
        <KpiCard
          title="Routes"
          value={stats.designated_routes}
          icon={<Map size={20} className="text-emerald-500" />}
          iconBg="bg-emerald-50"
          subtitle="Designated routes"
        />
        <KpiCard
          title="Total Parents"
          value={stats.total_parents}
          icon={<UserCircle size={20} className="text-amber-500" />}
          iconBg="bg-amber-50"
          subtitle="Registered accounts"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
        {/* Bar Chart */}
        <div className="xl:col-span-2 bg-white rounded-2xl border border-slate-100 shadow-card p-6">
          <div className="flex items-start justify-between mb-5">
            <div>
              <h2 className="text-sm font-bold text-slate-700">Route Occupancy</h2>
              <p className="text-xs text-slate-400 mt-0.5">Students vs capacity per route</p>
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-sky-400 inline-block" />
                Students
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-2.5 w-2.5 rounded-sm bg-slate-200 inline-block" />
                Capacity
              </span>
            </div>
          </div>
          {route_occupancy.length === 0 ? (
            <div className="flex items-center justify-center h-48 text-slate-400 text-sm">No route data yet</div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={route_occupancy} barGap={4} barCategoryGap="30%">
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis dataKey="route_name" tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#94A3B8' }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    borderRadius: 10,
                    border: '1px solid #E2E8F0',
                    fontSize: 12,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                  }}
                  cursor={{ fill: 'rgba(0,0,0,0.02)' }}
                />
                <Bar dataKey="students" name="Students" fill="#38BDF8" radius={[5, 5, 0, 0]} />
                <Bar dataKey="capacity" name="Capacity" fill="#E2E8F0" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Pie Chart */}
        <div className="bg-white rounded-2xl border border-slate-100 shadow-card p-6 flex flex-col justify-between">
          <div>
            <div className="mb-4">
              <h2 className="text-sm font-bold text-slate-700">Fee Status</h2>
              <p className="text-xs text-slate-400 mt-0.5">Payment collection overview</p>
            </div>
            {/* Stat pills */}
            <div className="grid grid-cols-2 gap-2 mb-4">
              <div className="bg-emerald-50 rounded-xl p-3 text-center border border-emerald-100">
                <p className="text-lg font-bold text-emerald-600">{fee_status.paid}</p>
                <p className="text-xs text-emerald-500 font-medium">Paid</p>
              </div>
              <div className="bg-orange-50 rounded-xl p-3 text-center border border-orange-100">
                <p className="text-lg font-bold text-orange-500">{fee_status.pending}</p>
                <p className="text-xs text-orange-400 font-medium">Pending</p>
              </div>
            </div>
            <ResponsiveContainer width="100%" height={170}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {pieData.map((_entry, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index]} />
                  ))}
                </Pie>
                <Legend iconType="circle" iconSize={8} wrapperStyle={{ fontSize: 12 }} />
                <Tooltip contentStyle={{ borderRadius: 10, border: '1px solid #E2E8F0', fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="text-center pt-2 border-t border-slate-100">
            <p className="text-xl font-bold text-slate-800">{paidPct}%</p>
            <p className="text-xs text-slate-400">collection rate</p>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-card p-6">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-sm font-bold text-slate-700">Quick Actions</h2>
            <p className="text-xs text-slate-400 mt-0.5">Navigate to any section quickly</p>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {QUICK_ACTIONS.map(({ label, path, color, icon: Icon }) => (
            <button
              key={path}
              onClick={() => navigate(path)}
              className={[
                'relative flex flex-col items-center justify-center gap-2.5 p-4 rounded-2xl font-semibold text-xs border transition-all duration-200 hover:scale-105 hover:shadow-md group',
                color,
              ].join(' ')}
            >
              <Icon size={20} className="transition-transform group-hover:scale-110 duration-200" />
              <span>{label}</span>
              <ArrowUpRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity absolute top-2 right-2" />
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
