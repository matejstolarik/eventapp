import { useState, useMemo, useEffect, useRef } from 'react'
import type { EventsData, Language, Event } from '../core/types'
import { getDict, formatDayLabel, tagLabel } from '../i18n'
import { usePullToRefresh } from '../core/usePullToRefresh'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK, EVENT_TYPE_TAG_TEXT, eventTags, eventIconKey } from '../core/eventType'
import { getEventsForPeriod, sortEvents, formatPeriodShortLabel, formatPeriodRangeText, isSingleDayPeriod, type Period, type SortMode } from '../core/period'
import { getStoredPeriod, setStoredPeriod, getLastKnownLocation, setLastKnownLocation, getFavorites, getStoredEventsFilters, setStoredEventsFilters } from '../core/store'
import { matchesSearch, isForYou, isNew } from '../core/search'
import { isNightMode, isNightEvent } from '../core/night'
import { EventTypeIcon } from '../icons'
import { SelectorSheet, InfinityIcon, CalendarIcon, ChevronDown, type SheetItem } from '../components/SelectorSheet'
import { PullRefreshIndicator } from '../components/PullRefreshIndicator'

interface Props {
  data: EventsData
  lang: Language
  isVisible?: boolean
  onEventOpen: (eventId: string) => void
  registerScrollToTop?: (fn: () => void) => void
  onRefresh?: () => Promise<void>
}



function eventCount(n: number, dict: ReturnType<typeof getDict>): string {
  const { eventCountSg, eventCountFw, eventCountPl } = dict.events
  if (n === 1) return `1 ${eventCountSg}`
  if (n >= 2 && n <= 4) return `${n} ${eventCountFw}`
  return `${n} ${eventCountPl}`
}

function SparkleIcon({ size = 16, color = 'currentColor' }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z" />
      <path d="M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" />
    </svg>
  )
}

function SearchIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="11" cy="11" r="7" />
      <path d="M20 20l-3.5-3.5" />
    </svg>
  )
}

function CloseIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M6 6l12 12M18 6L6 18" />
    </svg>
  )
}

function FilterIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 7h10M18 7h2M4 17h4M12 17h8" />
      <circle cx="16" cy="7" r="2" />
      <circle cx="10" cy="17" r="2" />
    </svg>
  )
}

interface EventCardProps {
  event: Event
  venue: { name: string; character: string[] } | undefined
  lang: Language
  now: Date
  eager: boolean
  baseUrl: string
  forYouFlag: boolean
  isNewFlag: boolean
  animIn: boolean
  onClick: () => void
}

