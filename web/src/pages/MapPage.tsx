import { useEffect, useRef, useState, useCallback } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { EventsData, Language, EventType } from '../core/types'
import { getEventType, EVENT_TYPE_COLOR } from '../core/eventType'
import { getVenueEvents, getActiveVenueIds, getPrimaryEvent, isEventLive } from '../core/events'
import { getToday, getUpcomingDays } from '../core/day'
import { isFavorite } from '../core/store'
import { getDict, formatDayLabel } from '../i18n'
import { loadMapStyle } from '../map/mapStyle'
import type { MapVariant } from '../map/mapStyle'
import { createPillElement, updatePillElement, resolveMarkerOverlaps } from '../map/markers'
import type { MarkerData } from '../map/markers'
import {
  IconChevronDown, IconFilter, IconHeart, IconLocation
} from '../icons'
import { EventPanel } from '../components/EventPanel'
import { DaySelector } from '../components/DaySelector'

// Prague center
const PRAGUE_CENTER: [number, number] = [14.4208, 50.0880]
const PRAGUE_BOUNDS: maplibregl.LngLatBoundsLike = [[13.90, 49.90], [14.90, 50.26]]

interface Props {
  data: EventsData
  lang: Language
  onEventOpen: (eventId: string) => void
}

function getMapVariant(): MapVariant {
  const params = new URLSearchParams(window.location.search)
  const param = params.get('map')
  if (param === 'a' || param === 'b' || param === 'c') {
    try { localStorage.setItem('mapVariant', param) } catch { /* ignore */ }
    return param
  }
  try {
    const stored = localStorage.getItem('mapVariant')
    if (stored === 'a' || stored === 'b' || stored === 'c') return stored
  } catch { /* ignore */ }
  return 'a'
}

