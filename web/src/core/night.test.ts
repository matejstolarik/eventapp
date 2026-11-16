import { describe, it, expect } from 'vitest'
import { isNightEvent, isNightMode, resolveSelectedDay, NIGHT_DAY } from './night'
import type { Event, EventsData, Venue } from './types'

function makeEvent(overrides: Partial<Event> = {}): Event {
  return {
    id: 'test-1', venue_id: 'venue-1', title: 'Test',
    date: '2026-11-09', start_time: '23:00', doors_time: null, end_time: null,
    formats: ['dj'], genres: [], character: [], artists: [],
    price_text: null, free: null, sold_out: null, room: null,
    ticket_url: null, image_url: null, image_thumb: null,
    description: null, description_source: null,
    sources: [{ type: 'rss', url: 'https://example.com' }],
    classification: null, first_seen: '2026-11-01', last_seen: '2026-11-09',
    status: 'scheduled', flags: [],
    ...overrides
  }
}

function makeVenue(overrides: Partial<Venue> = {}): Venue {
  return {
    id: 'venue-1', name: 'Test Club', city: 'Praha',
    address: 'Test 1', lat: 50.08, lng: 14.44,
    web: 'https://test.cz', ra_url: null, instagram: null,
    type: ['dance-club'], character: [], music: [], size: 'small',
    description: null, description_url: null,
    image_url: null, image_source: null, image_thumb: null,
    closing: null, sources: [], active: true,
    ...overrides
  }
}

function makeData(events: Event[], venues: Venue[]): EventsData {
  return { schema_version: 1, generated_at: '', venues, events }
}

describe('isNightEvent', () => {
  const now130 = new Date('2026-11-10T01:30:00')

  it('concert 20:00 without end → no (not party/dj/late-night)', () => {
    expect(isNightEvent(
      makeEvent({ date: '2026-11-09', start_time: '20:00', end_time: null, formats: ['concert'] }),
      ['alternative'], null, now130
    )).toBe(false)
  })

  it('dj 23:00 without end in late-night venue → yes', () => {
    expect(isNightEvent(
      makeEvent({ date: '2026-11-09', start_time: '23:00', end_time: null, formats: ['dj'] }),
      ['alternative', 'underground', 'late-night'], null, now130
    )).toBe(true)
  })

  it('dj 23:00 without end (no late-night venue) → yes (party/dj type is enough)', () => {
    expect(isNightEvent(
      makeEvent({ date: '2026-11-09', start_time: '23:00', end_time: null, formats: ['dj'] }),
      ['alternative'], null, now130
    )).toBe(true)
  })

  it('event 22:00–5:00 spanning midnight → yes', () => {
    expect(isNightEvent(
      makeEvent({ date: '2026-11-09', start_time: '22:00', end_time: '05:00', formats: ['party', 'dj'] }),
      ['late-night'], null, now130
    )).toBe(true)
  })

  it('event 22:00–1:00 already ended at 1:30 → no', () => {
    expect(isNightEvent(
      makeEvent({ date: '2026-11-09', start_time: '22:00', end_time: '01:00', formats: ['party', 'dj'] }),
      ['late-night'], null, now130
    )).toBe(false)
  })

  it('concert without start_time, without end → no', () => {
    expect(isNightEvent(
      makeEvent({ date: '2026-11-09', start_time: null, end_time: null, formats: ['concert'] }),
      [], null, now130
    )).toBe(false)
  })

  it('dj without start_time → no (cannot verify ≥20:00)', () => {
    expect(isNightEvent(
      makeEvent({ date: '2026-11-09', start_time: null, end_time: null, formats: ['dj'] }),
      [], null, now130
    )).toBe(false)
  })

  it('dj 23:00 with closing.sun = "07:00": still running at 6:30', () => {
    // 2026-11-09 is a Monday → use mon or sun? Use sun for the test
    // 2026-11-08 is a Sunday
    const now630 = new Date('2026-11-09T06:30:00')
    expect(isNightEvent(
      makeEvent({ date: '2026-11-08', start_time: '23:00', end_time: null, formats: ['dj'] }),
      ['late-night'], { sun: '07:00' }, now630
    )).toBe(true)
  })
})

