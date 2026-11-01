import apiClient from './client'

export interface Waypoint {
  name: string
  lat: number
  lng: number
  type: 'school' | 'stop'
}

export interface BusTrackingData {
  bus_id: number
  bus_number: string
  driver_name: string
  route_id?: number | null
  route_name: string
  latitude: number
  longitude: number
  speed: number
  heading: number
  status: 'In Transit' | 'Completed' | 'Idle'
  next_stop: string
  last_updated: string
  waypoints: Waypoint[]
}

export interface FleetResponse {
  count: number
  buses: BusTrackingData[]
}

export interface LocationUpdatePayload {
  bus_id: number
  latitude: number
  longitude: number
  speed?: number
  heading?: number
  status?: string
  next_stop?: string
}

export async function getBusTracking(busId: number): Promise<BusTrackingData> {
  const { data } = await apiClient.get<BusTrackingData>(`/tracking/bus/${busId}`)
  return data
}

export async function getFleetTracking(): Promise<FleetResponse> {
  const { data } = await apiClient.get<FleetResponse>('/tracking/fleet')
  return data
}

export async function updateBusLocation(payload: LocationUpdatePayload): Promise<{ status: string; timestamp: string }> {
  const { data } = await apiClient.post('/tracking/update', payload)
  return data
}

export async function startTrip(busId: number): Promise<{ status: string; tracking: BusTrackingData }> {
  const { data } = await apiClient.post('/tracking/trip/start', { bus_id: busId })
  return data
}

export async function stopTrip(busId: number): Promise<{ status: string }> {
  const { data } = await apiClient.post('/tracking/trip/stop', { bus_id: busId })
  return data
}
