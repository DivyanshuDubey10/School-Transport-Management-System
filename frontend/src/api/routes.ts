import apiClient from './client'

export interface Route {
  id: number
  route_id: number
  route_name: string
}

export interface RoutePayload {
  route_name: string
}

export async function getRoutes(search: string = ''): Promise<Route[]> {
  const { data } = await apiClient.get<Route[]>('/routes', {
    params: search ? { search } : {},
  })
  return data
}

export async function createRoute(payload: RoutePayload): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>('/routes', payload)
  return data
}

export async function updateRoute(id: number, payload: RoutePayload): Promise<{ message: string }> {
  const { data } = await apiClient.put<{ message: string }>(`/routes/${id}`, payload)
  return data
}

export async function deleteRoute(id: number): Promise<void> {
  await apiClient.delete(`/routes/${id}`)
}
