import { useState, useMemo, useEffect, useRef } from 'react'
import type { EventsData, Language, Event } from '../core/types'
import { getDict, formatDayLabel } from '../i18n'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'
import { getEventsForPeriod, sortEvents, formatPeriodShortLabel, formatPeriodRangeText, isSingleDayPeriod, type Period, type SortMode } from '../core/period'
import { getStoredPeriod, setStoredPeriod, getLastKnownLocation, getFavorites, getStoredEventsFilters, setStoredEventsFilters } from '../core/store'
import { matchesSearch, isForYou, isNew } from '../core/search'
import { isNightMode, isNightEvent } from '../core/night'
import { EventTypeIcon } from '../icons'
import { SelectorSheet, InfinityIcon, CalendarIcon, ChevronDown, type SheetItem } from '../components/SelectorSheet'

interface Props {
  data: EventsData
  lang: Language
  onEventOpen: (eventId: string) => void
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

interface EventCardProps {
  event: Event
  venue: { name: string; character: string[] } | undefined
  lang: Language
  now: Date
  eager: boolean
  baseUrl: string
  forYouFlag: boolean
  isNewFlag: boolean
  onClick: () => void
}

function EventCard({ event, venue, lang, now, eager, baseUrl, forYouFlag, isNewFlag, onClick }: EventCardProps) {
  const type = getEventType(event.formats)
  const color = EVENT_TYPE_COLOR[type]
  const dark = EVENT_TYPE_DARK[type]
  const dateLabel = formatDayLabel(event.date, lang, now)
  const timeLabel = event.start_time ?? ''
  const allTags = [...event.formats, ...event.genres]
  const venueTags = venue?.character ?? []

  return (
    <div style={{ minWidth: 0, cursor: 'pointer' }} onClick={onClick} role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && onClick()}>
      {/* Image / placeholder */}
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
          <EventTypeIcon type={type} size={40} color={dark} />
        )}
        {/* pre teba badge – top left */}
        {forYouFlag && (
          <span style={{ position: 'absolute', top: 6, left: 6, zIndex: 2, height: 18, padding: '0 6px', borderRadius: 9, background: '#111118', color: '#F4F2FF', fontSize: 10, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 3 }}>
            <SparkleIcon size={11} color="#F4F2FF" />
            {lang === 'en' ? 'for you' : lang === 'cs' ? 'pro tebe' : 'pre teba'}
          </span>
        )}
        {/* nové badge – top right */}
        {isNewFlag && (
          <span style={{ position: 'absolute', top: 6, right: 6, zIndex: 2, height: 18, padding: '0 6px', borderRadius: 9, background: '#F4F2FF', color: '#111118', fontSize: 10, fontWeight: 600, display: 'flex', alignItems: 'center' }}>
            {lang === 'en' ? 'new' : 'nové'}
          </span>
        )}
      </div>

      {/* Date · time */}
      <div style={{ marginTop: 6, fontSize: 12, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden' }}>
        <span style={{ color: '#8E8AA6', fontWeight: 500 }}>{dateLabel}{timeLabel ? ' · ' : ''}</span>
        {timeLabel && <span style={{ color }}>{timeLabel}</span>}
      </div>

      {/* Title */}
      <div style={{
        fontSize: 13, fontWeight: 500, lineHeight: 1.25,
        maxHeight: '2.5em', overflow: 'hidden', marginTop: 1,
        display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
      }}>
        {event.title}
      </div>

      {/* Venue */}
      {venue && (
        <div style={{ fontSize: 12, fontWeight: 700, color: '#B9B6CC', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginTop: 1 }}>
          {venue.name}
        </div>
      )}

      {/* Tags */}
      <div style={{ display: 'flex', gap: 4, marginTop: 5, overflow: 'hidden', WebkitMaskImage: 'linear-gradient(90deg,#000 78%,transparent)', maskImage: 'linear-gradient(90deg,#000 78%,transparent)' }}>
        {allTags.map(tag => (
          <span key={tag} style={{ flex: 'none', height: 18, padding: '0 6px', borderRadius: 9, fontSize: 10, fontWeight: 500, display: 'flex', alignItems: 'center', background: '#2A2838', color: '#E4DEFF' }}>
            {tag}
          </span>
        ))}
        {venueTags.map(tag => (
          <span key={`v-${tag}`} style={{ flex: 'none', height: 18, padding: '0 6px', borderRadius: 9, fontSize: 10, fontWeight: 500, display: 'flex', alignItems: 'center', border: '1.5px solid #5D5677', color: '#F4F2FF', boxSizing: 'border-box' }}>
            {tag}
          </span>
        ))}
      </div>
    </div>
  )
}

