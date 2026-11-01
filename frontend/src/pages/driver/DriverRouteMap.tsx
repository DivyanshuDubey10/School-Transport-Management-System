import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { MapPin, Users, Phone, Bus, Play, Square, Navigation, Radio } from 'lucide-react'
import { getDriverStudents, type StudentForDriver } from '../../api/attendance'
import { getBusTracking, updateBusLocation, startTrip, stopTrip, type BusTrackingData } from '../../api/tracking'
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
  const busId = user?.user_id || 1

  const [isTripActive, setIsTripActive] = useState(false)
  const [useSimulator, setUseSimulator] = useState(true)
  const simStepRef = useRef(0)
  const watchIdRef = useRef<number | null>(null)

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

  const startMut = useMutation({
    mutationFn: () => startTrip(busId),
    onSuccess: () => {
      setIsTripActive(true)
      showToast('Trip started! Live location broadcasting is active.', 'success')
      refetchTracking()
    },
  })

  const stopMut = useMutation({
    mutationFn: () => stopTrip(busId),
    onSuccess: () => {
      setIsTripActive(false)
      showToast('Trip ended. Broadcasting stopped.', 'info')
      refetchTracking()
    },
  })

  // Simulator loop or GPS watch
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

        updateBusLocation({
          bus_id: busId,
          latitude: currentLat,
          longitude: currentLng,
          speed,
          heading: 45,
          status: 'In Transit',
          next_stop: p2.name,
        }).catch(() => {})
      }, 3000)

      return () => clearInterval(interval)
    } else {
      // Use device GPS if available
      if ('geolocation' in navigator) {
        watchIdRef.current = navigator.geolocation.watchPosition(
          (pos) => {
            updateBusLocation({
              bus_id: busId,
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude,
              speed: pos.coords.speed ? pos.coords.speed * 3.6 : 25,
              heading: pos.coords.heading || 0,
              status: 'In Transit',
            }).catch(() => {})
          },
          () => {
            showToast('Could not access device GPS. Switching to simulator mode.', 'warning')
            setUseSimulator(true)
          },
          { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 },
        )
      }
    }
  }, [isTripActive, useSimulator, tracking?.waypoints, busId])

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
  const currentCenter: [number, number] = tracking
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
              {isTripActive ? 'Live GPS Active' : 'Trip Idle'}
            </Badge>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">
            {tracking?.bus_number || 'Route Bus'} — Live Route Map
          </h1>
          <p className="text-xs text-slate-300 mt-1">
            Route: <b className="text-white">{tracking?.route_name || 'Assigned Route'}</b> • Driver: {user?.name}
          </p>
        </div>

        {/* Live Trip Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-xs font-semibold bg-white/10 px-3 py-2 rounded-xl cursor-pointer hover:bg-white/15 transition-colors">
            <input
              type="checkbox"
              checked={useSimulator}
              onChange={(e) => setUseSimulator(e.target.checked)}
              className="rounded text-sky-500 focus:ring-0"
            />
            <Radio size={14} className={useSimulator ? 'text-sky-400' : 'text-slate-400'} />
            <span>Simulate Motion</span>
          </label>

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

        {/* Telemetry Card */}
        <div className="bg-white p-5 rounded-2xl border border-slate-100 shadow-card flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4">
              Trip Details
            </h3>

            <div className="space-y-4">
              <div>
                <span className="text-xs text-slate-400 font-medium">Next Stop</span>
                <p className="text-base font-bold text-slate-800 mt-0.5">
                  {tracking?.next_stop || 'Purana Bazar'}
                </p>
              </div>

              <div>
                <span className="text-xs text-slate-400 font-medium">Estimated Speed</span>
                <div className="flex items-baseline gap-1 mt-0.5">
                  <span className="text-3xl font-extrabold text-slate-800">
                    {Math.round(tracking?.speed || 0)}
                  </span>
                  <span className="text-xs text-slate-400 font-semibold">km/h</span>
                </div>
              </div>

              <div>
                <span className="text-xs text-slate-400 font-medium">Current Status</span>
                <p className="text-sm font-semibold text-sky-600 mt-0.5">
                  {tracking?.status || 'Idle'}
                </p>
              </div>

              <div>
                <span className="text-xs text-slate-400 font-medium">Allocated Students</span>
                <p className="text-sm font-semibold text-slate-700 mt-0.5">
                  {students.length} students on route
                </p>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-100 mt-4">
            <span className="text-[10px] text-slate-400 block text-center">
              Coordinates: {tracking?.latitude.toFixed(4)}, {tracking?.longitude.toFixed(4)}
            </span>
          </div>
        </div>
      </div>

      {/* Stop Itinerary Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-800">Designated Pickup Sequence</h2>
          <span className="text-xs text-slate-500">{stopGroups.length} Scheduled Stops</span>
        </div>

        {loadingStudents ? (
          <div className="py-12 flex justify-center">
            <LoadingSpinner size="md" />
          </div>
        ) : stopGroups.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center">
            <Bus size={32} className="text-slate-300 mx-auto mb-2" />
            <p className="text-sm text-slate-500 font-medium">No students or stops allocated to this bus.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {stopGroups.map((group, idx) => (
              <div
                key={group.stopName}
                className="bg-white rounded-2xl border border-slate-100 p-5 shadow-card hover:shadow-card-hover transition-all"
              >
                <div className="flex items-start justify-between pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-2.5">
                    <div className="w-7 h-7 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center font-bold text-xs">
                      #{idx + 1}
                    </div>
                    <div>
                      <h3 className="font-bold text-slate-800 text-sm">{group.stopName}</h3>
                      <span className="text-xs text-slate-400">{group.students.length} Students</span>
                    </div>
                  </div>
                  <Badge variant="info">Stop #{idx + 1}</Badge>
                </div>

                <div className="pt-3 space-y-2">
                  {group.students.map((s) => (
                    <div
                      key={s.student_id}
                      className="bg-slate-50/70 p-2.5 rounded-xl border border-slate-100 flex items-center justify-between"
                    >
                      <div>
                        <span className="font-semibold text-xs text-slate-800 block">
                          {s.student_name}
                        </span>
                        <span className="text-[11px] text-slate-400">
                          Class {s.student_class} • {s.parent_name || 'Parent'}
                        </span>
                      </div>
                      {s.phone && (
                        <a
                          href={`tel:${s.phone}`}
                          className="w-7 h-7 rounded-lg bg-white border border-slate-200 text-sky-600 flex items-center justify-center hover:bg-sky-50 transition-colors shadow-2xs"
                          title={`Call ${s.phone}`}
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
