import apiClient from './client'

export interface Parent {
  id: number
  parent_id: number
  name: string
  parent_name: string
  phone: string
  address: string
  pickup_point: string
  username: string
}

export interface ParentPayload {
  name?: string
  parent_name?: string
  phone: string
  address: string
  pickup_point: string
  username: string
  password?: string
}

export interface Child {
  id: number
  student_id: number
  name: string
  student_name: string
  class_name: string
  student_class: string
  fee_paid: number
  fee_balance: number
  bus_number: string | null
  driver_name: string | null
  driver_phone: string | null
  route_name: string | null
  pickup_point: string | null
  bus_id?: number | null
}

export async function getParents(search: string = ''): Promise<Parent[]> {
  const { data } = await apiClient.get<Parent[]>('/parents', {
    params: search ? { search } : {},
  })
  return data
}

export async function getMyChildren(): Promise<Child[]> {
  const { data } = await apiClient.get<Child[]>('/parents/my-children')
  return data
}

export async function createParent(payload: ParentPayload): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>('/parents', payload)
  return data
}

export async function updateParent(id: number, payload: Partial<ParentPayload>): Promise<{ message: string }> {
  const { data } = await apiClient.put<{ message: string }>(`/parents/${id}`, payload)
  return data
}

export async function deleteParent(id: number): Promise<void> {
  await apiClient.delete(`/parents/${id}`)
}
