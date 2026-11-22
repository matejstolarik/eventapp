import { describe, it, expect } from 'vitest'
import { normalizeText, matchesSearch, isForYou, isNew, hasAnyPrefs, hasOnlyTypes, forYouScore, forYouTier, FOR_YOU_TIER_NAME, type ForYouPrefs } from './search'
import { isSingleDayPeriod, sortAfterForYouToggle, sortEvents } from './period'
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

describe('forYouScore (task 087, model D)', () => {
  const P = (o: Partial<ForYouPrefs> = {}): ForYouPrefs => ({ favorites: new Set(), types: [], subtypes: [], genres: [], ...o })
  const dj = (o: Partial<Event> = {}) => makeEvent({ formats: ['dj'], genres: [], ...o })
  const concert = (o: Partial<Event> = {}) => makeEvent({ formats: ['concert'], genres: [], ...o })
  const culture = (fmt: string, o: Partial<Event> = {}) => makeEvent({ formats: [fmt], genres: [], ...o })
  const music = P({ types: ['concert', 'dj'] })
  const DIVO = ['blues', 'rock', 'techno', 'post-punk', 'shoegaze', 'experimental']

  it('examples from the task: genres without order', () => {
    expect(forYouScore(concert({ genres: ['rock'] }), { ...music, genres: ['rock'] })).toBe(80)
    expect(forYouScore(concert({ genres: ['rock', 'hip-hop'] }), { ...music, genres: ['hip-hop'] })).toBe(65)
    expect(forYouScore(concert({ genres: ['hip-hop', 'rock'] }), { ...music, genres: ['hip-hop'] })).toBe(65)
    expect(forYouScore(concert({ genres: ['rock', 'hip-hop'] }), { ...music, genres: ['rock', 'hip-hop'] })).toBe(80)
  })

  it('Divo Institute example, with and without favourite Palác Akropolis', () => {
    const e = concert({ venue_id: 'palac-akropolis', genres: DIVO })
    const fav = new Set(['palac-akropolis'])
    expect(forYouScore(e, { ...music, genres: ['alternative', 'punk'] })).toBe(60)
    expect(forYouScore(e, { ...music, genres: ['alternative', 'punk', 'rock'] })).toBe(65)
    expect(forYouScore(e, { ...music, genres: ['punk'] })).toBe(55)
    expect(forYouScore(e, { ...music, favorites: fav, genres: ['alternative', 'punk'] })).toBe(80)
    expect(forYouScore(e, { ...music, favorites: fav, genres: ['alternative', 'punk', 'rock'] })).toBe(85)
    expect(forYouScore(e, { ...music, favorites: fav, genres: ['punk'] })).toBe(75)
  })

  it('type is a gate, even in a favourite venue', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['dj'], genres: ['techno'] })
    expect(forYouScore(concert({ venue_id: 'cross-club', genres: ['techno'] }), p)).toBe(0)
    expect(forYouScore(culture('workshop', { venue_id: 'cross-club' }), p)).toBe(0)
  })

  it('no genre matched: only venue points', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['dj'], genres: ['techno'] })
    expect(forYouScore(dj({ venue_id: 'archa', genres: ['house'] }), p)).toBe(0)
    expect(forYouScore(dj({ venue_id: 'cross-club', genres: ['house'] }), p)).toBe(20)
  })

  it('event without genres: 40 (+20 in a favourite venue)', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['dj'], genres: ['techno'] })
    expect(forYouScore(dj({ venue_id: 'archa' }), p)).toBe(40)
    expect(forYouScore(dj({ venue_id: 'cross-club' }), p)).toBe(60)
  })

  it('user without liked genres (task 091): genre part 20, ✦ only in a favourite venue', () => {
    const p = P({ types: ['concert', 'dj'], favorites: new Set(['x']) })
    expect(forYouScore(dj({ genres: ['techno'] }), p)).toBe(20)
    expect(forYouScore(dj({ venue_id: 'x', genres: ['techno'] }), p)).toBe(40)
    expect(forYouScore(concert({}), p)).toBe(20)
    expect(forYouScore(concert({ venue_id: 'x' }), p)).toBe(40)
    expect(forYouTier(forYouScore(dj({ genres: ['techno'] }), p))).toBe(0)
    expect(forYouTier(forYouScore(dj({ venue_id: 'x', genres: ['techno'] }), p))).toBe(1)
    expect(forYouScore(concert({ venue_id: 'x' }), P({ types: ['dj'], favorites: new Set(['x']) }))).toBe(0)
  })

  it('only types (no venues, no genres, task 091): 0', () => {
    const p = P({ types: ['concert', 'dj', 'party'] })
    expect(hasOnlyTypes(p)).toBe(true)
    expect(forYouScore(dj({ genres: ['techno'] }), p)).toBe(0)
    expect(forYouScore(concert({ genres: ['rock'] }), p)).toBe(0)
    expect(forYouScore(concert(), p)).toBe(0)
    expect(forYouScore(culture('film'), P({ types: ['culture'], subtypes: ['film'] }))).toBe(0)
    expect(hasOnlyTypes(P({ types: ['dj'], genres: ['techno'] }))).toBe(false)
    expect(hasOnlyTypes(P({ types: ['dj'], favorites: new Set(['x']) }))).toBe(false)
    expect(hasOnlyTypes(P())).toBe(false)
  })

  it('types + genres unchanged (task 091): event without genres 40, no match 0', () => {
    const p = P({ types: ['concert', 'dj'], genres: ['techno'] })
    expect(forYouScore(dj({}), p)).toBe(40)
    expect(forYouScore(dj({ genres: ['techno'] }), p)).toBe(80)
    expect(forYouScore(dj({ genres: ['jazz'] }), p)).toBe(0)
  })

  it('no preferences at all: 0', () => {
    expect(forYouScore(dj({ venue_id: 'cross-club', genres: ['techno'] }), P())).toBe(0)
    expect(hasAnyPrefs(P())).toBe(false)
  })

  it('culture: subtype 80, culture without subtypes 40, other subtype 0', () => {
    const p = P({ favorites: new Set(['cross-club']), types: ['culture'], subtypes: ['film', 'talk'] })
    expect(forYouScore(culture('film', { venue_id: 'archa' }), p)).toBe(80)
    expect(forYouScore(culture('film', { venue_id: 'cross-club' }), p)).toBe(100)
    expect(forYouScore(culture('theatre', { venue_id: 'cross-club' }), p)).toBe(0)
    const q = P({ favorites: new Set(['cross-club']), types: ['culture'], genres: ['techno'] })
    expect(forYouScore(culture('film', { venue_id: 'archa', genres: ['techno'] }), q)).toBe(40)
    expect(forYouScore(culture('film', { venue_id: 'cross-club' }), q)).toBe(60)
  })

  it('no types selected: no gate, genres + venue; neutral 40 only in a favourite venue', () => {
    const p = P({ favorites: new Set(['cross-club']), genres: ['punk'] })
    expect(forYouScore(concert({ venue_id: 'archa', genres: ['post-punk'] }), p)).toBe(80)
    expect(forYouScore(culture('film', { venue_id: 'archa', genres: ['post-punk'] }), p)).toBe(80)
    expect(forYouScore(concert({ venue_id: 'archa', genres: ['jazz'] }), p)).toBe(0)
    expect(forYouScore(concert({ venue_id: 'archa' }), p)).toBe(0)
    expect(forYouScore(concert({ venue_id: 'cross-club' }), p)).toBe(60)
    expect(forYouScore(concert({ venue_id: 'cross-club', genres: ['jazz'] }), p)).toBe(20)
    // only favourites (old behaviour): favourite venue = one sparkle
    const f = P({ favorites: new Set(['cross-club']) })
    expect(forYouScore(culture('workshop', { venue_id: 'cross-club' }), f)).toBe(60)
    expect(forYouScore(dj({ venue_id: 'archa' }), f)).toBe(0)
  })

  it('capped at 100', () => {
    const p = P({ favorites: new Set(['x']), types: ['concert'], genres: ['rock'] })
    expect(forYouScore(concert({ venue_id: 'x', genres: ['rock'] }), p)).toBe(100)
  })

  it('tiers: two sparkles >= 75, one 40-74, nothing below; isForYou = either', () => {
    expect(forYouTier(100)).toBe(2)
    expect(forYouTier(75)).toBe(2)
    expect(forYouTier(74)).toBe(1)
    expect(forYouTier(40)).toBe(1)
    expect(forYouTier(39)).toBe(0)
    expect(forYouTier(0)).toBe(0)
    expect(FOR_YOU_TIER_NAME[2]).toBe('Presne pre teba')
    expect(FOR_YOU_TIER_NAME[1]).toBe('Mohlo by ťa baviť')
    const p = P({ types: ['dj'], genres: ['techno'] })
    expect(isForYou(dj({ genres: ['techno'] }), p)).toBe(true)
    expect(isForYou(dj({ genres: ['house'] }), p)).toBe(false)
  })
})

