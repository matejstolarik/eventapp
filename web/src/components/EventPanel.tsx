import { useState } from 'react'
import type { Event, Venue, Language } from '../core/types'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'
import { haversine, formatDistance } from '../core/distance'
import { EventTypeIcon } from '../icons'

interface Props {
  events: Event[]
  venue: Venue
  lang: Language
  userLocation: { lat: number; lng: number } | null
  onClose: () => void
  onEventOpen: (eventId: string) => void
}

const FORMAT_COLORS: Record<string, [string, string]> = {
  party:    ['#FF8A3D', '#2A1200'],
  dj:       ['#2FD4C0', '#002B26'],
  concert:  ['#8B6CFF', '#14063A'],
  music:    ['#8B6CFF', '#14063A'],
  dance:    ['#C6F432', '#1B2600'],
  theatre:  ['#C6F432', '#1B2600'],
  talk:     ['#C6F432', '#1B2600'],
  comedy:   ['#C6F432', '#1B2600'],
  film:     ['#C6F432', '#1B2600'],
  opening:  ['#C6F432', '#1B2600'],
  workshop: ['#C6F432', '#1B2600'],
  quiz:     ['#C6F432', '#1B2600'],
  other:    ['#C6F432', '#1B2600'],
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

export function EventPanel({ events, venue, lang, userLocation, onClose: _onClose, onEventOpen }: Props) {
  // venue is used for distance; character tags are shown only on the venue profile page
  const [currentIdx, setCurrentIdx] = useState(0)
  const [touchStartX, setTouchStartX] = useState<number | null>(null)

  const event = events[Math.min(currentIdx, events.length - 1)]!
  const eventType = getEventType(event.formats)
  const color = EVENT_TYPE_COLOR[eventType]
  const dark = EVENT_TYPE_DARK[eventType]

  const distStr = userLocation
    ? ' · ' + formatDistance(haversine(venue.lat, venue.lng, userLocation.lat, userLocation.lng), lang)
    : ''

  const timeStr = event.start_time ? ` · ${event.start_time}` : ''
  const subtitle = `${venue.name}${timeStr}${distStr}`

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

  // Row 1: event formats + genres
  const formatTags = event.formats.map(f => {
    const [bg, fg] = FORMAT_COLORS[f] ?? ['#2A2838', '#E4DEFF']
    return (
      <span key={f} style={{
        height: 32, padding: '0 14px', borderRadius: 16,
        background: bg, color: fg,
        fontSize: 14, fontWeight: 600,
        display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap', flexShrink: 0,
      }}>{f}</span>
    )
  })
  const genreTags = event.genres.map(g => (
    <span key={g} style={{
      height: 32, padding: '0 14px', borderRadius: 16,
      background: '#2A2838', color: '#E4DEFF',
      fontSize: 14, fontWeight: 600,
      display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap', flexShrink: 0,
    }}>{g}</span>
  ))

  return (
    <section
      className="event-panel-enter"
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
        aria-label="Otvoriť akciu"
      >
        {/* Image or color placeholder */}
        <div style={{
          width: 88, height: 88, borderRadius: 18,
          background: color, flexShrink: 0,
          overflow: 'hidden', position: 'relative',
        }}>
          {event.image_url ? (
            <img src={event.image_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <div style={{
              position: 'absolute', inset: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <EventTypeIcon type={eventType} size={36} color={dark} />
            </div>
          )}
        </div>
        <div style={{ minWidth: 0, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 6 }}>
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
          <p style={{ margin: 0, fontSize: 14, color: '#B9B6CC' }}>{subtitle}</p>
        </div>
      </button>

      {/* Tag row: event formats + genres only (venue character tags belong on venue profile) */}
      {(formatTags.length > 0 || genreTags.length > 0) && (
        <div style={{ marginTop: 12 }}>
          <TagRow aria-label="Štítky akcie">
            {formatTags}
            {genreTags}
          </TagRow>
        </div>
      )}

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
