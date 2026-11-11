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
  trip_id?: number | null
  latitude: number
  longitude: number
  speed: number
  heading: number
  status: 'In Transit' | 'Completed' | 'Idle'
  next_stop: string
  last_updated: string
  accuracy_metres?: number | null
  gps_quality?: 'high' | 'medium' | 'degraded' | 'unreliable' | 'no_fix' | string
  is_stale: boolean
  has_coordinates: boolean
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
  accuracy_metres?: number
}

export interface TelemetryEventPayload {
  client_event_id: string
  trip_id: number
  bus_id: number
  trip_sequence_number: number
  latitude: number
  longitude: number
  altitude_m?: number | null
  accuracy_metres?: number | null
  speed_kmh?: number | null
  bearing_degrees?: number | null
  recorded_at: string
  next_stop?: string | null
}

export interface TripStartResponse {
  status: string
  trip_id: number
  bus_id: number
  started_at: string
  tracking: BusTrackingData
}

export interface TripSummary {
  trip_id: number
  total_events: number
  distance_km: number
  ended_at: string
}

export interface TripStopResponse {
  status: string
  bus_id: number
  trip_id: number
  summary: TripSummary
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

export async function sendTelemetryEvent(payload: TelemetryEventPayload): Promise<{
  status: string
  event_id: number
  accepted: boolean
  out_of_order: boolean
  note: string
}> {
  const { data } = await apiClient.post('/tracking/event', payload)
  return data
}

export async function startTrip(busId: number): Promise<TripStartResponse> {
  const { data } = await apiClient.post<TripStartResponse>('/tracking/trip/start', { bus_id: busId })
  return data
}

export async function stopTrip(busId: number): Promise<TripStopResponse> {
  const { data } = await apiClient.post<TripStopResponse>('/tracking/trip/stop', { bus_id: busId })
  return data
}

export async function getTripEvents(
  tripId: number,
  limit: number = 500,
  offset: number = 0
): Promise<{ trip_id: number; count: number; events: any[] }> {
  const { data } = await apiClient.get(`/tracking/trip/${tripId}/events`, {
    params: { limit, offset }
  })
  return data
}
