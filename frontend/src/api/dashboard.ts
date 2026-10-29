import apiClient from './client'

export interface DashboardStats {
  total_students: number
  active_buses: number
  designated_routes: number
  total_parents: number
}

export interface RouteOccupancy {
  route_name: string
  students: number
  capacity: number
}

export interface FeeStatus {
  paid: number
  pending: number
}

export interface DashboardData {
  stats: DashboardStats
  route_occupancy: RouteOccupancy[]
  fee_status: FeeStatus
}

export async function getDashboard(): Promise<DashboardData> {
  const { data } = await apiClient.get<DashboardData>('/dashboard')
  return data
}
