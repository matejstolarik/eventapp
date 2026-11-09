import { describe, it, expect } from 'vitest'
import { isEventFinished, isEventLive, getVenueEvents, getPrimaryEvent } from './events'
import type { Event } from './types'

function makeEvent(overrides: Partial<Event> = {}): Event {
  return {
    id: 'test-1',
    venue_id: 'venue-1',
    title: 'Test Event',
    date: '2026-11-09',
    start_time: '20:00',
    doors_time: null,
    end_time: null,
    formats: ['concert'],
    genres: [],
    character: [],
    artists: [],
    price_text: null,
    free: null,
    sold_out: null,
    room: null,
    ticket_url: null,
    image_url: null,
    description: null,
    description_source: null,
    sources: [{ type: 'rss', url: 'https://example.com' }],
    classification: null,
    first_seen: '2026-11-01',
    last_seen: '2026-11-09',
    status: 'scheduled',
    flags: [],
    ...overrides
  }
}

describe('isEventFinished', () => {
  it('returns false when end_time is null', () => {
    const e = makeEvent({ end_time: null })
    expect(isEventFinished(e, new Date('2026-11-09T23:00:00'))).toBe(false)
  })

  it('returns true when known end_time has passed', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '20:00', end_time: '23:00' })
    expect(isEventFinished(e, new Date('2026-11-09T23:30:00'))).toBe(true)
    expect(isEventFinished(e, new Date('2026-11-09T22:00:00'))).toBe(false)
  })

  it('handles midnight-spanning event (end_time < start_time)', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '22:00', end_time: '03:00' })
    // end is 03:00 on 2026-11-10
    expect(isEventFinished(e, new Date('2026-11-10T02:00:00'))).toBe(false)
    expect(isEventFinished(e, new Date('2026-11-10T04:00:00'))).toBe(true)
  })
})

describe('isEventLive', () => {
  it('returns true when started and not finished', () => {
    const e = makeEvent({ start_time: '20:00', end_time: '23:00' })
    expect(isEventLive(e, new Date('2026-11-09T21:00:00'))).toBe(true)
  })

  it('returns false before start', () => {
    const e = makeEvent({ start_time: '20:00' })
    expect(isEventLive(e, new Date('2026-11-09T18:00:00'))).toBe(false)
  })

  it('returns false when no start_time', () => {
    const e = makeEvent({ start_time: null })
    expect(isEventLive(e, new Date('2026-11-09T21:00:00'))).toBe(false)
  })
})

describe('getVenueEvents', () => {
  const events: Event[] = [
    makeEvent({ id: 'e1', date: '2026-11-09', start_time: '20:00', status: 'scheduled' }),
    makeEvent({ id: 'e2', date: '2026-11-09', start_time: '22:00', status: 'scheduled' }),
    makeEvent({ id: 'e3', date: '2026-11-10', start_time: '20:00', status: 'scheduled' }),
    makeEvent({ id: 'e4', date: '2026-11-09', start_time: '19:00', status: 'cancelled' }),
    makeEvent({ id: 'e5', date: '2026-11-09', start_time: '19:00', end_time: '21:00', status: 'scheduled' })
  ]

  it('returns events for the correct venue and day', () => {
    const result = getVenueEvents(events, 'venue-1', '2026-11-09', new Date('2026-11-09T19:30:00'))
    expect(result.map(e => e.id)).not.toContain('e3') // wrong day
    expect(result.map(e => e.id)).not.toContain('e4') // cancelled
  })

  it('excludes finished events', () => {
    const now = new Date('2026-11-09T22:00:00')
    const result = getVenueEvents(events, 'venue-1', '2026-11-09', now)
    expect(result.map(e => e.id)).not.toContain('e5') // ended at 21:00
  })

  it('sorts live events first', () => {
    // at 21:30: e5 (19:00-21:00) finished, e1 (20:00, no end) live, e2 (22:00) not yet
    const now = new Date('2026-11-09T21:30:00')
    const result = getVenueEvents(events, 'venue-1', '2026-11-09', now)
    expect(result[0]!.id).toBe('e1')
  })
})

describe('getPrimaryEvent', () => {
  it('returns null for empty list', () => {
    expect(getPrimaryEvent([], new Date())).toBeNull()
  })

  it('prefers live event', () => {
    const live = makeEvent({ id: 'live', start_time: '20:00' })
    const upcoming = makeEvent({ id: 'upcoming', start_time: '22:00' })
    const now = new Date('2026-11-09T21:00:00')
    expect(getPrimaryEvent([upcoming, live], now)?.id).toBe('live')
  })
})
