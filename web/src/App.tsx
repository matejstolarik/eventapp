import { useState, useEffect, useRef } from 'react'
import type { EventsData, Language } from './core/types'
import { detectLanguage } from './core/store'
import { setLastFetched, getLastFetched } from './core/store'
import { BottomNav } from './components/BottomNav'
import type { Tab } from './components/BottomNav'
import { OfflineBanner } from './components/OfflineBanner'
import { ComingSoon } from './components/ComingSoon'
import { MapPage } from './pages/MapPage'
import { EventPage } from './pages/EventPage'
import { VenuePage } from './pages/VenuePage'
import { PlacesPage } from './pages/PlacesPage'
import { MyAccountPage } from './pages/MyAccountPage'
import { getDict } from './i18n'

type Route =
  | { page: Tab }
  | { page: 'event'; eventId: string }
  | { page: 'venue'; venueId: string }

function parseHash(hash: string): Route {
  const path = hash.replace(/^#\//, '')
  if (path.startsWith('akcia/')) {
    return { page: 'event', eventId: path.slice(6) }
  }
  if (path.startsWith('miesto/')) {
    return { page: 'venue', venueId: path.slice(7) }
  }
  if (path === 'miesta') {
    return { page: 'places' }
  }
  return { page: 'map' }
}


type MapPendingSelect = { venueId: string; date: string } | null

export default function App() {
  const [data, setData] = useState<EventsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [isOffline, setIsOffline] = useState(false)
  const [lastFetched, setLastFetchedState] = useState<Date | null>(null)
  const [lang, setLang] = useState<Language>(detectLanguage)
  const [activeTab, setActiveTab] = useState<Tab>(() => {
    const r = parseHash(window.location.hash)
    if (r.page === 'places') return 'places'
    return 'map'
  })
  const [mapPendingSelect, setMapPendingSelect] = useState<MapPendingSelect>(null)

  // Hash routing
  const [route, setRoute] = useState<Route>(() => {
    const r = parseHash(window.location.hash)
    return r
  })

  // Track if MapPage was ever mounted (once true, never unmount it)
  const mapMountedRef = useRef(false)
  if (data !== null) mapMountedRef.current = true

  useEffect(() => {
    function onHashChange() {
      const r = parseHash(window.location.hash)
      setRoute(r)
      // Sync activeTab from hash for tab pages
      if (r.page === 'places') setActiveTab('places')
      else if (r.page === 'map') setActiveTab('map')
    }
    window.addEventListener('hashchange', onHashChange)
    return () => window.removeEventListener('hashchange', onHashChange)
  }, [])

  function navigate(newRoute: Route) {
    if (newRoute.page === 'event') {
      window.location.hash = `/akcia/${(newRoute as { page: 'event'; eventId: string }).eventId}`
    } else if (newRoute.page === 'venue') {
      window.location.hash = `/miesto/${(newRoute as { page: 'venue'; venueId: string }).venueId}`
    } else if (newRoute.page === 'places') {
      window.location.hash = '/miesta'
    } else {
      window.location.hash = '/'
    }
    setRoute(newRoute)
  }

  function openEvent(eventId: string) {
    navigate({ page: 'event', eventId })
  }

  function openVenue(venueId: string) {
    navigate({ page: 'venue', venueId })
  }

  function openVenueFromPlaces(venueId: string) {
    // Ensure places hash in history so Back returns to places list
    if (window.location.hash !== '#/miesta') {
      history.pushState(null, '', '#/miesta')
    }
    navigate({ page: 'venue', venueId })
  }

  function goBack() {
    if (window.history.length > 1) {
      window.history.back()
    } else {
      navigate({ page: 'map' })
    }
  }

  function goToMap(venueId: string, date: string) {
    setActiveTab('map')
    setMapPendingSelect({ venueId, date })
    navigate({ page: 'map' })
  }

  function handleTabChange(tab: Tab) {
    setActiveTab(tab)
    if (tab === 'places') {
      window.location.hash = '/miesta'
    } else if (tab === 'map') {
      // Only clear the hash if we were on a named route
      if (window.location.hash && window.location.hash !== '#/' && window.location.hash !== '#') {
        window.location.hash = '/'
      }
    }
    // For 'events' and 'account' tabs: leave the hash as-is so we don't trigger onHashChange → setActiveTab('map')
  }

  // Fetch events data
  useEffect(() => {
    const url = `${import.meta.env.BASE_URL}events.json`
    fetch(url)
      .then(r => r.json())
      .then((d: EventsData) => {
        setData(d)
        setIsOffline(false)
        setLastFetchedState(d.generated_at ? new Date(d.generated_at) : new Date())
        setLastFetched()
      })
      .catch(() => {
        setIsOffline(true)
        setLastFetchedState(getLastFetched())
      })
      .finally(() => setLoading(false))
  }, [])

  // Network status
  useEffect(() => {
    function onOnline() { setIsOffline(false) }
    function onOffline() { setIsOffline(true) }
    window.addEventListener('online', onOnline)
    window.addEventListener('offline', onOffline)
    return () => {
      window.removeEventListener('online', onOnline)
      window.removeEventListener('offline', onOffline)
    }
  }, [])

  const dict = getDict(lang)
  void dict // used below

  if (loading) {
    return (
      <div style={{
        position: 'fixed', inset: 0, background: '#111118',
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        <div style={{
          width: 40, height: 40, borderRadius: 20,
          border: '3px solid #2A2838', borderTopColor: '#FF4D8D',
          animation: 'spin 0.8s linear infinite'
        }} />
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    )
  }

  // Map is active when on map tab and not on overlay page
  const isOverlay = route.page === 'event' || route.page === 'venue'
  const isMapActive = !isOverlay && activeTab === 'map'

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#111118', display: 'flex', flexDirection: 'column' }}>
      {isOffline && !isOverlay && <OfflineBanner lang={lang} lastFetched={lastFetched} />}

      {/* Page content */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        {/* Map — always mounted once data loads, hidden when not active tab.
            Never unmounted so the WebGL context survives tab switches and overlay navigation. */}
        {mapMountedRef.current && (
          <div style={{ position: 'absolute', inset: 0, display: isMapActive ? undefined : 'none' }}>
            <MapPage
              data={data!}
              lang={lang}
              isVisible={isMapActive}
              onEventOpen={openEvent}
              pendingSelect={mapPendingSelect}
              onPendingSelectHandled={() => setMapPendingSelect(null)}
            />
          </div>
        )}
        {!mapMountedRef.current && activeTab === 'map' && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: '#B9B6CC' }}>Žiadne dáta</p>
          </div>
        )}
        {activeTab === 'events' && !isOverlay && (
          <ComingSoon lang={lang} title={dict.nav.events} />
        )}
        {activeTab === 'places' && !isOverlay && (
          <PlacesPage
            data={data ?? { schema_version: 1, generated_at: '', venues: [], events: [] }}
            lang={lang}
            onVenueOpen={openVenueFromPlaces}
          />
        )}
        {activeTab === 'account' && !isOverlay && (
          <MyAccountPage
            data={data}
            lang={lang}
            onLangChange={newLang => setLang(newLang)}
            onEventOpen={openEvent}
          />
        )}
      </div>

      {!isOverlay && (
        <BottomNav active={activeTab} lang={lang} onChange={handleTabChange} />
      )}

      {/* Event page renders as a full-screen overlay; MapPage stays mounted underneath */}
      {route.page === 'event' && (
        <div style={{ position: 'fixed', inset: 0, background: '#111118', zIndex: 50 }}>
          {isOffline && <OfflineBanner lang={lang} lastFetched={lastFetched} />}
          <EventPage
            eventId={(route as { page: 'event'; eventId: string }).eventId}
            data={data ?? { schema_version: 1, generated_at: '', venues: [], events: [] }}
            lang={lang}
            userLocation={null}
            onBack={goBack}
            onVenueOpen={openVenue}
          />
        </div>
      )}

      {/* Venue profile renders as overlay above everything */}
      {route.page === 'venue' && (
        <div style={{ position: 'fixed', inset: 0, background: '#111118', zIndex: 55 }}>
          {isOffline && <OfflineBanner lang={lang} lastFetched={lastFetched} />}
          <VenuePage
            venueId={(route as { page: 'venue'; venueId: string }).venueId}
            data={data ?? { schema_version: 1, generated_at: '', venues: [], events: [] }}
            lang={lang}
            userLocation={null}
            onBack={goBack}
            onEventOpen={openEvent}
            onGoToMap={goToMap}
          />
        </div>
      )}
    </div>
  )
}
