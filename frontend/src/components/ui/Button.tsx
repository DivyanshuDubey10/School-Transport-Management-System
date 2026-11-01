import React from 'react'

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost' | 'success' | 'outline'
type Size = 'sm' | 'md' | 'lg'

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  isLoading?: boolean
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-gradient-to-b from-sky-400 to-sky-500 text-white shadow-sm hover:from-sky-300 hover:to-sky-400 active:scale-[0.98] focus:ring-2 focus:ring-sky-500/40',
  secondary:
    'bg-white text-slate-700 border border-slate-200 hover:bg-slate-50 active:scale-[0.98] focus:ring-2 focus:ring-slate-200 shadow-sm',
  danger:
    'bg-gradient-to-b from-rose-500 to-rose-600 text-white shadow-sm hover:from-rose-400 hover:to-rose-500 active:scale-[0.98] focus:ring-2 focus:ring-rose-500/40',
  ghost:
    'bg-transparent text-slate-600 hover:bg-slate-100 active:scale-[0.98] focus:ring-2 focus:ring-slate-200',
  success:
    'bg-gradient-to-b from-emerald-500 to-emerald-600 text-white shadow-sm hover:from-emerald-400 hover:to-emerald-500 active:scale-[0.98] focus:ring-2 focus:ring-emerald-500/40',
  outline:
    'border border-slate-200 text-slate-700 bg-white hover:bg-slate-50 active:scale-[0.98] focus:ring-2 focus:ring-slate-200',
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-xs rounded-lg gap-1.5',
  md: 'px-4 py-2 text-sm rounded-xl gap-2',
  lg: 'px-5 py-2.5 text-sm rounded-xl gap-2',
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  loading = false,
  leftIcon,
  rightIcon,
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
        'inline-flex items-center justify-center font-medium transition-all duration-150 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100',
        variantClasses[variant],
        sizeClasses[size],
        className,
      ].join(' ')}
    >
      {isBusy ? (
        <svg
          className="animate-spin h-4 w-4 shrink-0"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
        </svg>
      ) : leftIcon ? (
        <span className="shrink-0">{leftIcon}</span>
      ) : null}
      {children}
      {!isBusy && rightIcon && <span className="shrink-0">{rightIcon}</span>}
    </button>
  )
}
