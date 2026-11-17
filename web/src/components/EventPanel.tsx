import { useState } from 'react'
import type { Event, Venue, Language } from '../core/types'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK, EVENT_TYPE_TAG_TEXT, eventTags, eventIconKey } from '../core/eventType'
import { haversine, formatDistance } from '../core/distance'
import { EventTypeIcon } from '../icons'
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
  const [touchStartX, setTouchStartX] = useState<number | null>(null)

  const event = events[Math.min(currentIdx, events.length - 1)]!
  const eventType = getEventType(event.formats, event.primary_format)
  const iconKey = eventIconKey(event.formats, event.primary_format)
  const color = EVENT_TYPE_COLOR[eventType]
  const dark = EVENT_TYPE_DARK[eventType]
  const tagTextColor = EVENT_TYPE_TAG_TEXT[eventType]
  const tags = eventTags(event.formats, event.genres, event.primary_format)

  const distStr = userLocation
    ? ' Â· ' + formatDistance(haversine(venue.lat, venue.lng, userLocation.lat, userLocation.lng), lang)
    : ''

  const timeStr = event.start_time ? ` Â· ${event.start_time}` : ''
  const subtitle = `${venue.name}${timeStr}${distStr}`
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
      aria-label="VybranÃ¡ akcia"
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
        aria-label="OtvoriÅ¥ akciu"
      >
        {/* Image or color placeholder */}
        <div style={{
          width: 88, height: 88, borderRadius: 18,
          background: color, flexShrink: 0,
          overflow: 'hidden', position: 'relative',
        }}>
          {event.image_thumb ? (
            <img src={event.image_thumb} alt="" width={88} height={88} decoding="async" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <div style={{
              position: 'absolute', inset: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <EventTypeIcon iconKey={iconKey} size={36} color={dark} />
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
          {priceStr && <p style={{ margin: 0, fontSize: 13, color: '#8B8AA0' }}>{priceStr}</p>}
        </div>
      </button>

      {/* Tag row: culture subtypes + genres, dark pills, type text color; no type tag */}
      {tags.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <TagRow aria-label="Å tÃ­tky akcie">
            {tags.map(tag => (
              <span key={tag} style={{
                height: 32, padding: '0 14px', borderRadius: 16,
                background: '#2A2838', color: tagTextColor,
                fontSize: 14, fontWeight: 600,
                display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap', flexShrink: 0,
              }}>{tagLabel(tag, lang)}</span>
            ))}
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