describe('Best match sort and the Pre teba chip (task 087)', () => {
  it('turning the chip on switches to Best match and remembers the sort', () => {
    expect(sortAfterForYouToggle(true, 'size', 'date', true)).toEqual({ sort: 'match', remembered: 'size' })
  })
  it('turning it off restores the remembered sort', () => {
    expect(sortAfterForYouToggle(false, 'match', 'size', true)).toEqual({ sort: 'size', remembered: 'size' })
  })
  it('a manual change while on stays after turning off', () => {
    expect(sortAfterForYouToggle(false, 'date', 'size', true)).toEqual({ sort: 'date', remembered: 'size' })
  })
  it('distance falls back to date on a multi-day period', () => {
    expect(sortAfterForYouToggle(false, 'match', 'distance', false).sort).toBe('date')
    expect(sortAfterForYouToggle(false, 'match', 'distance', true).sort).toBe('distance')
  })
  it('sortEvents by score descending, ties by date/time', () => {
    const a = makeEvent({ id: 'a', date: '2026-11-16', start_time: '20:00' })
    const b = makeEvent({ id: 'b', date: '2026-11-15', start_time: '21:00' })
    const c = makeEvent({ id: 'c', date: '2026-11-15', start_time: '19:00' })
    const score: Record<string, number> = { a: 80, b: 40, c: 40 }
    expect(sortEvents([b, c, a], new Map(), 'match', null, undefined, e => score[e.id]!).map(e => e.id)).toEqual(['a', 'c', 'b'])
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

  // task 086: events of the venue's first load are not new
  it('event from the venue first load is not new', () => {
    const venue = { first_loaded: '2026-11-14' }
    expect(isNew(makeEvent({ first_seen: '2026-11-14' }), SUN, venue)).toBe(false)
    expect(isNew(makeEvent({ first_seen: '2026-11-13' }), SUN, venue)).toBe(false)
  })

  it('event added after the venue first load is new', () => {
    expect(isNew(makeEvent({ first_seen: '2026-11-15' }), SUN, { first_loaded: '2026-11-14' })).toBe(true)
  })

  it('venue without first_loaded (loaded before the rule) keeps the 7-day rule', () => {
    expect(isNew(makeEvent({ first_seen: '2026-11-14' }), SUN, { first_loaded: null })).toBe(true)
    expect(isNew(makeEvent({ first_seen: '2026-11-14' }), SUN, null)).toBe(true)
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
