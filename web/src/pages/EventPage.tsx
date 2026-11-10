import { useState, useEffect } from 'react'
import type { EventsData, Language } from '../core/types'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'
import { isGoing, toggleGoing } from '../core/store'
import { haversine, formatDistance } from '../core/distance'
import { getDict, formatEventDate } from '../i18n'
import {
  IconChevronLeft, IconExpand, IconCheck, IconCalendar,
  IconShare, IconInstagram, EventTypeIcon
} from '../icons'

interface Props {
  eventId: string
  data: EventsData
  lang: Language
  userLocation: { lat: number; lng: number } | null
  onBack: () => void
}

function generateICS(event: { title: string; date: string; start_time: string | null; end_time: string | null }, venueName: string, url: string): string {
  const dtstart = event.start_time
    ? `DTSTART;TZID=Europe/Prague:${event.date.replace(/-/g, '')}T${event.start_time.replace(':', '')}00`
    : `DTSTART;VALUE=DATE:${event.date.replace(/-/g, '')}`
  const dtend = event.end_time && event.start_time
    ? `DTEND;TZID=Europe/Prague:${event.date.replace(/-/g, '')}T${event.end_time.replace(':', '')}00`
    : ''

  return [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//EventApp//Praha//EN',
    'BEGIN:VEVENT',
    dtstart,
    dtend,
    `SUMMARY:${event.title}`,
    `LOCATION:${venueName}`,
    `URL:${url}`,
    `UID:${event.date}-${event.title.replace(/\s+/g, '-').toLowerCase()}@eventapp`,
    'END:VEVENT',
    'END:VCALENDAR'
  ].filter(Boolean).join('\r\n')
}

