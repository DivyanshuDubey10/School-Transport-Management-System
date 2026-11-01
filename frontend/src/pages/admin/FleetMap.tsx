import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bus, Navigation, Phone, User, RefreshCw } from 'lucide-react'
import { getFleetTracking, type BusTrackingData } from '../../api/tracking'
import { LiveMap } from '../../components/ui/LiveMap'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'

export default function FleetMap() {
  const [selectedBus, setSelectedBus] = useState<BusTrackingData | null>(null)

  // Fetch all bus locations, refresh every 3 seconds
  const { data: fleet, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['fleet-tracking'],
    queryFn: getFleetTracking,
    refetchInterval: 3000,
  })

  const buses = fleet?.buses ?? []
  const activeBuses = buses.filter((b) => b.status === 'In Transit' || b.speed > 0)

  // Focus map on selected bus or first active bus
  const mapCenter: [number, number] = selectedBus
    ? [selectedBus.latitude, selectedBus.longitude]
    : activeBuses.length > 0
    ? [activeBuses[0].latitude, activeBuses[0].longitude]
    : [28.6139, 77.2090]

  return (
    <div className="space-y-6 page-enter">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs uppercase tracking-wider text-sky-600 font-bold">
              Live Map
            </span>
            <span className="text-slate-300">•</span>
            <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500 pulse-dot" />
              Live Updates
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Live Bus Tracking</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Monitor all school buses, their routes, and current locations in real-time.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white px-3.5 py-2 rounded-xl border border-slate-200 shadow-sm text-xs font-medium text-slate-600">
            <span>On Route: <b className="text-emerald-600">{activeBuses.length}</b></span>
            <span className="text-slate-300">|</span>
            <span>Total Buses: <b className="text-slate-800">{buses.length}</b></span>
          </div>

          <Button
            size="sm"
            variant="outline"
            onClick={() => refetch()}
            leftIcon={<RefreshCw size={13} className={isFetching ? 'animate-spin text-sky-500' : ''} />}
          >
            Refresh
          </Button>
        </div>
      </div>

      {/* Main Grid: Map (Left) + Buses List (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        {/* Map View */}
        <div className="lg:col-span-3 bg-white p-4 rounded-2xl border border-slate-200 shadow-card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3 px-1">
            <div className="flex items-center gap-2">
              <Navigation size={18} className="text-sky-500" />
              <h2 className="text-sm font-bold text-slate-800">Bus Location Map</h2>
            </div>
            {selectedBus && (
              <span className="text-xs text-slate-600">
                Viewing: <b className="text-sky-600">{selectedBus.bus_number}</b> ({selectedBus.driver_name})
              </span>
            )}
          </div>

          {isLoading ? (
            <div className="h-[520px] flex items-center justify-center">
              <LoadingSpinner size="lg" />
            </div>
          ) : (
            <LiveMap
              center={mapCenter}
              zoom={selectedBus ? 15 : 13}
              buses={buses}
              waypoints={selectedBus?.waypoints || []}
              height="520px"
              onBusClick={(b) => setSelectedBus(b)}
            />
          )}

          <div className="pt-3 px-1 flex flex-wrap items-center justify-between text-xs text-slate-500 border-t border-slate-100 mt-3">
            <span className="flex items-center gap-2">
              <span>🚌 Bus</span> • <span>🏫 School</span> • <span>📍 Stops</span>
            </span>
            <span>Click any bus card to focus on its route and stops.</span>
          </div>
        </div>

        {/* Bus List on the right */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
              All Buses ({buses.length})
            </h3>
            {selectedBus && (
              <button
                onClick={() => setSelectedBus(null)}
                className="text-xs text-sky-600 hover:underline font-semibold"
              >
                Show All
              </button>
            )}
          </div>

          <div className="space-y-2.5 max-h-[560px] overflow-y-auto pr-1">
            {buses.length === 0 ? (
              <div className="bg-white p-6 rounded-2xl border border-slate-200 text-center text-xs text-slate-400">
                No buses registered yet.
              </div>
            ) : (
              buses.map((b) => {
                const isSelected = selectedBus?.bus_id === b.bus_id
                const isInTransit = b.status === 'In Transit' || b.speed > 0

                return (
                  <div
                    key={b.bus_id}
                    onClick={() => setSelectedBus(b)}
                    className={[
                      'p-4 rounded-2xl border transition-all cursor-pointer text-left',
                      isSelected
                        ? 'bg-sky-50 border-sky-300 shadow-sm'
                        : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-card',
                    ].join(' ')}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-bold text-sm text-slate-800 flex items-center gap-1.5">
                        <Bus size={15} className="text-sky-500" />
                        {b.bus_number}
                      </span>
                      <Badge variant={isInTransit ? 'success' : 'neutral'} dot>
                        {b.status}
                      </Badge>
                    </div>

                    <div className="space-y-1 text-xs text-slate-600">
                      <p className="flex items-center gap-1.5">
                        <User size={12} className="text-slate-400" />
                        <span>Driver: {b.driver_name}</span>
                      </p>
                      <p className="truncate">Route: {b.route_name}</p>
                      <div className="flex items-center justify-between pt-1">
                        <span className="text-slate-400">Speed:</span>
                        <span className="font-semibold text-slate-700">{Math.round(b.speed)} km/h</span>
                      </div>
                    </div>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
