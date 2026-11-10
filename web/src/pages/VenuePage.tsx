import { useState } from 'react'
import type { EventsData, Language, Venue, Event, EventType } from '../core/types'
import { getDict } from '../i18n'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK } from '../core/eventType'
import { isFavorite, toggleFavorite } from '../core/store'
import { haversine, formatDistance } from '../core/distance'
import { getToday } from '../core/day'
import { IconChevronLeft, IconHeart, EventTypeIcon } from '../icons'

interface Props {
  venueId: string
  data: EventsData
  lang: Language
  userLocation: { lat: number; lng: number } | null
  onBack: () => void
  onEventOpen: (eventId: string) => void
  onGoToMap: (venueId: string, date: string) => void
}

function normalize(s: string) {
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
}
normalize // used only for future search use

function venueEventType(venue: Venue): EventType {
  const t = venue.type
  if (t.some(x => x.includes('dance'))) return 'dj'
  if (t.some(x => x.includes('concert') || x.includes('jazz'))) return 'concert'
  if (t.some(x => x === 'culture-center' || x === 'cafe' || x === 'cinema' || x === 'culture')) return 'culture'
  return 'dj'
}

function getUpcomingEvents(events: Event[], venueId: string, today: string): Event[] {
  return events
    .filter(e => e.venue_id === venueId && e.date >= today && e.status !== 'cancelled' && e.status !== 'gone')
    .sort((a, b) => {
      if (a.date !== b.date) return a.date.localeCompare(b.date)
      if (!a.start_time && !b.start_time) return 0
      if (!a.start_time) return 1
      if (!b.start_time) return -1
      return a.start_time.localeCompare(b.start_time)
    })
}

