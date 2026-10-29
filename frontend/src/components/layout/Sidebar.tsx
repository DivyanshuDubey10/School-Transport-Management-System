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

const roleColor: Record<string, string> = {
  admin: 'text-sky-300',
  parent: 'text-emerald-300',
  driver: 'text-amber-300',
}

export { type NavItem }

export function Sidebar({ navItems, role }: SidebarProps) {
  return (
    <aside className="sidebar-scroll fixed top-0 left-0 h-full w-60 bg-sidebar flex flex-col z-30 overflow-y-auto">
      {/* Brand */}
      <div className="px-6 py-5 border-b border-white/5">
        <span className="text-xl font-bold text-white tracking-tight">
          Neo<span className="text-accent">Yatra</span>
        </span>
        <p className={['text-xs mt-0.5 font-medium capitalize', roleColor[role] ?? 'text-white/40'].join(' ')}>
          {role} Portal
        </p>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navItems.map(({ to, label, Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-accent/10 text-accent'
                  : 'text-slate-400 hover:text-white hover:bg-white/5',
              ].join(' ')
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={18} className={isActive ? 'text-accent' : ''} />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-white/5">
        <p className="text-xs text-white/20 text-center">NeoYatra v1.0</p>
      </div>
    </aside>
  )
}

// Pre-built nav configs
export const adminNavItems: NavItem[] = [
  { to: '/admin/dashboard', label: 'Dashboard', Icon: LayoutDashboard },
  { to: '/admin/students',  label: 'Students',  Icon: Users },
  { to: '/admin/parents',   label: 'Parents',   Icon: UserCircle },
  { to: '/admin/buses',     label: 'Buses',     Icon: Bus },
  { to: '/admin/routes',    label: 'Routes',    Icon: Map },
  { to: '/admin/attendance',label: 'Attendance',Icon: CalendarCheck },
  { to: '/admin/requests',  label: 'Requests',  Icon: FileText },
]

export const parentNavItems: NavItem[] = [
  { to: '/parent/dashboard',  label: 'Dashboard',  Icon: LayoutDashboard },
  { to: '/parent/attendance', label: 'Attendance', Icon: CalendarCheck },
  { to: '/parent/schedule',   label: 'Schedule',   Icon: Map },
]

export const driverNavItems: NavItem[] = [
  { to: '/driver/students',  label: 'Students',   Icon: Users },
  { to: '/driver/route-map', label: 'Route Map',  Icon: Map },
]
