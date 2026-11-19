import { describe, it, expect } from 'vitest'
import { normalizeText, matchesSearch, isForYou, isNew, hasAnyPrefs, type ForYouPrefs } from './search'
import { isSingleDayPeriod } from './period'
import type { Event, Venue } from './types'

const SUN = new Date('2026-11-15T18:00:00')

function makeEvent(overrides: Partial<Event> = {}): Event {
  return {
    id: 'e1', venue_id: 'v1', title: 'Test Event', date: '2026-11-15',
    start_time: null, end_time: null, doors_time: null,
    formats: [], genres: [], character: [], artists: [],
    price_text: null, free: null, sold_out: null, room: null,
    ticket_url: null, image_url: null, image_thumb: null,
    description: null, description_source: null,
    sources: [], classification: null,
    first_seen: '2026-11-15', last_seen: '2026-11-15',
    status: 'scheduled', flags: [],
    ...overrides,
  }
}

function makeVenue(overrides: Partial<Venue> = {}): Venue {
  return {
    id: 'v1', name: 'Cross Club', city: 'Prague', address: 'Plynárni 23',
    lat: 50.1, lng: 14.4, web: '', ra_url: null, instagram: null,
    type: [], character: [], music: [], size: 'medium',
    capacity: null, features: null, description: null, description_url: null,
    image_url: null, image_source: null, image_thumb: null,
    closing: null, sources: [], active: true, notes: null,
    ...overrides,
  }
}

describe('normalizeText', () => {
  it('lowercases', () => expect(normalizeText('TECHNO')).toBe('techno'))
  it('removes diacritics', () => expect(normalizeText('čajovňa')).toBe('cajovna'))
  it('removes mixed diacritics', () => expect(normalizeText('Čajovňa Alfa')).toBe('cajovna alfa'))
  it('cross club without diacritics', () => expect(normalizeText('Cross Club')).toBe('cross club'))
  it('handles empty string', () => expect(normalizeText('')).toBe(''))
})

describe('matchesSearch', () => {
  it('matches event title', () => {
    const e = makeEvent({ title: 'Techno Noc v Berlíne' })
    expect(matchesSearch('techno', e, undefined)).toBe(true)
  })

  it('matches without diacritics', () => {
    const e = makeEvent({ title: 'Čajovňa sessions' })
    expect(matchesSearch('cajovna', e, undefined)).toBe(true)
  })

  it('matches venue name', () => {
    const e = makeEvent()
    const v = makeVenue({ name: 'Cross Club' })
    expect(matchesSearch('cross', e, v)).toBe(true)
  })

  it('matches event format tag', () => {
    const e = makeEvent({ formats: ['techno', 'dj'] })
    expect(matchesSearch('techno', e, undefined)).toBe(true)
  })

  it('matches event genre tag', () => {
    const e = makeEvent({ genres: ['post-punk', 'indie'] })
    expect(matchesSearch('punk', e, undefined)).toBe(true)
  })

  it('matches venue character tag', () => {
    const e = makeEvent()
    const v = makeVenue({ character: ['late-night', 'diy'] })
    expect(matchesSearch('diy', e, v)).toBe(true)
  })

  it('no match', () => {
    const e = makeEvent({ title: 'Jazz evening', formats: ['concert'], genres: ['jazz'] })
    const v = makeVenue({ name: 'Archa', character: ['art-space'] })
    expect(matchesSearch('techno', e, v)).toBe(false)
  })

  it('empty query matches all', () => {
    expect(matchesSearch('', makeEvent(), undefined)).toBe(true)
    expect(matchesSearch('  ', makeEvent(), undefined)).toBe(true)
  })

  it('case insensitive', () => {
    const e = makeEvent({ title: 'TECHNO NIGHT' })
    expect(matchesSearch('Techno', e, undefined)).toBe(true)
  })
})

