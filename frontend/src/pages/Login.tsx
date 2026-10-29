import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Eye, EyeOff, Bus } from 'lucide-react'
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

  // Already logged in
  if (token && user) {
    if (user.user_type === 'admin') return <Navigate to="/admin/dashboard" replace />
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-[480px]">
        {/* Card */}
        <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
          {/* Top accent bar */}
          <div className="h-1.5 bg-gradient-to-r from-accent via-sky-400 to-blue-500" />

          <div className="px-10 py-10">
            {/* Brand */}
            <div className="flex items-center justify-center mb-8">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-accent/10 rounded-xl">
                  <Bus size={28} className="text-accent" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
                    Neo<span className="text-accent">Yatra</span>
                  </h1>
                  <p className="text-xs text-slate-400 font-medium">School Transport Management</p>
                </div>
              </div>
            </div>

            <h2 className="text-lg font-semibold text-slate-700 mb-1">Welcome back</h2>
            <p className="text-sm text-slate-400 mb-7">Sign in to your account to continue</p>

            {/* Error alert */}
            {error && (
              <div className="mb-5 px-4 py-3 bg-red-50 border border-red-100 rounded-xl text-sm text-red-600">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              <Input
                label="Username"
                type="text"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value)
                  setErrors((p) => ({ ...p, username: undefined }))
                }}
                placeholder="Enter your username"
                error={errors.username}
                autoComplete="username"
                autoFocus
              />

              <Input
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  setErrors((p) => ({ ...p, password: undefined }))
                }}
                placeholder="Enter your password"
                error={errors.password}
                autoComplete="current-password"
                rightIcon={
                  <button
                    type="button"
                    onClick={() => setShowPassword((v) => !v)}
                    className="focus:outline-none"
                    tabIndex={-1}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                }
              />

              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full mt-2"
                isLoading={isLoading}
              >
                Sign In
              </Button>
            </form>
          </div>

          {/* Footer */}
          <div className="bg-slate-50 px-10 py-4 border-t border-slate-100 text-center">
            <p className="text-xs text-slate-400">
              Secure portal · All rights reserved © {new Date().getFullYear()} NeoYatra
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
