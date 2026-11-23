import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { EventsData, Language, Event, Venue } from '../core/types'
import { getEventType, eventIconKey } from '../core/eventType'
import { getVenueEvents, getPrimaryEvent, isEventPulsing } from '../core/events'
import { getToday, toDateString, getUpcomingDays, getYesterday, isTomorrow } from '../core/day'
import { isFavorite } from '../core/store'
import { visibleEvents, nearestVisibleDay } from '../core/visible'
import { matchesFilter, isDefaultFilter, filterBadgeCount, DEFAULT_FILTER, type EventFilter, type FilterItem } from '../core/filter'
import { FilterSheet } from '../components/FilterSheet'
import { FilterEmptyCard } from '../components/FilterEmptyCard'
import { getDict } from '../i18n'
import { formatDayLabel } from '../i18n'
import { loadMapStyle, MAP_MIN_ZOOM } from '../map/mapStyle'
import { initPinShadows } from '../map/markers'
import type { MarkerData } from '../map/markers'
import { isNightMode, NIGHT_DAY } from '../core/night'
import { PIN_CSS } from '../map/pinCss'
import { checkPinOverlaps, checkNameCollisions } from '../map/collisions'
import { syncMarkers } from '../map/markerSync'
import { useNightMode, usePendingSelect } from '../map/useNightMode'
import { useUserLocation } from '../map/useUserLocation'
import {
  MapTopBar, MapCompass, MapLocationButton, MapAttribution, MapArrowButtons,
} from '../map/MapControls'
import { EventPanel } from '../components/EventPanel'
import { DaySelector } from '../components/DaySelector'

const PRAGUE_CENTER: [number, number] = [14.4208, 50.0880]
const PRAGUE_BOUNDS: maplibregl.LngLatBoundsLike = [[13.90, 49.90], [14.90, 50.26]]

interface Props {
  data: EventsData
  lang: Language
  isVisible?: boolean
  onEventOpen: (eventId: string) => void
  pendingSelect?: { venueId: string; date: string } | null
  onPendingSelectHandled?: () => void
  /** Reports whether the event panel at the bottom is open (task 055: update card hides under it). */
  onPanelOpenChange?: (open: boolean) => void
  /** Task 075: shared filter (Mapa and Akcie) */
  filter?: EventFilter
  onFilterChange?: (f: EventFilter) => void
}

