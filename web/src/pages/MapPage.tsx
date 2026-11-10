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
@keyframes card-slide-up {
  from { transform: translateY(100%); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

/* Pin structural styles */
.pin-inner {
  position: relative;
  width: 50px;
  height: 64px;
  transform: scale(1);
  transform-origin: 50% 100%;
  transition: transform 220ms ease-out;
}
.pin-selected .pin-inner {
  transform: scale(1.22);
}
@media (prefers-reduced-motion: reduce) {
  .pin-inner { transition: none; }
}

.pin-glow {
  position: absolute;
  left: -8px; top: -8px;
  width: 66px; height: 66px;
  border-radius: 33px;
  opacity: 0;
  transition: opacity 220ms ease-out;
  pointer-events: none;
  z-index: 0;
}
.pin-selected .pin-glow { opacity: 1; }
@media (prefers-reduced-motion: reduce) {
  .pin-glow { transition: none; }
}

.pin-live-ring {
  position: absolute;
  left: 3px; top: 3px;
  width: 44px; height: 44px;
  border-radius: 22px;
  animation: pinpulse 1.6s ease-out infinite;
  z-index: 0;
}
@media (prefers-reduced-motion: reduce) {
  .pin-live-ring {
    animation: none;
    box-shadow: 0 0 0 6px var(--pc);
    opacity: .5;
  }
}

.pin-svg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.pin-circle {
  position: absolute;
  left: 7px; top: 7px;
  width: 36px; height: 36px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2;
}

.pin-badge-heart {
  position: absolute;
  top: -2px; right: -4px;
  width: 20px; height: 20px;
  border-radius: 10px;
  background: #F4F2FF;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.4);
  z-index: 3;
}

.pin-badge-count {
  position: absolute;
  top: -2px; left: -6px;
  height: 20px; min-width: 20px;
  padding: 0 5px;
  box-sizing: border-box;
  border-radius: 10px;
  background: #111118;
  color: #F4F2FF;
  border: 1.5px solid #F4F2FF;
  font-size: 11px; font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: Outfit, sans-serif;
  z-index: 3;
}

.pin-name {
  position: absolute;
  left: 50%;
  top: 68px;
  transform: translateX(-50%);
  white-space: nowrap;
  font-family: 'Outfit', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #E4E2EE;
  text-shadow: 0 0 3px #111118, 0 0 3px #111118, 0 1px 2px #111118;
  letter-spacing: 0.01em;
  pointer-events: none;
  display: none;
  z-index: 4;
}
.pin-selected .pin-name {
  display: block !important;
  font-size: 13px !important;
  font-weight: 800 !important;
  color: #FFFFFF !important;
}
.map-zoom-13 .pin-name {
  display: block;
}

/* New pin appearance animation */
.pin-new .pin-inner {
  animation: pin-appear 180ms ease-out both;
}
@media (prefers-reduced-motion: reduce) {
  .pin-new .pin-inner { animation: none; }
}

/* Event panel slide-up */
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
  const [bearing, setBearing] = useState(0)
  const [showFilterMsg, setShowFilterMsg] = useState(false)
  const userMarkerRef = useRef<maplibregl.Marker | null>(null)
  const filterMsgTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

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
            // Deselect immediately (don't wait for React re-render)
            el.classList.remove('pin-selected')
            el.style.zIndex = ''
            closePanelRef.current()
          } else {
            // Deselect old, select new immediately
            const oldId = selectedVenueIdRef.current
            if (oldId) {
              const oldEntry = markersRef.current.get(oldId)
              if (oldEntry) {
                oldEntry.el.classList.remove('pin-selected')
                oldEntry.el.style.zIndex = ''
              }
            }
            el.classList.add('pin-selected')
            el.style.zIndex = '999'
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

    // Check name collisions after DOM settles
    requestAnimationFrame(() => checkNameCollisions())
  }, [buildMarkers, selectedVenueId])

  // Name collision detection: hide lower-priority names that overlap higher-priority ones
  function checkNameCollisions() {
    const map = mapRef.current
    if (!map || map.getZoom() < 13) return

    type PinEntry = { el: HTMLElement; nameEl: HTMLElement; priority: number }
    const entries: PinEntry[] = []

    for (const [, { el }] of markersRef.current) {
      const nameEl = el.querySelector('.pin-name') as HTMLElement | null
      if (!nameEl) continue
      const isSelected = el.classList.contains('pin-selected')
      const isLive = el.querySelector('.pin-live-ring') !== null
      const isFav = el.querySelector('.pin-badge-heart') !== null
      entries.push({
        el, nameEl,
        priority: isSelected ? 4 : isLive ? 3 : isFav ? 2 : 1,
      })
    }

    entries.sort((a, b) => b.priority - a.priority)

    const occupied: DOMRect[] = []
    for (const { nameEl, priority } of entries) {
      if (priority === 4) {
        // Selected pin name is always shown via CSS .pin-selected .pin-name
        nameEl.style.visibility = ''
        const r = nameEl.getBoundingClientRect()
        if (r.width > 0) occupied.push(r)
        continue
      }
      nameEl.style.visibility = 'visible'
      const r = nameEl.getBoundingClientRect()
      if (r.width === 0) continue

      let overlaps = false
      for (const occ of occupied) {
        if (!(r.right < occ.left || r.left > occ.right || r.bottom < occ.top || r.top > occ.bottom)) {
          overlaps = true
          break
        }
      }
      if (overlaps) {
        nameEl.style.visibility = 'hidden'
      } else {
        occupied.push(r)
      }
    }
  }

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
          if (!mounted) return
          const container = mapContainerRef.current
          if (container) container.classList.toggle('map-zoom-13', map.getZoom() >= 13)
          updateMarkers()
        })

        map.on('zoom', () => {
          const container = mapContainerRef.current
          if (container) container.classList.toggle('map-zoom-13', map.getZoom() >= 13)
          requestAnimationFrame(() => checkNameCollisions())
        })

        map.on('moveend', () => {
          requestAnimationFrame(() => checkNameCollisions())
        })

        map.on('rotate', () => {
          setBearing(map.getBearing())
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

  function handleFilterClick() {
    if (filterMsgTimerRef.current) clearTimeout(filterMsgTimerRef.current)
    setShowFilterMsg(true)
    filterMsgTimerRef.current = setTimeout(() => setShowFilterMsg(false), 2500)
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
    // Immediately update marker visuals (don't wait for React re-render)
    const oldId = selectedVenueIdRef.current
    if (oldId) {
      const oldEntry = markersRef.current.get(oldId)
      if (oldEntry) {
        oldEntry.el.classList.remove('pin-selected')
        oldEntry.el.style.zIndex = ''
      }
    }
    const newEntry = markersRef.current.get(venue.id)
    if (newEntry) {
      newEntry.el.classList.add('pin-selected')
      newEntry.el.style.zIndex = '999'
    }

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

        <div
          style={{ height: 44, borderRadius: 22, background: '#23232F', display: 'flex', alignItems: 'center' }}
          role="group" aria-label={dict.map.all + ' / ' + dict.map.favorites}
        >
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

        {/* Filter — active pink, panel not yet implemented */}
        <button
          style={{
            width: 44, height: 44, borderRadius: 22,
            background: '#FF4D8D', color: '#1A0710',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
          aria-label={dict.map.filter}
          onClick={handleFilterClick}
        >
          <IconFilter size={20} color="#1A0710" />
        </button>
      </div>

      {/* Compass — shown when map is rotated */}
      {bearing !== 0 && (
        <button
          style={{
            position: 'absolute', right: 16, top: 108,
            width: 44, height: 44, borderRadius: 22,
            background: '#F4F2FF',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)', zIndex: 10,
            border: 0,
          }}
          onClick={() => mapRef.current?.easeTo({ bearing: 0, duration: 400 })}
          aria-label={dict.map.compassLabel}
        >
          <svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true"
            style={{ transform: `rotate(${-bearing}deg)`, transition: 'transform 100ms' }}>
            <path d="M12 2l4 10h-8z" fill="#FF4D8D" />
            <path d="M12 22l-4-10h8z" fill="#5D5677" />
            <circle cx="12" cy="12" r="1.6" fill="#111118" />
          </svg>
        </button>
      )}

      {/* Filter coming soon toast */}
      {showFilterMsg && (
        <div style={{
          position: 'absolute',
          bottom: panelOpen ? 230 : 112,
          left: '50%',
          transform: 'translateX(-50%)',
          background: '#1C1C27',
          color: '#F4F2FF',
          padding: '10px 20px',
          borderRadius: 20,
          fontSize: 14,
          fontWeight: 500,
          zIndex: 30,
          boxShadow: '0 4px 16px rgba(0,0,0,0.5)',
          border: '1px solid #2E2D3C',
          whiteSpace: 'nowrap',
          fontFamily: "'Outfit', sans-serif",
          pointerEvents: 'none',
        }}>
          {dict.map.filterComingSoon}
        </div>
      )}

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
