import maplibregl from 'maplibre-gl'
import { createPinElement, updatePinElement } from './markers'
import { checkPinOverlaps, checkNameCollisions } from './collisions'
import type { MarkerData } from './markers'
import type { MarkerEntry } from './collisions'

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
}

export function syncMarkers(opts: SyncMarkersOptions): void {
  const {
    map, markerData, markers, leavingMarkers,
    selectedVenueIdRef, pendingPanelOpenRef, pairsRef,
    combinedLabelRef, combinedMarkerRef, dataRef,
    openPanel, closePanel,
  } = opts

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

      el.classList.add('pin-new')
      setTimeout(() => el.classList.remove('pin-new'), 300)

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

  runCollisions()
}
