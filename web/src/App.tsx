import { useState, useEffect, useRef } from 'react'
import type { EventsData, Language } from './core/types'
import { detectLanguage, shouldShowOnboarding, setOnboardingPending } from './core/store'
import { setLastFetched, getLastFetched, getStoredFilter, setStoredFilter } from './core/store'
import type { EventFilter } from './core/filter'
import { BottomNav } from './components/BottomNav'
import type { Tab } from './components/BottomNav'
import { OfflineBanner } from './components/OfflineBanner'
import { UpdatePrompt } from './components/UpdatePrompt'
import { EventsPage } from './pages/EventsPage'
import { MapPage } from './pages/MapPage'
import { EventPage } from './pages/EventPage'
import { VenuePage } from './pages/VenuePage'
import { PlacesPage } from './pages/PlacesPage'
import { MyAccountPage } from './pages/MyAccountPage'
import { OnboardingPage } from './pages/OnboardingPage'
import { PreferencesPage } from './pages/PreferencesPage'
import { getDict } from './i18n'

type Route =
  | { page: Tab }
  | { page: 'event'; eventId: string }
  | { page: 'venue'; venueId: string }
  | { page: 'preferences' }

// Debug switch for screenshots/tests: ?dbg=onboarding always shows the onboarding.
const DEBUG_ONBOARDING = typeof window !== 'undefined'
  && new URLSearchParams(window.location.search).get('dbg') === 'onboarding'

