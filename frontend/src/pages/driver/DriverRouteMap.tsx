import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { MapPin, Users, Phone, Bus, Play, Square, Navigation, Radio, AlertTriangle, Activity } from 'lucide-react'
import { getDriverStudents, type StudentForDriver } from '../../api/attendance'
import {
  getBusTracking,
  updateBusLocation,
  sendTelemetryEvent,
  startTrip,
  stopTrip,
  type BusTrackingData
} from '../../api/tracking'
import { LiveMap } from '../../components/ui/LiveMap'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'
import { useToast } from '../../components/ui/Toast'
import { useAuth } from '../../hooks/useAuth'

interface StopGroup {
  stopName: string
  students: StudentForDriver[]
}

export default function DriverRouteMap() {
  const { user } = useAuth()
  const { showToast } = useToast()
  // Validated driver bus allocation
  const busId = user?.bus_id || user?.user_id || 1

  const [isTripActive, setIsTripActive] = useState(false)
  const [activeTripId, setActiveTripId] = useState<number | null>(null)
  const [useSimulator, setUseSimulator] = useState(false)
  const [gpsError, setGpsError] = useState<string | null>(null)
  const [tripSummary, setTripSummary] = useState<{ distance_km: number; total_events: number } | null>(null)

  const simStepRef = useRef(0)
  const watchIdRef = useRef<number | null>(null)
  const sequenceNumberRef = useRef(1)

  const isSimulatorAllowed = import.meta.env.VITE_ENABLE_SIMULATOR === 'true' || import.meta.env.DEV

  // 1. Fetch Route Students
  const { data: students = [], isLoading: loadingStudents } = useQuery({
    queryKey: ['driver-students'],
    queryFn: getDriverStudents,
  })

  // 2. Fetch Live Tracking State with 3-second auto-refresh
  const { data: tracking, refetch: refetchTracking } = useQuery({
    queryKey: ['driver-tracking', busId],
    queryFn: () => getBusTracking(busId),
    refetchInterval: 3000,
  })

  // Sync active trip state with backend state
  useEffect(() => {
    if (tracking) {
      if (tracking.status === 'In Transit' && tracking.trip_id) {
        setIsTripActive(true)
        setActiveTripId(tracking.trip_id)
      } else if (tracking.status === 'Idle' || tracking.status === 'Completed') {
        if (isTripActive && !activeTripId) {
          // Keep local active state until user stops or mutation finishes
        } else {
          setIsTripActive(false)
          setActiveTripId(null)
        }
      }
    }
  }, [tracking?.status, tracking?.trip_id])

  const startMut = useMutation({
    mutationFn: () => startTrip(busId),
    onSuccess: (data) => {
      setIsTripActive(true)
      setActiveTripId(data.trip_id)
      sequenceNumberRef.current = 1
      setGpsError(null)
      setTripSummary(null)
      showToast('Trip started! Live telemetry broadcasting is active.', 'success')
      refetchTracking()
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'Failed to start trip'
      showToast(msg, 'error')
    },
  })

  const stopMut = useMutation({
    mutationFn: () => stopTrip(busId),
    onSuccess: (data) => {
      setIsTripActive(false)
      setActiveTripId(null)
      if (data?.summary) {
        setTripSummary({
          distance_km: data.summary.distance_km || 0,
          total_events: data.summary.total_events || 0
        })
        showToast(
          `Trip ended successfully! Distance: ${data.summary.distance_km?.toFixed(2) || 0} km (${data.summary.total_events} events).`,
          'info'
        )
      } else {
        showToast('Trip ended. Broadcasting stopped.', 'info')
      }
      refetchTracking()
    },
    onError: (err: any) => {
      const msg = err?.response?.data?.detail || 'Failed to stop trip'
      showToast(msg, 'error')
    },
  })

  // Telemetry loop: device GPS watch or simulator
  useEffect(() => {
    if (!isTripActive) {
      if (watchIdRef.current !== null) {
        navigator.geolocation.clearWatch(watchIdRef.current)
        watchIdRef.current = null
      }
      return
    }

    if (useSimulator) {
      // Smoothly advance through route waypoints
      const waypoints = tracking?.waypoints ?? []
      if (waypoints.length === 0) return

      const interval = setInterval(() => {
        simStepRef.current = (simStepRef.current + 1) % (waypoints.length * 10)
        const totalSegments = waypoints.length - 1
        const segmentProgress = (simStepRef.current / (waypoints.length * 10)) * totalSegments
        const currIndex = Math.min(Math.floor(segmentProgress), totalSegments - 1)
        const nextIndex = currIndex + 1
        const t = segmentProgress - currIndex

        const p1 = waypoints[currIndex]
        const p2 = waypoints[nextIndex]

        const currentLat = p1.lat + (p2.lat - p1.lat) * t
        const currentLng = p1.lng + (p2.lng - p1.lng) * t
        const speed = 28 + Math.sin(simStepRef.current) * 6
        const seq = sequenceNumberRef.current++

        if (activeTripId) {
          sendTelemetryEvent({
            client_event_id: crypto.randomUUID(),
            trip_id: activeTripId,
            bus_id: busId,
            trip_sequence_number: seq,
            latitude: currentLat,
            longitude: currentLng,
            speed_kmh: speed,
            bearing_degrees: 45,
            accuracy_metres: 8.5,
            recorded_at: new Date().toISOString(),
            next_stop: p2.name,
          }).catch(() => {})
        } else {
          updateBusLocation({
            bus_id: busId,
            latitude: currentLat,
            longitude: currentLng,
            speed,
            heading: 45,
            status: 'In Transit',
            next_stop: p2.name,
            accuracy_metres: 8.5,
          }).catch(() => {})
        }
      }, 3000)

      return () => clearInterval(interval)
    } else {
      // Device GPS Geolocation
      if ('geolocation' in navigator) {
        watchIdRef.current = navigator.geolocation.watchPosition(
          (pos) => {
            setGpsError(null)
            const speedKmh = pos.coords.speed ? pos.coords.speed * 3.6 : 0
            const seq = sequenceNumberRef.current++

            if (activeTripId) {
              sendTelemetryEvent({
                client_event_id: crypto.randomUUID(),
                trip_id: activeTripId,
                bus_id: busId,
                trip_sequence_number: seq,
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude,
                altitude_m: pos.coords.altitude || null,
                accuracy_metres: pos.coords.accuracy || null,
                speed_kmh: speedKmh,
                bearing_degrees: pos.coords.heading || 0,
                recorded_at: new Date(pos.timestamp).toISOString(),
                next_stop: tracking?.next_stop || null,
              }).catch((err) => {
                console.warn('Telemetry event transmission failed:', err)
              })
            } else {
              updateBusLocation({
                bus_id: busId,
                latitude: pos.coords.latitude,
                longitude: pos.coords.longitude,
                speed: speedKmh,
                heading: pos.coords.heading || 0,
                status: 'In Transit',
                accuracy_metres: pos.coords.accuracy || undefined,
              }).catch(() => {})
            }
          },
          (err) => {
            const errorMsg = `GPS signal error (${err.message}). Verify location permissions in your browser.`
            setGpsError(errorMsg)
            showToast(errorMsg, 'error')
          },
          { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
        )
      } else {
        setGpsError('Geolocation API is not supported on this device/browser.')
      }
    }
  }, [isTripActive, useSimulator, tracking?.waypoints, busId, activeTripId])

  // Group students by pickup point
  const stopGroups: StopGroup[] = []
  const groupMap: Record<string, StudentForDriver[]> = {}

  for (const s of students) {
    const stop = s.pickup_point || 'General Campus Stop'
    if (!groupMap[stop]) groupMap[stop] = []
    groupMap[stop].push(s)
  }

  for (const [stopName, list] of Object.entries(groupMap)) {
    stopGroups.push({ stopName, students: list })
  }

  const mapBuses: BusTrackingData[] = tracking ? [tracking] : []
  const currentCenter: [number, number] = tracking && tracking.has_coordinates
    ? [tracking.latitude, tracking.longitude]
    : [28.6139, 77.209]

  return (
    <div className="space-y-6 page-enter">
      {/* Header Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-gradient-to-r from-slate-900 to-slate-800 p-6 rounded-2xl text-white shadow-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs uppercase tracking-wider text-amber-400 font-bold">
              Driver Operations
            </span>
            <span className="text-slate-500">•</span>
            <Badge
              variant={isTripActive ? 'success' : 'neutral'}
              dot
              className={isTripActive ? 'bg-emerald-500/20 text-emerald-300 ring-emerald-500/40' : 'bg-slate-700 text-slate-300'}
            >
              {isTripActive ? 'Live Telemetry Active' : 'Trip Idle'}
            </Badge>

            {tracking?.is_stale && isTripActive && (
              <Badge variant="warning" className="bg-amber-500/20 text-amber-300 ring-amber-500/40">
                Stale GPS (&gt;30s)
              </Badge>
            )}

            {tracking?.accuracy_metres != null && (
              <Badge variant="neutral" className="bg-sky-950/60 text-sky-300 border border-sky-700/50">
                ±{Math.round(tracking.accuracy_metres)}m ({tracking.gps_quality || 'GPS'})
              </Badge>
            )}
          </div>
          <h1 className="text-2xl font-bold tracking-tight">
            {tracking?.bus_number || 'Route Bus'} — Driver Console
          </h1>
          <p className="text-xs text-slate-300 mt-1">
            Route: <b className="text-white">{tracking?.route_name || 'Assigned Route'}</b> • Driver: {user?.name}
            {activeTripId ? ` • Trip #${activeTripId}` : ''}
          </p>
        </div>

        {/* Live Trip Controls */}
        <div className="flex flex-wrap items-center gap-3">
          {isSimulatorAllowed && (
            <label className="flex items-center gap-2 text-xs font-semibold bg-white/10 px-3 py-2 rounded-xl cursor-pointer hover:bg-white/15 transition-colors">
              <input
                type="checkbox"
                checked={useSimulator}
                onChange={(e) => setUseSimulator(e.target.checked)}
                className="rounded text-sky-500 focus:ring-0"
              />
              <Radio size={14} className={useSimulator ? 'text-sky-400' : 'text-slate-400'} />
              <span>Simulate Motion (Dev)</span>
            </label>
          )}

          {!isTripActive ? (
            <Button
              onClick={() => startMut.mutate()}
              isLoading={startMut.isPending}
              variant="success"
              leftIcon={<Play size={16} />}
              className="px-5 py-2.5 font-bold"
            >
              Start Trip
            </Button>
          ) : (
            <Button
              onClick={() => stopMut.mutate()}
              isLoading={stopMut.isPending}
              variant="danger"
              leftIcon={<Square size={16} />}
              className="px-5 py-2.5 font-bold"
            >
              End Trip
            </Button>
          )}
        </div>
      </div>

      {/* GPS Error Alert */}
      {gpsError && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl flex items-start gap-3 text-rose-800 text-sm">
          <AlertTriangle className="text-rose-600 shrink-0 mt-0.5" size={18} />
          <div className="flex-1">
            <p className="font-semibold">GPS Tracking Blocked</p>
            <p className="text-xs text-rose-700 mt-0.5">{gpsError}</p>
          </div>
        </div>
      )}

      {/* Trip Completed Summary */}
      {tripSummary && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center justify-between text-emerald-900 text-sm">
          <div className="flex items-center gap-3">
            <Activity className="text-emerald-600" size={20} />
            <div>
              <p className="font-bold">Trip Completed</p>
              <p className="text-xs text-emerald-700">
                Total Distance: <b>{tripSummary.distance_km.toFixed(2)} km</b> • Telemetry Records: <b>{tripSummary.total_events}</b>
              </p>
            </div>
          </div>
          <Button size="sm" variant="ghost" onClick={() => setTripSummary(null)}>
            Dismiss
          </Button>
        </div>
      )}

      {/* Live Map & Telemetry Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Map View */}
        <div className="lg:col-span-3 bg-white p-4 rounded-2xl border border-slate-100 shadow-card">
          <div className="flex items-center justify-between mb-3 px-1">
            <div className="flex items-center gap-2">
              <Navigation size={18} className="text-sky-500" />
              <h2 className="text-sm font-bold text-slate-800">Live GPS Map</h2>
            </div>
            {isTripActive && (
              <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 pulse-dot" />
                Live Tracking Active
              </span>
            )}
          </div>
          <LiveMap
            center={currentCenter}
            zoom={14}
            buses={mapBuses}
            waypoints={tracking?.waypoints || []}
            height="380px"
          />
        </div>

        {/* Telemetry Stat Cards */}
        <div className="space-y-3">
          <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-card">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Speed & Next Stop
            </span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-slate-800">
                {Math.round(tracking?.speed || 0)}
              </span>
              <span className="text-xs font-semibold text-slate-400">km/h</span>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600 flex items-center justify-between">
              <span>Next Designated Stop:</span>
              <b className="text-slate-800 truncate max-w-[120px]">
                {tracking?.next_stop || 'Main Campus'}
              </b>
            </div>
          </div>

          <div className="bg-white p-4 rounded-2xl border border-slate-100 shadow-card">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Total Students Assigned
            </span>
            <div className="mt-2 flex items-baseline gap-2">
              <span className="text-3xl font-extrabold text-sky-600">
                {students.length}
              </span>
              <span className="text-xs font-semibold text-slate-400">on this route</span>
            </div>
            <div className="mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600 flex items-center justify-between">
              <span>Pickup Locations:</span>
              <b className="text-slate-800">{stopGroups.length} stops</b>
            </div>
          </div>
        </div>
      </div>

      {/* Stop by Stop Manifest */}
      <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-card space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-base font-bold text-slate-800 flex items-center gap-2">
              <MapPin size={18} className="text-amber-500" />
              Route Pickup Manifest
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Pickup stops ordered by designated student locations.
            </p>
          </div>
          <span className="text-xs font-semibold bg-slate-100 text-slate-600 px-3 py-1 rounded-lg">
            {stopGroups.length} Stops Total
          </span>
        </div>

        {loadingStudents ? (
          <div className="py-8 flex justify-center">
            <LoadingSpinner size="md" />
          </div>
        ) : stopGroups.length === 0 ? (
          <div className="py-8 text-center text-sm text-slate-400">
            No students currently assigned to this bus route.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {stopGroups.map((group, idx) => (
              <div
                key={group.stopName}
                className="p-4 rounded-xl border border-slate-100 bg-slate-50/50 hover:bg-slate-50 transition-colors space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="h-6 w-6 rounded-full bg-sky-100 text-sky-700 text-xs font-bold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <h3 className="font-bold text-sm text-slate-800 truncate">
                      {group.stopName}
                    </h3>
                  </div>
                  <span className="text-xs font-semibold text-slate-500 bg-white px-2 py-0.5 rounded border border-slate-200">
                    {group.students.length} {group.students.length === 1 ? 'student' : 'students'}
                  </span>
                </div>

                <div className="space-y-1.5 pt-1">
                  {group.students.map((student) => (
                    <div
                      key={student.student_id}
                      className="text-xs flex items-center justify-between bg-white px-2.5 py-1.5 rounded-lg border border-slate-100"
                    >
                      <div>
                        <p className="font-semibold text-slate-700">{student.student_name}</p>
                        <p className="text-[10px] text-slate-400">Class {student.student_class}</p>
                      </div>
                      {student.phone && (
                        <a
                          href={`tel:${student.phone}`}
                          className="text-sky-600 hover:text-sky-700 p-1"
                          title={`Call ${student.parent_name || 'parent'}`}
                        >
                          <Phone size={13} />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
