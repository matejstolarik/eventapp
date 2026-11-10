import { useEffect, useRef, useState, useCallback } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { EventsData, Language } from '../core/types'
import { getEventType } from '../core/eventType'
import { getVenueEvents, getActiveVenueIds, getPrimaryEvent, isEventLive } from '../core/events'
import { getToday, getUpcomingDays } from '../core/day'
import { isFavorite } from '../core/store'
import { getDict, formatDayLabel } from '../i18n'
import { loadMapStyle, MAP_MIN_ZOOM } from '../map/mapStyle'
import { createPinElement, updatePinElement } from '../map/markers'
import type { MarkerData } from '../map/markers'
import {
  IconChevronDown, IconFilter, IconHeart, IconLocation
} from '../icons'
import { EventPanel } from '../components/EventPanel'
import { DaySelector } from '../components/DaySelector'

const PIN_CSS = `
@keyframes pinpulse {
  0%   { box-shadow: 0 0 0 0 var(--pc); opacity: .9 }
  100% { box-shadow: 0 0 0 16px transparent; opacity: 0 }
}
@keyframes pin-appear {
  from { opacity: 0; transform: scale(0.82); }
  to   { opacity: 1; transform: scale(1); }
}
.pin-live-ring {
  position: absolute;
  animation: pinpulse 1.6s ease-out infinite;
}
@media (prefers-reduced-motion: reduce) {
  .pin-live-ring {
    animation: none;
    box-shadow: 0 0 0 6px var(--pc);
    opacity: .5;
  }
}
.pin-new .pin-inner {
  animation: pin-appear 180ms ease-out both;
}
@media (prefers-reduced-motion: reduce) {
  .pin-new .pin-inner { animation: none; }
}
@keyframes card-slide-up {
  from { transform: translateY(100%); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}
.event-panel-enter {
  animation: card-slide-up 200ms ease-out both;
}
@media (prefers-reduced-motion: reduce) {
  .event-panel-enter { animation: none; }
}
`

const PRAGUE_CENTER: [number, number] = [14.4208, 50.0880]
const PRAGUE_BOUNDS: maplibregl.LngLatBoundsLike = [[13.90, 49.90], [14.90, 50.26]]

interface Props {
  data: EventsData
  lang: Language
  onEventOpen: (eventId: string) => void
}