export function EventsPage({ data, lang, onEventOpen }: Props) {
  const dict = getDict(lang)
  const now = new Date()
  const baseUrl = import.meta.env.BASE_URL

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
  const sortMenuRef = useRef<HTMLDivElement>(null)

  // Search state
  const [searchOpen, setSearchOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const [searchPreviousPeriod, setSearchPreviousPeriod] = useState<Period | null>(null)
  const searchInputRef = useRef<HTMLInputElement>(null)
  const searchDebounceRef = useRef<ReturnType<typeof setTimeout>>(0 as unknown as ReturnType<typeof setTimeout>)

  // Chip filters
  const [forYouActive, setForYouActive] = useState(() => getStoredEventsFilters().forYou)
  const [isNewActive, setIsNewActive] = useState(() => getStoredEventsFilters().isNew)

  const userLocation = getLastKnownLocation()

  const favorites = useMemo(() => getFavorites(), []) // eslint-disable-line react-hooks/exhaustive-deps
  const hasFavorites = favorites.size > 0

  // Build venue map for fast lookup
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

  // Events filtered by period + search (before forYou/isNew chips)
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

  // Final events after all filters + sort
  const events = useMemo(() => {
    let evts = periodSearchEvents
    if (forYouActive) evts = evts.filter(e => isForYou(e, favorites))
    if (isNewActive) evts = evts.filter(e => isNew(e, now))
    return sortEvents(evts, venueLocations, sort, userLocation)
  }, [periodSearchEvents, forYouActive, isNewActive, favorites, now.getTime(), venueLocations, sort, userLocation]) // eslint-disable-line react-hooks/exhaustive-deps

  // Count of "for you" events in the current display (used when forYou chip is OFF)
  const forYouCountInDisplay = useMemo(() => {
    if (forYouActive || !hasFavorites) return 0
    return events.filter(e => isForYou(e, favorites)).length
  }, [events, forYouActive, hasFavorites, favorites])

  // Persist period (not custom)
  useEffect(() => { setStoredPeriod(period) }, [period])

  // Persist chip filters
  useEffect(() => { setStoredEventsFilters({ forYou: forYouActive, isNew: isNewActive }) }, [forYouActive, isNewActive])

  // Close sort menu on outside click
  useEffect(() => {
    if (!showSortMenu) return
    function handler(e: MouseEvent) {
      if (sortMenuRef.current && !sortMenuRef.current.contains(e.target as Node)) {
        setShowSortMenu(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [showSortMenu])

  function openSearch() {
    setSearchPreviousPeriod(period)
    setPeriod({ type: 'anytime' })
    setSearchOpen(true)
    // Focus input after animation starts
    setTimeout(() => searchInputRef.current?.focus(), 50)
  }

  function closeSearch() {
    setSearchOpen(false)
    setSearchQuery('')
    setDebouncedQuery('')
    clearTimeout(searchDebounceRef.current)
    if (searchPreviousPeriod) {
      setPeriod(searchPreviousPeriod)
      setSearchPreviousPeriod(null)
    }
  }

  function handleSearchInput(value: string) {
    setSearchQuery(value)
    clearTimeout(searchDebounceRef.current)
    searchDebounceRef.current = setTimeout(() => setDebouncedQuery(value), 150)
  }

  function toggleForYou() {
    setForYouActive(v => !v)
  }

  function toggleIsNew() {
    setIsNewActive(v => !v)
  }

  // Period sheet items
  const periodItems: SheetItem[] = useMemo(() => {
    const days = dict.days
    function right(p: Period): string {
      return formatPeriodRangeText(p, lang, days, now)
    }

    const items: SheetItem[] = [
      {
        id: 'anytime',
        label: dict.events.anytime,
        iconLeft: <InfinityIcon />,
        rightText: dict.events.anytimeSub,
        selected: period.type === 'anytime',
        separator: false,
      },
    ]
    items.push({
      id: '__sep__', label: '', selected: false, separator: true,
    } as SheetItem)
    if (isNight) {
      items.push({ id: 'night', label: dict.events.nightNow, rightText: '', selected: period.type === 'night' })
    }
    items.push({ id: 'today', label: dict.map.today, rightText: right({ type: 'today' }), selected: period.type === 'today' })
    items.push({ id: 'tomorrow', label: dict.map.tomorrow, rightText: right({ type: 'tomorrow' }), selected: period.type === 'tomorrow' })
    items.push({ id: 'weekend', label: dict.events.weekend, rightText: right({ type: 'weekend' }), selected: period.type === 'weekend' })
    items.push({ id: 'next7', label: dict.events.next7, rightText: right({ type: 'next7' }), selected: period.type === 'next7' })
    items.push({ id: 'next30', label: dict.events.next30, rightText: right({ type: 'next30' }), selected: period.type === 'next30' })
    items.push({
      id: 'custom',
      label: dict.map.otherDate,
      iconLeft: <CalendarIcon />,
      selected: period.type === 'custom',
      isCalendarTrigger: true,
    })
    return items
  }, [period, lang, now]) // eslint-disable-line react-hooks/exhaustive-deps

  function handlePeriodItemSelect(id: string) {
    if (id === '__sep__') return
    const p: Period = id === 'today' ? { type: 'today' }
      : id === 'tomorrow' ? { type: 'tomorrow' }
      : id === 'night' ? { type: 'night' }
      : id === 'weekend' ? { type: 'weekend' }
      : id === 'next7' ? { type: 'next7' }
      : id === 'next30' ? { type: 'next30' }
      : { type: 'anytime' }
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

  const isFilterActive = forYouActive || isNewActive || debouncedQuery.trim() !== ''
  const isForYouNoFavs = forYouActive && !hasFavorites
  const isEmpty = events.length === 0

  // Count row text
  function countRowText(): string {
    const base = eventCount(events.length, dict)
    if (forYouActive) return `${base} ${dict.events.forYouInCount}`
    if (hasFavorites && forYouCountInDisplay > 0) {
      return `${base} · ${forYouCountInDisplay} ${dict.events.forYouInCount}`
    }
    return base
  }

  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', fontFamily: "'Outfit', sans-serif", color: '#F4F2FF' }}>
      {/* Header */}
      <div style={{ padding: '52px 16px 0', display: 'flex', flexDirection: 'column', gap: 14, flexShrink: 0 }}>
        {/* Title row */}
        <div style={{ display: 'flex', alignItems: 'center', height: 44, position: 'relative' }}>
          {/* Title */}
          <h1 style={{
            margin: 0, flex: 1, fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: 32, fontWeight: 700, letterSpacing: '-0.02em', color: '#F4F2FF',
            opacity: searchOpen ? 0 : 1,
            transition: 'opacity 200ms',
            pointerEvents: searchOpen ? 'none' : 'auto',
          }}>
            {dict.events.title}
          </h1>

          {/* Search input – expands from right to left */}
          <div style={{
            position: 'absolute',
            left: 0,
            right: 52, // 44px button + 8px gap
            opacity: searchOpen ? 1 : 0,
            transform: searchOpen ? 'scaleX(1)' : 'scaleX(0)',
            transformOrigin: 'right',
            transition: 'transform 200ms, opacity 200ms',
            pointerEvents: searchOpen ? 'auto' : 'none',
          }}>
            <div style={{ height: 44, borderRadius: 22, background: '#F4F2FF', color: '#111118', display: 'flex', alignItems: 'center', gap: 8, padding: '0 14px' }}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ flex: 'none', color: '#8E8AA6' }}>
                <circle cx="11" cy="11" r="7" />
                <path d="M20 20l-3.5-3.5" />
              </svg>
              <input
                ref={searchInputRef}
                value={searchQuery}
                onChange={e => handleSearchInput(e.target.value)}
                style={{ flex: 1, border: 'none', background: 'transparent', outline: 'none', fontSize: 15, fontWeight: 500, color: '#111118', fontFamily: "'Outfit', sans-serif", caretColor: '#FF4D8D', minWidth: 0 }}
              />
            </div>
          </div>

          {/* Lupa / X button */}
          <button
            style={{ marginLeft: 'auto', flex: 'none', width: 44, height: 44, borderRadius: 22, border: 0, background: '#23232F', color: '#F4F2FF', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}
            onClick={searchOpen ? closeSearch : openSearch}
            aria-label={searchOpen ? 'Zavrieť hľadanie' : 'Hľadať'}
          >
            {searchOpen ? <CloseIcon /> : <SearchIcon />}
          </button>
        </div>

        {/* Bar: period button + chips */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button
            style={{ height: 44, padding: '0 14px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontFamily: 'Outfit,sans-serif', fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flex: 'none', cursor: 'pointer' }}
            onClick={() => setShowPeriodSheet(true)}
          >
            {periodLabel}
            <ChevronDown />
          </button>

          {/* Chips area – scrollable with right fade */}
          <div style={{ flex: 1, minWidth: 0, display: 'flex', gap: 8, overflow: 'hidden', WebkitMaskImage: 'linear-gradient(90deg,#000 80%,transparent)', maskImage: 'linear-gradient(90deg,#000 80%,transparent)' }}>
            {/* Pre teba chip */}
            <button
              style={{ height: 40, padding: '0 14px', borderRadius: 20, border: 0, background: forYouActive ? '#FF4D8D' : '#23232F', color: forYouActive ? '#1A0710' : '#B9B6CC', fontFamily: 'Outfit,sans-serif', fontSize: 14, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flex: 'none', cursor: 'pointer' }}
              onClick={toggleForYou}
            >
              <SparkleIcon size={16} color={forYouActive ? '#1A0710' : '#B9B6CC'} />
              {dict.events.forYou}
            </button>

            {/* Nové chip */}
            <button
              style={{ height: 40, padding: '0 14px', borderRadius: 20, border: 0, background: isNewActive ? '#FF4D8D' : '#23232F', color: isNewActive ? '#1A0710' : '#B9B6CC', fontFamily: 'Outfit,sans-serif', fontSize: 14, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flex: 'none', cursor: 'pointer' }}
              onClick={toggleIsNew}
            >
              {dict.events.newLabel}
            </button>
          </div>
        </div>

        {/* Count + sort row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 13, color: '#8E8AA6', marginTop: 2 }}>
          <span>{countRowText()}</span>
          <div style={{ position: 'relative' }} ref={sortMenuRef}>
            <button
              style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, color: '#8E8AA6', padding: 0, fontFamily: "'Outfit', sans-serif" }}
              onClick={() => setShowSortMenu(s => !s)}
            >
              {dict.events.sort}: <b style={{ color: '#F4F2FF', fontWeight: 600 }}>{sort === 'date' ? sortDateLabel : dict.events.sortDistance}</b>
              <ChevronDown size={14} />
            </button>
            {showSortMenu && (
              <div style={{ position: 'absolute', right: 0, top: '100%', marginTop: 4, background: '#1C1C27', borderRadius: 12, padding: '4px 0', boxShadow: '0 4px 16px rgba(0,0,0,0.5)', zIndex: 10, minWidth: 140 }}>
                {(['date', ...(userLocation ? ['distance'] : [])] as SortMode[]).map(s => (
                  <button key={s} style={{ display: 'block', width: '100%', textAlign: 'left', padding: '10px 16px', background: 'none', border: 'none', fontSize: 15, color: s === sort ? '#F4F2FF' : '#B9B6CC', fontWeight: s === sort ? 600 : 400, cursor: 'pointer', fontFamily: "'Outfit', sans-serif" }} onClick={() => { setSort(s); setShowSortMenu(false) }}>
                    {s === 'date' ? sortDateLabel : dict.events.sortDistance}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Grid */}
      {isEmpty ? (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, padding: '0 32px' }}>
          <p style={{ margin: 0, fontSize: 16, color: '#B9B6CC', textAlign: 'center' }}>
            {isForYouNoFavs
              ? dict.events.noFavoriteVenues
              : (isEmpty && period.type === 'today' && !isFilterActive)
                ? dict.events.emptyToday
                : dict.events.emptyOther}
          </p>
          {isForYouNoFavs ? null : isFilterActive ? (
            <button
              style={{ height: 44, padding: '0 20px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontSize: 15, fontWeight: 600, cursor: 'pointer', fontFamily: "'Outfit', sans-serif" }}
              onClick={() => { setForYouActive(false); setIsNewActive(false); if (searchOpen) closeSearch() }}
            >
              {dict.events.clearFilters}
            </button>
          ) : (
            <button
              style={{ height: 44, padding: '0 20px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontSize: 15, fontWeight: 600, cursor: 'pointer', fontFamily: "'Outfit', sans-serif" }}
              onClick={() => { setPeriod(period.type === 'today' ? { type: 'next7' } : { type: 'anytime' }) }}
            >
              {period.type === 'today' ? dict.events.tryWeek : dict.events.tryAnytime}
            </button>
          )}
        </div>
      ) : (
        <div style={{ flex: 1, overflowY: 'auto', padding: '14px 16px 100px' }}>
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
                onClick={() => onEventOpen(event.id)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Period sheet */}
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
    </div>
  )
}
