import { useEffect, useRef, useState, useCallback, useMemo } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import type { EventsData, Language } from '../core/types'
import { getEventType } from '../core/eventType'
import { getVenueEvents, getActiveVenueIds, getPrimaryEvent, isEventLive } from '../core/events'
import { getToday, getUpcomingDays } from '../core/day'
import { isFavorite } from '../core/store'
import { haversine } from '../core/distance'
import { getDict, formatDayLabel } from '../i18n'
import { loadMapStyle, MAP_MIN_ZOOM } from '../map/mapStyle'
import { createPinElement, updatePinElement, initPinShadows } from '../map/markers'
import type { MarkerData } from '../map/markers'
import { isNightTime, isNightEvent, NIGHT_DAY } from '../core/night'
import { decidePairLabel } from '../map/pairLabel'
import {
  IconChevronDown, IconFilter, IconLocation
} from '../icons'
import { EventPanel } from '../components/EventPanel'
import { DaySelector } from '../components/DaySelector'
import { AllFavsToggle } from '../components/AllFavsToggle'

const PIN_CSS = `
@keyframes pinpulse {
  0%   { transform: scale(1); opacity: 0.9; }
  70%  { transform: scale(1.9); opacity: 0; }
  100% { transform: scale(1.9); opacity: 0; }
}
@keyframes pin-appear {
  from { opacity: 0; transform: scale(0.82); }
  to   { opacity: 1; transform: scale(1); }
}
@keyframes card-slide-up {
  from { transform: translateY(100%); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

.pin-inner {
  position: relative;
  width: 50px;
  height: 64px;
  transform: translateX(var(--pin-dx, 0px)) scale(1);
  transform-origin: 50% 100%;
  transition: transform 220ms ease-out;
}
.pin-selected .pin-inner {
  transform: translateX(var(--pin-dx, 0px)) scale(1.22);
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
  border: 2px solid var(--pc, #fff);
  animation: pinpulse 1.6s ease-out infinite;
  transform-origin: center;
  z-index: 0;
  pointer-events: none;
}
@media (prefers-reduced-motion: reduce) {
  .pin-live-ring {
    animation: none;
    opacity: 0.5;
    border-width: 4px;
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
  left: 50% !important;
  right: auto !important;
  transform: translateX(-50%) !important;
  text-align: center !important;
}
.map-zoom-13 .pin-name {
  display: block;
}

/* Combined pair label — maplibregl.Marker element, moves with the map */
.pin-combined-name {
  white-space: nowrap;
  font-family: 'Outfit', sans-serif;
  font-size: 12px;
  font-weight: 600;
  color: #E4E2EE;
  text-shadow: 0 0 3px #111118, 0 0 3px #111118, 0 1px 2px #111118;
  letter-spacing: 0.01em;
  pointer-events: none;
  display: none;
  z-index: 10;
}
.map-zoom-13 .pin-combined-name.is-active {
  display: block;
}

.pin-new .pin-inner {
  animation: pin-appear 180ms ease-out both;
}
@media (prefers-reduced-motion: reduce) {
  .pin-new .pin-inner { animation: none; }
}

.event-panel-enter {
  animation: card-slide-up 150ms ease-out both;
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
  isVisible?: boolean
  onEventOpen: (eventId: string) => void
  pendingSelect?: { venueId: string; date: string } | null
  onPendingSelectHandled?: () => void
}

export function MapPage({ data, lang, isVisible = true, onEventOpen, pendingSelect, onPendingSelectHandled }: Props) {
  const dict = getDict(lang)
  const mapContainerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const markersRef = useRef<Map<string, { marker: maplibregl.Marker; el: HTMLElement }>>(new Map())
  const currentMarkerDataRef = useRef<MarkerData[]>([])

  const now = new Date()
  const [selectedDay, setSelectedDay] = useState(() => getToday(now))
  const [showFavorites, setShowFavorites] = useState(false)
  const [selectedVenueId, setSelectedVenueId] = useState<string | null>(null)
  const [showDaySelector, setShowDaySelector] = useState(false)
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationLoading, setLocationLoading] = useState(false)
  const [showAttribution, setShowAttribution] = useState(false)
  const [panelKey, setPanelKey] = useState(0)
  const [panelAnimated, setPanelAnimated] = useState(false)
  const [bearing, setBearing] = useState(0)
  const [showFilterMsg, setShowFilterMsg] = useState(false)
  const [showNight, setShowNight] = useState(() => isNightTime(new Date()))

  const userMarkerRef = useRef<maplibregl.Marker | null>(null)
  const filterMsgTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
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

  useEffect(() => { selectedVenueIdRef.current = selectedVenueId }, [selectedVenueId])
  useEffect(() => { dataRef.current = data }, [data])
  useEffect(() => { selectedDayRef.current = selectedDay }, [selectedDay])
  useEffect(() => { showFavoritesRef.current = showFavorites }, [showFavorites])
  useEffect(() => { isVisibleRef.current = isVisible }, [isVisible])

  // External "Na mape" selection: set day and queue panel open after markers update
  useEffect(() => {
    if (!pendingSelect) return
    setSelectedDay(pendingSelect.date)
    pendingPanelOpenRef.current = pendingSelect.venueId
    onPendingSelectHandled?.()
  }, [pendingSelect, onPendingSelectHandled])

  useEffect(() => {
    const el = toggleRef.current
    if (!el) return
    const obs = new ResizeObserver(entries => {
      setToggleWidth(entries[0]?.contentRect.width ?? 999)
    })
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  // Resize map when it becomes visible again (was display:none)
  useEffect(() => {
    if (isVisible && mapRef.current?.loaded()) {
      mapRef.current.resize()
    }
  }, [isVisible])

  // Night mode: auto-switch at midnight, auto-disable at 5:00
  useEffect(() => {
    const checkNight = () => {
      const isNight = isNightTime(new Date())
      setShowNight(isNight)
      // If selected day is 'night' but night mode ended, revert to today
      if (!isNight && selectedDayRef.current === NIGHT_DAY) {
        setSelectedDay(getToday(new Date()))
      }
    }

    // Schedule next check at midnight or 5:00
    const scheduleNext = () => {
      const n = new Date()
      const h = n.getHours()
      let targetMs: number
      if (h >= 5) {
        // Schedule at midnight
        const midnight = new Date(n)
        midnight.setDate(midnight.getDate() + 1)
        midnight.setHours(0, 0, 10, 0)
        targetMs = midnight.getTime() - n.getTime()
      } else {
        // Schedule at 5:00
        const five = new Date(n)
        five.setHours(5, 0, 10, 0)
        targetMs = five.getTime() - n.getTime()
      }
      return setTimeout(() => { checkNight(); scheduleNext() }, Math.max(targetMs, 1000))
    }

    const timer = scheduleNext()
    return () => clearTimeout(timer)
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
      setPanelAnimated(!wasOpen) // animate only on first open from closed
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
        // Returned from event page back to the card state — keep panel open
        panelOpenRef.current = true
      } else if (panelOpenRef.current && !window.location.hash.includes('/akcia/')) {
        // Left the card state (pressed Back from card).
        // Guard: Chrome fires popstate for hash navigation TO event page (state=null,
        // hash=#/akcia/...) — in that case the hash already changed, so ignore it.
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

    let venues
    if (import.meta.env.DEV && new URLSearchParams(window.location.search).has('debugPair')) {
      venues = data.venues
    } else if (selectedDay === NIGHT_DAY) {
      const nightDate = getToday(curNow)
      venues = data.venues.filter(v => {
        const events = getVenueEvents(data.events, v.id, nightDate, curNow)
        return events.some(e => isNightEvent(e, v.character, curNow))
      })
    } else {
      const activeIds = getActiveVenueIds(data.events, selectedDay, curNow)
      venues = showFavorites
        ? data.venues.filter(v => activeIds.has(v.id) && isFavorite(v.id))
        : data.venues.filter(v => activeIds.has(v.id))
    }

    return venues.map(venue => {
      const dateKey = selectedDay === NIGHT_DAY ? getToday(curNow) : selectedDay
      const events = getVenueEvents(data.events, venue.id, dateKey, curNow)
      const primary = getPrimaryEvent(events, curNow)
      const eventType = primary ? getEventType(primary.formats) : 'other'
      const isLive = primary ? isEventLive(primary, curNow) : false
      void venueById
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
    currentMarkerDataRef.current = markerData
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
          const map = mapRef.current
          if (selectedVenueIdRef.current === venueId) {
            el.classList.remove('pin-selected')
            el.style.zIndex = ''
            closePanelRef.current()
          } else {
            const oldId = selectedVenueIdRef.current
            if (oldId) {
              const oldEntry = markersRef.current.get(oldId)
              if (oldEntry) {
                oldEntry.el.classList.remove('pin-selected')
                oldEntry.el.style.zIndex = ''
              }
            }
            el.classList.add('pin-selected')
            el.style.zIndex = '10'
            openPanelRef.current(venueId)

            // Pan to reveal selected pin if behind UI
            if (map) {
              const venue = dataRef.current.venues.find(v => v.id === venueId)
              if (venue) {
                const pt = map.project([venue.lng, venue.lat])
                const cv = map.getCanvas().getBoundingClientRect()
                const isCovered = pt.y < 110 || pt.y > cv.height - 260 || pt.x < 50 || pt.x > cv.width - 50
                if (isCovered) {
                  map.easeTo({
                    center: [venue.lng, venue.lat],
                    padding: { top: 100, bottom: 240, left: 60, right: 60 },
                    duration: 320,
                  })
                }
              }
            }
          }
        })
        const marker = new maplibregl.Marker({ element: el, anchor: 'bottom', offset: [0, 0] })
          .setLngLat([md.lng, md.lat])
          .addTo(map)

        el.classList.add('pin-new')
        setTimeout(() => el.classList.remove('pin-new'), 300)

        markersRef.current.set(venueId, { marker, el })
      }
    }

    // Handle external "Na mape" navigation
    if (pendingPanelOpenRef.current) {
      const vid = pendingPanelOpenRef.current
      pendingPanelOpenRef.current = null
      const entry = markersRef.current.get(vid)
      if (entry) {
        const oldId = selectedVenueIdRef.current
        if (oldId && oldId !== vid) {
          const oldEntry = markersRef.current.get(oldId)
          if (oldEntry) { oldEntry.el.classList.remove('pin-selected'); oldEntry.el.style.zIndex = '' }
        }
        entry.el.classList.add('pin-selected')
        entry.el.style.zIndex = '10'
        openPanelRef.current(vid)
        const venue = dataRef.current.venues.find(v => v.id === vid)
        if (venue && map) {
          map.easeTo({
            center: [venue.lng, venue.lat],
            padding: { top: 100, bottom: 240, left: 60, right: 60 },
            duration: 320,
          })
        }
      }
    }

    requestAnimationFrame(() => { checkPinOverlaps(); checkNameCollisions() })
  }, [buildMarkers, selectedVenueId])

  function checkNameCollisions() {
    const map = mapRef.current
    if (!map || map.getZoom() < 13) return

    // Reset combined label for this pass — re-activated below if a pair combines
    if (combinedLabelRef.current) combinedLabelRef.current.classList.remove('is-active')

    type PinEntry = { venueId: string; el: HTMLElement; nameEl: HTMLElement; priority: number }
    const entries: PinEntry[] = []

    for (const [venueId, { el }] of markersRef.current) {
      const nameEl = el.querySelector('.pin-name') as HTMLElement | null
      if (!nameEl) continue
      const isSelected = el.classList.contains('pin-selected')
      const isLive = el.querySelector('.pin-live-ring') !== null
      const isFav = el.querySelector('.pin-badge-heart') !== null
      entries.push({ venueId, el, nameEl, priority: isSelected ? 4 : isLive ? 3 : isFav ? 2 : 1 })
    }

    entries.sort((a, b) => b.priority - a.priority)

    const processedPairs = new Set<string>()
    const occupied: DOMRect[] = []

    for (const { venueId, el, nameEl, priority } of entries) {
      const partnerId = pairsRef.current.get(venueId)

      if (partnerId && !processedPairs.has(venueId)) {
        processedPairs.add(venueId)
        processedPairs.add(partnerId)

        const partnerEntry = entries.find(e => e.venueId === partnerId)
        if (!partnerEntry) continue

        const thisSelected = el.classList.contains('pin-selected')
        const partnerSelected = partnerEntry.el.classList.contains('pin-selected')

        // When one of the pair is selected: show only its own name, centered under its pin
        if (thisSelected || partnerSelected) {
          const selectedEntry = thisSelected ? { venueId, el, nameEl } : partnerEntry
          const otherEntry = thisSelected ? partnerEntry : { venueId, el, nameEl }
          otherEntry.nameEl.style.visibility = 'hidden'
          selectedEntry.nameEl.style.visibility = ''
          const r = selectedEntry.nameEl.getBoundingClientRect()
          if (r.width > 0) occupied.push(r)
          continue
        }

        // Both unselected: show centered names and check for significant overlap
        nameEl.style.visibility = 'visible'
        partnerEntry.nameEl.style.visibility = 'visible'

        const rA = nameEl.getBoundingClientRect()
        const rB = partnerEntry.nameEl.getBoundingClientRect()
        const markerA = markersRef.current.get(venueId)
        const markerB = markersRef.current.get(partnerId)

        if (rA.width > 0 && rB.width > 0 && markerA && markerB) {
          const ptA = map.project(markerA.marker.getLngLat())
          const ptB = map.project(markerB.marker.getLngLat())
          const llA = markerA.marker.getLngLat()
          const llB = markerB.marker.getLngLat()
          const decision = decidePairLabel(rA, rB, ptA, ptB, llA, llB)

          if (decision.action === 'combine' && combinedLabelRef.current && combinedMarkerRef.current) {
            nameEl.style.visibility = 'hidden'
            partnerEntry.nameEl.style.visibility = 'hidden'

            const { order, midLng, lowerLat } = decision
            let firstName: string, secondName: string
            if (order === 'west-east') {
              const [westId, eastId] = ptA.x <= ptB.x ? [venueId, partnerId] : [partnerId, venueId]
              firstName = dataRef.current.venues.find(v => v.id === westId)?.name ?? westId
              secondName = dataRef.current.venues.find(v => v.id === eastId)?.name ?? eastId
            } else {
              const [northId, southId] = ptA.y <= ptB.y ? [venueId, partnerId] : [partnerId, venueId]
              firstName = dataRef.current.venues.find(v => v.id === northId)?.name ?? northId
              secondName = dataRef.current.venues.find(v => v.id === southId)?.name ?? southId
            }

            const lbl = combinedLabelRef.current
            lbl.textContent = `${firstName} · ${secondName}`
            lbl.classList.add('is-active')
            combinedMarkerRef.current.setLngLat([midLng, lowerLat])

            const rC = lbl.getBoundingClientRect()
            if (rC.width > 0) occupied.push(rC)
          } else {
            // No significant overlap: pair members never hide each other — both always show
            for (const ne of [nameEl, partnerEntry.nameEl]) {
              ne.style.visibility = 'visible'
              const r = ne.getBoundingClientRect()
              if (r.width > 0) occupied.push(r)
            }
          }
        }
        continue
      }

      if (processedPairs.has(venueId)) continue

      // Non-pair pin: standard logic
      if (priority === 4) {
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
          overlaps = true; break
        }
      }
      if (overlaps) nameEl.style.visibility = 'hidden'
      else occupied.push(r)
    }
  }

  function checkPinOverlaps() {
    const map = mapRef.current
    if (!map) return

    type PinInfo = { venueId: string; el: HTMLElement; pt: { x: number; y: number }; lng: number }
    const pins: PinInfo[] = []
    for (const [venueId, { el, marker }] of markersRef.current) {
      const ll = marker.getLngLat()
      const pt = map.project([ll.lng, ll.lat])
      pins.push({ venueId, el, pt, lng: ll.lng })
    }

    // Reset
    pairsRef.current.clear()
    for (const { el } of pins) {
      el.style.removeProperty('--pin-dx')
    }

    for (let i = 0; i < pins.length; i++) {
      for (let j = i + 1; j < pins.length; j++) {
        const a = pins[i], b = pins[j]
        const dx = a.pt.x - b.pt.x
        const dy = a.pt.y - b.pt.y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < 40) {
          const west = a.lng <= b.lng ? a : b
          const east = a.lng <= b.lng ? b : a
          pairsRef.current.set(west.venueId, east.venueId)
          pairsRef.current.set(east.venueId, west.venueId)
          if (dist < 20) {
            const off = west === a ? -8 : 8
            a.el.style.setProperty('--pin-dx', `${off}px`)
            b.el.style.setProperty('--pin-dx', `${-off}px`)
          }
        }
      }
    }
  }

  // Init map
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return
    let mounted = true

    async function initMap() {
      try {
        initPinShadows()
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

        // Combined pair label as a maplibregl.Marker — moves with the map during panning
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

        // WebGL context loss recovery
        const canvas = map.getCanvas()
        canvas.addEventListener('webglcontextlost', (e) => { e.preventDefault() })
        canvas.addEventListener('webglcontextrestored', () => { map.triggerRepaint() })

        // Repaint on tab visibility restore
        function handleVisChange() {
          if (document.visibilityState === 'visible') {
            map.triggerRepaint()
            if (isVisibleRef.current) map.resize()
          }
        }
        document.addEventListener('visibilitychange', handleVisChange)

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

          // Initial view: check if geolocation is already granted, flyTo if near Prague
          navigator.permissions?.query({ name: 'geolocation' }).then(perm => {
            if (perm.state !== 'granted') return
            navigator.geolocation.getCurrentPosition(pos => {
              const { latitude: lat, longitude: lng } = pos.coords
              const curNow = new Date()
              const activeIds = getActiveVenueIds(dataRef.current.events, selectedDayRef.current, curNow)
              const activeVenues = dataRef.current.venues.filter(v => activeIds.has(v.id))
              if (activeVenues.length === 0) return
              const nearest = activeVenues.reduce((best, v) =>
                haversine(lat, lng, v.lat, v.lng) < haversine(lat, lng, best.lat, best.lng) ? v : best
              )
              if (haversine(lat, lng, nearest.lat, nearest.lng) <= 2) {
                map.flyTo({ center: [lng, lat], zoom: 14, duration: 1200 })
                setUserLocation({ lat, lng })
              }
            }, () => {}, { timeout: 5000 })
          }).catch(() => {})
        })

        map.on('zoom', () => {
          const container = mapContainerRef.current
          if (container) container.classList.toggle('map-zoom-13', map.getZoom() >= 13)
        })

        map.on('zoomend', () => {
          requestAnimationFrame(() => { checkPinOverlaps(); checkNameCollisions() })
        })

        map.on('moveend', () => {
          requestAnimationFrame(() => { checkPinOverlaps(); checkNameCollisions() })
        })

        map.on('rotate', () => setBearing(map.getBearing()))

        return () => { document.removeEventListener('visibilitychange', handleVisChange) }
      } catch (err) {
        console.error('Map init failed', err)
      }
    }

    void initMap()
    return () => {
      mounted = false
      // Keep map alive — MapPage is never truly unmounted in normal app flow.
      // Only clean up if something went wrong (map never finished init).
      if (mapRef.current && !mapRef.current.loaded()) {
        mapRef.current.remove()
        mapRef.current = null
        markersRef.current.clear()
      }
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
  const panelEvents = panelVenue
    ? getVenueEvents(data.events, panelVenue.id, selectedDay === NIGHT_DAY ? getToday(curNow) : selectedDay, curNow)
    : []

  const activeIds = getActiveVenueIds(data.events, selectedDay === NIGHT_DAY ? getToday(curNow) : selectedDay, curNow)
  const sortedVenues = [...data.venues
    .filter(v => activeIds.has(v.id) && (!showFavorites || isFavorite(v.id)))
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
    openPanelRef.current(venue.id)
    mapRef.current?.easeTo({
      center: [venue.lng, venue.lat],
      padding: { bottom: 240, top: 80, left: 60, right: 60 },
      duration: 320,
    })
  }

  // Responsive toggle: shrink padding → smaller font
  const togglePad = toggleWidth < 160 ? '0 6px' : toggleWidth < 200 ? '0 8px' : '0 14px'
  const toggleFontSize = toggleWidth < 140 ? 13 : 14

  const days = getUpcomingDays(14, curNow)
  const selectedDayLabel = formatDayLabel(selectedDay, lang, curNow)
  const panelOpen = panelVenue && panelEvents.length > 0

  // Arrow button style (40px, grey when disabled/at edge)
  function arrowBtnStyle(enabled: boolean): React.CSSProperties {
    return {
      position: 'absolute', bottom: 310,
      width: 40, height: 40, borderRadius: 20,
      background: enabled ? '#F4F2FF' : '#2A2838',
      color: enabled ? '#111118' : '#5D5677',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      boxShadow: enabled ? '0 4px 12px rgba(0,0,0,0.45)' : 'none',
      zIndex: 25,
      border: 'none',
      cursor: enabled ? 'pointer' : 'default',
      opacity: enabled ? 1 : 0.5,
    }
  }

  // Count badge on arrow buttons: how many venues are in each direction
  const leftCount = selIdx > 0 ? selIdx : 0
  const rightCount = selIdx >= 0 && selIdx < sortedVenues.length - 1 ? sortedVenues.length - 1 - selIdx : 0

  return (
    <div style={{ position: 'absolute', inset: 0 }}>
      <div ref={mapContainerRef} style={{ width: '100%', height: '100%' }} />

      {/* Top bar */}
      <div style={{
        position: 'absolute', top: 56, left: 16, right: 16,
        display: 'grid', gridTemplateColumns: 'auto 1fr 44px',
        alignItems: 'center', gap: 8, zIndex: 20,
      }}>
        <button
          style={{
            height: 44, padding: '0 14px', borderRadius: 22,
            background: '#F4F2FF', color: '#111118',
            fontSize: 15, fontWeight: 600,
            display: 'flex', alignItems: 'center', gap: 6,
            border: 'none', cursor: 'pointer',
            whiteSpace: 'nowrap',
          }}
          onClick={() => setShowDaySelector(true)}
          aria-label={dict.map.daySelector}
        >
          {selectedDayLabel}
          <IconChevronDown size={16} color="#111118" />
        </button>

        <AllFavsToggle
          containerRef={toggleRef}
          showFavorites={showFavorites}
          onChange={setShowFavorites}
          allLabel={dict.map.all}
          favLabel={dict.map.favorites}
          fontSize={toggleFontSize}
          padding={togglePad}
          style={{ flex: 1, minWidth: 0 }}
        />

        <button
          style={{
            width: 44, height: 44, borderRadius: 22,
            background: '#FF4D8D', color: '#1A0710',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: 'none', cursor: 'pointer',
          }}
          aria-label={dict.map.filter}
          onClick={handleFilterClick}
        >
          <IconFilter size={20} color="#1A0710" />
        </button>
      </div>

      {/* Compass — above location button (bottom: 132+52+8 = 192) */}
      {bearing !== 0 && (
        <button
          style={{
            position: 'absolute', right: 16, bottom: 192,
            width: 44, height: 44, borderRadius: 22,
            background: '#F4F2FF',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(0,0,0,0.4)', zIndex: 20,
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
          left: '50%', transform: 'translateX(-50%)',
          background: '#1C1C27', color: '#F4F2FF',
          padding: '10px 20px', borderRadius: 20,
          fontSize: 14, fontWeight: 500, zIndex: 30,
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
          boxShadow: '0 2px 12px rgba(0,0,0,0.4)', zIndex: 20,
          border: 'none', cursor: 'pointer',
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
          display: 'flex', alignItems: 'center', gap: 6, zIndex: 20,
          whiteSpace: 'nowrap', cursor: 'pointer',
        }}
        onClick={() => setShowAttribution(a => !a)}
        aria-label="Autorstvo mapy"
      >
        {showAttribution ? '© OpenStreetMap prispievatelia | OpenFreeMap' : 'i'}
      </button>

      {/* Navigation arrows — 40px, grey when at edge, with count badge when count > 0 */}
      {panelOpen && (
        <>
          <button
            style={{ ...arrowBtnStyle(!!prevVenue), left: 16 }}
            onClick={() => prevVenue && handleArrow(prevVenue)}
            disabled={!prevVenue}
            aria-label="Predošlé miesto"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M15 6l-6 6 6 6" />
            </svg>
            {leftCount > 0 && (
              <span style={{
                position: 'absolute', top: -4, right: -4,
                minWidth: 18, height: 18, borderRadius: 9,
                background: '#111118', color: '#F4F2FF',
                fontSize: 11, fontWeight: 700, lineHeight: '18px',
                textAlign: 'center', padding: '0 4px',
                pointerEvents: 'none',
              }}>{leftCount}</span>
            )}
          </button>
          <button
            style={{ ...arrowBtnStyle(!!nextVenue), right: 16 }}
            onClick={() => nextVenue && handleArrow(nextVenue)}
            disabled={!nextVenue}
            aria-label="Ďalšie miesto"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M9 6l6 6-6 6" />
            </svg>
            {rightCount > 0 && (
              <span style={{
                position: 'absolute', top: -4, left: -4,
                minWidth: 18, height: 18, borderRadius: 9,
                background: '#111118', color: '#F4F2FF',
                fontSize: 11, fontWeight: 700, lineHeight: '18px',
                textAlign: 'center', padding: '0 4px',
                pointerEvents: 'none',
              }}>{rightCount}</span>
            )}
          </button>
        </>
      )}

      {/* Event panel */}
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


      {/* Day selector sheet */}
      {showDaySelector && (
        <DaySelector
          days={days}
          selectedDay={selectedDay}
          lang={lang}
          now={curNow}
          showNight={showNight}
          availableDates={availableDates}
          onSelect={day => { setSelectedDay(day); setShowDaySelector(false) }}
          onClose={() => setShowDaySelector(false)}
        />
      )}
    </div>
  )
}
