import apiClient from './client'

export interface LoginPayload {
  username: string
  password: string
  school_code?: string
  user_type?: 'admin' | 'parent' | 'driver'
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user_type: 'admin' | 'parent' | 'driver'
  user_id: number
  name: string
  school_id?: number
}

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/auth/login', payload)
  return data
}
