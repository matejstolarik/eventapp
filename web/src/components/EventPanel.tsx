import { pressClass } from '../core/motion'
import { useState } from 'react'
import type { Event, Venue, Language } from '../core/types'
import { eventTags, getEventType, EVENT_TYPE_TAG_TEXT } from '../core/eventType'
import { joinDot, DOT_SEP } from '../core/dot'
import { haversine, formatDistance } from '../core/distance'
import { EventImage43, TypeIconPill } from './EventRow'
import { isNew, forYouScore, forYouTier } from '../core/search'
import { useForYouPrefs } from '../core/useForYouPrefs'
import { tagLabel } from '../i18n'
import { priceLabel } from '../core/eventText'

interface Props {
  events: Event[]
  venue: Venue
  lang: Language
  userLocation: { lat: number; lng: number } | null
  className?: string
  onClose: () => void
  onEventOpen: (eventId: string) => void
}


/** Horizontally scrollable tag row with right-edge fade-out. */
function TagRow({ children, 'aria-label': ariaLabel }: { children: React.ReactNode; 'aria-label': string }) {
  return (
    <div
      aria-label={ariaLabel}
      style={{
        position: 'relative',
        overflow: 'hidden',
        height: 32,
      }}
    >
      <div
        style={{
          display: 'flex',
          gap: 6,
          overflowX: 'auto',
          height: '100%',
          alignItems: 'center',
          scrollbarWidth: 'none',
          // Fade-out at right edge
          WebkitMaskImage: 'linear-gradient(to right, black calc(100% - 36px), transparent)',
          maskImage: 'linear-gradient(to right, black calc(100% - 36px), transparent)',
        }}
      >
        {children}
        {/* Spacer so last tag doesn't get cut by gradient */}
        <span style={{ flexShrink: 0, width: 32, display: 'inline-block' }} />
      </div>
    </div>
  )
}

export function EventPanel({ events, venue, lang, userLocation, className, onClose: _onClose, onEventOpen }: Props) {
  // venue is used for distance; character tags are shown only on the venue profile page
  const [currentIdx, setCurrentIdx] = useState(0)
  const forYouPrefs = useForYouPrefs()
  const [touchStartX, setTouchStartX] = useState<number | null>(null)

  const event = events[Math.min(currentIdx, events.length - 1)]!
  const tags = eventTags(event.formats, event.genres, event.primary_format)
  const tagText = EVENT_TYPE_TAG_TEXT[getEventType(event.formats, event.primary_format)]
  const now = new Date()
  const newFlag = isNew(event, now, venue && venue.id === event.venue_id ? venue : null)
  const forYouFlag = forYouTier(forYouScore(event, forYouPrefs))
  const pill: React.CSSProperties = {
    height: 32, padding: '0 14px', borderRadius: 16, fontSize: 14, fontWeight: 600,
    display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap', flexShrink: 0,
  }

  const distStr = userLocation
    ? formatDistance(haversine(venue.lat, venue.lng, userLocation.lat, userLocation.lng), lang)
    : ''
  // "time · distance" after the venue name (task 069: one shared joinDot)
  const tail = joinDot([event.start_time, distStr])
  const priceStr = priceLabel(event, lang)

  function handleTouchStart(e: React.TouchEvent) {
    setTouchStartX(e.touches[0]?.clientX ?? null)
  }
  function handleTouchEnd(e: React.TouchEvent) {
    if (touchStartX === null) return
    const dx = (e.changedTouches[0]?.clientX ?? 0) - touchStartX
    if (Math.abs(dx) > 40) {
      if (dx < 0) setCurrentIdx(i => Math.min(i + 1, events.length - 1))
      else setCurrentIdx(i => Math.max(i - 1, 0))
    }
    setTouchStartX(null)
  }


  return (
    <section
      className={className}
      style={{
        position: 'absolute', left: 12, right: 12, bottom: 112,
        borderRadius: 28, background: '#1C1C27',
        padding: 16, border: '1px solid #2E2D3C',
        zIndex: 20,
        touchAction: 'pan-y',
      }}
      aria-label="Vybraná akcia"
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <button
        style={{
          display: 'flex', gap: 14, textDecoration: 'none', color: '#F4F2FF',
          width: '100%', background: 'none', border: 'none', textAlign: 'left',
          cursor: 'pointer', padding: 0,
        }}
        onClick={() => onEventOpen(event.id)}
        className={pressClass()}
        aria-label="Otvoriť akciu"
      >
        {/* 4:3 image (task 068; type ring removed in 069; new + for you on the image in 070) */}
        <EventImage43 event={event} venue={venue} width={120} eager isNew={newFlag} forYou={forYouFlag} lang={lang} />
        <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 6 }}>
          <p style={{
            margin: 0,
            fontFamily: "'Bricolage Grotesque', sans-serif",
            fontSize: 21, fontWeight: 700,
            lineHeight: 1.1, letterSpacing: '-0.01em',
            overflow: 'hidden', display: '-webkit-box',
            WebkitLineClamp: 2, WebkitBoxOrient: 'vertical',
          }}>
            {event.title}
          </p>
          {/* venue · time · distance, always one line; only the venue name is shortened */}
          <div style={{ display: 'flex', minWidth: 0, whiteSpace: 'nowrap', fontSize: 14, color: '#B9B6CC' }}>
            <span style={{ minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis' }}>{venue.name}</span>
            {/* white-space: pre keeps the space before the dot at the start of this flex item */}
            {tail && <span style={{ flexShrink: 0, whiteSpace: 'pre' }}>{DOT_SEP + tail}</span>}
          </div>
          {priceStr && <p style={{ margin: 0, fontSize: 13, color: '#8B8AA0' }}>{priceStr}</p>}
        </div>
      </button>

      {/* Tag row: type icon pill first (task 071, as in Akcie), then event tags with
          type-coloured text (task 069); new / for you are on the image (070) */}
      <div style={{ marginTop: 12 }}>
        <TagRow aria-label="Štítky akcie">
          <TypeIconPill event={event} height={32} iconSize={20} />
          {tags.map(tag => (
            <span key={tag} style={{ ...pill, background: '#2A2838', color: tagText }}>{tagLabel(tag, lang)}</span>
          ))}
        </TagRow>
      </div>

      {/* Dots for multiple events */}
      {events.length > 1 && (
        <div style={{ display: 'flex', gap: 6, marginTop: 10, justifyContent: 'center' }}>
          {events.map((_, i) => (
            <button
              key={i}
              style={{
                width: i === currentIdx ? 16 : 6,
                height: 6, borderRadius: 3,
                background: i === currentIdx ? '#F4F2FF' : '#3A3A50',
                border: 'none', cursor: 'pointer', padding: 0,
                transition: 'width 0.2s',
              }}
              onClick={(e) => { e.stopPropagation(); setCurrentIdx(i) }}
              aria-label={`Akcia ${i + 1}`}
            />
          ))}
        </div>
      )}
    </section>
  )
}
