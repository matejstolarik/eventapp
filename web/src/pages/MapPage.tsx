import { useEffect, useRef, useState, useCallback } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { EventsData, Language, EventType } from '../core/types'
import { getEventType } from '../core/eventType'
import { getVenueEvents, getActiveVenueIds, getPrimaryEvent, isEventLive } from '../core/events'
import { getToday, getUpcomingDays } from '../core/day'
import { isFavorite } from '../core/store'
import { getDict, formatDayLabel } from '../i18n'
import { loadDarkMapStyle } from '../map/mapStyle'
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
  const [isDotMode, setIsDotMode] = useState(false)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationLoading, setLocationLoading] = useState(false)
  const userMarkerRef = useRef<maplibregl.Marker | null>(null)

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
        // Mutate existing element in-place — never replaceWith() as that breaks MapLibre's
        // internal _element reference, causing all markers to scatter on the next update.
        updatePillElement(existing.el, md, isSelected, isDotMode)
      } else {
        const el = createPillElement(md, isSelected, isDotMode)
        el.addEventListener('click', () => setSelectedVenueId(id => id === md.venueId ? null : md.venueId))
        const marker = new maplibregl.Marker({ element: el, anchor: 'bottom', offset: [0, 0] })
          .setLngLat([md.lng, md.lat])
          .addTo(map)
        markersRef.current.set(md.venueId, { marker, el })
      }
    }

    // Resolve overlaps after all markers are placed/updated
    resolveMarkerOverlaps(
      Array.from(markersRef.current.values()).map(({ marker, el }) => ({
        el,
        setOffset: (o: [number, number]) => marker.setOffset(o),
      }))
    )
  }, [buildMarkers, selectedVenueId, isDotMode])

  // Init map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return
    let mounted = true

    async function initMap() {
      try {
        const style = await loadDarkMapStyle()
        if (!mounted || !mapContainerRef.current) return

        const map = new maplibregl.Map({
          container: mapContainerRef.current,
          style: style as maplibregl.StyleSpecification,
          center: PRAGUE_CENTER,
          zoom: 12,
          maxBounds: PRAGUE_BOUNDS,
          attributionControl: { compact: true },
          logoPosition: 'bottom-right'
        })
        mapRef.current = map

        map.on('zoom', () => {
          setIsDotMode(map.getZoom() < 11)
        })

        // Re-resolve overlaps after each pan/zoom (pixel positions change)
        const resolveOverlaps = () => {
          resolveMarkerOverlaps(
            Array.from(markersRef.current.values()).map(({ marker, el }) => ({
              el,
              setOffset: (o: [number, number]) => marker.setOffset(o),
            }))
          )
        }
        map.on('moveend', resolveOverlaps)
        map.on('zoomend', resolveOverlaps)

        map.on('click', (e) => {
          // Close panel if click was on the map (not a marker)
          if ((e.originalEvent.target as HTMLElement).classList.contains('maplibregl-canvas')) {
            setSelectedVenueId(null)
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

      {/* Event panel */}
      {panelVenue && panelEvents.length > 0 && (
        <EventPanel
          events={panelEvents}
          venue={panelVenue}
          lang={lang}
          userLocation={userLocation}
          onClose={() => setSelectedVenueId(null)}
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
