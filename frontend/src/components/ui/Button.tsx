import React from 'react'

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'success'
type Size = 'sm' | 'md' | 'lg'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  isLoading?: boolean
  loading?: boolean
  leftIcon?: React.ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-sky-500 text-white hover:bg-sky-400 focus:ring-sky-500/40 shadow-sm',
  secondary:
    'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 focus:ring-slate-200/60 shadow-sm',
  danger:
    'bg-rose-500 text-white hover:bg-rose-600 focus:ring-rose-500/40 shadow-sm',
  ghost:
    'bg-transparent text-slate-600 hover:bg-slate-100 focus:ring-slate-200/60',
  success:
    'bg-emerald-500 text-white hover:bg-emerald-600 focus:ring-emerald-500/40 shadow-sm',
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs',
  md: 'px-4 py-2 text-sm',
  lg: 'px-5 py-2.5 text-base',
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  loading = false,
  leftIcon,
  children,
  className = '',
  disabled,
  ...rest
}: ButtonProps) {
  const isBusy = isLoading || loading

  return (
    <button
      {...rest}
      disabled={disabled || isBusy}
      className={[
        'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 disabled:opacity-50 disabled:cursor-not-allowed',
        variantClasses[variant],
        sizeClasses[size],
        className,
      ].join(' ')}
    >
      {isBusy ? (
        <svg
          className="animate-spin h-4 w-4"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8v8H4z"
          />
        </svg>
      ) : leftIcon ? (
        <span className="shrink-0">{leftIcon}</span>
      ) : null}
      {children}
    </button>
  )
}
