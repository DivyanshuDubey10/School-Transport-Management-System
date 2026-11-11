import React, { createContext, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { login as apiLogin, type LoginPayload } from '../api/auth'

export interface AuthUser {
  user_id: number
  user_type: 'admin' | 'parent' | 'driver'
  name: string
  bus_id?: number
  parent_id?: number
  school_id?: number
}

export interface AuthContextValue {
  user: AuthUser | null
  token: string | null
  login: (payload: LoginPayload) => Promise<void>
  logout: () => void
  isLoading: boolean
}

export const AuthContext = createContext<AuthContextValue | null>(null)

const TOKEN_KEY = 'neoyatra_token'
const USER_KEY = 'neoyatra_user'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  // Rehydrate from localStorage on mount
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_KEY)
    const storedUser = localStorage.getItem(USER_KEY)
    if (storedToken && storedUser) {
      try {
        setToken(storedToken)
        setUser(JSON.parse(storedUser) as AuthUser)
      } catch {
        localStorage.removeItem(TOKEN_KEY)
        localStorage.removeItem(USER_KEY)
      }
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(
    async (payload: LoginPayload) => {
      const response = await apiLogin(payload)
      const { access_token, user_type, user_id, name, school_id } = response

      const authUser: AuthUser = {
        user_id,
        user_type,
        name,
        school_id,
        bus_id: user_type === 'driver' ? user_id : undefined,
        parent_id: user_type === 'parent' ? user_id : undefined,
      }

      localStorage.setItem(TOKEN_KEY, access_token)
      localStorage.setItem(USER_KEY, JSON.stringify(authUser))

      setToken(access_token)
      setUser(authUser)

      // Redirect based on role
      if (user_type === 'admin') navigate('/admin/dashboard')
      else if (user_type === 'parent') navigate('/parent/dashboard')
      else if (user_type === 'driver') navigate('/driver/students')
    },
    [navigate],
  )

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    setToken(null)
    setUser(null)
    navigate('/login')
  }, [navigate])

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}
