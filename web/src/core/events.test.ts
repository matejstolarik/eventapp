import { describe, it, expect } from 'vitest'
import { isEventFinished, isEventLive, isEventPulsing, eventEndsAt, getVenueEvents, getPrimaryEvent } from './events'
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
    image_thumb: null,
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

describe('eventEndsAt', () => {
  it('concert 20:00 without end → ends at 23:00 (start + 3h)', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '20:00', end_time: null, formats: ['concert'] })
    const endsAt = eventEndsAt(e, null, [])
    expect(endsAt).toEqual(new Date('2026-11-09T23:00:00'))
  })

  it('concert 20:00 without end: runs at 22:59, finished at 23:01', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '20:00', end_time: null, formats: ['concert'] })
    expect(isEventFinished(e, new Date('2026-11-09T22:59:00'), null, [])).toBe(false)
    expect(isEventFinished(e, new Date('2026-11-09T23:01:00'), null, [])).toBe(true)
  })

  it('party without end, closing.sat = "05:00": runs at 4:30, finished at 5:01', () => {
    // 2026-11-14 is a Saturday (Nov 16 = Mon → Nov 15 = Sun → Nov 14 = Sat)
    // sat 22:00 party, closing.sat = "05:00" < "22:00" → next day 05:00 (2026-11-15T05:00)
    const eSat = makeEvent({ date: '2026-11-14', start_time: '22:00', end_time: null, formats: ['party'] })
    const closing = { sat: '05:00' }
    expect(isEventFinished(eSat, new Date('2026-11-15T04:30:00'), closing, [])).toBe(false)
    expect(isEventFinished(eSat, new Date('2026-11-15T05:01:00'), closing, [])).toBe(true)
  })

  it('party without end, no closing: ends at 3:00 next day', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '22:00', end_time: null, formats: ['party'] })
    const endsAt = eventEndsAt(e, null, [])
    expect(endsAt).toEqual(new Date('2026-11-10T03:00:00'))
    expect(isEventFinished(e, new Date('2026-11-10T03:01:00'), null, [])).toBe(true)
  })

  it('event with known end_time: finished by end_time', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '20:00', end_time: '23:00' })
    expect(isEventFinished(e, new Date('2026-11-09T22:00:00'))).toBe(false)
    expect(isEventFinished(e, new Date('2026-11-09T23:30:00'))).toBe(true)
  })

  it('handles midnight-spanning event (end_time < start_time)', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '22:00', end_time: '03:00' })
    expect(isEventFinished(e, new Date('2026-11-10T02:00:00'))).toBe(false)
    expect(isEventFinished(e, new Date('2026-11-10T04:00:00'))).toBe(true)
  })

  it('no start_time → ends at 3:00 next day', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: null, end_time: null, formats: ['concert'] })
    const endsAt = eventEndsAt(e, null, [])
    expect(endsAt).toEqual(new Date('2026-11-10T03:00:00'))
  })

  it('late-night venue party with closing.fri = "06:00": correct end time', () => {
    // fri 22:00 → closing fri "06:00" < "22:00" → next day 06:00
    const e = makeEvent({ date: '2026-11-13', start_time: '22:00', end_time: null, formats: ['party'] })
    // 2026-11-13 is a Friday
    const endsAt = eventEndsAt(e, { fri: '06:00' }, ['late-night'])
    expect(endsAt).toEqual(new Date('2026-11-14T06:00:00'))
  })

  it('roxy tue closing 22:00 >= start 19:00 → same day', () => {
    // 2026-11-10 is a Tuesday
    const e = makeEvent({ date: '2026-11-10', start_time: '19:00', end_time: null, formats: ['dj'] })
    const endsAt = eventEndsAt(e, { tue: '22:00' }, [])
    expect(endsAt).toEqual(new Date('2026-11-10T22:00:00'))
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

describe('isEventPulsing', () => {
  it('concert on today pulses while running', () => {
    // today = 2026-11-09, event starts 20:00, ends 23:00 (start+3h)
    const e = makeEvent({ date: '2026-11-09', start_time: '20:00', formats: ['concert'] })
    expect(isEventPulsing(e, [], null, new Date('2026-11-09T21:00:00'))).toBe(true)
    expect(isEventPulsing(e, [], null, new Date('2026-11-09T23:30:00'))).toBe(false)
  })

  it('yesterday party pulses in night window (02:00)', () => {
    // yesterday = 2026-11-09, now = 2026-11-10 02:00 (night window)
    const e = makeEvent({ date: '2026-11-09', start_time: '22:00', formats: ['party'] })
    // no closing → ends at 3:00
    expect(isEventPulsing(e, [], null, new Date('2026-11-10T02:00:00'))).toBe(true)
  })

  it('yesterday party does NOT pulse at 7:00+ (outside night window)', () => {
    const e = makeEvent({ date: '2026-11-09', start_time: '22:00', formats: ['party'] })
    expect(isEventPulsing(e, [], null, new Date('2026-11-10T07:30:00'))).toBe(false)
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

  it('sorts pulsing events first', () => {
    // at 21:30: e5 (19:00-21:00) finished, e1 (20:00, concert → ends 23:00) pulsing, e2 (22:00) not yet
    const now = new Date('2026-11-09T21:30:00')
    const result = getVenueEvents(events, 'venue-1', '2026-11-09', now)
    expect(result[0]!.id).toBe('e1')
  })
})

describe('getPrimaryEvent', () => {
  it('returns null for empty list', () => {
    expect(getPrimaryEvent([])).toBeNull()
  })

  it('returns first event', () => {
    const live = makeEvent({ id: 'live', start_time: '20:00' })
    const upcoming = makeEvent({ id: 'upcoming', start_time: '22:00' })
    expect(getPrimaryEvent([live, upcoming])?.id).toBe('live')
  })
})
