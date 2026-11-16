import { describe, it, expect } from 'vitest'
import { visibleEvents } from './visible'
import { isEventPulsing } from './events'
import { isNightTime, NIGHT_DAY } from './night'
import { getToday, toDateString, getUpcomingDays } from './day'
import type { Event, Venue, EventsData } from './types'

function makeEvent(overrides: Partial<Event> = {}): Event {
  return {
    id: 'test-1',
    venue_id: 'v1',
    title: 'Test',
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

function makeVenue(id: string, character: string[] = [], closing: Record<string, string> | null = null): Venue {
  return {
    id,
    name: id,
    city: 'Praha',
    address: 'Testova 1',
    lat: 50.08,
    lng: 14.42,
    web: '',
    ra_url: null,
    instagram: null,
    type: ['club'],
    character,
    music: [],
    size: 'medium',
    description: null,
    description_url: null,
    image_url: null,
    image_source: null,
    image_thumb: null,
    closing,
    sources: [],
    active: true,
  }
}

function makeData(events: Event[], venues: Venue[]): EventsData {
  return { schema_version: 1, generated_at: '', venues, events }
}

// now = 01:30 on 2026-11-16 (night window; calendar today = 2026-11-16, yesterday = 2026-11-15)
const now130 = new Date('2026-11-16T01:30:00')

describe('A. visibleEvents – NIGHT_DAY filtering', () => {
  it('concert from prev day 19:00 no end: hidden in NIGHT_DAY', () => {
    const concert = makeEvent({ id: 'c1', date: '2026-11-15', start_time: '19:00', end_time: null, formats: ['concert'] })
    const venue = makeVenue('v1', ['alternative'])
    const data = makeData([concert], [venue])
    const vm = visibleEvents(data, NIGHT_DAY, now130, { favoritesOnly: false, isFavorite: () => false })
    expect(vm.has('v1')).toBe(false)
  })

  it('party from prev day 23:00 no end: visible in NIGHT_DAY', () => {
    const party = makeEvent({ id: 'p1', date: '2026-11-15', start_time: '23:00', end_time: null, formats: ['party'] })
    const venue = makeVenue('v1', ['late-night'])
    const data = makeData([party], [venue])
    const vm = visibleEvents(data, NIGHT_DAY, now130, { favoritesOnly: false, isFavorite: () => false })
    expect(vm.has('v1')).toBe(true)
    expect(vm.get('v1')!.length).toBe(1)
  })

  it('event with end 02:00: visible at 01:30', () => {
    const event = makeEvent({ id: 'e1', date: '2026-11-15', start_time: '22:00', end_time: '02:00', formats: ['party'] })
    const venue = makeVenue('v1', ['late-night'])
    const data = makeData([event], [venue])
    const vm = visibleEvents(data, NIGHT_DAY, now130, { favoritesOnly: false, isFavorite: () => false })
    expect(vm.has('v1')).toBe(true)
  })

  it('event with end 02:00: hidden at 02:30', () => {
    const now230 = new Date('2026-11-16T02:30:00')
    const event = makeEvent({ id: 'e1', date: '2026-11-15', start_time: '22:00', end_time: '02:00', formats: ['party'] })
    const venue = makeVenue('v1', ['late-night'])
    const data = makeData([event], [venue])
    const vm = visibleEvents(data, NIGHT_DAY, now230, { favoritesOnly: false, isFavorite: () => false })
    expect(vm.has('v1')).toBe(false)
  })

  it('favoritesOnly in NIGHT_DAY: non-fav hidden, fav visible', () => {
    const party = makeEvent({ id: 'p1', venue_id: 'v1', date: '2026-11-15', start_time: '23:00', formats: ['party'] })
    const party2 = makeEvent({ id: 'p2', venue_id: 'v2', date: '2026-11-15', start_time: '23:00', formats: ['party'] })
    const v1 = makeVenue('v1', ['late-night'])
    const v2 = makeVenue('v2', ['late-night'])
    const data = makeData([party, party2], [v1, v2])
    const vm = visibleEvents(data, NIGHT_DAY, now130, { favoritesOnly: true, isFavorite: id => id === 'v1' })
    expect(vm.has('v1')).toBe(true)
    expect(vm.has('v2')).toBe(false)
  })
})

describe('B. isEventPulsing', () => {
  it('party 23:00 no end, at 01:30: pulses (yesterday night window)', () => {
    const party = makeEvent({ date: '2026-11-15', start_time: '23:00', end_time: null, formats: ['party'] })
    expect(isEventPulsing(party, ['late-night'], null, now130)).toBe(true)
  })

  it('concert 19:00 no end, at 01:30: does not pulse (finished at 22:00)', () => {
    const concert = makeEvent({ date: '2026-11-15', start_time: '19:00', end_time: null, formats: ['concert'] })
    expect(isEventPulsing(concert, ['alternative'], null, now130)).toBe(false)
  })

  it('event with end 02:00: pulses at 01:30', () => {
    const event = makeEvent({ date: '2026-11-15', start_time: '22:00', end_time: '02:00', formats: ['party'] })
    expect(isEventPulsing(event, ['late-night'], null, now130)).toBe(true)
  })

  it('event with end 02:00: does not pulse at 02:30', () => {
    const now230 = new Date('2026-11-16T02:30:00')
    const event = makeEvent({ date: '2026-11-15', start_time: '22:00', end_time: '02:00', formats: ['party'] })
    expect(isEventPulsing(event, ['late-night'], null, now230)).toBe(false)
  })

  it('concert 19:00 no end, at 21:00: pulses (within 3h)', () => {
    const now2100 = new Date('2026-11-15T21:00:00')
    const concert = makeEvent({ date: '2026-11-15', start_time: '19:00', end_time: null, formats: ['concert'] })
    expect(isEventPulsing(concert, ['alternative'], null, now2100)).toBe(true)
  })

  it('concert 19:00 no end, at 22:30: does not pulse (3h expired)', () => {
    const now2230 = new Date('2026-11-15T22:30:00')
    const concert = makeEvent({ date: '2026-11-15', start_time: '19:00', end_time: null, formats: ['concert'] })
    expect(isEventPulsing(concert, ['alternative'], null, now2230)).toBe(false)
  })

  it('event 3 days later (EPIC 22:00–05:00) never pulses', () => {
    const future = makeEvent({ date: '2026-11-18', start_time: '22:00', end_time: '05:00', formats: ['party', 'dj'] })
    expect(isEventPulsing(future, ['late-night'], null, now130)).toBe(false)
  })
})

describe('D. Initial day selection', () => {
  it('at 01:30 (night): initial day is NIGHT_DAY', () => {
    const initial = isNightTime(now130) ? NIGHT_DAY : getToday(now130)
    expect(initial).toBe(NIGHT_DAY)
  })

  it('at 10:00 (day): initial day is calendar today', () => {
    const now1000 = new Date('2026-11-15T10:00:00')
    const initial = isNightTime(now1000) ? NIGHT_DAY : getToday(now1000)
    expect(initial).toBe('2026-11-15')
  })
})

describe('E. Day list in night mode', () => {
  it('at 01:30: day list starts from calendar today (Nov 16), not 5:00-rule today (Nov 15)', () => {
    expect(isNightTime(now130)).toBe(true)
    const calendarToday = toDateString(now130)
    expect(calendarToday).toBe('2026-11-16')
    const noonToday = new Date(calendarToday + 'T12:00:00')
    const days = getUpcomingDays(4, noonToday)
    expect(days).toEqual(['2026-11-16', '2026-11-17', '2026-11-18', '2026-11-19'])
  })

  it('normal mode: day list starts from 5:00-rule today', () => {
    const now1000 = new Date('2026-11-15T10:00:00')
    expect(isNightTime(now1000)).toBe(false)
    const days = getUpcomingDays(5, now1000)
    expect(days[0]).toBe('2026-11-15')
    expect(days).toHaveLength(5)
  })
})
