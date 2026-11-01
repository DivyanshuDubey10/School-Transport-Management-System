import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
  hover?: boolean
}

const paddingClass = {
  none: '',
  sm: 'p-4',
  md: 'p-5',
  lg: 'p-6',
}

export function Card({ children, className = '', padding = 'md', hover = false }: CardProps) {
  return (
    <div
      className={[
        'bg-white rounded-2xl border border-slate-100 shadow-card',
        hover && 'transition-all duration-200 hover:shadow-card-hover hover:-translate-y-0.5 cursor-pointer',
        paddingClass[padding],
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  )
}

interface KpiCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  iconBg?: string
  trend?: string
  trendUp?: boolean
  subtitle?: string
}

export function KpiCard({ title, value, icon, iconBg = 'bg-sky-50', trend, trendUp, subtitle }: KpiCardProps) {
  return (
    <Card className="relative overflow-hidden group transition-all duration-200 hover:shadow-card-hover hover:-translate-y-0.5">
      <div
        className="absolute top-0 right-0 w-24 h-24 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-current pointer-events-none"
        style={{ color: 'rgba(56,189,248,0.06)' }}
      />
      <div className="flex items-start gap-4">
        <div className={['p-3 rounded-xl flex-shrink-0', iconBg].join(' ')}>{icon}</div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{title}</p>
          <p className="text-3xl font-bold text-slate-800 mt-1 tracking-tight">{value}</p>
          {trend && (
            <p
              className={[
                'text-xs font-medium mt-1 flex items-center gap-1',
                trendUp ? 'text-emerald-500' : 'text-slate-400',
              ].join(' ')}
            >
              {trendUp ? '↑' : '→'} {trend}
            </p>
          )}
          {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
      </div>
    </Card>
  )
}
