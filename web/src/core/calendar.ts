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

function formatCalDate(d: Date): string {
  return `${d.getFullYear()}${pad2(d.getMonth() + 1)}${pad2(d.getDate())}`
}

function formatCalDateTime(d: Date): string {
  return `${formatCalDate(d)}T${pad2(d.getHours())}${pad2(d.getMinutes())}00`
}

/** Build a Google Calendar URL for the event (Android). Times are Prague local (no Z). */
export function buildGoogleCalendarUrl(
  event: Pick<Event, 'title' | 'date' | 'start_time' | 'end_time' | 'formats'>,
  venue: VenueCalendar | undefined,
  sourceUrl: string
): string {
  const dateNoDash = event.date.replace(/-/g, '')

  let dates: string
  if (!event.start_time) {
    // All-day event
    const nextDay = new Date(event.date + 'T12:00:00')
    nextDay.setDate(nextDay.getDate() + 1)
    dates = `${dateNoDash}/${formatCalDate(nextDay)}`
  } else {
    const startStr = `${dateNoDash}T${event.start_time.replace(':', '')}00`
    const endsAt = eventEndsAt(
      event as Event,
      venue?.closing ?? null,
      venue?.character ?? []
    )
    dates = `${startStr}/${formatCalDateTime(endsAt)}`
  }

  const location = venue ? `${venue.name}, ${venue.address}` : ''

  const params = new URLSearchParams({
    action: 'TEMPLATE',
    text: event.title,
    dates,
    ctz: 'Europe/Prague',
    details: sourceUrl,
    location,
  })

  return `https://calendar.google.com/calendar/render?${params}`
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
