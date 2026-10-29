import apiClient from './client'

export interface TransportRequest {
  id: number
  request_id: number
  student_id: number
  student_name: string
  student_class: string
  class_name: string
  parent_id: number
  parent_name: string
  requested_pickup_point: string
  current_pickup_point?: string
  status: string
  request_status: string
}

export interface CreateRequestPayload {
  student_id: number
  requested_pickup_point: string
}

export interface ApproveRequestPayload {
  new_route_id?: number
  new_pickup_point?: string
}

export async function getRequests(): Promise<TransportRequest[]> {
  const { data } = await apiClient.get<TransportRequest[]>('/requests')
  return data
}

export async function createRequest(payload: CreateRequestPayload): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>('/requests', payload)
  return data
}

export async function approveRequest(id: number, payload?: ApproveRequestPayload): Promise<{ message: string }> {
  const { data } = await apiClient.put<{ message: string }>(`/requests/${id}/approve`, payload || {})
  return data
}

export async function rejectRequest(id: number): Promise<{ message: string }> {
  const { data } = await apiClient.put<{ message: string }>(`/requests/${id}/reject`)
  return data
}
