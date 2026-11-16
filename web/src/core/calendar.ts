import { eventEndsAt } from './events'
import type { Event } from './types'

type VenueCalendar = {
  name: string
  address: string
  closing: Record<string, string> | null
  character: string[]
}

function pad2(n: number): string {
  return String(n).padStart(2, '0')
}

/** Build an Android Chrome intent URL for the system calendar app (ACTION_INSERT). */
export function buildAndroidCalendarIntent(
  event: Pick<Event, 'title' | 'date' | 'start_time' | 'end_time' | 'formats'>,
  venue: VenueCalendar | undefined,
  sourceUrl: string
): string {
  const location = venue ? `${venue.name}, ${venue.address}` : ''

  let beginMs: number
  let endMs: number
  let allDay = false

  if (!event.start_time) {
    allDay = true
    beginMs = new Date(event.date + 'T00:00:00').getTime()
    endMs = beginMs + 86400000
  } else {
    const start = new Date(`${event.date}T${event.start_time}:00`)
    beginMs = start.getTime()
    const endsAt = eventEndsAt(
      event as Event,
      venue?.closing ?? null,
      venue?.character ?? []
    )
    endMs = endsAt.getTime()
  }

  const extras: string[] = [
    `S.title=${encodeURIComponent(event.title)}`,
    `l.beginTime=${beginMs}`,
    `l.endTime=${endMs}`,
  ]
  if (location) extras.push(`S.eventLocation=${encodeURIComponent(location)}`)
  if (sourceUrl) extras.push(`S.description=${encodeURIComponent(sourceUrl)}`)
  if (allDay) extras.push('B.allDay=true')

  return `intent:#Intent;action=android.intent.action.INSERT;type=vnd.android.cursor.item%2Fevent;${extras.join(';')};end`
}

/** Generate an .ics file content for the event. */
export function generateICS(
  event: Pick<Event, 'title' | 'date' | 'start_time' | 'end_time' | 'formats'>,
  venue: VenueCalendar | undefined,
  shareUrl: string
): string {
  const dateNoDash = event.date.replace(/-/g, '')

  const dtstart = event.start_time
    ? `DTSTART;TZID=Europe/Prague:${dateNoDash}T${event.start_time.replace(':', '')}00`
    : `DTSTART;VALUE=DATE:${dateNoDash}`

  let dtend = ''
  if (event.end_time && event.start_time) {
    // Check if end is next day (crosses midnight)
    const endDateStr = event.end_time < event.start_time
      ? (() => {
          const d = new Date(event.date + 'T12:00:00')
          d.setDate(d.getDate() + 1)
          return `${d.getFullYear()}${pad2(d.getMonth() + 1)}${pad2(d.getDate())}`
        })()
      : dateNoDash
    dtend = `DTEND;TZID=Europe/Prague:${endDateStr}T${event.end_time.replace(':', '')}00`
  }

  const locationLine = venue ? `LOCATION:${venue.name}` : ''

  return [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//EventApp//Praha//EN',
    'BEGIN:VEVENT',
    dtstart,
    dtend,
    `SUMMARY:${event.title}`,
    locationLine,
    `URL:${shareUrl}`,
    `UID:${event.date}-${event.title.replace(/\s+/g, '-').toLowerCase()}@eventapp`,
    'END:VEVENT',
    'END:VCALENDAR'
  ].filter(Boolean).join('\r\n')
}
