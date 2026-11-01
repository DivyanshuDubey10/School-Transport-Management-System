import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Eye, EyeOff, Bus, ShieldCheck } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'

export default function Login() {
  const { login, token, user } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [errors, setErrors] = useState<{ username?: string; password?: string }>({})

  if (token && user) {
    if (user.user_type === 'admin')  return <Navigate to="/admin/dashboard" replace />
    if (user.user_type === 'parent') return <Navigate to="/parent/dashboard" replace />
    if (user.user_type === 'driver') return <Navigate to="/driver/students" replace />
  }

  const validate = () => {
    const e: { username?: string; password?: string } = {}
    if (!username.trim()) e.username = 'Username is required'
    if (!password) e.password = 'Password is required'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setError(null)
    setIsLoading(true)
    try {
      await login({ username: username.trim(), password })
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        'Invalid username or password. Please try again.'
      setError(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex-col items-center justify-center p-16 overflow-hidden">
        {/* Decorative circles */}
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl" />
        <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-accent/5 rounded-full blur-3xl" />

        {/* Grid pattern overlay */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)',
            backgroundSize: '40px 40px',
          }}
        />

        <div className="relative z-10 text-center">
          {/* Logo */}
          <div className="flex items-center justify-center mb-8">
            <div className="p-4 bg-accent/10 rounded-2xl border border-accent/20 backdrop-blur-sm">
              <Bus size={40} className="text-accent" />
            </div>
          </div>
          <h1 className="text-5xl font-bold text-white tracking-tight mb-3">
            Neo<span className="text-accent">Yatra</span>
          </h1>
          <p className="text-slate-400 text-lg mb-12">School Transport Management</p>

          {/* Feature pills */}
          <div className="flex flex-col gap-3 items-center">
            {[
              'Real-time attendance tracking',
              'Route & bus management',
              'Parent portal access',
            ].map((f) => (
              <div key={f} className="flex items-center gap-2.5 bg-white/5 border border-white/10 rounded-full px-5 py-2.5 backdrop-blur-sm">
                <ShieldCheck size={14} className="text-accent flex-shrink-0" />
                <span className="text-sm text-slate-300">{f}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom version tag */}
        <div className="absolute bottom-6 text-xs text-slate-600">NeoYatra v1.0 · © {new Date().getFullYear()}</div>
      </div>

      {/* Right panel — login form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-slate-50">
        <div className="w-full max-w-[420px]">
          {/* Mobile logo */}
          <div className="flex items-center gap-3 mb-8 lg:hidden">
            <div className="p-2 bg-accent/10 rounded-xl">
              <Bus size={22} className="text-accent" />
            </div>
            <div>
              <span className="text-xl font-bold text-slate-800 tracking-tight">
                Neo<span className="text-accent">Yatra</span>
              </span>
              <p className="text-[11px] text-slate-400">School Transport Management</p>
            </div>
          </div>

          <div className="bg-white rounded-3xl shadow-lg border border-slate-100 overflow-hidden">
            {/* Top accent bar */}
            <div className="h-1 bg-gradient-to-r from-accent via-sky-400 to-blue-500" />

            <div className="px-8 py-8">
              <h2 className="text-2xl font-bold text-slate-800 mb-1">Welcome back</h2>
              <p className="text-sm text-slate-400 mb-7">Sign in to your portal to continue</p>

              {error && (
                <div className="mb-5 flex items-start gap-3 px-4 py-3 bg-red-50 border border-red-100 rounded-xl">
                  <div className="mt-0.5 h-4 w-4 rounded-full bg-red-500/20 flex items-center justify-center flex-shrink-0">
                    <div className="h-1.5 w-1.5 rounded-full bg-red-500" />
                  </div>
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                <Input
                  label="Username"
                  type="text"
                  value={username}
                  onChange={(e) => { setUsername(e.target.value); setErrors((p) => ({ ...p, username: undefined })) }}
                  placeholder="Enter your username"
                  error={errors.username}
                  autoComplete="username"
                  autoFocus
                />
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: undefined })) }}
                  placeholder="Enter your password"
                  error={errors.password}
                  autoComplete="current-password"
                  rightIcon={
                    <button type="button" onClick={() => setShowPassword((v) => !v)} className="focus:outline-none text-slate-400 hover:text-slate-600 transition-colors" tabIndex={-1}>
                      {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                    </button>
                  }
                />
                <Button type="submit" variant="primary" size="lg" className="w-full mt-2" isLoading={isLoading}>
                  Sign In
                </Button>
              </form>
            </div>

            <div className="bg-slate-50 px-8 py-4 border-t border-slate-100 flex items-center justify-center gap-2">
              <ShieldCheck size={12} className="text-slate-400" />
              <p className="text-xs text-slate-400">Secure · Encrypted · Private</p>
            </div>
          </div>

          {/* Role hints */}
          <div className="mt-5 grid grid-cols-3 gap-2 text-center">
            {[
              { role: 'Admin', color: 'text-sky-600 bg-sky-50 border-sky-100' },
              { role: 'Parent', color: 'text-emerald-600 bg-emerald-50 border-emerald-100' },
              { role: 'Driver', color: 'text-amber-600 bg-amber-50 border-amber-100' },
            ].map(({ role, color }) => (
              <div key={role} className={`rounded-xl border px-3 py-2 text-xs font-semibold ${color}`}>
                {role} Portal
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