describe('isForYou (task 079)', () => {
  const P = (o: Partial<ForYouPrefs> = {}): ForYouPrefs => ({ favorites: new Set(), types: [], subtypes: [], genres: [], ...o })
  const dj = (o: Partial<Event> = {}) => makeEvent({ formats: ['dj'], genres: [], ...o })
  const concert = (o: Partial<Event> = {}) => makeEvent({ formats: ['concert'], genres: [], ...o })
  const culture = (fmt: string, o: Partial<Event> = {}) => makeEvent({ formats: [fmt], genres: [], ...o })

  it('no preferences at all → nothing', () => {
    expect(isForYou(dj({ venue_id: 'cross-club', genres: ['techno'] }), P())).toBe(false)
    expect(hasAnyPrefs(P())).toBe(false)
  })

  it('no types (skipped): favourite venue, any type (old behaviour)', () => {
    const p = P({ favorites: new Set(['cross-club']) })
    expect(isForYou(dj({ venue_id: 'cross-club' }), p)).toBe(true)
    expect(isForYou(culture('workshop', { venue_id: 'cross-club' }), p)).toBe(true)
    expect(isForYou(dj({ venue_id: 'archa' }), p)).toBe(false)
  })

  it('no types: genre match counts too, any type', () => {
    const p = P({ genres: ['punk'] })
    expect(isForYou(concert({ venue_id: 'archa', genres: ['post-punk'] }), p)).toBe(true)
    expect(isForYou(concert({ venue_id: 'archa', genres: ['jazz'] }), p)).toBe(false)
  })

  it('type not selected → no, even in a favourite venue', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['dj'] })
    expect(isForYou(concert({ venue_id: 'cross-club' }), p)).toBe(false)
  })

  it('workshop in a favourite venue without culture selected → no', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['dj', 'concert'] })
    expect(isForYou(culture('workshop', { venue_id: 'cross-club' }), p)).toBe(false)
  })

  it('DJ + techno in a non-favourite venue → yes', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['dj'], genres: ['techno'] })
    expect(isForYou(dj({ venue_id: 'archa', genres: ['techno'] }), p)).toBe(true)
    expect(isForYou(dj({ venue_id: 'archa', genres: ['house'] }), p)).toBe(false)
  })

  it('music in a favourite venue without genre match → yes', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['party'] })
    expect(isForYou(makeEvent({ formats: ['party'], venue_id: 'cross-club' }), p)).toBe(true)
  })

  it('genre matched via umbrella (post-punk → punk)', () => {
    const p = P({ types: ['concert'], genres: ['punk'] })
    expect(isForYou(concert({ genres: ['post-punk'] }), p)).toBe(true)
  })

  it('only types, no venues and no genres → nothing from music', () => {
    const p = P({ types: ['concert', 'dj', 'party'] })
    expect(isForYou(dj({ genres: ['techno'] }), p)).toBe(false)
    expect(isForYou(concert({ genres: ['rock'] }), p)).toBe(false)
  })

  it('culture with subtypes → subtype must match, venue does not matter', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['culture'], subtypes: ['film', 'talk'] })
    expect(isForYou(culture('film', { venue_id: 'archa' }), p)).toBe(true)
    expect(isForYou(culture('theatre', { venue_id: 'cross-club' }), p)).toBe(false)
  })

  it('culture without subtypes → culture in a favourite venue only', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['culture'] })
    expect(isForYou(culture('film', { venue_id: 'cross-club' }), p)).toBe(true)
    expect(isForYou(culture('film', { venue_id: 'archa' }), p)).toBe(false)
  })

  it('culture genre in prefs does not pull in music genres for culture', () => {
    const p = P({ types: ['culture'], genres: ['techno'] })
    expect(isForYou(culture('film', { genres: ['techno'] }), p)).toBe(false)
  })
})

describe('isNew', () => {
  // SUN = 2026-11-15T18:00:00
  // 7 days inclusive: 2026-11-09 (6 days back) to 2026-11-15

  it('today is new', () => {
    expect(isNew(makeEvent({ first_seen: '2026-11-15' }), SUN)).toBe(true)
  })

  it('6 days ago is new (boundary)', () => {
    expect(isNew(makeEvent({ first_seen: '2026-11-09' }), SUN)).toBe(true)
  })

  it('7 days ago is not new', () => {
    expect(isNew(makeEvent({ first_seen: '2026-11-08' }), SUN)).toBe(false)
  })

  it('yesterday is new', () => {
    expect(isNew(makeEvent({ first_seen: '2026-11-14' }), SUN)).toBe(true)
  })

  it('much older is not new', () => {
    expect(isNew(makeEvent({ first_seen: '2026-10-01' }), SUN)).toBe(false)
  })
})

describe('isSingleDayPeriod', () => {
  it('today is single day', () => expect(isSingleDayPeriod({ type: 'today' })).toBe(true))
  it('tomorrow is single day', () => expect(isSingleDayPeriod({ type: 'tomorrow' })).toBe(true))
  it('custom same day is single day', () => expect(isSingleDayPeriod({ type: 'custom', from: '2026-11-20', to: '2026-11-20' })).toBe(true))
  it('custom range is not single day', () => expect(isSingleDayPeriod({ type: 'custom', from: '2026-11-20', to: '2026-11-24' })).toBe(false))
  it('weekend is not single day', () => expect(isSingleDayPeriod({ type: 'weekend' })).toBe(false))
  it('next7 is not single day', () => expect(isSingleDayPeriod({ type: 'next7' })).toBe(false))
  it('anytime is not single day', () => expect(isSingleDayPeriod({ type: 'anytime' })).toBe(false))
})
