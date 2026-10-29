import apiClient from './client'

export interface AttendanceRecord {
  date: string
  student_name: string
  student_class: string
  bus_number: string
  attendance_status: string
  status?: string
}

export interface StudentForDriver {
  student_id: number
  student_name: string
  student_class: string
  pickup_point: string | null
  phone: string | null
  parent_name: string | null
}

export interface StudentAttendanceHistory {
  date: string
  attendance_status: string
}

export interface MarkAttendanceRecord {
  student_id: number
  status: string
}

export interface MarkAttendancePayload {
  date: string
  records: MarkAttendanceRecord[]
}

export async function getAttendance(search: string = ''): Promise<AttendanceRecord[]> {
  const { data } = await apiClient.get<AttendanceRecord[]>('/attendance', {
    params: search ? { search } : {},
  })
  return data
}

export async function getDriverStudents(): Promise<StudentForDriver[]> {
  const { data } = await apiClient.get<StudentForDriver[]>('/attendance/my-students')
  return data
}

export async function markAttendance(payload: MarkAttendancePayload): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>('/attendance/mark', payload)
  return data
}

export async function getStudentAttendance(studentId: number): Promise<StudentAttendanceHistory[]> {
  const { data } = await apiClient.get<StudentAttendanceHistory[]>(`/attendance/student/${studentId}`)
  return data
}
