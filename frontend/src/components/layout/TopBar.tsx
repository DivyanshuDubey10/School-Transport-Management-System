import { useLocation } from 'react-router-dom'
import { LogOut, Bell } from 'lucide-react'
import { useAuth } from '../../hooks/useAuth'

interface TopBarProps {
  breadcrumb?: string
}

export function TopBar({ breadcrumb }: TopBarProps) {
  const { user, logout } = useAuth()
  const location = useLocation()

  // Auto-derive breadcrumb from path if not provided
  const label =
    breadcrumb ??
    location.pathname
      .split('/')
      .filter(Boolean)
      .map((seg) => seg.charAt(0).toUpperCase() + seg.slice(1).replace(/-/g, ' '))
      .join(' / ')

  return (
    <header className="fixed top-0 left-60 right-0 h-14 bg-white border-b border-slate-100 flex items-center justify-between px-6 z-20 shadow-sm">
      {/* Breadcrumb */}
      <div>
        <p className="text-sm font-semibold text-slate-700">{label}</p>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        <button className="p-2 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors relative">
          <Bell size={18} />
        </button>

        {/* User chip */}
        <div className="flex items-center gap-2 pl-3 border-l border-slate-100">
          <div className="h-8 w-8 rounded-full bg-accent/20 flex items-center justify-center">
            <span className="text-xs font-bold text-accent uppercase">
              {user?.name?.charAt(0) ?? '?'}
            </span>
          </div>
          <div className="hidden sm:block text-left">
            <p className="text-xs font-semibold text-slate-700 leading-tight">
              {user?.name ?? 'User'}
            </p>
            <p className="text-[10px] text-slate-400 capitalize">{user?.user_type}</p>
          </div>
        </div>

        <button
          onClick={logout}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-500 hover:text-danger hover:bg-red-50 rounded-lg transition-colors"
        >
          <LogOut size={14} />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  )
}
