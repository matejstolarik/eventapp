import { useState, useMemo, useEffect, useRef } from 'react'
import type { EventsData, Language, Event } from '../core/types'
import { getDict, formatDayLabel } from '../i18n'
import { getEventType, EVENT_TYPE_COLOR } from '../core/eventType'
import { getEventsForPeriod, sortEvents, formatPeriodShortLabel, formatPeriodRangeText, type Period, type SortMode } from '../core/period'
import { getStoredPeriod, setStoredPeriod, getLastKnownLocation } from '../core/store'
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

function TypeIcon({ type }: { type: string }) {
  const color = EVENT_TYPE_COLOR[type as keyof typeof EVENT_TYPE_COLOR] ?? '#C6F432'
  if (type === 'concert') return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"/>
      <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3M8 22h8"/>
    </svg>
  )
  if (type === 'party') return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M8 22h8M12 2l1.5 4L18 7.5l-4.5 1.5L12 14l-1.5-5L6 7.5l4.5-1.5z"/>
    </svg>
  )
  if (type === 'dj') return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"/>
      <circle cx="12" cy="12" r="8"/>
      <path d="M12 4v2M12 18v2M4 12h2M18 12h2"/>
    </svg>
  )
  // culture / other
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2 10s3-3 6-3 5 2 8 2 6-3 6-3v10s-3 3-6 3-5-2-8-2-6 3-6 3V10z"/>
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
  onClick: () => void
}

function EventCard({ event, venue, lang, now, eager, baseUrl, onClick }: EventCardProps) {
  const type = getEventType(event.formats)
  const color = EVENT_TYPE_COLOR[type]
  const dateLabel = formatDayLabel(event.date, lang, now)
  const timeLabel = event.start_time ?? ''
  const allTags = [...event.formats, ...event.genres]
  const venueTags = venue?.character ?? []

  return (
    <div style={{ minWidth: 0, cursor: 'pointer' }} onClick={onClick} role="button" tabIndex={0} onKeyDown={e => e.key === 'Enter' && onClick()}>
      {/* Image / placeholder */}
      <div style={{ width: '100%', aspectRatio: '1/1', borderRadius: 12, overflow: 'hidden', position: 'relative', background: color, display: 'flex', alignItems: 'flex-end', padding: 7, boxSizing: 'border-box' }}>
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
          <span style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', width: '100%', paddingBottom: 8 }}>
            <TypeIcon type={type} />
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

  const [period, setPeriod] = useState<Period>(() => getStoredPeriod() ?? { type: 'today' })
  const [sort, setSort] = useState<SortMode>('date')
  const [showPeriodSheet, setShowPeriodSheet] = useState(false)
  const [showSortMenu, setShowSortMenu] = useState(false)
  const sortMenuRef = useRef<HTMLDivElement>(null)

  const userLocation = getLastKnownLocation()

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

  const events = useMemo(() => {
    const filtered = getEventsForPeriod(data.events, period, now)
    return sortEvents(filtered, venueLocations, sort, userLocation)
  }, [data.events, period, sort, now.getTime(), venueLocations, userLocation]) // eslint-disable-line react-hooks/exhaustive-deps

  // Persist period (not custom)
  useEffect(() => { setStoredPeriod(period) }, [period])

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
      : id === 'weekend' ? { type: 'weekend' }
      : id === 'next7' ? { type: 'next7' }
      : id === 'next30' ? { type: 'next30' }
      : { type: 'anytime' }
    setPeriod(p)
    setShowPeriodSheet(false)
  }

  function handleCalendarSelect(from: string, to: string) {
    setPeriod({ type: 'custom', from, to })
    setShowPeriodSheet(false)
  }

  const periodLabel = formatPeriodShortLabel(period, lang)

  const isEmptyToday = events.length === 0 && period.type === 'today'
  const isEmpty = events.length === 0

  return (
    <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', fontFamily: "'Outfit', sans-serif", color: '#F4F2FF' }}>
      {/* Header */}
      <div style={{ padding: '52px 16px 0', display: 'flex', flexDirection: 'column', gap: 14, flexShrink: 0 }}>
        {/* Title row */}
        <div style={{ display: 'flex', alignItems: 'center', height: 44 }}>
          <h1 style={{ margin: 0, fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: 32, fontWeight: 700, letterSpacing: '-0.02em', color: '#F4F2FF' }}>
            {dict.events.title}
          </h1>
        </div>

        {/* Bar: period button */}
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button
            style={{ height: 44, padding: '0 14px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontFamily: 'Outfit,sans-serif', fontSize: 15, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 6, whiteSpace: 'nowrap', flex: 'none', cursor: 'pointer' }}
            onClick={() => setShowPeriodSheet(true)}
          >
            {periodLabel}
            <ChevronDown />
          </button>
        </div>

        {/* Count + sort row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 13, color: '#8E8AA6', marginTop: 2 }}>
          <span>{eventCount(events.length, dict)}</span>
          <div style={{ position: 'relative' }} ref={sortMenuRef}>
            <button
              style={{ display: 'flex', alignItems: 'center', gap: 4, background: 'none', border: 'none', cursor: 'pointer', fontSize: 13, color: '#8E8AA6', padding: 0, fontFamily: "'Outfit', sans-serif" }}
              onClick={() => setShowSortMenu(s => !s)}
            >
              {dict.events.sort}: <b style={{ color: '#F4F2FF', fontWeight: 600 }}>{sort === 'date' ? dict.events.sortDate : dict.events.sortDistance}</b>
              <ChevronDown size={14} />
            </button>
            {showSortMenu && (
              <div style={{ position: 'absolute', right: 0, top: '100%', marginTop: 4, background: '#1C1C27', borderRadius: 12, padding: '4px 0', boxShadow: '0 4px 16px rgba(0,0,0,0.5)', zIndex: 10, minWidth: 140 }}>
                {(['date', ...(userLocation ? ['distance'] : [])] as SortMode[]).map(s => (
                  <button key={s} style={{ display: 'block', width: '100%', textAlign: 'left', padding: '10px 16px', background: 'none', border: 'none', fontSize: 15, color: s === sort ? '#F4F2FF' : '#B9B6CC', fontWeight: s === sort ? 600 : 400, cursor: 'pointer', fontFamily: "'Outfit', sans-serif" }} onClick={() => { setSort(s); setShowSortMenu(false) }}>
                    {s === 'date' ? dict.events.sortDate : dict.events.sortDistance}
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
            {isEmptyToday ? dict.events.emptyToday : dict.events.emptyOther}
          </p>
          <button
            style={{ height: 44, padding: '0 20px', borderRadius: 22, border: 0, background: '#F4F2FF', color: '#111118', fontSize: 15, fontWeight: 600, cursor: 'pointer', fontFamily: "'Outfit', sans-serif" }}
            onClick={() => { setPeriod(isEmptyToday ? { type: 'next7' } : { type: 'anytime' }) }}
          >
            {isEmptyToday ? dict.events.tryWeek : dict.events.tryAnytime}
          </button>
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