export function EventPage({ eventId, data, lang, userLocation, onBack }: Props) {
  const dict = getDict(lang)
  const event = data.events.find(e => e.id === eventId)
  const [going, setGoing] = useState(() => isGoing(eventId))
  const [showPoster, setShowPoster] = useState(false)
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    setGoing(isGoing(eventId))
  }, [eventId])

  function showToast(msg: string) {
    setToast(msg)
    setTimeout(() => setToast(null), 2000)
  }

  if (!event) {
    return (
      <div style={{
        position: 'absolute', inset: 0, background: '#111118',
        display: 'flex', flexDirection: 'column', alignItems: 'center',

        justifyContent: 'center', gap: 16, padding: 24, zIndex: 50
      }}>
        <p style={{ fontSize: 20, fontWeight: 600 }}>{dict.event.notFound}</p>
        <button
          style={{
            height: 48, padding: '0 24px', borderRadius: 24,
            background: '#FF4D8D', color: '#1A0710', fontSize: 16, fontWeight: 700
          }}
          onClick={onBack}
        >
          {dict.event.backToMap}
        </button>
      </div>
    )
  }

  const ev = event
  const venue = data.venues.find(v => v.id === ev.venue_id)
  const eventType = getEventType(ev.formats)
  const color = EVENT_TYPE_COLOR[eventType]
  const dark = EVENT_TYPE_DARK[eventType]

  const dateLabel = formatEventDate(ev.date, lang)
  const timePart = ev.start_time ? ` · ${ev.start_time}` : ''
  const pricePart = ev.price_text ? ` · ${ev.price_text}` : (ev.free ? ` · ${dict.event.free}` : '')
  const metaLine = `${dateLabel}${timePart}${pricePart}`

  const distStr = userLocation && venue
    ? ` · ${formatDistance(haversine(venue.lat, venue.lng, userLocation.lat, userLocation.lng), lang)}`
    : ''

  const sourceUrl = ev.sources[0]?.url ?? '#'
  const shareUrl = `${window.location.origin}${window.location.pathname}#/akcia/${eventId}`

  function handleTickets() {
    window.open(ev.ticket_url ?? sourceUrl, '_blank', 'noopener')
  }
  function handleGoing() {
    const newState = toggleGoing(eventId)
    setGoing(newState)
  }
  function handleCalendar() {
    const ics = generateICS(ev, venue?.name ?? '', shareUrl)
    const blob = new Blob([ics], { type: 'text/calendar' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${ev.title.slice(0, 40).replace(/[^a-z0-9]/gi, '-')}.ics`
    a.click()
    URL.revokeObjectURL(url)
  }
  async function handleShare() {
    if (navigator.share) {
      try { await navigator.share({ title: ev.title, url: shareUrl }) } catch { /* cancelled */ }
    } else {
      try { await navigator.clipboard.writeText(shareUrl) } catch { /* ignore */ }
      showToast(dict.event.linkCopied)
    }
  }
  function handleIG() {
    if (venue?.instagram) {
      window.open(`https://instagram.com/${venue.instagram}`, '_blank', 'noopener')
    }
  }

  const FORMAT_COLORS: Record<string, [string, string]> = {
    party: ['#FF8A3D', '#2A1200'],
    dj: ['#2FD4C0', '#002B26'],
    concert: ['#8B6CFF', '#14063A'],
    music: ['#8B6CFF', '#14063A'],
    dance: ['#C6F432', '#1B2600'],
    theatre: ['#C6F432', '#1B2600'],
    talk: ['#C6F432', '#1B2600'],
    comedy: ['#C6F432', '#1B2600'],
    film: ['#C6F432', '#1B2600'],
    opening: ['#C6F432', '#1B2600'],
    workshop: ['#C6F432', '#1B2600'],
    quiz: ['#C6F432', '#1B2600'],
    other: ['#C6F432', '#1B2600'],
  }

  return (
    <div style={{
      position: 'absolute', inset: 0, background: '#111118',
      overflowY: 'auto', zIndex: 50
    }}>
      {/* Poster/image */}
      <div style={{ position: 'relative', width: '100%', paddingTop: '100%' }}>
        <div style={{
          position: 'absolute', inset: 0,
          background: color, overflow: 'hidden'
        }}>
          {ev.image_url ? (
            <img src={ev.image_url} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <div style={{
              position: 'absolute', inset: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <EventTypeIcon type={eventType} size={80} color={dark} />
            </div>
          )}
          {/* Gradient */}
          <div style={{
            position: 'absolute', inset: 0,
            background: 'linear-gradient(180deg, rgba(17,17,24,0) 55%, #111118 100%)'
          }} />
        </div>

        {/* Back button */}
        <button
          style={{
            position: 'absolute', top: 52, left: 16,
            width: 44, height: 44, borderRadius: 22,
            background: 'rgba(17,17,24,0.7)', color: '#F4F2FF',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}
          onClick={onBack}
          aria-label={dict.event.back}
        >
          <IconChevronLeft size={22} />
        </button>

        {/* Poster button */}
        {ev.image_url && (
          <button
            style={{
              position: 'absolute', bottom: 52, right: 16,
              height: 36, padding: '0 12px', borderRadius: 18,
              background: 'rgba(17,17,24,0.7)', color: '#F4F2FF',
              display: 'flex', alignItems: 'center', gap: 6,
              fontSize: 13, fontWeight: 600
            }}
            onClick={() => setShowPoster(true)}
            aria-label={dict.event.poster}
          >
            <IconExpand size={16} />
            {dict.event.poster}
          </button>
        )}
      </div>

      {/* Content */}
      <div style={{ padding: '0 16px 100px' }}>
        {/* Title */}
        <h1 style={{
          margin: '16px 0 8px',
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 28, fontWeight: 700,
          lineHeight: 1.08, letterSpacing: '-0.02em'
        }}>
          {ev.title}
        </h1>

        {/* Venue */}
        <p style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>
          {venue?.name ?? ev.venue_id}
          {distStr && <span style={{ color: '#B9B6CC', fontWeight: 400 }}>{distStr}</span>}
        </p>

        {/* Meta */}
        <p style={{ fontSize: 15, color: '#B9B6CC', marginBottom: 12 }}>
          {metaLine}
          {ev.sold_out && (
            <span style={{ color: '#FF4D8D', marginLeft: 8, fontWeight: 600 }}>
              {dict.event.soldOut}
            </span>
          )}
        </p>

        {/* Tags: event formats + genres only (venue character tags are on venue profile) */}
        {(ev.formats.length > 0 || ev.genres.length > 0) && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 20 }}>
            {ev.formats.map(f => {
              const [bg, fg] = FORMAT_COLORS[f] ?? ['#2A2838', '#E4DEFF']
              return (
                <span key={f} style={{
                  height: 24, padding: '0 10px', borderRadius: 12,
                  background: bg, color: fg, fontSize: 12, fontWeight: 600,
                  display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap'
                }}>{f}</span>
              )
            })}
            {ev.genres.map(g => (
              <span key={g} style={{
                height: 24, padding: '0 10px', borderRadius: 12,
                background: '#2A2838', color: '#E4DEFF', fontSize: 12, fontWeight: 600,
                display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap'
              }}>{g}</span>
            ))}
          </div>
        )}

        {/* Main CTA */}
        <button
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            width: '100%', height: 54, borderRadius: 27,
            background: '#FF4D8D', color: '#1A0710',
            fontSize: 17, fontWeight: 700, marginBottom: 12
          }}
          onClick={handleTickets}
        >
          {ev.ticket_url ? dict.event.tickets : dict.event.website}
        </button>

        {/* Secondary actions */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          {[
            { label: going ? dict.event.going : dict.event.going, onClick: handleGoing, active: going, Icon: IconCheck },
            { label: dict.event.calendar, onClick: handleCalendar, active: false, Icon: IconCalendar },
            { label: dict.event.share, onClick: handleShare, active: false, Icon: IconShare },
            ...(venue?.instagram ? [{ label: dict.event.ig, onClick: handleIG, active: false, Icon: IconInstagram }] : [])
          ].map(({ label, onClick, active: isActive, Icon }) => (
            <button
              key={label}
              style={{
                flex: 1, height: 64, borderRadius: 18,
                background: isActive ? '#2D1A30' : '#1C1C27',
                color: isActive ? '#FF4D8D' : '#F4F2FF',
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center', gap: 4,
                fontSize: 12, fontWeight: 600
              }}
              onClick={onClick}
            >
              <Icon size={20} color={isActive ? '#FF4D8D' : '#F4F2FF'} />
              {label}
            </button>
          ))}
        </div>

        {/* Description */}
        {ev.description && (
          <p style={{ fontSize: 14, lineHeight: 1.5, color: '#B9B6CC' }}>
            {ev.description}
          </p>
        )}
      </div>

      {/* Full-screen poster overlay */}
      {showPoster && ev.image_url && (
        <div
          style={{
            position: 'fixed', inset: 0, background: '#000', zIndex: 200,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}
          onClick={() => setShowPoster(false)}
        >
          <img src={ev.image_url} alt={ev.title}
            style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
          <button
            style={{
              position: 'absolute', top: 52, left: 16,
              width: 44, height: 44, borderRadius: 22,
              background: 'rgba(0,0,0,0.6)', color: '#fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}
            onClick={() => setShowPoster(false)}
            aria-label={dict.event.back}
          >
            <IconChevronLeft size={22} />
          </button>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 120, left: '50%', transform: 'translateX(-50%)',
          background: '#2A2838', color: '#F4F2FF', padding: '10px 20px',
          borderRadius: 20, fontSize: 14, fontWeight: 600, zIndex: 300,
          whiteSpace: 'nowrap', boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
        }}>
          {toast}
        </div>
      )}
    </div>
  )
}
