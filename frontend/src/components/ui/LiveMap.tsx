import { useEffect, useRef } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import type { BusTrackingData, Waypoint } from '../../api/tracking'

interface LiveMapProps {
  center?: [number, number]
  zoom?: number
  buses?: BusTrackingData[]
  waypoints?: Waypoint[]
  highlightStopName?: string
  height?: string
  onBusClick?: (bus: BusTrackingData) => void
}

function createBusIcon(busNumber: string, isMoving: boolean) {
  return L.divIcon({
    className: 'custom-bus-marker',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; transform: translate(-50%, -50%); pointer-events: auto;">
        ${
          isMoving
            ? `<div style="position: absolute; width: 44px; height: 44px; background: rgba(56, 189, 248, 0.35); border-radius: 9999px; animation: ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite; top: -6px; left: -6px;"></div>`
            : ''
        }
        <div style="width: 32px; height: 32px; background: #0284C7; color: white; border-radius: 10px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.3); border: 2px solid white; font-size: 16px;">
          🚌
        </div>
        <div style="margin-top: 2px; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(4px); color: white; padding: 2px 6px; border-radius: 6px; font-size: 10px; font-weight: 700; white-space: nowrap; border: 1px solid rgba(255,255,255,0.2); box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
          ${busNumber}
        </div>
      </div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  })
}

function createStopIcon(name: string, isHighlighted: boolean) {
  return L.divIcon({
    className: 'custom-stop-marker',
    html: `
      <div style="position: relative; display: flex; flex-direction: column; align-items: center; transform: translate(-50%, -50%); pointer-events: auto;">
        <div style="width: ${isHighlighted ? '24px' : '18px'}; height: ${
      isHighlighted ? '24px' : '18px'
    }; background: ${isHighlighted ? '#10B981' : '#F59E0B'}; color: white; border-radius: 9999px; display: flex; align-items: center; justify-content: center; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.2); font-size: 11px;">
          ${isHighlighted ? '⭐' : '📍'}
        </div>
        <div style="margin-top: 2px; background: white; color: ${
          isHighlighted ? '#065F46' : '#475569'
        }; padding: 1px 5px; border-radius: 4px; font-size: 9px; font-weight: 700; white-space: nowrap; border: 1px solid ${
      isHighlighted ? '#A7F3D0' : '#E2E8F0'
    }; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
          ${name}
        </div>
      </div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  })
}

function createSchoolIcon(name: string) {
  return L.divIcon({
    className: 'custom-school-marker',
    html: `
      <div style="display: flex; flex-direction: column; align-items: center; transform: translate(-50%, -50%);">
        <div style="width: 30px; height: 30px; background: #4F46E5; color: white; border-radius: 9999px; display: flex; align-items: center; justify-content: center; border: 2px solid white; box-shadow: 0 4px 8px rgba(0,0,0,0.25); font-size: 15px;">
          🏫
        </div>
        <div style="margin-top: 2px; background: #1E1B4B; color: white; padding: 2px 6px; border-radius: 5px; font-size: 10px; font-weight: 700; white-space: nowrap;">
          ${name}
        </div>
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  })
}

export function LiveMap({
  center = [28.6139, 77.2090],
  zoom = 13,
  buses = [],
  waypoints = [],
  highlightStopName,
  height = '420px',
  onBusClick,
}: LiveMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapInstanceRef = useRef<L.Map | null>(null)
  const markersLayerRef = useRef<L.LayerGroup | null>(null)
  const routeLayerRef = useRef<L.Polyline | null>(null)

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return

    // Prevent duplicate map instances
    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center,
        zoom,
        zoomControl: true,
      })

      // Standard free OpenStreetMap tile layer
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 19,
      }).addTo(map)

      markersLayerRef.current = L.layerGroup().addTo(map)
      mapInstanceRef.current = map

      // Resize observer to ensure tile rendering on modal/tab switch
      const resizeTimer = setTimeout(() => {
        map.invalidateSize()
      }, 200)

      return () => {
        clearTimeout(resizeTimer)
        map.remove()
        mapInstanceRef.current = null
      }
    }
  }, [])

  // Update center & zoom if changed
  useEffect(() => {
    if (mapInstanceRef.current && center) {
      mapInstanceRef.current.setView(center, zoom, { animate: true })
    }
  }, [center[0], center[1], zoom])

  // Update Layers (Buses, Waypoints, Polyline)
  useEffect(() => {
    const map = mapInstanceRef.current
    const markersLayer = markersLayerRef.current
    if (!map || !markersLayer) return

    markersLayer.clearLayers()

    // 1. Draw route polyline
    if (routeLayerRef.current) {
      map.removeLayer(routeLayerRef.current)
      routeLayerRef.current = null
    }

    if (waypoints.length > 1) {
      const latlngs: [number, number][] = waypoints.map((w) => [w.lat, w.lng])
      routeLayerRef.current = L.polyline(latlngs, {
        color: '#38BDF8',
        weight: 5,
        opacity: 0.8,
        dashArray: '8, 8',
      }).addTo(map)
    }

    // 2. Add Waypoint markers
    waypoints.forEach((w) => {
      let icon = createStopIcon(w.name, highlightStopName === w.name)
      if (w.type === 'school') {
        icon = createSchoolIcon(w.name)
      }
      const marker = L.marker([w.lat, w.lng], { icon })
      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; padding: 2px;">
          <p style="font-weight: 700; color: #1E293B; margin: 0 0 4px 0;">${w.name}</p>
          <p style="color: #64748B; margin: 0;">Type: <b>${w.type === 'school' ? 'School Campus' : 'Pickup Stop'}</b></p>
        </div>
      `)
      markersLayer.addLayer(marker)
    })

    // 3. Add Bus markers
    buses.forEach((b) => {
      const isMoving = b.status === 'In Transit' && b.speed > 0
      const marker = L.marker([b.latitude, b.longitude], {
        icon: createBusIcon(b.bus_number, isMoving),
        zIndexOffset: 1000,
      })

      marker.bindPopup(`
        <div style="font-family: sans-serif; font-size: 12px; min-width: 160px;">
          <div style="font-weight: 800; font-size: 13px; color: #0284C7; margin-bottom: 4px;">
            🚌 ${b.bus_number}
          </div>
          <div style="color: #334155; line-height: 1.4;">
            <p style="margin: 2px 0;">Driver: <b>${b.driver_name}</b></p>
            <p style="margin: 2px 0;">Route: <b>${b.route_name}</b></p>
            <p style="margin: 2px 0;">Next Stop: <b>${b.next_stop}</b></p>
            <p style="margin: 2px 0;">Speed: <b>${Math.round(b.speed)} km/h</b></p>
            <p style="margin: 2px 0;">Status: <span style="color: ${b.status === 'In Transit' ? '#10B981' : '#64748B'}; font-weight: 700;">${b.status}</span></p>
          </div>
        </div>
      `)

      if (onBusClick) {
        marker.on('click', () => onBusClick(b))
      }

      markersLayer.addLayer(marker)
    })
  }, [buses, waypoints, highlightStopName])

  return (
    <div
      ref={mapContainerRef}
      style={{ height, width: '100%' }}
      className="rounded-2xl overflow-hidden border border-slate-200 shadow-inner z-0"
    />
  )
}

