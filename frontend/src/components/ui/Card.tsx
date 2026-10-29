import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: 'none' | 'sm' | 'md' | 'lg'
}

const paddingClass = {
  none: '',
  sm: 'p-4',
  md: 'p-5',
  lg: 'p-6',
}

export function Card({ children, className = '', padding = 'md' }: CardProps) {
  return (
    <div
      className={[
        'bg-white rounded-2xl shadow-sm border border-slate-100',
        paddingClass[padding],
        className,
      ].join(' ')}
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
}

export function KpiCard({ title, value, icon, iconBg = 'bg-sky-50', trend, trendUp }: KpiCardProps) {
  return (
    <Card className="flex items-center gap-4">
      <div className={['p-3 rounded-xl', iconBg].join(' ')}>{icon}</div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">{title}</p>
        <p className="text-2xl font-bold text-slate-800 mt-0.5">{value}</p>
        {trend && (
          <p className={['text-xs mt-1', trendUp ? 'text-emerald-600' : 'text-red-500'].join(' ')}>
            {trend}
          </p>
        )}
      </div>
    </Card>
  )
}