/** Task 079: Akcie is the first tab and the start page (empty hash); the map has its own hash. */
export function parseHash(hash: string): Route {
  const path = hash.replace(/^#\//, '')
  if (path.startsWith('akcia/')) {
    return { page: 'event', eventId: path.slice(6) }
  }
  if (path.startsWith('miesto/')) {
    return { page: 'venue', venueId: path.slice(7) }
  }
  if (path === 'miesta') return { page: 'places' }
  if (path === 'mapa') return { page: 'map' }
  if (path === 'ucet') return { page: 'account' }
  if (path === 'preferencie') return { page: 'preferences' }
  return { page: 'events' }
}

/** Tab shown for a route (overlays keep the tab underneath; preferences belong to My account). */
export function tabOfRoute(r: Route): Tab {
  if (r.page === 'map' || r.page === 'places' || r.page === 'account' || r.page === 'events') return r.page
  if (r.page === 'preferences') return 'account'
  return 'events'
}


type MapPendingSelect = { venueId: string; date: string } | null

export default function App() {
  const [data, setData] = useState<EventsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [isOffline, setIsOffline] = useState(false)
  const [lastFetched, setLastFetchedState] = useState<Date | null>(null)
  const [lang, setLang] = useState<Language>(detectLanguage)
  const [activeTab, setActiveTab] = useState<Tab>(() => tabOfRoute(parseHash(window.location.hash)))
  // Task 079: onboarding only on a new install (decided before any state is written)
  const [showOnboarding, setShowOnboarding] = useState(() => {
    if (shouldShowOnboarding()) { setOnboardingPending(); return true }
    return DEBUG_ONBOARDING
  })
  const [skipToast, setSkipToast] = useState(false)
  const [mapPendingSelect, setMapPendingSelect] = useState<MapPendingSelect>(null)
  const [mapPanelOpen, setMapPanelOpen] = useState(false)
  // Task 075: one filter for Mapa and Akcie, stored locally
  const [filter, setFilter] = useState<EventFilter>(getStoredFilter)
  useEffect(() => { setStoredFilter(filter) }, [filter])

  // Hash routing
  const [route, setRoute] = useState<Route>(() => {
    const r = parseHash(window.location.hash)
    return r
  })

  // Track which pages were ever mounted (once true, never unmount)
  const mapMountedRef = useRef(false)
  const eventsMountedRef = useRef(false)
  const accountMountedRef = useRef(false)
  if (data !== null && !showOnboarding) mapMountedRef.current = true
  if (activeTab === 'events' && !showOnboarding) eventsMountedRef.current = true
  if (activeTab === 'account') accountMountedRef.current = true

  useEffect(() => {
    function onHashChange() {
      const r = parseHash(window.location.hash)
      setRoute(r)
      // Sync activeTab from hash for tab pages
      if (r.page === 'places' || r.page === 'events' || r.page === 'account' || r.page === 'map') setActiveTab(r.page)
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
    } else if (newRoute.page === 'events') {
      window.location.hash = '/akcie'
    } else if (newRoute.page === 'account') {
      window.location.hash = '/ucet'
    } else if (newRoute.page === 'preferences') {
      window.location.hash = '/preferencie'
    } else {
      window.location.hash = '/mapa'
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
      navigate({ page: 'events' })
    }
  }

  function openPreferences() {
    setSkipToast(false)
    navigate({ page: 'preferences' })
  }

  function closeOnboarding(skipped: boolean) {
    setShowOnboarding(false)
    setActiveTab('events')
    if (parseHash(window.location.hash).page !== 'events') window.location.hash = '/akcie'
    if (skipped) setSkipToast(true)
  }

  function goToMap(venueId: string, date: string) {
    setActiveTab('map')
    setMapPendingSelect({ venueId, date })
    navigate({ page: 'map' })
  }

  // Callbacks for EventsPage/PlacesPage to register their scroll-to-top functions
  const eventsScrollTopRef = useRef<(() => void) | null>(null)
  const placesScrollTopRef = useRef<(() => void) | null>(null)

  function handleTabChange(tab: Tab) {
    if (tab === activeTab) {
      // Tap on active tab → scroll to top
      if (tab === 'events') eventsScrollTopRef.current?.()
      if (tab === 'places') placesScrollTopRef.current?.()
      return
    }
    setActiveTab(tab)
    if (tab === 'places') {
      window.location.hash = '/miesta'
    } else if (tab === 'events') {
      window.location.hash = '/akcie'
    } else if (tab === 'account') {
      window.location.hash = '/ucet'
    } else if (tab === 'map') {
      window.location.hash = '/mapa'
    }
  }

  async function refreshData(noStore = false) {
    const url = `${import.meta.env.BASE_URL}events.json`
    const res = await fetch(url, noStore ? { cache: 'no-store' } : {})
    const d: EventsData = await res.json()
    setData(d)
    setIsOffline(false)
    setLastFetchedState(d.generated_at ? new Date(d.generated_at) : new Date())
    setLastFetched()
  }

  // Fetch events data
  useEffect(() => {
    refreshData()
      .catch(() => {
        setIsOffline(true)
        setLastFetchedState(getLastFetched())
      })
      .finally(() => setLoading(false))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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
  const isOverlay = route.page === 'event' || route.page === 'venue' || route.page === 'preferences'
  const isMapActive = !isOverlay && activeTab === 'map'

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#111118', display: 'flex', flexDirection: 'column' }}>
      {isOffline && !isOverlay && <OfflineBanner lang={lang} lastFetched={lastFetched} />}

      {/* Page content — no overflow:hidden so nested scroll containers work on mobile */}
      <div style={{ flex: 1, position: 'relative' }}>
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
              onPanelOpenChange={setMapPanelOpen}
              filter={filter}
              onFilterChange={setFilter}
            />
          </div>
        )}
        {!mapMountedRef.current && activeTab === 'map' && (
          <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <p style={{ color: '#B9B6CC' }}>Žiadne dáta</p>
          </div>
        )}
        {eventsMountedRef.current && (
          <div style={{ position: 'absolute', inset: 0, display: activeTab === 'events' && !isOverlay ? undefined : 'none' }}>
            <EventsPage
              data={data ?? { schema_version: 1, generated_at: '', venues: [], events: [] }}
              lang={lang}
              isVisible={activeTab === 'events' && !isOverlay}
              onEventOpen={openEvent}
              filter={filter}
              onFilterChange={setFilter}
              registerScrollToTop={fn => { eventsScrollTopRef.current = fn }}
              onRefresh={() => refreshData(true).catch(() => { throw new Error('refresh failed') })}
              onOpenPreferences={openPreferences}
            />
          </div>
        )}
        {activeTab === 'places' && !isOverlay && (
          <PlacesPage
            data={data ?? { schema_version: 1, generated_at: '', venues: [], events: [] }}
            lang={lang}
            onVenueOpen={openVenueFromPlaces}
            registerScrollToTop={fn => { placesScrollTopRef.current = fn }}
            onRefresh={() => refreshData(true).catch(() => { throw new Error('refresh failed') })}
          />
        )}
        {accountMountedRef.current && (
          <div style={{ position: 'absolute', inset: 0, display: activeTab === 'account' && !isOverlay ? undefined : 'none' }}>
            <MyAccountPage
              data={data}
              lang={lang}
              onLangChange={newLang => setLang(newLang)}
              onEventOpen={openEvent}
              onOpenPreferences={openPreferences}
            />
          </div>
        )}
      </div>

      <UpdatePrompt lang={lang} visible={!isOverlay && !(isMapActive && mapPanelOpen)} />

      {!isOverlay && (
        <BottomNav active={activeTab} lang={lang} onChange={handleTabChange} />
      )}

      {/* Event page renders as a full-screen overlay; MapPage stays mounted underneath */}
      {route.page === 'event' && (
        <div style={{ position: 'fixed', inset: 0, background: '#111118', zIndex: 50 }}>
          {isOffline && <OfflineBanner lang={lang} lastFetched={lastFetched} />}
          <EventPage
            key={(route as { page: 'event'; eventId: string }).eventId}
            eventId={(route as { page: 'event'; eventId: string }).eventId}
            data={data ?? { schema_version: 1, generated_at: '', venues: [], events: [] }}
            lang={lang}
            userLocation={null}
            onBack={goBack}
            onVenueOpen={openVenue}
            onGoToMap={goToMap}
          />
        </div>
      )}

      {/* Task 079: My account -> Event preferences */}
      {route.page === 'preferences' && (
        <div style={{ position: 'fixed', inset: 0, background: '#111118', zIndex: 55 }}>
          <PreferencesPage
            data={data ?? { schema_version: 1, generated_at: '', venues: [], events: [] }}
            lang={lang}
            onBack={goBack}
          />
        </div>
      )}

      {/* Task 079: onboarding on a new install, above everything */}
      {showOnboarding && data && (
        <OnboardingPage data={data} lang={lang} onClose={closeOnboarding} />
      )}

      {skipToast && !isOverlay && (
        <SkipToast text={dict.onboarding.skipToast} onTap={openPreferences} onHide={() => setSkipToast(false)} />
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

/** Short toast after skipping the onboarding (design 7c); tap -> Event preferences. */
function SkipToast({ text, onTap, onHide }: { text: string; onTap: () => void; onHide: () => void }) {
  useEffect(() => {
    const id = setTimeout(onHide, 5000)
    return () => clearTimeout(id)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps
  return (
    <div role="status" data-testid="onb-skip-toast" onClick={onTap} style={{
      position: 'fixed', left: 16, right: 16, bottom: 28 + 72 + 12, zIndex: 40,
      background: '#2A2838', color: '#F4F2FF', borderRadius: 20, padding: '12px 16px',
      fontFamily: "'Outfit', sans-serif", fontSize: 14, fontWeight: 600, lineHeight: 1.35,
      boxShadow: '0 4px 20px rgba(0,0,0,0.5)', cursor: 'pointer',
    }}>{text}</div>
  )
}