function EventCard({ event, venue, lang, now, eager, baseUrl, forYouFlag, isNewFlag, animIn, onClick }: EventCardProps) {
  const type = getEventType(event.formats, event.primary_format)
  const iconKey = eventIconKey(event.formats, event.primary_format)
  const color = EVENT_TYPE_COLOR[type]
  const dark = EVENT_TYPE_DARK[type]
  const tagTextColor = EVENT_TYPE_TAG_TEXT[type]
  const dateLabel = formatDayLabel(event.date, lang, now)
  const timeLabel = event.start_time ?? ''
  const allTags = eventTags(event.formats, event.genres, event.primary_format)

  return (
    <div
      style={{
        minWidth: 0, cursor: 'pointer',
        ...(animIn ? { animation: 'evCardIn 180ms ease-out both' } : {}),
      }}
      onClick={onClick} role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && onClick()}
    >
      <div style={{ width: '100%', aspectRatio: '1/1', borderRadius: 12, overflow: 'hidden', position: 'relative', background: color, display: 'flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box' }}>
        {event.image_thumb ? (
          <img
            src={`${baseUrl}${event.image_thumb}`}
            alt=""
            width={120} height={120}
            decoding="async"
            loading={eager ? 'eager' : 'lazy'}
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }}
          />
        ) : (
          <EventTypeIcon iconKey={iconKey} size={40} color={dark} />
        )}
        {forYouFlag && (
          <span style={{ position: 'absolute', top: 6, left: 6, zIndex: 2, height: 18, padding: '0 6px', borderRadius: 9, background: '#111118', color: '#F4F2FF', fontSize: 10, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 3 }}>
            <SparkleIcon size={11} color="#F4F2FF" />
            {lang === 'en' ? 'for you' : lang === 'cs' ? 'pro tebe' : 'pre teba'}
          </span>
        )}
        {isNewFlag && (
          <span style={{ position: 'absolute', top: 6, right: 6, zIndex: 2, height: 18, padding: '0 6px', borderRadius: 9, background: '#F4F2FF', color: '#111118', fontSize: 10, fontWeight: 600, display: 'flex', alignItems: 'center' }}>
            new
          </span>
        )}
        {/* Tags overlay — only event tags, no venue character tags */}
        {allTags.length > 0 && (
          <div style={{ position: 'absolute', bottom: 6, left: 6, right: 0, zIndex: 1, display: 'flex', gap: 4, overflow: 'hidden', WebkitMaskImage: 'linear-gradient(90deg,#000 80%,transparent)', maskImage: 'linear-gradient(90deg,#000 80%,transparent)' }}>
            {allTags.map(tag => (
              <span key={tag} style={{
                flex: 'none', height: 18, padding: '0 6px', borderRadius: 9, fontSize: 10, fontWeight: 500, display: 'flex', alignItems: 'center',
                background: 'rgba(17,17,24,0.9)', color: tagTextColor,
              }}>
                {tagLabel(tag, lang)}
              </span>
            ))}
          </div>
        )}
      </div>

      <div style={{ fontSize: 13, fontWeight: 700, color: '#F4F2FF', lineHeight: 1.25, maxHeight: '2.5em', overflow: 'hidden', marginTop: 6, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
        {event.title}
      </div>

      <div style={{ fontSize: 12, fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', color: '#8E8AA6', marginTop: 1 }}>
        {dateLabel}{timeLabel ? ` · ${timeLabel}` : ''}
      </div>

      {venue && (
        <div style={{ fontSize: 12, fontWeight: 400, color: '#8E8AA6', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginTop: 1 }}>
          {venue.name}
        </div>
      )}
    </div>
  )
}

export function EventsPage({ data, lang, isVisible, onEventOpen, registerScrollToTop, onRefresh }: Props) {
  const dict = getDict(lang)
  const [now, setNow] = useState(() => new Date())
  const baseUrl = import.meta.env.BASE_URL

  const scrollRef = useRef<HTMLDivElement>(null)
  const headerSentinelRef = useRef<HTMLDivElement>(null)
  const [collapsed, setCollapsed] = useState(false)
  const [showScrollTop, setShowScrollTop] = useState(false)
  const [animKey, setAnimKey] = useState(0)
  const { pullDist, isRefreshing, refreshError } = usePullToRefresh(scrollRef, onRefresh)

  useEffect(() => {
    registerScrollToTop?.(() => scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' }))
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const refresh = () => setNow(new Date())
    const handleVis = () => { if (document.visibilityState === 'visible') refresh() }
    document.addEventListener('visibilitychange', handleVis)
    window.addEventListener('focus', refresh)
    const timer = setInterval(refresh, 60_000)
    return () => { clearInterval(timer); document.removeEventListener('visibilitychange', handleVis); window.removeEventListener('focus', refresh) }
  }, [])

  // Reset collapse state when page becomes hidden (prevents compact bar preblik on return)
  useEffect(() => {
    if (isVisible === false) {
      setCollapsed(false)
      setShowScrollTop(false)
    }
  }, [isVisible])

  // IntersectionObserver on sentinel at bottom of full header — only while visible
  useEffect(() => {
    const sentinel = headerSentinelRef.current
    if (!sentinel || isVisible === false) return
    const obs = new IntersectionObserver(([entry]) => setCollapsed(!entry!.isIntersecting), { threshold: 0 })
    obs.observe(sentinel)
    return () => obs.disconnect()
  }, [isVisible])

  // Scroll tracking for scroll-to-top button — only while visible
  useEffect(() => {
    const el = scrollRef.current
    if (!el || isVisible === false) return
    const onScroll = () => setShowScrollTop(el.scrollTop > window.innerHeight * 2)
    el.addEventListener('scroll', onScroll, { passive: true })
    return () => el.removeEventListener('scroll', onScroll)
  }, [isVisible])

  const isNight = isNightMode(data, now)

  const [period, setPeriod] = useState<Period>(() => {
    const stored = getStoredPeriod() ?? { type: 'today' }
    const night = isNightMode(data, new Date())
    if (night && (stored.type === 'today' || stored.type === 'night')) return { type: 'night' }
    if (!night && stored.type === 'night') return { type: 'today' }
    return stored
  })
  const [sort, setSort] = useState<SortMode>('date')
  const [showPeriodSheet, setShowPeriodSheet] = useState(false)
  const [showSortMenu, setShowSortMenu] = useState(false)
  const [sortMenuPos, setSortMenuPos] = useState({ top: 0, right: 0 })
  const sortBtnRef = useRef<HTMLButtonElement>(null)
  const sortHistoryRef = useRef(false)

  const chipsScrollRef = useRef<HTMLDivElement>(null)
  const chipsCompactScrollRef = useRef<HTMLDivElement>(null)
  const [chipsScrollLeft, setChipsScrollLeft] = useState(0)
  const [chipsCompactScrollLeft, setChipsCompactScrollLeft] = useState(0)

  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [searchPreviousPeriod, setSearchPreviousPeriod] = useState<Period | null>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const searchDebounceRef = useRef<ReturnType<typeof setTimeout>>(0 as unknown as ReturnType<typeof setTimeout>)

  const [forYouActive, setForYouActive] = useState(() => getStoredEventsFilters().forYou)
  const [isNewActive, setIsNewActive] = useState(() => getStoredEventsFilters().isNew)

  const [userLocationState, setUserLocationState] = useState(() => getLastKnownLocation())
  const [locationToast, setLocationToast] = useState(false)
  const favorites = useMemo(() => getFavorites(), []) // eslint-disable-line react-hooks/exhaustive-deps
  const hasFavorites = favorites.size > 0

  const venueMap = useMemo(() => {
    const m = new Map<string, (typeof data.venues)[0]>()
    for (const v of data.venues) m.set(v.id, v)
    return m
  }, [data.venues])

  const venueLocations = useMemo(() => {
    const m = new Map<string, { lat: number; lng: number }>()
    for (const v of data.venues) m.set(v.id, { lat: v.lat, lng: v.lng })
    return m
  }, [data.venues])

  const periodSearchEvents = useMemo(() => {
    let evts = getEventsForPeriod(data.events, period, now)
    if (period.type === 'night') {
      evts = evts.filter(e => {
        const venue = venueMap.get(e.venue_id)
        return isNightEvent(e, venue?.character ?? [], venue?.closing ?? null, now)
      })
    }
    if (debouncedQuery.trim()) {
      evts = evts.filter(e => matchesSearch(debouncedQuery, e, venueMap.get(e.venue_id)))
    }
    return evts
  }, [data.events, period, debouncedQuery, now.getTime(), venueMap]) // eslint-disable-line react-hooks/exhaustive-deps

  const events = useMemo(() => {
    let evts = periodSearchEvents
    if (forYouActive) evts = evts.filter(e => isForYou(e, favorites))
    if (isNewActive) evts = evts.filter(e => isNew(e, now))
    return sortEvents(evts, venueLocations, sort, userLocationState)
  }, [periodSearchEvents, forYouActive, isNewActive, favorites, now.getTime(), venueLocations, sort, userLocationState]) // eslint-disable-line react-hooks/exhaustive-deps

  const forYouCountInDisplay = useMemo(() => {
    if (forYouActive || !hasFavorites) return 0
    return events.filter(e => isForYou(e, favorites)).length
  }, [events, forYouActive, hasFavorites, favorites])

  // Scroll to top + animate on filter change
  const prevFilterRef = useRef({ period, forYouActive, isNewActive, sort, debouncedQuery })
  useEffect(() => {
    const prev = prevFilterRef.current
    const changed = prev.period !== period || prev.forYouActive !== forYouActive ||
      prev.isNewActive !== isNewActive || prev.sort !== sort || prev.debouncedQuery !== debouncedQuery
    prevFilterRef.current = { period, forYouActive, isNewActive, sort, debouncedQuery }
    if (changed) {
      scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
      setAnimKey(k => k + 1)
    }
  }, [period, forYouActive, isNewActive, sort, debouncedQuery])

  useEffect(() => {
    if (!isNight && period.type === 'night') setPeriod({ type: 'today' })
  }, [isNight]) // eslint-disable-line react-hooks/exhaustive-deps

  // Revert distance sort when period becomes multi-day
  useEffect(() => {
    if (!isSingleDayPeriod(period) && sort === 'distance') setSort('date')
  }, [period]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { setStoredPeriod(period) }, [period])
  useEffect(() => { setStoredEventsFilters({ forYou: forYouActive, isNew: isNewActive }) }, [forYouActive, isNewActive])

  useEffect(() => {
    function onPopState() {
      if (sortHistoryRef.current) { sortHistoryRef.current = false; setShowSortMenu(false) }
    }
    window.addEventListener('popstate', onPopState)
    return () => window.removeEventListener('popstate', onPopState)
  }, [])

  function scrollToTop() {
    scrollRef.current?.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function openSortMenu() {
    const rect = sortBtnRef.current?.getBoundingClientRect()
    if (rect) setSortMenuPos({ top: rect.bottom + 4, right: window.innerWidth - rect.right })
    history.pushState({ sortMenu: true }, '')
    sortHistoryRef.current = true
    setShowSortMenu(true)
  }

  function closeSortMenu() {
    setShowSortMenu(false)
    if (sortHistoryRef.current) {
      sortHistoryRef.current = false
      history.back()
    }
  }

  function requestLocationForSort() {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      pos => {
        const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        setLastKnownLocation(loc)
        setUserLocationState(loc)
        setSort('distance')
      },
      () => {
        setLocationToast(true)
        setTimeout(() => setLocationToast(false), 3000)
      },
      { timeout: 10000, maximumAge: 60000 }
    )
  }

  function openSearch() {
    setSearchPreviousPeriod(period)
    setPeriod({ type: 'anytime' })
    setSearchOpen(true)
    scrollToTop()
    setTimeout(() => searchInputRef.current?.focus(), 50)
  }

  function closeSearch() {
    setSearchOpen(false)
    setSearchQuery('')
    setDebouncedQuery('')
    clearTimeout(searchDebounceRef.current)
    if (searchPreviousPeriod) { setPeriod(searchPreviousPeriod); setSearchPreviousPeriod(null) }
  }

  function handleSearchInput(value: string) {
    setSearchQuery(value)
    clearTimeout(searchDebounceRef.current)
    searchDebounceRef.current = setTimeout(() => setDebouncedQuery(value), 150)
  }

  function toggleForYou() { setForYouActive(v => !v) }
  function toggleIsNew() { setIsNewActive(v => !v) }

  const periodItems: SheetItem[] = useMemo(() => {
    const days = dict.days
    function right(p: Period): string { return formatPeriodRangeText(p, lang, days, now) }
    const items: SheetItem[] = [
      { id: 'anytime', label: dict.events.anytime, iconLeft: <InfinityIcon />, rightText: dict.events.anytimeSub, selected: period.type === 'anytime', separator: false },
    ]
    items.push({ id: '__sep__', label: '', selected: false, separator: true } as SheetItem)
    if (isNight) items.push({ id: 'night', label: dict.events.nightNow, rightText: '', selected: period.type === 'night' })
    items.push({ id: 'today', label: dict.map.today, rightText: right({ type: 'today' }), selected: period.type === 'today' })
    items.push({ id: 'tomorrow', label: dict.map.tomorrow, rightText: right({ type: 'tomorrow' }), selected: period.type === 'tomorrow' })
    items.push({ id: 'weekend', label: dict.events.weekend, rightText: right({ type: 'weekend' }), selected: period.type === 'weekend' })
    items.push({ id: 'next7', label: dict.events.next7, rightText: right({ type: 'next7' }), selected: period.type === 'next7' })
    items.push({ id: 'next30', label: dict.events.next30, rightText: right({ type: 'next30' }), selected: period.type === 'next30' })
    items.push({ id: 'custom', label: dict.map.otherDate, iconLeft: <CalendarIcon />, selected: period.type === 'custom', isCalendarTrigger: true })
    return items
  }, [period, lang, now]) // eslint-disable-line react-hooks/exhaustive-deps

  function handlePeriodItemSelect(id: string) {
    if (id === '__sep__') return
    const p: Period = id === 'today' ? { type: 'today' } : id === 'tomorrow' ? { type: 'tomorrow' }
      : id === 'night' ? { type: 'night' } : id === 'weekend' ? { type: 'weekend' }
      : id === 'next7' ? { type: 'next7' } : id === 'next30' ? { type: 'next30' } : { type: 'anytime' }
    setPeriod(p)
    if (searchOpen) setSearchPreviousPeriod(p)
    setShowPeriodSheet(false)
  }

  function handleCalendarSelect(from: string, to: string) {
    const p: Period = { type: 'custom', from, to }
    setPeriod(p)
    if (searchOpen) setSearchPreviousPeriod(p)
    setShowPeriodSheet(false)
  }

  const periodLabel = formatPeriodShortLabel(period, lang)
  const isSingleDay = isSingleDayPeriod(period)
  const sortDateLabel = isSingleDay ? dict.events.sortTime : dict.events.sortDate

  const sortItems: SheetItem[] = useMemo(() => [
    { id: 'date', label: sortDateLabel, selected: sort === 'date' },
    ...(isSingleDay ? [{ id: 'distance', label: dict.events.sortDistance, selected: sort === 'distance' }] : []),
  ], [sort, sortDateLabel, isSingleDay, dict.events.sortDistance]) // eslint-disable-line react-hooks/exhaustive-deps
  const isFilterActive = forYouActive || isNewActive || debouncedQuery.trim() !== ''
  const isForYouNoFavs = forYouActive && !hasFavorites
  const isEmpty = events.length === 0

  function countRowText(): string {
    if (period.type === 'anytime') return ''
    const base = eventCount(events.length, dict)
    if (forYouActive) return `${base} ${dict.events.forYouInCount}`
    if (hasFavorites && forYouCountInDisplay > 0) return `${base} · ${forYouCountInDisplay} ${dict.events.forYouInCount}`
    return base
  }

  const chipStyle = (active: boolean) => ({
    height: 40, padding: '0 14px', borderRadius: 20 as const, border: 0 as const,
    background: active ? '#FF4D8D' : '#23232F', color: active ? '#1A0710' : '#B9B6CC',
    fontFamily: 'Outfit,sans-serif', fontSize: 14, fontWeight: 500,
    display: 'flex' as const, alignItems: 'center' as const, gap: 6, whiteSpace: 'nowrap' as const, flex: 'none' as const, cursor: 'pointer' as const,
  })

  return (
    <div ref={scrollRef} style={{ position: 'absolute', inset: 0, fontFamily: "'Outfit', sans-serif", color: '#F4F2FF', overflowY: 'auto', overscrollBehaviorY: 'contain' }}>
      <style>{`
        @keyframes evCardIn { from { opacity:0; transform:scale(0.96) } to { opacity:1; transform:scale(1) } }
        @media (prefers-reduced-motion:reduce) { @keyframes evCardIn { from { opacity:1 } } }
        .chips-scroll::-webkit-scrollbar { display: none }
      `}</style>

      <PullRefreshIndicator pullDist={pullDist} isRefreshing={isRefreshing} />
      {refreshError && (
        <div style={{
          position: 'fixed', bottom: 100, left: '50%', transform: 'translateX(-50%)',
          background: '#2A2838', color: '#F4F2FF', padding: '10px 20px',
          borderRadius: 20, fontSize: 14, fontWeight: 600, zIndex: 300,
          whiteSpace: 'nowrap', boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
          pointerEvents: 'none',
        }}>
          {dict.event.refreshError}
        </div>
      )}
      {locationToast && (
        <div style={{
          position: 'fixed', bottom: 100, left: '50%', transform: 'translateX(-50%)',
          background: '#2A2838', color: '#F4F2FF', padding: '10px 20px',
          borderRadius: 20, fontSize: 14, fontWeight: 600, zIndex: 300,
          whiteSpace: 'nowrap', boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
          pointerEvents: 'none',
        }}>
          {dict.events.locationToastForSort}
        </div>
      )}

      {/* Compact sticky bar — fixed, only shown when this tab is visible and header scrolled away */}
      {isVisible !== false && <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 10,
        background: '#111118', boxShadow: '0 8px 16px rgba(17,17,24,.9)',
        padding: '10px 16px', display: 'flex', gap: 8, alignItems: 'center',
        opacity: collapsed ? 1 : 0,
        pointerEvents: collapsed ? 'auto' : 'none',
        transition: 'opacity 200ms',
      }}>
        {/* Scrollable section: period + chips */}
        <div style={{ flex: 1, minWidth: 0, position: 'relative' }}>
          {chipsCompactScrollLeft > 0 && (
            <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 40, background: 'linear-gradient(90deg,#111118,transparent)', pointerEvents: 'none', zIndex: 1 }} />
          )}
          <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: 40, background: 'linear-gradient(to left,#111118,transparent)', pointerEvents: 'none', zIndex: 1 }} />
          <div
            ref={chipsCompactScrollRef}
            data-no-ptr
            className="chips-scroll"
            style={{ display: 'flex', gap: 8, overflowX: 'auto', scrollbarWidth: 'none' }}
            onScroll={e => setChipsCompactScrollLeft((e.currentTarget as HTMLDivElement).scrollLeft)}
          >
            <button
              style={{ height: 44, padding: '0 14px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontFamily: 'Outfit,sans-serif', fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flex: 'none', cursor: 'pointer' }}
              onClick={() => setShowPeriodSheet(true)}
            >
              {periodLabel}<ChevronDown />
            </button>
            <button style={chipStyle(forYouActive)} onClick={toggleForYou}>
              <SparkleIcon size={16} color={forYouActive ? '#1A0710' : '#B9B6CC'} />{dict.events.forYou}
            </button>
            <button style={chipStyle(isNewActive)} onClick={toggleIsNew}>{dict.events.newLabel}</button>
            <div style={{ width: 40, flex: 'none' }} />
          </div>
        </div>
        <button
          style={{ flex: 'none', width: 44, height: 44, borderRadius: 22, border: 0, background: '#23232F', color: '#F4F2FF', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
          onClick={() => { scrollToTop(); setTimeout(openSearch, 300) }}
          aria-label="Hľadať"
        >
          <SearchIcon />
        </button>
        <button style={{ flex: 'none', width: 44, height: 44, borderRadius: 22, border: 0, background: '#FF4D8D', color: '#1A0710', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }} aria-label="Filter">
          <FilterIcon />
        </button>
      </div>}

      {/* Full header — scrolls away with content */}
      <div style={{ padding: '52px 16px 0', display: 'flex', flexDirection: 'column', gap: 14 }}>
        {/* Title row + search */}
        <div style={{ display: 'flex', alignItems: 'center', height: 44, position: 'relative' }}>
          <h1 style={{ margin: 0, flex: 1, fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: 32, fontWeight: 700, letterSpacing: '-0.02em', color: '#F4F2FF', opacity: searchOpen ? 0 : 1, transition: 'opacity 200ms', pointerEvents: searchOpen ? 'none' : 'auto' }}>
            {dict.events.title}
          </h1>
          {/* Search field — expands left using clip-path (no text deformation) */}
          <div style={{ position: 'absolute', left: 0, right: 52, opacity: searchOpen ? 1 : 0, clipPath: searchOpen ? 'inset(0 0% 0 0%)' : 'inset(0 100% 0 0%)', transition: 'clip-path 200ms, opacity 200ms', pointerEvents: searchOpen ? 'auto' : 'none' }}>
            <div style={{ height: 44, borderRadius: 22, background: '#F4F2FF', color: '#111118', display: 'flex', alignItems: 'center', gap: 8, padding: '0 14px' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8E8AA6" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flex: 'none' }}><circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" /></svg>
              <input ref={searchInputRef} value={searchQuery} onChange={e => handleSearchInput(e.target.value)} placeholder={dict.events.searchEvents} style={{ flex: 1, border: 'none', background: 'transparent', outline: 'none', fontSize: 15, fontWeight: 500, color: '#111118', fontFamily: "'Outfit', sans-serif", caretColor: '#FF4D8D', minWidth: 0 }} />
            </div>
          </div>
          <button style={{ marginLeft: 'auto', flex: 'none', width: 44, height: 44, borderRadius: 22, border: 0, background: '#23232F', color: '#F4F2FF', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }} onClick={searchOpen ? closeSearch : openSearch} aria-label={searchOpen ? 'Zavrieť hľadanie' : 'Hľadať'}>
            {searchOpen ? <CloseIcon /> : <SearchIcon />}
          </button>
        </div>

        {/* Bar: period + chips (scrollable) | filter (fixed) */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <div style={{ flex: 1, minWidth: 0, position: 'relative' }}>
            {chipsScrollLeft > 0 && (
              <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 40, background: 'linear-gradient(90deg,#111118,transparent)', pointerEvents: 'none', zIndex: 1 }} />
            )}
            <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: 40, background: 'linear-gradient(to left,#111118,transparent)', pointerEvents: 'none', zIndex: 1 }} />
            <div
              ref={chipsScrollRef}
              data-no-ptr
              className="chips-scroll"
              style={{ display: 'flex', gap: 8, overflowX: 'auto', scrollbarWidth: 'none' }}
              onScroll={e => setChipsScrollLeft((e.currentTarget as HTMLDivElement).scrollLeft)}
            >
              <button style={{ height: 44, padding: '0 14px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontFamily: 'Outfit,sans-serif', fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flex: 'none', cursor: 'pointer' }} onClick={() => setShowPeriodSheet(true)}>
                {periodLabel}<ChevronDown />
              </button>
              <button style={chipStyle(forYouActive)} onClick={toggleForYou}>
                <SparkleIcon size={16} color={forYouActive ? '#1A0710' : '#B9B6CC'} />{dict.events.forYou}
              </button>
              <button style={chipStyle(isNewActive)} onClick={toggleIsNew}>{dict.events.newLabel}</button>
              <div style={{ width: 40, flex: 'none' }} />
            </div>
          </div>
          <button style={{ marginLeft: 8, flex: 'none', width: 44, height: 44, borderRadius: 22, border: 0, background: '#FF4D8D', color: '#1A0710', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }} aria-label="Filter">
            <FilterIcon />
          </button>
        </div>

        {/* Count + sort row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 13, color: '#8E8AA6', marginTop: 2, position: 'relative' }}>
          <span>{countRowText()}</span>
          <button ref={sortBtnRef} style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, color: '#8E8AA6', padding: 0, fontFamily: "'Outfit', sans-serif" }} onClick={openSortMenu}>
            {dict.events.sort}: <b style={{ color: '#F4F2FF', fontWeight: 600 }}>{sort === 'date' ? sortDateLabel : dict.events.sortDistance}</b>
            <ChevronDown size={14} />
          </button>
        </div>

        {/* Sentinel: when this exits viewport, header is considered collapsed */}
        <div ref={headerSentinelRef} style={{ height: 1 }} />
      </div>

      {/* Grid or empty state */}
      {isEmpty ? (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, padding: '48px 32px' }}>
          <p style={{ margin: 0, fontSize: 16, color: '#B9B6CC', textAlign: 'center' }}>
            {isForYouNoFavs ? dict.events.noFavoriteVenues
              : (isEmpty && period.type === 'today' && !isFilterActive) ? dict.events.emptyToday
              : dict.events.emptyOther}
          </p>
          {isForYouNoFavs ? null : isFilterActive ? (
            <button style={{ height: 44, padding: '0 20px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontSize: 15, fontWeight: 600, cursor: 'pointer', fontFamily: "'Outfit', sans-serif" }} onClick={() => { setForYouActive(false); setIsNewActive(false); if (searchOpen) closeSearch() }}>
              {dict.events.clearFilters}
            </button>
          ) : (
            <button style={{ height: 44, padding: '0 20px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontSize: 15, fontWeight: 600, cursor: 'pointer', fontFamily: "'Outfit', sans-serif" }} onClick={() => setPeriod(period.type === 'today' ? { type: 'next7' } : { type: 'anytime' })}>
              {period.type === 'today' ? dict.events.tryWeek : dict.events.tryAnytime}
            </button>
          )}
        </div>
      ) : (
        <div style={{ padding: '14px 16px 100px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,minmax(0,1fr))', gap: '16px 8px', alignItems: 'start' }}>
            {events.map((event, idx) => (
              <EventCard
                key={event.id}
                event={event}
                venue={venueMap.get(event.venue_id)}
                lang={lang}
                now={now}
                eager={idx < 9}
                baseUrl={baseUrl}
                forYouFlag={isForYou(event, favorites)}
                isNewFlag={isNew(event, now)}
                animIn={animKey > 0 && idx < 12}
                onClick={() => onEventOpen(event.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Scroll-to-top button — only when this tab is visible */}
      {isVisible !== false && (
        <button
          onClick={scrollToTop}
          style={{ position: 'fixed', right: 16, bottom: 116, zIndex: 9, width: 44, height: 44, borderRadius: 22, border: 0, background: '#23232F', color: '#F4F2FF', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', boxShadow: '0 4px 12px rgba(0,0,0,.5)', opacity: showScrollTop ? 1 : 0, pointerEvents: showScrollTop ? 'auto' : 'none', transition: 'opacity 150ms' }}
          aria-label="Navrch" aria-hidden={!showScrollTop}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M12 19V5M6 11l6-6 6 6" /></svg>
        </button>
      )}

      {showPeriodSheet && (
        <SelectorSheet
          title={dict.events.period}
          items={periodItems}
          calendarMode="interval"
          now={now}
          lang={lang}
          onItemSelect={handlePeriodItemSelect}
          onCalendarSelect={handleCalendarSelect}
          onClose={() => setShowPeriodSheet(false)}
        />
      )}

      {showSortMenu && (
        <>
          <div style={{ position: 'fixed', inset: 0, zIndex: 25 }} onClick={closeSortMenu} />
          <div style={{
            position: 'fixed', right: sortMenuPos.right, top: sortMenuPos.top,
            zIndex: 26, background: '#1C1C27', borderRadius: 16,
            boxShadow: '0 4px 24px rgba(0,0,0,0.6)', minWidth: 160, overflow: 'hidden',
          }}>
            {sortItems.map(item => (
              <button key={item.id} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '12px 16px', background: 'none', border: 'none',
                color: item.selected ? '#F4F2FF' : '#B9B6CC',
                fontWeight: item.selected ? 600 : 400, fontFamily: "'Outfit', sans-serif",
                fontSize: 15, width: '100%', cursor: 'pointer', textAlign: 'left',
              }} onClick={() => {
                if (item.id === 'distance' && !userLocationState) {
                  closeSortMenu()
                  requestLocationForSort()
                } else {
                  setSort(item.id as SortMode)
                  closeSortMenu()
                }
              }}>
                {item.label}
                {item.selected && (
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FF4D8D" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10" /></svg>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
