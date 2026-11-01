import axios from 'axios'

// Normalize URL: handles trailing slashes and missing /api/v1 automatically
let rawUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').trim()
rawUrl = rawUrl.replace(/\/+$/, '')
if (!rawUrl.endsWith('/api/v1')) {
  rawUrl = `${rawUrl}/api/v1`
}

const apiClient = axios.create({
  baseURL: rawUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor — attach JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('neoyatra_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// Response interceptor — handle 401 without breaking login attempts
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const isLoginEndpoint = error.config?.url?.includes('/auth/login')
    if (error.response?.status === 401 && !isLoginEndpoint) {
      localStorage.removeItem('neoyatra_token')
      localStorage.removeItem('neoyatra_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  },
)

export default apiClient
