import apiClient from './client'

export interface Student {
  id: number
  student_id: number
  name: string
  student_name: string
  class_name: string
  student_class: string
  parent_id: number
  parent_phone?: string
  phone?: string
  address?: string
  route_id: number | null
  route_name?: string | null
  bus_id?: number | null
  fee_paid: number
  fee_balance: number
  transport_status: string
}

export interface StudentPayload {
  name?: string
  student_name?: string
  class_name?: string
  student_class?: string
  parent_id: number
  route_id: number | null
  fee_paid: number
  fee_balance: number
}

export async function getStudents(search: string = ''): Promise<Student[]> {
  const { data } = await apiClient.get<Student[]>('/students', {
    params: search ? { search } : {},
  })
  return data
}

export async function createStudent(payload: StudentPayload): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>('/students', payload)
  return data
}

export async function updateStudent(id: number, payload: Partial<StudentPayload>): Promise<{ message: string }> {
  const { data } = await apiClient.put<{ message: string }>(`/students/${id}`, payload)
  return data
}

export async function deleteStudent(id: number): Promise<void> {
  await apiClient.delete(`/students/${id}`)
}
