type BadgeVariant = 'success' | 'danger' | 'warning' | 'info' | 'neutral'

interface BadgeProps {
  variant?: BadgeVariant
  children: React.ReactNode
  dot?: boolean
}

const variants: Record<BadgeVariant, string> = {
  success: 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200',
  danger:  'bg-red-50 text-red-700 ring-1 ring-red-200',
  warning: 'bg-amber-50 text-amber-700 ring-1 ring-amber-200',
  info:    'bg-sky-50 text-sky-700 ring-1 ring-sky-200',
  neutral: 'bg-slate-100 text-slate-600 ring-1 ring-slate-200',
}

const dotColors: Record<BadgeVariant, string> = {
  success: 'bg-emerald-500',
  danger:  'bg-red-500',
  warning: 'bg-amber-500',
  info:    'bg-sky-500',
  neutral: 'bg-slate-400',
}

export function Badge({ variant = 'neutral', children, dot = false }: BadgeProps) {
  return (
    <span
      className={[
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium',
        variants[variant],
      ].join(' ')}
    >
      {dot && (
        <span className={['w-1.5 h-1.5 rounded-full shrink-0', dotColors[variant]].join(' ')} />
      )}
      {children}
    </span>
  )
}