export function MapPage({ data, lang, isVisible = true, onEventOpen, pendingSelect, onPendingSelectHandled, onPanelOpenChange, filter = DEFAULT_FILTER, onFilterChange }: Props) {
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const markersRef = useRef<Map<string, { marker: maplibregl.Marker; el: HTMLElement }>>(new Map())

  const now = new Date()
  const [selectedDay, setSelectedDay] = useState(() => isNightMode(data, now) ? NIGHT_DAY : getToday(now))
  const [showFavorites, setShowFavorites] = useState(false)
  const [selectedVenueId, setSelectedVenueId] = useState<string | null>(null)
  const [showDaySelector, setShowDaySelector] = useState(false)
  const [showAttribution, setShowAttribution] = useState(false)
  const [panelKey, setPanelKey] = useState(0)
  const [panelAnimated, setPanelAnimated] = useState(false)
  const [bearing, setBearing] = useState(0)
  const [showFilterSheet, setShowFilterSheet] = useState(false)

  const leavingMarkersRef = useRef<Map<string, { marker: maplibregl.Marker; el: HTMLElement; timerId: ReturnType<typeof setTimeout>; cancelled: boolean }>>(new Map())
  const updateMarkersRef = useRef<(drop?: boolean) => void>(() => {})
  const isVisibleRef = useRef(isVisible)
  const selectedVenueIdRef = useRef<string | null>(null)
  const dataRef = useRef(data)
  const selectedDayRef = useRef(selectedDay)
  const showFavoritesRef = useRef(showFavorites)
  const panelOpenRef = useRef(false)
  const openPanelRef = useRef<(venueId: string) => void>(() => {})
  const closePanelRef = useRef<() => void>(() => {})
  const toggleRef = useRef<HTMLDivElement>(null)
  const [toggleWidth, setToggleWidth] = useState(999)
  const pendingPanelOpenRef = useRef<string | null>(null)
  const pairsRef = useRef<Map<string, string>>(new Map())
  const combinedLabelRef = useRef<HTMLElement | null>(null)
  const combinedMarkerRef = useRef<maplibregl.Marker | null>(null)
  // Task 092: true from the map's 'load' event.  map.loaded() is false while tiles
  // load (e.g. right after the hidden map is shown), which skipped pin updates.
  const mapReadyRef = useRef(false)

  useEffect(() => { selectedVenueIdRef.current = selectedVenueId }, [selectedVenueId])
  // Sync pin visual state whenever selection changes (e.g. deselect on back/map-click)
  useEffect(() => {
    if (mapReadyRef.current) updateMarkersRef.current()
  }, [selectedVenueId])
  useEffect(() => { dataRef.current = data }, [data])
  useEffect(() => { selectedDayRef.current = selectedDay }, [selectedDay])
  useEffect(() => { showFavoritesRef.current = showFavorites }, [showFavorites])
  useEffect(() => { isVisibleRef.current = isVisible }, [isVisible])

  // Task 075: events that pass the filter (undefined = default filter, nothing to check)
  const eventFilter = useMemo(
    () => isDefaultFilter(filter) ? undefined : (e: Event, v: Venue) => matchesFilter(e, v, filter),
    [filter],
  )
  const eventFilterRef = useRef(eventFilter)
  eventFilterRef.current = eventFilter

  // Night mode hook
  const showNight = useNightMode({ data, selectedDayRef, pendingPanelOpenRef, setSelectedDay })

  // Resize map when it becomes visible again; also process any pending panel open.
  // Task 092: runs before the "Na mape" effect below, so the map has its real size
  // before it is centred on the venue.
  useEffect(() => {
    if (isVisible && mapRef.current && mapReadyRef.current) {
      mapRef.current.resize()
      updateMarkersRef.current(true) // map opened: pins drop (task 081)
    }
  }, [isVisible])

  // Handle external "Na mape" selection
  const forcePendingUpdateRef = useRef(() => {})
  forcePendingUpdateRef.current = () => {
    if (mapReadyRef.current && isVisibleRef.current) updateMarkersRef.current()
  }
  usePendingSelect(pendingSelect, data, pendingPanelOpenRef, setSelectedDay, onPendingSelectHandled,
    () => forcePendingUpdateRef.current())

  useEffect(() => {
    const el = toggleRef.current
    if (!el) return
    const obs = new ResizeObserver(entries => {
      setToggleWidth(entries[0]?.contentRect.width ?? 999)
    })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  openPanelRef.current = (venueId: string) => {
    const isNew = venueId !== selectedVenueIdRef.current
    const wasOpen = panelOpenRef.current
    if (!wasOpen) {
      history.pushState({ panel: 'open' }, '')
      panelOpenRef.current = true
    }
    if (isNew) {
      setPanelKey(k => k + 1)
      setPanelAnimated(!wasOpen)
    }
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
    function onPopState(event: PopStateEvent) {
      if (event.state?.panel === 'open') {
        panelOpenRef.current = true
      } else if (panelOpenRef.current && !window.location.hash.includes('/akcia/')) {
        panelOpenRef.current = false
        setSelectedVenueId(null)
        setPanelAnimated(false)
      }
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  // Inject CSS once
  useEffect(() => {
    const style = document.createElement('style')
    style.textContent = PIN_CSS
    document.head.appendChild(style)
    return () => { document.head.removeChild(style) }
  }, [])

  const availableDates = useMemo(
    () => new Set(data.events.map(e => e.date)),
    [data.events]
  )

  const buildMarkers = useCallback((): MarkerData[] => {
    const curNow = new Date()
    const venueById = Object.fromEntries(data.venues.map(v => [v.id, v]))

    if (import.meta.env.DEV && new URLSearchParams(window.location.search).has('debugPair')) {
      return data.venues.map(venue => {
        const events = getVenueEvents(data.events, venue.id, getToday(curNow), curNow, venue.character, venue.closing)
        const primary = getPrimaryEvent(events)
        const eventType = primary ? getEventType(primary.formats, primary.primary_format) : 'other'
        const iconKey = primary ? eventIconKey(primary.formats, primary.primary_format) : 'culture'
        return {
          venueId: venue.id, name: venue.name, eventType, iconKey,
          isFavorite: isFavorite(venue.id),
          isLive: primary ? isEventPulsing(primary, venue.character, venue.closing, curNow) : false,
          extraCount: Math.max(0, events.length - 1),
          lat: venue.lat, lng: venue.lng,
        }
      })
    }

    const vm = visibleEvents(data, selectedDay, curNow, { favoritesOnly: showFavorites, isFavorite, eventFilter })
    return [...vm.entries()].map(([venueId, events]) => {
      const venue = venueById[venueId]!
      const primary = getPrimaryEvent(events)
      const eventType = primary ? getEventType(primary.formats, primary.primary_format) : 'other'
      const iconKey = primary ? eventIconKey(primary.formats, primary.primary_format) : 'culture'
      return {
        venueId, name: venue.name, eventType, iconKey,
        isFavorite: isFavorite(venueId),
        isLive: primary ? isEventPulsing(primary, venue.character, venue.closing, curNow) : false,
        extraCount: Math.max(0, events.length - 1),
        lat: venue.lat, lng: venue.lng,
      }
    })
  }, [data, selectedDay, showFavorites, eventFilter])

  const updateMarkers = useCallback((drop = false) => {
    const map = mapRef.current
    if (!map) return
    const markerData = buildMarkers()
    syncMarkers({
      map, markerData, drop,
      markers: markersRef.current,
      leavingMarkers: leavingMarkersRef.current,
      selectedVenueIdRef,
      pendingPanelOpenRef,
      pairsRef,
      combinedLabelRef,
      combinedMarkerRef,
      dataRef,
      openPanel: (id) => openPanelRef.current(id),
      closePanel: () => closePanelRef.current(),
    })
  }, [buildMarkers])

  const runCollisions = useCallback(() => {
    const map = mapRef.current
    if (!map) return
    requestAnimationFrame(() => {
      checkPinOverlaps(map, markersRef.current, pairsRef.current)
      checkNameCollisions(
        map, markersRef.current, pairsRef.current,
        combinedLabelRef.current, combinedMarkerRef.current,
        (id) => dataRef.current.venues.find(v => v.id === id)?.name ?? id,
      )
    })
  }, [])

  // User location hook
  const { userLocation, locationLoading, handleLocationClick, tryInitialLocation, stopWatch, reattachUserMarker } =
    useUserLocation({ mapRef, dataRef, selectedDayRef, showFavoritesRef, isVisibleRef, isVisible, eventFilterRef })

  // Init map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return
    let mounted = true

    let removeVisListener = () => {}

    // Task 092: a mobile browser may drop the WebGL context of a map left in the
    // background for long.  MapLibre then draws only black (tiles, glyphs and images
    // were GPU objects of the lost context), the HTML pins stay.  The map is created
    // again with the same view; pins, day, filter and the open panel are kept
    // (React state; the pins are moved to the new map).
    let recreating = false
    function recreateMap() {
      const old = mapRef.current
      if (!old || recreating || !mounted) return
      recreating = true
      const view = { center: old.getCenter(), zoom: old.getZoom(), bearing: old.getBearing(), pitch: old.getPitch() }
      removeVisListener()
      mapReadyRef.current = false
      for (const l of leavingMarkersRef.current.values()) { clearTimeout(l.timerId); l.marker.remove() }
      leavingMarkersRef.current.clear()
      old.remove()
      mapRef.current = null
      void initMap(view).finally(() => { recreating = false })
    }

    async function initMap(view?: { center: maplibregl.LngLat; zoom: number; bearing: number; pitch: number }) {
      try {
        initPinShadows()
        const style = await loadMapStyle()
        if (!mounted || !mapContainerRef.current) return

        const map = new maplibregl.Map({
          container: mapContainerRef.current,
          style: style as maplibregl.StyleSpecification,
          center: view?.center ?? PRAGUE_CENTER,
          zoom: view?.zoom ?? 12,
          bearing: view?.bearing ?? 0,
          pitch: view?.pitch ?? 0,
          minZoom: MAP_MIN_ZOOM,
          maxBounds: PRAGUE_BOUNDS,
          attributionControl: false,
        })
        mapRef.current = map
        // dev only: Playwright tests read the map state (task 092)
        if (import.meta.env.DEV) (window as unknown as { __map?: maplibregl.Map }).__map = map
        if (view) {
          // recreated map: keep the existing pins (no new appear animation)
          for (const { marker } of markersRef.current.values()) marker.addTo(map)
          reattachUserMarker(map)
        }

        const combinedLabelEl = document.createElement('div')
        combinedLabelEl.className = 'pin-combined-name'
        const combinedMarker = new maplibregl.Marker({
          element: combinedLabelEl,
          anchor: 'top',
          offset: [0, 4],
        })
          .setLngLat(PRAGUE_CENTER)
          .addTo(map)
        combinedLabelRef.current = combinedLabelEl
        combinedMarkerRef.current = combinedMarker

        const canvas = map.getCanvas()
        canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault() })
        // a restored context has none of the map's textures -> new map (task 092)
        canvas.addEventListener('webglcontextrestored', () => recreateMap())
        let lostTimer: ReturnType<typeof setTimeout> | undefined
        const contextLost = () => (map.painter as unknown as { context?: { gl?: WebGLRenderingContext } } | undefined)
          ?.context?.gl?.isContextLost() ?? false

        function handleVisChange() {
          if (document.visibilityState === 'visible') {
            // context still lost on return: wait briefly for the browser to restore it
            // ('webglcontextrestored' recreates the map), otherwise create it again
            if (contextLost()) {
              clearTimeout(lostTimer)
              lostTimer = setTimeout(() => { if (mapRef.current === map && contextLost()) recreateMap() }, 600)
              return
            }
            map.triggerRepaint()
            if (isVisibleRef.current) {
              map.resize()
              updateMarkersRef.current()
            }
          }
        }
        document.addEventListener('visibilitychange', handleVisChange)
        removeVisListener = () => {
          clearTimeout(lostTimer)
          document.removeEventListener('visibilitychange', handleVisChange)
        }

        map.on('click', (e) => {
          if ((e.originalEvent.target as HTMLElement).classList.contains('maplibregl-canvas')) {
            closePanelRef.current()
          }
        })

        map.on('load', () => {
          if (!mounted) return
          mapReadyRef.current = true
          const container = mapContainerRef.current
          if (container) container.classList.toggle('map-zoom-13', map.getZoom() >= 13)
          updateMarkersRef.current()
          if (!view) tryInitialLocation(map)
        })

        map.on('zoom', () => {
          const container = mapContainerRef.current
          if (!container) return
          container.classList.toggle('map-zoom-13', map.getZoom() >= 13)
          requestAnimationFrame(() => {
            checkPinOverlaps(map, markersRef.current, pairsRef.current)
            checkNameCollisions(map, markersRef.current, pairsRef.current,
              combinedLabelRef.current, combinedMarkerRef.current,
              (id) => dataRef.current.venues.find(v => v.id === id)?.name ?? id)
          })
        })

        map.on('zoomend', () => {
          requestAnimationFrame(() => {
            checkPinOverlaps(map, markersRef.current, pairsRef.current)
            checkNameCollisions(map, markersRef.current, pairsRef.current,
              combinedLabelRef.current, combinedMarkerRef.current,
              (id) => dataRef.current.venues.find(v => v.id === id)?.name ?? id)
          })
        })

        map.on('moveend', () => {
          requestAnimationFrame(() => {
            checkPinOverlaps(map, markersRef.current, pairsRef.current)
            checkNameCollisions(map, markersRef.current, pairsRef.current,
              combinedLabelRef.current, combinedMarkerRef.current,
              (id) => dataRef.current.venues.find(v => v.id === id)?.name ?? id)
          })
        })

        map.on('rotate', () => setBearing(map.getBearing()))

      } catch (err) {
        console.error('Map init failed', err)
      }
    }

    void initMap()
    return () => {
      mounted = false
      removeVisListener()
      stopWatch()
      if (mapRef.current && !mapRef.current.loaded()) {
        mapRef.current.remove()
        mapRef.current = null
        markersRef.current.clear()
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  updateMarkersRef.current = updateMarkers

  // Pins drop (task 081) only when the user changed the day, filter or
  // Všetko | Obľúbené, not on background data refreshes.
  const dropKeyRef = useRef('')
  useEffect(() => {
    const key = `${selectedDay}|${showFavorites}|${JSON.stringify(eventFilter)}`
    const drop = dropKeyRef.current !== '' && dropKeyRef.current !== key
    dropKeyRef.current = key
    if (mapReadyRef.current) updateMarkers(drop)
  }, [updateMarkers]) // eslint-disable-line react-hooks/exhaustive-deps

  // Refresh every 60s when map is visible
  useEffect(() => {
    const interval = setInterval(() => {
      if (mapReadyRef.current && isVisibleRef.current) updateMarkersRef.current()
    }, 60000)
    return () => clearInterval(interval)
  }, [])

  function handleFilterClick() {
    setShowFilterSheet(true)
  }

  // Sorted venues for ‹ › navigation (by longitude: west → east)
  const curNow = new Date()
  const venueMap = Object.fromEntries(data.venues.map(v => [v.id, v]))
  const panelVenue = selectedVenueId ? venueMap[selectedVenueId] : null
  const visibleMapForPanel = visibleEvents(data, selectedDay, curNow, { favoritesOnly: showFavorites, isFavorite, eventFilter })
  const panelEvents = panelVenue ? (visibleMapForPanel.get(panelVenue.id) ?? []) : []
  const sortedVenues = [...data.venues
    .filter(v => visibleMapForPanel.has(v.id))
  ].sort((a, b) => a.lng - b.lng)

  const selIdx = selectedVenueId ? sortedVenues.findIndex(v => v.id === selectedVenueId) : -1
  const prevVenue = selIdx > 0 ? sortedVenues[selIdx - 1] : null
  const nextVenue = selIdx >= 0 && selIdx < sortedVenues.length - 1 ? sortedVenues[selIdx + 1] : null

  function handleArrow(venue: { id: string; lng: number; lat: number }) {
    const oldId = selectedVenueIdRef.current
    if (oldId) {
      const oldEntry = markersRef.current.get(oldId)
      if (oldEntry) { oldEntry.el.classList.remove('pin-selected'); oldEntry.el.style.zIndex = '' }
    }
    const newEntry = markersRef.current.get(venue.id)
    if (newEntry) { newEntry.el.classList.add('pin-selected'); newEntry.el.style.zIndex = '10' }
    runCollisions()
    openPanelRef.current(venue.id)
    mapRef.current?.easeTo({
      center: [venue.lng, venue.lat],
      padding: { bottom: 240, top: 80, left: 60, right: 60 },
      duration: 320,
    })
  }

  const calendarToday = toDateString(curNow)
  const noonToday = new Date(calendarToday + 'T12:00:00')
  const days = showNight ? getUpcomingDays(4, noonToday) : getUpcomingDays(5, curNow)
  const selectedDayLabel = formatDayLabel(selectedDay, lang, curNow)
  const panelOpen = panelVenue && panelEvents.length > 0
  useEffect(() => { onPanelOpenChange?.(!!panelOpen) }, [panelOpen, onPanelOpenChange])

  // Task 075: filter panel items (results before the filter) and empty result card
  const filterItems: FilterItem[] = showFilterSheet
    ? [...visibleEvents(data, selectedDay, curNow, { favoritesOnly: showFavorites, isFavorite }).entries()]
      .flatMap(([vid, evs]) => evs.map(event => ({ event, venue: venueMap[vid] })))
    : []
  const filterEmpty = isVisible && !!eventFilter && visibleMapForPanel.size === 0 && !showFilterSheet
  const nearestDay = filterEmpty
    ? nearestVisibleDay(data, selectedDay === NIGHT_DAY ? getYesterday(curNow) : selectedDay, curNow,
      { favoritesOnly: showFavorites, isFavorite, eventFilter })
    : null
  const fDict = getDict(lang).filter
  const filterEmptyText = selectedDay === NIGHT_DAY ? fDict.emptyNight
    : selectedDay === calendarToday ? fDict.emptyToday
    : isTomorrow(selectedDay, curNow) ? fDict.emptyTomorrow
    : fDict.emptyDay

  const leftCount = selIdx > 0 ? selIdx : 0
  const rightCount = selIdx >= 0 && selIdx < sortedVenues.length - 1 ? sortedVenues.length - 1 - selIdx : 0

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      <MapTopBar
        lang={lang}
        selectedDayLabel={selectedDayLabel}
        showFavorites={showFavorites}
        toggleRef={toggleRef}
        toggleWidth={toggleWidth}
        onDaySelectorOpen={() => setShowDaySelector(true)}
        onFavoritesChange={setShowFavorites}
        onFilterClick={handleFilterClick}
        filterBadge={filterBadgeCount(filter)}
      />

      <MapCompass bearing={bearing} lang={lang} mapRef={mapRef} />

      {filterEmpty && (
        <FilterEmptyCard
          text={filterEmptyText}
          nearestLabel={nearestDay ? `${fDict.nearest}: ${formatDayLabel(nearestDay, lang, curNow)}` : null}
          onNearest={() => nearestDay && setSelectedDay(nearestDay)}
          clearLabel={fDict.clear}
          onClear={() => onFilterChange?.(DEFAULT_FILTER)}
        />
      )}

      {showFilterSheet && (
        <FilterSheet
          lang={lang}
          mode="venues"
          items={filterItems}
          allEvents={data.events}
          venues={data.venues}
          filter={filter}
          onChange={f => onFilterChange?.(f)}
          onClose={() => setShowFilterSheet(false)}
        />
      )}

      <MapLocationButton
        lang={lang}
        locationLoading={locationLoading}
        onClick={handleLocationClick}
      />

      <MapAttribution
        showAttribution={showAttribution}
        onToggle={() => setShowAttribution(a => !a)}
      />

      {panelOpen && (
        <MapArrowButtons
          prevVenue={prevVenue}
          nextVenue={nextVenue}
          leftCount={leftCount}
          rightCount={rightCount}
          onPrev={() => prevVenue && handleArrow(prevVenue)}
          onNext={() => nextVenue && handleArrow(nextVenue)}
        />
      )}

      {panelOpen && (
        <EventPanel
          key={panelKey}
          events={panelEvents}
          venue={panelVenue!}
          lang={lang}
          userLocation={userLocation}
          className={panelAnimated ? 'event-panel-enter' : undefined}
          onClose={() => closePanelRef.current()}
          onEventOpen={onEventOpen}
        />
      )}

      {showDaySelector && (
        <DaySelector
          days={days}
          selectedDay={selectedDay}
          lang={lang}
          now={curNow}
          showNight={showNight}
          availableDates={availableDates}
          onSelect={day => setSelectedDay(day)}
          onClose={() => setShowDaySelector(false)}
        />
      )}
    </div>
  )
}
