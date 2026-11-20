import maplibregl from 'maplibre-gl'
import { createPinElement, updatePinElement } from './markers'
import { checkPinOverlaps, checkNameCollisions } from './collisions'
import type { MarkerData } from './markers'
import type { MarkerEntry } from './collisions'
import { motionOn, pinDropDelay } from '../core/motion'

export type LeavingEntry = {
  marker: maplibregl.Marker
  el: HTMLElement
  timerId: ReturnType<typeof setTimeout>
  cancelled: boolean
}

interface SyncMarkersOptions {
  map: maplibregl.Map
  markerData: MarkerData[]
  markers: Map<string, MarkerEntry>
  leavingMarkers: Map<string, LeavingEntry>
  selectedVenueIdRef: React.MutableRefObject<string | null>
  pendingPanelOpenRef: React.MutableRefObject<string | null>
  pairsRef: React.MutableRefObject<Map<string, string>>
  combinedLabelRef: React.MutableRefObject<HTMLElement | null>
  combinedMarkerRef: React.MutableRefObject<maplibregl.Marker | null>
  dataRef: React.MutableRefObject<{ venues: Array<{ id: string; name: string; lat: number; lng: number }> }>
  openPanel: (venueId: string) => void
  closePanel: () => void
  /** Task 081: replay the drop on all visible pins (map opened, day / filter /
   * favourites changed). Never set for pan, zoom, rotate or pin taps. */
  drop?: boolean
}

let dropToken = 0

/** Pins "fall" into place (task 081, replaces pin-appear): from ~12 px above with a
 * small bounce, delayed by distance from the screen centre, all within ≤ 300 ms. */
function dropPins(map: maplibregl.Map, all: Array<{ el: HTMLElement; lng: number; lat: number }>, restart: boolean): void {
  // the selected pin keeps its scale (it may have been selected by "Na mape" above)
  const items = all.filter(it => !it.el.classList.contains('pin-selected'))
  if (items.length === 0) return
  const token = String(++dropToken)
  const c = map.getContainer()
  const w = c.clientWidth, h = c.clientHeight
  for (const it of items) {
    if (restart) it.el.classList.remove('pin-drop')
    const pt = map.project([it.lng, it.lat])
    it.el.style.setProperty('--pin-delay', `${pinDropDelay(pt.x, pt.y, w, h)}ms`)
    it.el.dataset.dropToken = token
  }
  if (restart) void c.offsetWidth // restart the CSS animation (one reflow per batch)
  for (const it of items) it.el.classList.add('pin-drop')
  setTimeout(() => {
    for (const it of items) {
      if (it.el.dataset.dropToken === token) it.el.classList.remove('pin-drop')
    }
  }, 340)
}

