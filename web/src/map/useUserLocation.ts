import { useState, useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import { visibleEvents, type VisibleOpts } from '../core/visible'
import { haversine } from '../core/distance'
import { isFavorite, setLastKnownLocation } from '../core/store'
import type { EventsData } from '../core/types'

interface UseUserLocationOptions {
  mapRef: React.MutableRefObject<maplibregl.Map | null>
  dataRef: React.MutableRefObject<EventsData>
  selectedDayRef: React.MutableRefObject<string>
  showFavoritesRef: React.MutableRefObject<boolean>
  isVisibleRef: React.MutableRefObject<boolean>
  isVisible: boolean
  /** Task 075: the filter applies to the initial view too */
  eventFilterRef?: React.MutableRefObject<VisibleOpts['eventFilter']>
}

export function useUserLocation({
  mapRef, dataRef, selectedDayRef, showFavoritesRef, isVisibleRef, isVisible, eventFilterRef,
}: UseUserLocationOptions) {
  const [userLocation, setUserLocation] = useState<{ lat: number; lng: number } | null>(null)
  const [locationLoading, setLocationLoading] = useState(false)
  const userMarkerRef = useRef<maplibregl.Marker | null>(null)
  const watchIdRef = useRef<number | null>(null)
  const lastKnownLocationRef = useRef<{ lat: number; lng: number } | null>(null)

  function startWatch() {
    if (!navigator.geolocation || watchIdRef.current !== null) return
    watchIdRef.current = navigator.geolocation.watchPosition(
      pos => {
        const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        lastKnownLocationRef.current = loc
        setLastKnownLocation(loc)
        setUserLocation(loc)
      },
      () => {},
      { enableHighAccuracy: true, maximumAge: 10000 }
    )
  }

  function stopWatch() {
    if (watchIdRef.current !== null) {
      navigator.geolocation?.clearWatch(watchIdRef.current)
      watchIdRef.current = null
    }
  }

  // watchPosition: start/stop based on tab visibility
  useEffect(() => {
    if (isVisible && document.visibilityState === 'visible') {
      if (lastKnownLocationRef.current) startWatch()
    } else {
      stopWatch()
    }
    const handleVisChange = () => {
      if (!isVisibleRef.current) return
      if (document.visibilityState === 'visible') {
        if (lastKnownLocationRef.current) startWatch()
      } else {
        stopWatch()
      }
    }
    document.addEventListener('visibilitychange', handleVisChange)
    return () => {
      document.removeEventListener('visibilitychange', handleVisChange)
      stopWatch()
    }
  }, [isVisible]) // eslint-disable-line react-hooks/exhaustive-deps

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
  }, [userLocation]) // eslint-disable-line react-hooks/exhaustive-deps

  function handleLocationClick() {
    if (!navigator.geolocation) return
    if (lastKnownLocationRef.current) {
      const { lat, lng } = lastKnownLocationRef.current
      mapRef.current?.flyTo({ center: [lng, lat], zoom: 14 })
      return
    }
    setLocationLoading(true)
    navigator.geolocation.getCurrentPosition(
      pos => {
        const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        lastKnownLocationRef.current = loc
        setLastKnownLocation(loc)
        setUserLocation(loc)
        setLocationLoading(false)
        mapRef.current?.flyTo({ center: [pos.coords.longitude, pos.coords.latitude], zoom: 14 })
        startWatch()
      },
      () => setLocationLoading(false),
      { timeout: 8000, maximumAge: 60000 }
    )
  }

  /** Show the position; fly there only when it is within 2 km of an active venue. */
  function applyInitialPosition(map: maplibregl.Map, pos: GeolocationPosition) {
    const { latitude: lat, longitude: lng } = pos.coords
    const curNow = new Date()
    const vm = visibleEvents(dataRef.current, selectedDayRef.current, curNow, { favoritesOnly: showFavoritesRef.current, isFavorite, eventFilter: eventFilterRef?.current })
    const activeVenues = dataRef.current.venues.filter(v => vm.has(v.id))
    if (activeVenues.length === 0) return
    const nearest = activeVenues.reduce((best, v) =>
      haversine(lat, lng, v.lat, v.lng) < haversine(lat, lng, best.lat, best.lng) ? v : best
    )
    if (haversine(lat, lng, nearest.lat, nearest.lng) <= 2) {
      map.flyTo({ center: [lng, lat], zoom: 14, duration: 1200 })
      lastKnownLocationRef.current = { lat, lng }
      setLastKnownLocation({ lat, lng })
      setUserLocation({ lat, lng })
      startWatch()
    }
  }

  // Initial view: check if geolocation already granted
  function tryInitialLocation(map: maplibregl.Map) {
    navigator.permissions?.query({ name: 'geolocation' }).then(perm => {
      if (perm.state !== 'granted') return
      navigator.geolocation.getCurrentPosition(pos => applyInitialPosition(map, pos), () => {}, { timeout: 5000 })
    }).catch(() => {})
  }

  // Task 079: the app starts in Akcie, so the location is asked for the first
  // time the map is opened, if it was neither granted nor denied yet.
  const askedRef = useRef(false)
  useEffect(() => {
    if (!isVisible || askedRef.current || !navigator.geolocation) return
    askedRef.current = true
    navigator.permissions?.query({ name: 'geolocation' }).then(perm => {
      if (perm.state !== 'prompt') return
      navigator.geolocation.getCurrentPosition(pos => {
        const map = mapRef.current
        if (map) applyInitialPosition(map, pos)
      }, () => {}, { timeout: 8000, maximumAge: 60000 })
    }).catch(() => {})
  }, [isVisible]) // eslint-disable-line react-hooks/exhaustive-deps

  // Task 092: the map was created again (lost WebGL context) -> move the dot to it
  function reattachUserMarker(map: maplibregl.Map) {
    userMarkerRef.current?.addTo(map)
  }

  return { userLocation, locationLoading, handleLocationClick, tryInitialLocation, stopWatch, reattachUserMarker }
}
