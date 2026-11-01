import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Users,
  UserCircle,
  Bus,
  Map,
  CalendarCheck,
  FileText,
  type LucideIcon,
} from 'lucide-react'

interface NavItem {
  to: string
  label: string
  Icon: LucideIcon
}

interface SidebarProps {
  navItems: NavItem[]
  role: string
}

const roleConfig: Record<string, { color: string; bg: string; label: string }> = {
  admin:  { color: 'text-sky-300',     bg: 'bg-sky-500/10',     label: 'Admin Portal' },
  parent: { color: 'text-emerald-300', bg: 'bg-emerald-500/10', label: 'Parent Portal' },
  driver: { color: 'text-amber-300',   bg: 'bg-amber-500/10',   label: 'Driver Portal' },
}

export { type NavItem }

export function Sidebar({ navItems, role }: SidebarProps) {
  const cfg = roleConfig[role] ?? { color: 'text-white/50', bg: 'bg-white/5', label: `${role} Portal` }

  return (
    <aside className="sidebar-scroll fixed top-0 left-0 h-full w-60 bg-sidebar flex flex-col z-30 overflow-y-auto shadow-sidebar">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent/10 rounded-xl border border-accent/20 flex-shrink-0">
            <Bus size={18} className="text-accent" />
          </div>
          <div>
            <span className="text-lg font-bold text-white tracking-tight">
              Neo<span className="text-accent">Yatra</span>
            </span>
            <div className={`inline-flex items-center gap-1.5 mt-0.5 px-2 py-0.5 rounded-full text-[10px] font-semibold ${cfg.color} ${cfg.bg} border border-white/5`}>
              <div className={`h-1.5 w-1.5 rounded-full pulse-dot ${cfg.color.replace('text-', 'bg-')}`} />
              {cfg.label}
            </div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        <p className="px-3 mb-2 text-[10px] font-semibold text-white/20 uppercase tracking-widest">Navigation</p>
        {navItems.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [
                'relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 group',
                isActive
                  ? 'bg-accent/10 text-accent'
                  : 'text-slate-400 hover:text-white hover:bg-white/5',
              ].join(' ')
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-accent rounded-r-full" />
                )}
                <Icon size={17} className={`flex-shrink-0 transition-colors ${isActive ? 'text-accent' : 'text-slate-500 group-hover:text-white'}`} />
                <span>{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-white/5">
        <p className="text-[10px] text-white/20 text-center tracking-wide">NeoYatra v1.0 · Built with ♥</p>
      </div>
    </aside>
  )
}

// Pre-built nav configs
export const adminNavItems: NavItem[] = [
  { to: '/admin/dashboard',  label: 'Dashboard',  Icon: LayoutDashboard },
  { to: '/admin/students',   label: 'Students',   Icon: Users },
  { to: '/admin/parents',    label: 'Parents',    Icon: UserCircle },
  { to: '/admin/buses',      label: 'Buses',      Icon: Bus },
  { to: '/admin/routes',     label: 'Routes',     Icon: Map },
  { to: '/admin/attendance', label: 'Attendance', Icon: CalendarCheck },
  { to: '/admin/requests',   label: 'Requests',   Icon: FileText },
]

export const parentNavItems: NavItem[] = [
  { to: '/parent/dashboard',  label: 'Dashboard',  Icon: LayoutDashboard },
  { to: '/parent/attendance', label: 'Attendance', Icon: CalendarCheck },
  { to: '/parent/schedule',   label: 'Schedule',   Icon: Map },
]

export const driverNavItems: NavItem[] = [
  { to: '/driver/students',  label: 'My Students', Icon: Users },
  { to: '/driver/route-map', label: 'Route Map',   Icon: Map },
]