export function syncMarkers(opts: SyncMarkersOptions): void {
  const {
    map, markerData, markers, leavingMarkers,
    selectedVenueIdRef, pendingPanelOpenRef, pairsRef,
    combinedLabelRef, combinedMarkerRef, dataRef,
    openPanel, closePanel, drop = false,
  } = opts
  const dropOn = motionOn('pinDrop')
  const newPins: Array<{ el: HTMLElement; lng: number; lat: number }> = []
  const replay: Array<{ el: HTMLElement; lng: number; lat: number }> = []

  const newIds = new Set(markerData.map(m => m.venueId))

  for (const [id, { marker, el }] of markers) {
    if (!newIds.has(id)) {
      if (id === selectedVenueIdRef.current) {
        el.classList.remove('pin-selected')
        el.style.zIndex = ''
      }
      markers.delete(id)
      const prefersReduced = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
      if (prefersReduced) {
        marker.remove()
      } else {
        el.classList.add('pin-leaving')
        el.style.pointerEvents = 'none'
        const leavingEntry: LeavingEntry = { marker, el, timerId: 0 as ReturnType<typeof setTimeout>, cancelled: false }
        leavingMarkers.set(id, leavingEntry)
        let cleaned = false
        const cleanup = () => {
          if (cleaned || leavingEntry.cancelled) return
          cleaned = true
          marker.remove()
          leavingMarkers.delete(id)
        }
        const inner = el.querySelector('.pin-inner')
        if (inner) inner.addEventListener('animationend', cleanup, { once: true })
        leavingEntry.timerId = setTimeout(cleanup, 250)
      }
    }
  }

  if (selectedVenueIdRef.current && !newIds.has(selectedVenueIdRef.current)) {
    closePanel()
  }

  const runCollisions = () => requestAnimationFrame(() => {
    checkPinOverlaps(map, markers, pairsRef.current)
    checkNameCollisions(
      map, markers, pairsRef.current,
      combinedLabelRef.current, combinedMarkerRef.current,
      (id) => dataRef.current.venues.find(v => v.id === id)?.name ?? id,
    )
  })

  for (const md of markerData) {
    const isSelected = md.venueId === selectedVenueIdRef.current
    const existing = markers.get(md.venueId)
    const leaving = leavingMarkers.get(md.venueId)

    if (existing) {
      updatePinElement(existing.el, md, isSelected)
      if (drop && dropOn && !isSelected) replay.push({ el: existing.el, lng: md.lng, lat: md.lat })
    } else if (leaving) {
      leaving.cancelled = true
      clearTimeout(leaving.timerId)
      leavingMarkers.delete(md.venueId)
      const inner = leaving.el.querySelector('.pin-inner')
      const anims = inner ? inner.getAnimations() : []
      if (anims.length > 0) {
        anims.forEach(a => { a.playbackRate = -1 })
        anims[0].addEventListener('finish', () => {
          leaving.el.classList.remove('pin-leaving')
          leaving.el.style.pointerEvents = ''
        }, { once: true })
      } else {
        leaving.el.classList.remove('pin-leaving')
        leaving.el.style.pointerEvents = ''
      }
      updatePinElement(leaving.el, md, isSelected)
      markers.set(md.venueId, leaving)
    } else {
      const el = createPinElement(md, isSelected)
      const venueId = md.venueId
      el.addEventListener('click', () => {
        if (selectedVenueIdRef.current === venueId) {
          el.classList.remove('pin-selected')
          el.style.zIndex = ''
          runCollisions()
          closePanel()
        } else {
          const oldId = selectedVenueIdRef.current
          if (oldId) {
            const oldEntry = markers.get(oldId)
            if (oldEntry) {
              oldEntry.el.classList.remove('pin-selected')
              oldEntry.el.style.zIndex = ''
            }
          }
          el.classList.add('pin-selected')
          el.style.zIndex = '10'
          runCollisions()
          openPanel(venueId)

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
      })
      const marker = new maplibregl.Marker({ element: el, anchor: 'bottom', offset: [0, 0] })
        .setLngLat([md.lng, md.lat])
        .addTo(map)

      if (dropOn && !isSelected) {
        newPins.push({ el, lng: md.lng, lat: md.lat })
      } else if (!dropOn) {
        // switch off: pre-081 appear animation
        el.classList.add('pin-new')
        setTimeout(() => el.classList.remove('pin-new'), 300)
      }

      markers.set(venueId, { marker, el })
    }
  }

  // Handle external "Na mape" navigation
  if (pendingPanelOpenRef.current) {
    const vid = pendingPanelOpenRef.current
    const entry = markers.get(vid)
    if (entry) {
      pendingPanelOpenRef.current = null
      const oldId = selectedVenueIdRef.current
      if (oldId && oldId !== vid) {
        const oldEntry = markers.get(oldId)
        if (oldEntry) { oldEntry.el.classList.remove('pin-selected'); oldEntry.el.style.zIndex = '' }
      }
      entry.el.classList.add('pin-selected')
      entry.el.style.zIndex = '10'
      openPanel(vid)
      const venue = dataRef.current.venues.find(v => v.id === vid)
      if (venue) {
        map.easeTo({
          center: [venue.lng, venue.lat],
          padding: { top: 100, bottom: 240, left: 60, right: 60 },
          duration: 320,
        })
      }
    }
  }

  dropPins(map, newPins, false)
  dropPins(map, replay, true)

  runCollisions()
}