export function MapPage({ data, lang, onEventOpen }: Props) {
  const dict = getDict(lang)
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const markersRef = useRef<Map<string, { marker: maplibregl.Marker; el: HTMLElement; offset: [number, number] }>>(new Map())

  const now = new Date()
  const [selectedDay, setSelectedDay] = useState(() => getToday(now))
  const [showFavorites, setShowFavorites] = useState(false)
  const [selectedVenueId, setSelectedVenueId] = useState<string | null>(null)
  const [showDaySelector, setShowDaySelector] = useState(false)
  const [isDotMode, setIsDotMode] = useState(false)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationLoading, setLocationLoading] = useState(false)
  const [showAttribution, setShowAttribution] = useState(false)
  const userMarkerRef = useRef<maplibregl.Marker | null>(null)

  // Refs for stale-closure-safe access in map event callbacks
  const selectedVenueIdRef = useRef<string | null>(null)
  const isDotModeRef = useRef(isDotMode)
  const dataRef = useRef(data)
  const panelOpenRef = useRef(false)
  const openPanelRef = useRef<(venueId: string) => void>(() => {})
  const closePanelRef = useRef<() => void>(() => {})

  useEffect(() => { selectedVenueIdRef.current = selectedVenueId }, [selectedVenueId])
  useEffect(() => { isDotModeRef.current = isDotMode }, [isDotMode])
  useEffect(() => { dataRef.current = data }, [data])

  // Keep open/close panel refs up to date every render
  openPanelRef.current = (venueId: string) => {
    if (!panelOpenRef.current) {
      history.pushState({ panel: 'open' }, '')
      panelOpenRef.current = true
    }
    setSelectedVenueId(venueId)
  }
  closePanelRef.current = () => {
    if (panelOpenRef.current) {
      history.back()   // popstate handler will set selectedVenueId(null)
    } else {
      setSelectedVenueId(null)
    }
  }

  // Handle browser back button: close panel
  useEffect(() => {
    function onPopState() {
      if (panelOpenRef.current) {
        panelOpenRef.current = false
        setSelectedVenueId(null)
      }
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  // Update connector GeoJSON on the map
  function updateConnectorData() {
    const map = mapRef.current
    if (!map) return
    const src = map.getSource('connectors') as maplibregl.GeoJSONSource | undefined
    if (!src) return

    if (isDotModeRef.current) {
      src.setData({ type: 'FeatureCollection', features: [] })
      return
    }

    type Feat = {
      type: 'Feature'
      properties: { color: string }
      geometry:
        | { type: 'LineString'; coordinates: number[][] }
        | { type: 'Point'; coordinates: number[] }
    }
    const features: Feat[] = []

    for (const [venueId, entry] of markersRef.current) {
      const { offset, el } = entry
      if (offset[0] === 0 && offset[1] === 0) continue

      const venue = dataRef.current.venues.find(v => v.id === venueId)
      if (!venue) continue

      const eventType = (el.dataset.eventType ?? 'other') as EventType
      const color = EVENT_TYPE_COLOR[eventType]

      const actualScreen = map.project([venue.lng, venue.lat])
      const pillScreen = {
        x: actualScreen.x + offset[0],
        y: actualScreen.y + offset[1],
      }
      const pillLngLat = map.unproject([pillScreen.x, pillScreen.y])

      features.push({
        type: 'Feature',
        properties: { color },
        geometry: { type: 'LineString', coordinates: [[pillLngLat.lng, pillLngLat.lat], [venue.lng, venue.lat]] },
      })
      features.push({
        type: 'Feature',
        properties: { color },
        geometry: { type: 'Point', coordinates: [venue.lng, venue.lat] },
      })
    }

    src.setData({ type: 'FeatureCollection', features })
  }

  // Build marker data from current state
  const buildMarkers = useCallback((): MarkerData[] => {
    const curNow = new Date()
    const activeIds = getActiveVenueIds(data.events, selectedDay, curNow)
    const venues = showFavorites
      ? data.venues.filter(v => activeIds.has(v.id) && isFavorite(v.id))
      : data.venues.filter(v => activeIds.has(v.id))

    return venues.map(venue => {
      const events = getVenueEvents(data.events, venue.id, selectedDay, curNow)
      const primary = getPrimaryEvent(events, curNow)
      const eventType: EventType = primary ? getEventType(primary.formats) : 'other'
      const isLive = primary ? isEventLive(primary, curNow) : false
      return {
        venueId: venue.id,
        name: venue.name,
        eventType,
        isFavorite: isFavorite(venue.id),
        isLive,
        extraCount: Math.max(0, events.length - 1),
        lat: venue.lat,
        lng: venue.lng,
        stackOffset: 0
      }
    })
  }, [data, selectedDay, showFavorites])

  // Update markers on the map
  const updateMarkers = useCallback(() => {
    const map = mapRef.current
    if (!map) return
    const markerData = buildMarkers()
    const newIds = new Set(markerData.map(m => m.venueId))

    // Remove stale markers
    for (const [id, { marker }] of markersRef.current) {
      if (!newIds.has(id)) {
        marker.remove()
        markersRef.current.delete(id)
      }
    }

    // Add/update markers
    for (const md of markerData) {
      const isSelected = md.venueId === selectedVenueId
      const existing = markersRef.current.get(md.venueId)

      if (existing) {
        updatePillElement(existing.el, md, isSelected, isDotMode)
      } else {
        const el = createPillElement(md, isSelected, isDotMode)
        const venueId = md.venueId
        el.addEventListener('click', () => {
          if (selectedVenueIdRef.current === venueId) {
            closePanelRef.current()
          } else {
            openPanelRef.current(venueId)
          }
        })
        const marker = new maplibregl.Marker({ element: el, anchor: 'bottom', offset: [0, 0] })
          .setLngLat([md.lng, md.lat])
          .addTo(map)
        markersRef.current.set(venueId, { marker, el, offset: [0, 0] })
      }
    }

    // Resolve overlaps after all markers are placed/updated
    resolveMarkerOverlaps(
      Array.from(markersRef.current.entries()).map(([, entry]) => ({
        el: entry.el,
        setOffset: (o: [number, number]) => {
          entry.marker.setOffset(o)
          entry.offset = o
        },
      }))
    )
    updateConnectorData()
  }, [buildMarkers, selectedVenueId, isDotMode])  // eslint-disable-line react-hooks/exhaustive-deps

  // Init map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return
    let mounted = true

    async function initMap() {
      try {
        const variant = getMapVariant()
        const style = await loadMapStyle(variant)
        if (!mounted || !mapContainerRef.current) return

        const map = new maplibregl.Map({
          container: mapContainerRef.current,
          style: style as maplibregl.StyleSpecification,
          center: PRAGUE_CENTER,
          zoom: 12,
          maxBounds: PRAGUE_BOUNDS,
          attributionControl: false,  // custom attribution button
        })
        mapRef.current = map

        map.on('zoom', () => {
          setIsDotMode(map.getZoom() < 11)
        })

        // Re-resolve overlaps + connectors after each pan/zoom (pixel positions change)
        const resolveOverlaps = () => {
          resolveMarkerOverlaps(
            Array.from(markersRef.current.entries()).map(([, entry]) => ({
              el: entry.el,
              setOffset: (o: [number, number]) => {
                entry.marker.setOffset(o)
                entry.offset = o
              },
            }))
          )
          updateConnectorData()
        }
        map.on('moveend', resolveOverlaps)
        map.on('zoomend', resolveOverlaps)

        map.on('click', (e) => {
          if ((e.originalEvent.target as HTMLElement).classList.contains('maplibregl-canvas')) {
            closePanelRef.current()
          }
        })

        map.on('load', () => {
          // Connector source and layers (drawn below HTML markers)
          map.addSource('connectors', {
            type: 'geojson',
            data: { type: 'FeatureCollection', features: [] },
          })
          map.addLayer({
            id: 'connector-lines',
            type: 'line',
            source: 'connectors',
            filter: ['==', ['geometry-type'], 'LineString'],
            paint: {
              'line-color': ['get', 'color'],
              'line-width': 2,
              'line-opacity': 0.8,
            },
          })
          map.addLayer({
            id: 'connector-dots',
            type: 'circle',
            source: 'connectors',
            filter: ['==', ['geometry-type'], 'Point'],
            paint: {
              'circle-color': ['get', 'color'],
              'circle-radius': 4,
              'circle-stroke-color': '#111118',
              'circle-stroke-width': 1.5,
            },
          })

          if (mounted) updateMarkers()
        })
      } catch (err) {
        console.error('Map init failed', err)
      }
    }

    void initMap()
    return () => {
      mounted = false
      mapRef.current?.remove()
      mapRef.current = null
      markersRef.current.clear()
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Update markers when data/state changes
  useEffect(() => {
    if (mapRef.current?.loaded()) updateMarkers()
  }, [updateMarkers])

  // User location marker
  useEffect(() => {
    const map = mapRef.current
    if (!map || !userLocation) return
    if (userMarkerRef.current) {
      userMarkerRef.current.setLngLat([userLocation.lng, userLocation.lat])
      return
    }
    const dot = document.createElement('div')
    dot.style.cssText = 'width:14px;height:14px;border-radius:7px;background:#4A90E2;border:2.5px solid #fff;box-shadow:0 2px 8px rgba(0,0,0,0.5)'
    userMarkerRef.current = new maplibregl.Marker({ element: dot })
      .setLngLat([userLocation.lng, userLocation.lat])
      .addTo(map)
    return () => {
      userMarkerRef.current?.remove()
      userMarkerRef.current = null
    }
  }, [userLocation])

  function handleLocationClick() {
    if (!navigator.geolocation) return
    setLocationLoading(true)
    navigator.geolocation.getCurrentPosition(
      pos => {
        setUserLocation({ lat: pos.coords.latitude, lng: pos.coords.longitude })
        setLocationLoading(false)
        mapRef.current?.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 14 })
      },
      () => setLocationLoading(false),
      { timeout: 8000 }
    )
  }

  // Active venues for the selected day
  const curNow = new Date()
  const venueMap = Object.fromEntries(data.venues.map(v => [v.id, v]))
  const panelVenue = selectedVenueId ? venueMap[selectedVenueId] : null
  const panelEvents = panelVenue ? getVenueEvents(data.events, panelVenue.id, selectedDay, curNow) : []

  const days = getUpcomingDays(14, curNow)
  const selectedDayLabel = formatDayLabel(selectedDay, lang, curNow)

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      {/* Map container */}
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Top bar */}
      <div style={{
        position: 'absolute', top: 56, left: 16, right: 16,
        display: 'grid', gridTemplateColumns: 'auto 1fr auto',
        alignItems: 'center', gap: 8, zIndex: 10
      }}>
        {/* Day selector button */}
        <button
          style={{
            height: 44, padding: '0 14px', borderRadius: 22,
            background: '#F4F2FF', color: '#111118',
            fontSize: 15, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 6
          }}
          onClick={() => setShowDaySelector(true)}
          aria-label={dict.map.daySelector}
        >
          {selectedDayLabel}
          <IconChevronDown size={16} color="#111118" />
        </button>

        {/* All / Favorites toggle */}
        <div
          style={{
            height: 44, borderRadius: 22, background: '#23232F',
            display: 'flex', alignItems: 'center'
          }}
          role="group"
          aria-label={dict.map.all + ' / ' + dict.map.favorites}
        >
          <button
            style={{
              flex: 1, height: 44, borderRadius: 22,
              background: !showFavorites ? '#F4F2FF' : 'transparent',
              color: !showFavorites ? '#111118' : '#B9B6CC',
              fontSize: 14, fontWeight: !showFavorites ? 600 : 500,
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}
            onClick={() => setShowFavorites(false)}
          >
            {dict.map.all}
          </button>
          <button
            style={{
              flex: 1, height: 44, borderRadius: 22,
              background: showFavorites ? '#FF4D8D' : 'transparent',
              color: showFavorites ? '#1A0710' : '#B9B6CC',
              fontSize: 14, fontWeight: showFavorites ? 600 : 500,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5
            }}
            onClick={() => setShowFavorites(true)}
          >
            <IconHeart size={14} color={showFavorites ? '#1A0710' : '#B9B6CC'} filled={showFavorites} />
            {dict.map.favorites}
          </button>
        </div>

        {/* Filter button (inactive for now) */}
        <button
          style={{
            width: 44, height: 44, borderRadius: 22,
            background: '#23232F', color: '#6A6680',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: 0.6
          }}
          aria-label={dict.map.filter}
          disabled
        >
          <IconFilter size={20} color="#6A6680" />
        </button>
      </div>

      {/* My location button */}
      <button
        style={{
          position: 'absolute', right: 16, bottom: 132,
          width: 52, height: 52, borderRadius: 26,
          background: '#F4F2FF', color: '#111118',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 2px 12px rgba(0,0,0,0.4)', zIndex: 10,
          opacity: locationLoading ? 0.6 : 1
        }}
        onClick={handleLocationClick}
        aria-label={dict.map.myLocation}
      >
        <IconLocation size={22} color="#111118" />
      </button>

      {/* Attribution "i" button – required by OSM/OpenFreeMap licence */}
      <button
        style={{
          position: 'absolute', left: 16, bottom: 108,
          height: 28, padding: '0 10px', borderRadius: 14,
          background: 'rgba(28,28,39,0.90)', color: '#B9B6CC',
          border: '1px solid #2E2D3C',
          fontSize: 12, fontWeight: showAttribution ? 400 : 700,
          display: 'flex', alignItems: 'center', gap: 6, zIndex: 10,
          whiteSpace: 'nowrap',
        }}
        onClick={() => setShowAttribution(a => !a)}
        aria-label="Autorstvo mapy"
      >
        {showAttribution
          ? '© OpenStreetMap prispievatelia | OpenFreeMap'
          : 'i'}
      </button>

      {/* Event panel – NO backdrop div; map canvas click handles closing */}
      {panelVenue && panelEvents.length > 0 && (
        <EventPanel
          events={panelEvents}
          venue={panelVenue}
          lang={lang}
          userLocation={userLocation}
          onClose={() => closePanelRef.current()}
          onEventOpen={onEventOpen}
        />
      )}

      {/* Day selector sheet */}
      {showDaySelector && (
        <DaySelector
          days={days}
          selectedDay={selectedDay}
          lang={lang}
          now={curNow}
          onSelect={day => { setSelectedDay(day); setShowDaySelector(false) }}
          onClose={() => setShowDaySelector(false)}
        />
      )}
    </div>
  )
}
