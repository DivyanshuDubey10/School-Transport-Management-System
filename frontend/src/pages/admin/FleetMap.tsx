import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Bus, Navigation, Phone, User, Radio, RefreshCw } from 'lucide-react'
import { getFleetTracking, type BusTrackingData } from '../../api/tracking'
import { LiveMap } from '../../components/ui/LiveMap'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { LoadingSpinner } from '../../components/ui/LoadingSpinner'

export default function FleetMap() {
  const [selectedBus, setSelectedBus] = useState<BusTrackingData | null>(null)

  const { data: fleet, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['fleet-tracking'],
    queryFn: getFleetTracking,
    refetchInterval: 3000,
  })

  const buses = fleet?.buses ?? []
  const activeBuses = buses.filter((b) => b.status === 'In Transit' || b.speed > 0)

  // Map center defaults to selected bus or first active bus or Delhi campus
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
            <span className="text-xs uppercase tracking-wider text-sky-500 font-bold">
              Fleet Command Center
            </span>
            <span className="text-slate-300">•</span>
            <span className="text-xs font-semibold text-emerald-600 flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-500 pulse-dot" />
              Live Telemetry Stream
            </span>
          </div>
          <h1 className="text-2xl font-bold text-slate-800">Live Bus Fleet Tracking</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time geospatial locations, transit velocities, and route progress across all school buses.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-white px-3 py-1.5 rounded-xl border border-slate-100 shadow-sm text-xs font-medium text-slate-600">
            <span>In Transit: <b className="text-emerald-600">{activeBuses.length}</b></span>
            <span className="text-slate-200">|</span>
            <span>Total Fleet: <b className="text-slate-800">{buses.length}</b></span>
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

      {/* Main Grid: Interactive Map (Left) + Bus Fleet List (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-5">
        {/* Map Panel */}
        <div className="lg:col-span-3 bg-white p-4 rounded-2xl border border-slate-100 shadow-card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3 px-1">
            <div className="flex items-center gap-2">
              <Navigation size={18} className="text-sky-500" />
              <h2 className="text-sm font-bold text-slate-800">City-Wide Fleet Radar</h2>
            </div>
            {selectedBus && (
              <span className="text-xs text-slate-500">
                Focused on: <b className="text-sky-600">{selectedBus.bus_number}</b> ({selectedBus.driver_name})
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

          <div className="pt-3 px-1 flex flex-wrap items-center justify-between text-[11px] text-slate-400 border-t border-slate-100 mt-3">
            <span className="flex items-center gap-1.5">
              <span>🚌 Bus Marker</span> • <span>🏫 School Campus</span> • <span>📍 Designated Stop</span>
            </span>
            <span>Click any bus card or marker to focus and view assigned waypoints.</span>
          </div>
        </div>

        {/* Fleet Sidebar List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Buses ({buses.length})
            </h3>
            {selectedBus && (
              <button
                onClick={() => setSelectedBus(null)}
                className="text-xs text-sky-600 hover:underline font-semibold"
              >
                Reset Focus
              </button>
            )}
          </div>

          <div className="space-y-2.5 max-h-[560px] overflow-y-auto pr-1">
            {buses.map((b) => {
              const isSelected = selectedBus?.bus_id === b.bus_id
              const isInTransit = b.status === 'In Transit' || b.speed > 0

              return (
                <div
                  key={b.bus_id}
                  onClick={() => setSelectedBus(b)}
                  className={[
                    'p-4 rounded-2xl border transition-all cursor-pointer text-left',
                    isSelected
                      ? 'bg-sky-50/80 border-sky-300 shadow-sm'
                      : 'bg-white border-slate-100 hover:border-slate-200 hover:shadow-card',
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

                  <div className="space-y-1 text-xs text-slate-500">
                    <p className="flex items-center gap-1.5">
                      <User size={12} className="text-slate-400" />
                      <span>{b.driver_name}</span>
                    </p>
                    <p className="text-slate-600 font-medium truncate">
                      Route: {b.route_name}
                    </p>
                    <div className="flex items-center justify-between pt-1 font-semibold">
                      <span className="text-slate-400">Velocity:</span>
                      <span className="text-slate-700">{Math.round(b.speed)} km/h</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}