describe('isNightMode', () => {
  it('Monday 1:00 without running events → false', () => {
    // No events from yesterday → not night mode
    const data = makeData([], [makeVenue()])
    expect(isNightMode(data, new Date('2026-11-16T01:00:00'))).toBe(false)
  })

  it('Monday 1:00 with running party from yesterday → true', () => {
    // yesterday = 2026-11-15 (Sunday), now = 2026-11-16 01:00
    const venue = makeVenue({ id: 'venue-1', character: [] })
    const event = makeEvent({
      venue_id: 'venue-1', date: '2026-11-15', start_time: '23:00',
      end_time: null, formats: ['party']
    })
    // party without closing → ends at 03:00 → still running at 01:00
    const data = makeData([event], [venue])
    expect(isNightMode(data, new Date('2026-11-16T01:00:00'))).toBe(true)
  })

  it('party ends at 2:00, at 2:01 → false', () => {
    const venue = makeVenue({ id: 'venue-1', character: [] })
    const event = makeEvent({
      venue_id: 'venue-1', date: '2026-11-15', start_time: '22:00',
      end_time: '02:00', formats: ['party']
    })
    const data = makeData([event], [venue])
    expect(isNightMode(data, new Date('2026-11-16T02:01:00'))).toBe(false)
  })

  it('Saturday 5:30 with cross-club party (closing.sat = "07:00") → true', () => {
    // 2026-11-14 is Saturday (Nov 16=Mon → Nov 15=Sun → Nov 14=Sat)
    // yesterday of 2026-11-15T05:30 (Sunday) = 2026-11-14 (Saturday)
    // sat closing 07:00 < 23:00 → next day 07:00 (2026-11-15T07:00); at 05:30 still running
    const venue = makeVenue({ id: 'venue-1', character: ['late-night'], closing: { sat: '07:00' } })
    const event = makeEvent({
      venue_id: 'venue-1', date: '2026-11-14', start_time: '23:00',
      end_time: null, formats: ['dj']
    })
    const data = makeData([event], [venue])
    expect(isNightMode(data, new Date('2026-11-15T05:30:00'))).toBe(true)
  })

  it('Saturday 7:01 → false regardless of events', () => {
    const venue = makeVenue({ id: 'venue-1', character: ['late-night'], closing: { sat: '10:00' } })
    const event = makeEvent({
      venue_id: 'venue-1', date: '2026-11-15', start_time: '23:00',
      end_time: null, formats: ['dj']
    })
    const data = makeData([event], [venue])
    expect(isNightMode(data, new Date('2026-11-16T07:01:00'))).toBe(false)
  })

  it('during daytime → false', () => {
    const venue = makeVenue()
    const data = makeData([], [venue])
    expect(isNightMode(data, new Date('2026-11-15T14:00:00'))).toBe(false)
  })
})

describe('resolveSelectedDay', () => {
  it('keeps correct day during daytime', () => {
    const data = makeData([], [makeVenue()])
    expect(resolveSelectedDay('2026-11-15', new Date('2026-11-15T14:00:00'), data)).toBe('2026-11-15')
  })

  it('advances stale day after overnight background', () => {
    const data = makeData([], [makeVenue()])
    expect(resolveSelectedDay('2026-11-14', new Date('2026-11-15T09:00:00'), data)).toBe('2026-11-15')
  })

  it('converts NIGHT_DAY to today when not night anymore', () => {
    const data = makeData([], [makeVenue()])
    expect(resolveSelectedDay(NIGHT_DAY, new Date('2026-11-15T09:00:00'), data)).toBe('2026-11-15')
  })

  it('keeps NIGHT_DAY during night hours if events running', () => {
    const venue = makeVenue({ id: 'venue-1', character: [] })
    const event = makeEvent({
      venue_id: 'venue-1', date: '2026-11-14', start_time: '23:00',
      end_time: null, formats: ['party']
    })
    const data = makeData([event], [venue])
    expect(resolveSelectedDay(NIGHT_DAY, new Date('2026-11-15T02:00:00'), data)).toBe(NIGHT_DAY)
  })

  it('converts NIGHT_DAY to today at 2:00 when no events running', () => {
    const data = makeData([], [makeVenue()])
    expect(resolveSelectedDay(NIGHT_DAY, new Date('2026-11-15T02:00:00'), data)).toBe('2026-11-15')
  })
})
