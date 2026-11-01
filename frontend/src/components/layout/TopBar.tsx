import { useLocation } from 'react-router-dom'
import { LogOut, Bell, ChevronRight } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'

interface TopBarProps {
  breadcrumb?: string
}

const roleColors: Record<string, string> = {
  admin: 'bg-sky-500/10 text-sky-600 border-sky-200',
  parent: 'bg-emerald-500/10 text-emerald-600 border-emerald-200',
  driver: 'bg-amber-500/10 text-amber-600 border-amber-200',
}

export function TopBar({ breadcrumb }: TopBarProps) {
  const { user, logout } = useAuth()
  const location = useLocation()

  const segments = location.pathname.split('/').filter(Boolean)
  const label =
    breadcrumb ??
    segments.map((s) => s.charAt(0).toUpperCase() + s.slice(1).replace(/-/g, ' ')).join(' / ')

  const initials = (user?.name ?? 'U')
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()
  const roleBadge = roleColors[user?.user_type ?? ''] ?? 'bg-slate-100 text-slate-600 border-slate-200'

  return (
    <header className="fixed top-0 left-60 right-0 h-14 bg-white/80 backdrop-blur-md border-b border-slate-100 flex items-center justify-between px-6 z-20 shadow-sm">
      {/* Breadcrumb */}
      <div className="flex items-center gap-1.5 text-sm">
        {segments.map((seg, i) => {
          const isLast = i === segments.length - 1
          return (
            <span key={i} className="flex items-center gap-1.5">
              {i > 0 && <ChevronRight size={12} className="text-slate-300" />}
              <span className={isLast ? 'font-semibold text-slate-800' : 'text-slate-400 capitalize'}>
                {seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' ')}
              </span>
            </span>
          )
        })}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-2">
        {/* Bell */}
        <button className="p-2 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors">
          <Bell size={17} />
        </button>

        <div className="w-px h-6 bg-slate-100 mx-1" />

        {/* Avatar + name */}
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-accent to-sky-600 flex items-center justify-center shadow-sm">
            <span className="text-xs font-bold text-white">{initials}</span>
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-slate-800 leading-tight">{user?.name ?? 'User'}</p>
            <span className={`inline-block text-[10px] font-semibold px-1.5 py-0.5 rounded-full border capitalize ${roleBadge}`}>
              {user?.user_type}
            </span>
          </div>
        </div>

        <div className="w-px h-6 bg-slate-100 mx-1" />

        {/* Logout */}
        <button
          onClick={logout}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-danger hover:bg-red-50 rounded-xl transition-colors"
        >
          <LogOut size={14} />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  )
}