function HeaderImage({ venue, et }: { venue: Venue; et: EventType }) {
  const [err, setErr] = useState(false)
  const bg = EVENT_TYPE_COLOR[et]
  const fg = EVENT_TYPE_DARK[et]
  if (!venue.image_url || err) {
    return (
      <div style={{
        width: '100%', height: '100%', background: bg,
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        <EventTypeIcon type={et} size={56} color={fg} />
      </div>
    )
  }
  return (
    <img
      src={venue.image_url}
      alt={venue.name}
      onError={() => setErr(true)}
      style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
    />
  )
}

function EventThumbnail({ event }: { event: Event }) {
  const [err, setErr] = useState(false)
  const et = getEventType(event.formats)
  const bg = EVENT_TYPE_COLOR[et]
  const fg = EVENT_TYPE_DARK[et]
  if (!event.image_url || err) {
    return (
      <div style={{
        width: 56, height: 56, borderRadius: 12, background: bg, flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}>
        <EventTypeIcon type={et} size={22} color={fg} />
      </div>
    )
  }
  return (
    <img
      src={event.image_url}
      alt={event.title}
      onError={() => setErr(true)}
      style={{ width: 56, height: 56, borderRadius: 12, objectFit: 'cover', flexShrink: 0 }}
    />
  )
}

export function VenuePage({ venueId, data, lang, userLocation, onBack, onEventOpen, onGoToMap }: Props) {
  const dict = getDict(lang)
  const [descExpanded, setDescExpanded] = useState(false)
  const [, forceUpdate] = useState(0)

  const venue: Venue | undefined = data.venues.find(v => v.id === venueId)

  if (!venue) {
    return (
      <div style={{
        position: 'absolute', inset: 0, overflowY: 'auto', background: '#111118',
        display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'
      }}>
        <p style={{ color: '#B9B6CC', fontSize: 14 }}>Miesto sa nenašlo.</p>
        <button onClick={onBack} style={{
          marginTop: 16, background: '#23232F', color: '#E4E2EE',
          border: 'none', borderRadius: 22, height: 44, padding: '0 20px',
          fontSize: 14, fontWeight: 600, cursor: 'pointer', fontFamily: "'Outfit', sans-serif"
        }}>
          {dict.venue.back}
        </button>
      </div>
    )
  }

  const et = venueEventType(venue)
  const today = getToday(new Date())
  const upcoming = getUpcomingEvents(data.events, venueId, today)
  const nearestDate = upcoming[0]?.date ?? null

  const isFav = isFavorite(venueId)

  const distStr = userLocation
    ? formatDistance(haversine(userLocation.lat, userLocation.lng, venue.lat, venue.lng), lang)
    : null

  const addressLine = distStr ? `${venue.address} ${dict.venue.dot} ${distStr}` : venue.address

  // Group events by date for rendering
  const eventsByDate: { date: string; events: Event[] }[] = []
  for (const ev of upcoming) {
    const last = eventsByDate[eventsByDate.length - 1]
    if (last && last.date === ev.date) last.events.push(ev)
    else eventsByDate.push({ date: ev.date, events: [ev] })
  }

  return (
    <div style={{
      position: 'absolute', inset: 0, overflowY: 'auto', background: '#111118'
    }}>
      {/* Hero image */}
      <div style={{ position: 'relative', height: 200, flexShrink: 0 }}>
        <HeaderImage venue={venue} et={et} />
        {/* Gradient overlay */}
        <div style={{
          position: 'absolute', inset: 0,
          background: 'linear-gradient(180deg, rgba(17,17,24,0) 30%, #111118 100%)'
        }} />
        {/* Back button */}
        <button onClick={onBack} style={{
          position: 'absolute', top: 52, left: 16,
          width: 44, height: 44, borderRadius: 22,
          background: 'rgba(17,17,24,0.7)', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          color: '#F4F2FF'
        }} aria-label={dict.venue.back}>
          <IconChevronLeft size={22} color="#F4F2FF" />
        </button>
        {/* Heart button */}
        <button onClick={() => { toggleFavorite(venueId); forceUpdate(n => n + 1) }} style={{
          position: 'absolute', top: 52, right: 16,
          width: 44, height: 44, borderRadius: 22,
          background: '#FF4D8D', border: 'none', cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center'
        }} aria-label={isFav ? 'Odobrať z obľúbených' : 'Pridať do obľúbených'}>
          <IconHeart size={20} color="#1A0710" filled={isFav} />
        </button>
      </div>

      {/* Content */}
      <div style={{ padding: '0 16px 100px' }}>
        {/* Name */}
        <h1 style={{
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 34, fontWeight: 700, letterSpacing: '-0.02em',
          margin: '8px 0 4px', color: '#F4F2FF', lineHeight: 1.1
        }}>
          {venue.name}
        </h1>

        {/* Address · distance */}
        <p style={{ fontSize: 14, color: '#B9B6CC', margin: '0 0 12px' }}>
          {addressLine}
        </p>

        {/* Description */}
        {venue.description && (
          <div style={{ marginBottom: 12 }}>
            <p style={{
              fontSize: 14, color: '#E4E2EE', lineHeight: 1.5, margin: '0 0 4px',
              display: descExpanded ? 'block' : '-webkit-box',
              WebkitLineClamp: descExpanded ? undefined : 2,
              WebkitBoxOrient: 'vertical',
              overflow: descExpanded ? 'visible' : 'hidden'
            } as React.CSSProperties}>
              {venue.description}
            </p>
            <button onClick={() => setDescExpanded(e => !e)} style={{
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
              fontSize: 14, fontWeight: 600, color: '#B9B6CC',
              textDecoration: 'underline', textUnderlineOffset: 3,
              fontFamily: "'Outfit', sans-serif"
            }}>
              {descExpanded ? dict.venue.less : dict.venue.more}
            </button>
          </div>
        )}

        {/* Character tags */}
        {venue.character.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 20 }}>
            {venue.character.map(tag => (
              <span key={tag} style={{
                height: 24, padding: '0 10px', borderRadius: 12,
                border: '1.5px solid #5D5677', color: '#B9B6CC',
                fontSize: 12, fontWeight: 600,
                display: 'inline-flex', alignItems: 'center'
              }}>
                {tag}
              </span>
            ))}
          </div>
        )}

        {/* Program */}
        <h2 style={{
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 22, fontWeight: 700, margin: '0 0 12px',
          color: '#F4F2FF'
        }}>
          {dict.venue.program}
        </h2>

        {upcoming.length === 0 && (
          <p style={{ color: '#B9B6CC', fontSize: 14 }}>{dict.venue.noProgram}</p>
        )}

        {eventsByDate.map(({ date, events }) => {
          const d = new Date(date + 'T12:00:00')
          const dayName = dict.days[d.getDay()].toUpperCase()
          const dayNum = d.getDate()
          const monthNum = d.getMonth() + 1
          return (
            <div key={date} style={{ marginBottom: 4 }}>
              {events.map((ev, i) => {
                const evType = getEventType(ev.formats)
                const timeColor = EVENT_TYPE_COLOR[evType]
                return (
                  <div
                    key={ev.id}
                    onClick={() => onEventOpen(ev.id)}
                    style={{
                      display: 'flex', alignItems: 'center', gap: 12,
                      padding: '10px 0', cursor: 'pointer',
                      borderTop: i === 0 ? '1px solid #23232F' : 'none'
                    }}
                  >
                    {/* Date column */}
                    {i === 0 ? (
                      <div style={{ width: 52, flexShrink: 0, textAlign: 'center' }}>
                        <div style={{ fontSize: 12, color: '#8E8AA6', fontWeight: 600 }}>{dayName}</div>
                        <div style={{
                          fontFamily: "'Bricolage Grotesque', sans-serif",
                          fontSize: 22, fontWeight: 700, color: '#F4F2FF', lineHeight: 1.1
                        }}>{dayNum}</div>
                        <div style={{ fontSize: 12, color: '#8E8AA6' }}>{monthNum}.</div>
                      </div>
                    ) : (
                      <div style={{ width: 52, flexShrink: 0 }} />
                    )}

                    {/* Event info */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <p style={{
                        fontFamily: "'Bricolage Grotesque', sans-serif",
                        fontSize: 16, fontWeight: 700, color: '#F4F2FF',
                        margin: '0 0 3px', overflow: 'hidden',
                        textOverflow: 'ellipsis', whiteSpace: 'nowrap'
                      }}>
                        {ev.title}
                      </p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                        {ev.start_time && (
                          <span style={{ fontSize: 13, color: timeColor, fontWeight: 600 }}>
                            {ev.start_time}
                          </span>
                        )}
                        {ev.formats.slice(0, 2).map(f => (
                          <span key={f} style={{
                            height: 20, padding: '0 8px', borderRadius: 10,
                            background: '#1E1D2A', color: '#B9B6CC',
                            fontSize: 11, fontWeight: 600,
                            display: 'inline-flex', alignItems: 'center'
                          }}>{f}</span>
                        ))}
                      </div>
                    </div>

                    {/* Thumbnail */}
                    <EventThumbnail event={ev} />
                  </div>
                )
              })}
            </div>
          )
        })}

        {/* Bottom buttons */}
        <div style={{ display: 'flex', gap: 8, marginTop: 24, flexWrap: 'wrap' }}>
          {venue.web && (
            <a href={venue.web} target="_blank" rel="noopener noreferrer" style={{
              height: 44, borderRadius: 22, background: '#23232F', color: '#E4E2EE',
              fontSize: 14, fontWeight: 600, padding: '0 20px', textDecoration: 'none',
              display: 'inline-flex', alignItems: 'center', fontFamily: "'Outfit', sans-serif"
            }}>
              {dict.venue.web}
            </a>
          )}
          {venue.instagram && (
            <a href={`https://instagram.com/${venue.instagram}`} target="_blank" rel="noopener noreferrer" style={{
              height: 44, borderRadius: 22, background: '#23232F', color: '#E4E2EE',
              fontSize: 14, fontWeight: 600, padding: '0 20px', textDecoration: 'none',
              display: 'inline-flex', alignItems: 'center', fontFamily: "'Outfit', sans-serif"
            }}>
              {dict.venue.instagram}
            </a>
          )}
          {nearestDate && (
            <button onClick={() => onGoToMap(venueId, nearestDate)} style={{
              height: 44, borderRadius: 22, background: '#23232F', color: '#E4E2EE',
              fontSize: 14, fontWeight: 600, padding: '0 20px', border: 'none',
              cursor: 'pointer', fontFamily: "'Outfit', sans-serif",
              display: 'inline-flex', alignItems: 'center'
            }}>
              {dict.venue.onMap}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