export function MapPage({ data, lang, onEventOpen }: Props) {
  const dict = getDict(lang)
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const markersRef = useRef<Map<string, { marker: maplibregl.Marker; el: HTMLElement }>>(new Map())

  const now = new Date()
  const [selectedDay, setSelectedDay] = useState(() => getToday(now))
  const [showFavorites, setShowFavorites] = useState(false)
  const [selectedVenueId, setSelectedVenueId] = useState<string | null>(null)
  const [showDaySelector, setShowDaySelector] = useState(false)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationLoading, setLocationLoading] = useState(false)
  const [showAttribution, setShowAttribution] = useState(false)
  const [panelKey, setPanelKey] = useState(0)
  const userMarkerRef = useRef<maplibregl.Marker | null>(null)

  const selectedVenueIdRef = useRef<string | null>(null)
  const dataRef = useRef(data)
  const panelOpenRef = useRef(false)
  const openPanelRef = useRef<(venueId: string) => void>(() => {})
  const closePanelRef = useRef<() => void>(() => {})

  useEffect(() => { selectedVenueIdRef.current = selectedVenueId }, [selectedVenueId])
  useEffect(() => { dataRef.current = data }, [data])

  openPanelRef.current = (venueId: string) => {
    const isNew = venueId !== selectedVenueIdRef.current
    if (!panelOpenRef.current) {
      history.pushState({ panel: 'open' }, '')
      panelOpenRef.current = true
    }
    if (isNew) setPanelKey(k => k + 1)
    setSelectedVenueId(venueId)
  }
  closePanelRef.current = () => {
    if (panelOpenRef.current) {
      history.back()
    } else {
      setSelectedVenueId(null)
    }
  }

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

  // Inject animation CSS once
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = PIN_CSS
    document.head.appendChild(style)
    return () => { document.head.removeChild(style) }
  }, [])

  const buildMarkers = useCallback((): MarkerData[] => {
    const curNow = new Date()
    const activeIds = getActiveVenueIds(data.events, selectedDay, curNow)
    const venues = showFavorites
      ? data.venues.filter(v => activeIds.has(v.id) && isFavorite(v.id))
      : data.venues.filter(v => activeIds.has(v.id))

    return venues.map(venue => {
      const events = getVenueEvents(data.events, venue.id, selectedDay, curNow)
      const primary = getPrimaryEvent(events, curNow)
      const eventType = primary ? getEventType(primary.formats) : 'other'
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
      }
    })
  }, [data, selectedDay, showFavorites])

  const updateMarkers = useCallback(() => {
    const map = mapRef.current
    if (!map) return
    const markerData = buildMarkers()
    const newIds = new Set(markerData.map(m => m.venueId))

    for (const [id, { marker }] of markersRef.current) {
      if (!newIds.has(id)) {
        marker.remove()
        markersRef.current.delete(id)
      }
    }

    for (const md of markerData) {
      const isSelected = md.venueId === selectedVenueId
      const existing = markersRef.current.get(md.venueId)

      if (existing) {
        updatePinElement(existing.el, md, isSelected)
      } else {
        const el = createPinElement(md, isSelected)
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

        // Appear animation for new pins
        el.classList.add('pin-new')
        setTimeout(() => el.classList.remove('pin-new'), 300)

        markersRef.current.set(venueId, { marker, el })
      }
    }
  }, [buildMarkers, selectedVenueId])

  // Init map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return
    let mounted = true

    async function initMap() {
      try {
        const style = await loadMapStyle()
        if (!mounted || !mapContainerRef.current) return

        const map = new maplibregl.Map({
          container: mapContainerRef.current,
          style: style as maplibregl.StyleSpecification,
          center: PRAGUE_CENTER,
          zoom: 12,
          minZoom: MAP_MIN_ZOOM,
          maxBounds: PRAGUE_BOUNDS,
          attributionControl: false,
        })
        mapRef.current = map

        map.on('click', (e) => {
          if ((e.originalEvent.target as HTMLElement).classList.contains('maplibregl-canvas')) {
            closePanelRef.current()
          }
        })

        map.on('load', () => {
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

  // Sorted venues for ‹ › navigation (by longitude: west → east)
  const curNow = new Date()
  const venueMap = Object.fromEntries(data.venues.map(v => [v.id, v]))
  const panelVenue = selectedVenueId ? venueMap[selectedVenueId] : null
  const panelEvents = panelVenue ? getVenueEvents(data.events, panelVenue.id, selectedDay, curNow) : []

  const activeIds = getActiveVenueIds(data.events, selectedDay, curNow)
  const sortedVenues = [...data.venues
    .filter(v => activeIds.has(v.id) && (!showFavorites || isFavorite(v.id)))
  ].sort((a, b) => a.lng - b.lng)

  const selIdx = selectedVenueId ? sortedVenues.findIndex(v => v.id === selectedVenueId) : -1
  const prevVenue = selIdx > 0 ? sortedVenues[selIdx - 1] : null
  const nextVenue = selIdx >= 0 && selIdx < sortedVenues.length - 1 ? sortedVenues[selIdx + 1] : null

  function handleArrow(venue: { id: string; lng: number; lat: number }) {
    openPanelRef.current(venue.id)
    mapRef.current?.easeTo({
      center: [venue.lng, venue.lat],
      padding: { bottom: 240, top: 80, left: 60, right: 60 },
      duration: 320,
    })
  }

  const days = getUpcomingDays(14, curNow)
  const selectedDayLabel = formatDayLabel(selectedDay, lang, curNow)
  const panelOpen = panelVenue && panelEvents.length > 0

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Top bar */}
      <div style={{
        position: 'absolute', top: 56, left: 16, right: 16,
        display: 'grid', gridTemplateColumns: 'auto 1fr auto',
        alignItems: 'center', gap: 8, zIndex: 10,
      }}>
        <button
          style={{
            height: 44, padding: '0 14px', borderRadius: 22,
            background: '#F4F2FF', color: '#111118',
            fontSize: 15, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 6,
          }}
          onClick={() => setShowDaySelector(true)}
          aria-label={dict.map.daySelector}
        >
          {selectedDayLabel}
          <IconChevronDown size={16} color="#111118" />
        </button>

        <div style={{ height: 44, borderRadius: 22, background: '#23232F', display: 'flex', alignItems: 'center' }}
          role="group" aria-label={dict.map.all + ' / ' + dict.map.favorites}>
          <button
            style={{
              flex: 1, height: 44, borderRadius: 22,
              background: !showFavorites ? '#F4F2FF' : 'transparent',
              color: !showFavorites ? '#111118' : '#B9B6CC',
              fontSize: 14, fontWeight: !showFavorites ? 600 : 500,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
            onClick={() => setShowFavorites(false)}
          >{dict.map.all}</button>
          <button
            style={{
              flex: 1, height: 44, borderRadius: 22,
              background: showFavorites ? '#FF4D8D' : 'transparent',
              color: showFavorites ? '#1A0710' : '#B9B6CC',
              fontSize: 14, fontWeight: showFavorites ? 600 : 500,
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 5,
            }}
            onClick={() => setShowFavorites(true)}
          >
            <IconHeart size={14} color={showFavorites ? '#1A0710' : '#B9B6CC'} filled={showFavorites} />
            {dict.map.favorites}
          </button>
        </div>

        <button
          style={{
            width: 44, height: 44, borderRadius: 22,
            background: '#23232F', color: '#6A6680',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: 0.6,
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
          opacity: locationLoading ? 0.6 : 1,
        }}
        onClick={handleLocationClick}
        aria-label={dict.map.myLocation}
      >
        <IconLocation size={22} color="#111118" />
      </button>

      {/* Attribution */}
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
        {showAttribution ? '© OpenStreetMap prispievatelia | OpenFreeMap' : 'i'}
      </button>

      {/* Navigation arrows ‹ › above panel */}
      {panelOpen && prevVenue && (
        <button
          style={{
            position: 'absolute', left: 16, bottom: 310,
            width: 36, height: 36, borderRadius: 18,
            background: '#F4F2FF', color: '#111118',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.45)', zIndex: 25,
          }}
          onClick={() => handleArrow(prevVenue)}
          aria-label="Predošlé miesto"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M15 6l-6 6 6 6" />
          </svg>
        </button>
      )}
      {panelOpen && nextVenue && (
        <button
          style={{
            position: 'absolute', right: 16, bottom: 310,
            width: 36, height: 36, borderRadius: 18,
            background: '#F4F2FF', color: '#111118',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.45)', zIndex: 25,
          }}
          onClick={() => handleArrow(nextVenue)}
          aria-label="Ďalšie miesto"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M9 6l6 6-6 6" />
          </svg>
        </button>
      )}

      {/* Event panel */}
      {panelOpen && (
        <EventPanel
          key={panelKey}
          events={panelEvents}
          venue={panelVenue!}
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
