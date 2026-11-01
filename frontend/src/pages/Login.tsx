import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Eye, EyeOff, Bus, ShieldCheck, UserCheck } from 'lucide-react'
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

  const fillDemoAccount = (u: string, p: string) => {
    setUsername(u)
    setPassword(p)
    setError(null)
    setErrors({})
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setError(null)
    setIsLoading(true)
    try {
      await login({ username: username.trim(), password: password.trim() })
    } catch (err: unknown) {
      const resp = (err as { response?: { status?: number; data?: { detail?: string } } })?.response
      let msg = resp?.data?.detail
      if (!msg) {
        if (!resp) {
          msg = 'Unable to connect to backend. Render free tier takes ~30s to wake up on first load — please wait a moment and click Sign In again.'
        } else if (resp.status === 401) {
          msg = 'Invalid username or password. Click one of the demo buttons below to auto-fill valid credentials.'
        } else {
          msg = `Server status ${resp.status}. Please try again.`
        }
      }
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
              'Real-time bus tracking with Leaflet',
              'Attendance logging & route optimization',
              'Parent & driver multi-role portal',
            ].map((f) => (
              <div key={f} className="flex items-center gap-2.5 bg-white/5 border border-white/10 rounded-full px-5 py-2.5 backdrop-blur-sm">
                <ShieldCheck size={14} className="text-accent flex-shrink-0" />
                <span className="text-sm text-slate-300">{f}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom version tag */}
        <div className="absolute bottom-6 text-xs text-slate-600">NeoYatra v1.0 · Semester Portfolio Project</div>
      </div>

      {/* Right panel — login form */}
      <div className="flex-1 flex items-center justify-center p-6 bg-slate-50">
        <div className="w-full max-w-[440px]">
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
                  <p className="text-sm text-red-600 leading-snug">{error}</p>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-4" noValidate>
                <Input
                  label="Username"
                  type="text"
                  value={username}
                  onChange={(e) => { setUsername(e.target.value); setErrors((p) => ({ ...p, username: undefined })) }}
                  placeholder="e.g. admin or parent"
                  error={errors.username}
                  autoComplete="username"
                  autoFocus
                />
                <Input
                  label="Password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setErrors((p) => ({ ...p, password: undefined })) }}
                  placeholder="Enter password"
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

            <div className="bg-slate-50 px-8 py-3.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
              <span className="flex items-center gap-1.5">
                <ShieldCheck size={14} className="text-emerald-500" />
                Live Demo Environment
              </span>
              <span className="font-mono text-[11px] text-slate-400">PostgreSQL + FastAPI</span>
            </div>
          </div>

          {/* Quick Demo Credentials Autofill */}
          <div className="mt-5 p-4 bg-white rounded-2xl border border-slate-200/80 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold text-slate-600 uppercase tracking-wider flex items-center gap-1.5">
                <UserCheck size={14} className="text-sky-500" />
                Quick Demo Login
              </span>
              <span className="text-[11px] text-sky-600 font-medium">Click to fill</span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-center">
              <button
                type="button"
                onClick={() => fillDemoAccount('admin', 'admin123')}
                className={`group rounded-xl border p-2.5 transition-all text-left ${
                  username === 'admin'
                    ? 'border-sky-500 bg-sky-50 shadow-sm'
                    : 'border-slate-200 hover:border-sky-300 hover:bg-sky-50/50'
                }`}
              >
                <div className="text-xs font-bold text-sky-700 flex items-center justify-between">
                  Admin
                  <span className="w-1.5 h-1.5 rounded-full bg-sky-500" />
                </div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">admin</div>
                <div className="text-[10px] text-slate-400 font-mono">admin123</div>
              </button>

              <button
                type="button"
                onClick={() => fillDemoAccount('parent', 'parent123')}
                className={`group rounded-xl border p-2.5 transition-all text-left ${
                  username === 'parent'
                    ? 'border-emerald-500 bg-emerald-50 shadow-sm'
                    : 'border-slate-200 hover:border-emerald-300 hover:bg-emerald-50/50'
                }`}
              >
                <div className="text-xs font-bold text-emerald-700 flex items-center justify-between">
                  Parent
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                </div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">parent</div>
                <div className="text-[10px] text-slate-400 font-mono">parent123</div>
              </button>

              <button
                type="button"
                onClick={() => fillDemoAccount('driver', 'driver123')}
                className={`group rounded-xl border p-2.5 transition-all text-left ${
                  username === 'driver'
                    ? 'border-amber-500 bg-amber-50 shadow-sm'
                    : 'border-slate-200 hover:border-amber-300 hover:bg-amber-50/50'
                }`}
              >
                <div className="text-xs font-bold text-amber-700 flex items-center justify-between">
                  Driver
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                </div>
                <div className="text-[10px] text-slate-500 font-mono mt-0.5">driver</div>
                <div className="text-[10px] text-slate-400 font-mono">driver123</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
