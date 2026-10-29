import apiClient from './client'

export interface Bus {
  id: number
  bus_id: number
  bus_number: string
  driver_name: string
  driver_phone: string
  capacity: number
  route_id: number | null
  route_name: string | null
  driver_username?: string | null
  username?: string | null
}

export interface BusPayload {
  bus_number: string
  driver_name: string
  driver_phone: string
  capacity: number
  route_id: number | null
  driver_username?: string
  username?: string
  driver_password?: string
  password?: string
}

export async function getBuses(search: string = ''): Promise<Bus[]> {
  const { data } = await apiClient.get<Bus[]>('/buses', {
    params: search ? { search } : {},
  })
  return data
}

export async function createBus(payload: BusPayload): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>('/buses', payload)
  return data
}

export async function updateBus(id: number, payload: Partial<BusPayload>): Promise<{ message: string }> {
  const { data } = await apiClient.put<{ message: string }>(`/buses/${id}`, payload)
  return data
}

export async function deleteBus(id: number): Promise<void> {
  await apiClient.delete(`/buses/${id}`)
}
