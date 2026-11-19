import { describe, it, expect, beforeEach } from 'vitest'
import type { Event, Venue } from './types'
import {
  DEFAULT_FILTER, matchesFilter, filterCounts, filterBadgeCount, toggleType, availableGenres,
  umbrellasOf, eventUmbrellas, parseFilter, availableCultureGenres, activeCultureGenres, serializeFilter, isDefaultFilter, orderByCount,
  GENRE_HIERARCHY, type EventFilter, type FilterItem, type Hierarchy,
} from './filter'
import { cultureSubtype, eventIconKey } from './eventType'

function ev(id: string, o: Partial<Event> = {}): Event {
  return {
    id, venue_id: 'v1', title: id, date: '2026-11-20', start_time: '20:00', doors_time: null, end_time: null,
    formats: ['concert'], genres: [], character: [], artists: [], price_text: null, free: null, sold_out: null,
    room: null, ticket_url: null, image_url: null, image_thumb: null, description: null, description_source: null,
    sources: [], classification: null, first_seen: '2026-11-01', last_seen: '2026-11-19', status: 'scheduled', flags: [],
    ...o,
  }
}

function venue(id: string, o: Partial<Venue> = {}): Venue {
  return {
    id, name: id, city: 'Praha', address: '', lat: 50, lng: 14, web: '', ra_url: null, instagram: null,
    type: [], character: [], music: [], size: 'medium', description: null, description_url: null,
    image_url: null, image_source: null, image_thumb: null, closing: null, sources: [], active: true, ...o,
  }
}

const H: Hierarchy = {
  'hard-techno': ['techno'], 'post-punk': ['alternative'], 'noise-rock': ['rock', 'alternative'],
  grindcore: ['metal', 'punk'], goregrind: ['grindcore'], drama: ['film', 'theatre'], horror: ['film'],
  musical: ['theatre'], ballet: ['dance'],
}

const f = (o: Partial<EventFilter>): EventFilter => ({ ...DEFAULT_FILTER, ...o })

const v1 = venue('v1', { character: ['underground'], size: 'small' })
const v2 = venue('v2', { character: ['commercial'], size: 'large' })

describe('genre hierarchy', () => {
  it('a genre without parents is its own umbrella; parents are followed to the roots', () => {
    expect(umbrellasOf('techno', H)).toEqual(['techno'])
    expect(umbrellasOf('hard-techno', H)).toEqual(['techno'])
    expect(umbrellasOf('noise-rock', H).sort()).toEqual(['alternative', 'rock'])
    expect(umbrellasOf('goregrind', H).sort()).toEqual(['metal', 'punk'])
  })
  it('culture subtype umbrellas (film, theatre, dance) are not genre chips', () => {
    expect(eventUmbrellas(ev('a', { genres: ['drama', 'horror'] }), H)).toEqual([])
  })
  it('loads data/genre_hierarchy.json without the comment key', () => {
    expect(GENRE_HIERARCHY['hard-techno']).toEqual(['techno'])
    expect(GENRE_HIERARCHY['_comment']).toBeUndefined()
  })
})

describe('matchesFilter', () => {
  const techno = ev('techno', { formats: ['dj'], genres: ['hard-techno'] })
  const punk = ev('punk', { formats: ['concert'], genres: ['post-punk'] })
  const house = ev('house', { formats: ['dj'], genres: ['house'] })

  it('default filter lets everything through', () => {
    expect([techno, punk, house].every(e => matchesFilter(e, v1, DEFAULT_FILTER, H))).toBe(true)
  })
  it('parent chip includes its subgenres', () => {
    expect(matchesFilter(techno, v1, f({ genres: ['techno'] }), H)).toBe(true)
    expect(matchesFilter(house, v1, f({ genres: ['techno'] }), H)).toBe(false)
  })
  it('OR within a group, AND between groups', () => {
    const g = f({ genres: ['techno', 'alternative'] })
    expect(matchesFilter(techno, v1, g, H)).toBe(true)
    expect(matchesFilter(punk, v1, g, H)).toBe(true)
    expect(matchesFilter(house, v1, g, H)).toBe(false)
    const g2 = { ...g, types: ['dj', 'party'] as EventFilter['types'] }
    expect(matchesFilter(techno, v1, g2, H)).toBe(true)
    expect(matchesFilter(punk, v1, g2, H)).toBe(false)
    expect(matchesFilter(techno, v1, { ...g, characters: ['commercial'] }, H)).toBe(false)
    expect(matchesFilter(techno, v2, { ...g, characters: ['commercial'] }, H)).toBe(true)
  })
  it('venue size', () => {
    expect(matchesFilter(techno, v1, f({ sizes: ['small', 'medium'] }), H)).toBe(true)
    expect(matchesFilter(techno, v2, f({ sizes: ['small', 'medium'] }), H)).toBe(false)
    expect(matchesFilter(techno, venue('x', { size: null as unknown as string }), f({ sizes: ['small'] }), H)).toBe(false)
  })
  it('free = free === true only (no price is not free)', () => {
    expect(matchesFilter(ev('a', { free: true }), v1, f({ free: true }), H)).toBe(true)
    expect(matchesFilter(ev('b', { free: null }), v1, f({ free: true }), H)).toBe(false)
    expect(matchesFilter(ev('c', { free: false }), v1, f({ free: true }), H)).toBe(false)
  })
  it('culture subtypes: none selected = all culture; selected = only those', () => {
    const film = ev('film', { formats: ['film'] })
    const talk = ev('talk', { formats: ['talk'] })
    const other = ev('other', { formats: ['other'] })
    expect([film, talk, other].every(e => matchesFilter(e, v1, DEFAULT_FILTER, H))).toBe(true)
    const s = f({ subtypes: ['film'] })
    expect(matchesFilter(film, v1, s, H)).toBe(true)
    expect(matchesFilter(talk, v1, s, H)).toBe(false)
    expect(matchesFilter(other, v1, s, H)).toBe(false)
    // subtypes do not touch other types
    expect(matchesFilter(punk, v1, s, H)).toBe(true)
    // culture off: subtypes remembered but no culture shown
    const off = { ...s, types: ['concert', 'party', 'dj'] as EventFilter['types'] }
    expect(matchesFilter(film, v1, off, H)).toBe(false)
  })
})

describe('culture subtype = icon rule', () => {
  it('uses the same choice as eventIconKey', () => {
    expect(cultureSubtype(['talk', 'film'])).toBe('film')
    expect(eventIconKey(['talk', 'film'])).toBe('film')
    expect(cultureSubtype(['talk', 'film'], 'talk')).toBe('talk')
    expect(eventIconKey(['talk', 'film'], 'talk')).toBe('talk')
    expect(cultureSubtype(['theatre'])).toBe('theatre')
    expect(eventIconKey(['theatre'])).toBe('culture')
    expect(cultureSubtype(['performance', 'dance'], 'performance')).toBe(null)
    expect(eventIconKey(['performance', 'dance'], 'performance')).toBe('culture')
    expect(cultureSubtype(['concert', 'film'])).toBe(null)
  })
})

describe('toggleType', () => {
  it('turns types off and on, keeps legend order', () => {
    let x = toggleType(DEFAULT_FILTER, 'concert')
    expect(x.types).toEqual(['party', 'dj', 'culture'])
    x = toggleType(x, 'concert')
    expect(x.types).toEqual(['concert', 'party', 'dj', 'culture'])
  })
  it('the last enabled type cannot be turned off', () => {
    const one = f({ types: ['dj'] })
    expect(toggleType(one, 'dj').types).toEqual(['dj'])
  })
})

describe('badge', () => {
  it('default = 0', () => expect(filterBadgeCount(DEFAULT_FILTER)).toBe(0))
  it('tags incl. subtypes and free, +1 when some types are off', () => {
    expect(filterBadgeCount(f({ genres: ['techno', 'rock'], characters: ['cozy'], sizes: ['small'] }))).toBe(4)
    expect(filterBadgeCount(f({ subtypes: ['film', 'talk'], free: true }))).toBe(3)
    expect(filterBadgeCount(f({ types: ['dj', 'party'] }))).toBe(1)
    expect(filterBadgeCount(f({ types: ['dj'], genres: ['techno'] }))).toBe(2)
  })
})

describe('available genres', () => {
  const events = [
    ev('a', { formats: ['concert'], genres: ['post-punk'] }),
    ev('b', { formats: ['dj'], genres: ['hard-techno'] }),
    ev('c', { formats: ['film'], genres: ['horror'] }),
  ]
  it('only genres of enabled types, umbrellas only', () => {
    expect(availableGenres(events, ['concert', 'party', 'dj', 'culture'], [], H).sort()).toEqual(['alternative', 'techno'])
    expect(availableGenres(events, ['dj'], [], H)).toEqual(['techno'])
    expect(availableGenres(events, ['culture'], [], H)).toEqual([])
  })
  it('selected genres stay offered', () => {
    expect(availableGenres(events, ['dj'], ['latin'], H).sort()).toEqual(['latin', 'techno'])
  })
})

describe('filterCounts', () => {
  // v1: two techno DJ nights + one punk concert; v2: one techno DJ night
  const items: FilterItem[] = [
    { event: ev('t1', { venue_id: 'v1', formats: ['dj'], genres: ['techno'] }), venue: v1 },
    { event: ev('t2', { venue_id: 'v1', formats: ['dj'], genres: ['hard-techno'] }), venue: v1 },
    { event: ev('p1', { venue_id: 'v1', formats: ['concert'], genres: ['post-punk'], free: true }), venue: v1 },
    { event: ev('t3', { venue_id: 'v2', formats: ['dj'], genres: ['techno'] }), venue: v2 },
  ]
  it('Akcie counts events, map counts venues', () => {
    const e = filterCounts(items, DEFAULT_FILTER, 'events', H)
    const m = filterCounts(items, DEFAULT_FILTER, 'venues', H)
    expect(e.total).toBe(4)
    expect(m.total).toBe(2)
    expect(e.genres.get('techno')).toBe(3)
    expect(m.genres.get('techno')).toBe(2)
    expect(e.types.dj).toBe(3)
    expect(m.types.dj).toBe(2)
    expect(m.types.concert).toBe(1)
    expect(e.free).toBe(1)
  })
  it('chip count = its results under the other groups', () => {
    const sel = f({ genres: ['techno'], characters: ['underground'] })
    const c = filterCounts(items, sel, 'events', H)
    expect(c.total).toBe(2)
    expect(c.genres.get('techno')).toBe(2)
    expect(c.genres.get('alternative')).toBe(1)
    expect(c.characters.get('underground')).toBe(2)
    expect(c.characters.get('commercial')).toBe(1)
    expect(c.sizes.small).toBe(2)
    expect(c.sizes.large).toBe(0) // the large venue is not underground
    expect(c.types.concert).toBe(0)
  })
  it('subtype counts', () => {
    const c = filterCounts([
      { event: ev('f', { formats: ['film'] }), venue: v1 },
      { event: ev('q', { formats: ['quiz'] }), venue: v1 },
    ], f({ subtypes: ['film'] }), 'events', H)
    expect(c.subtypes.film).toBe(1)
    expect(c.subtypes.quiz).toBe(1)
    expect(c.types.culture).toBe(1)
    expect(c.total).toBe(1)
  })
  it('order by count, 0 at the end', () => {
    const counts = new Map([['a', 0], ['b', 5], ['c', 2]])
    expect(orderByCount(['a', 'b', 'c', 'd'], counts)).toEqual(['b', 'c', 'a', 'd'])
  })
})

describe('storage', () => {
  beforeEach(() => {
    const mem = new Map<string, string>()
    ;(globalThis as unknown as { localStorage: Storage }).localStorage = {
      getItem: (k: string) => mem.get(k) ?? null,
      setItem: (k: string, v: string) => { mem.set(k, v) },
      removeItem: (k: string) => { mem.delete(k) },
      clear: () => mem.clear(), key: () => null, length: 0,
    }
  })
  it('round trip', () => {
    const x = f({ types: ['dj', 'party'], subtypes: ['film'], genres: ['techno'], characters: ['cozy'], sizes: ['large'], free: true })
    expect(parseFilter(serializeFilter(x))).toEqual({ ...x, types: ['party', 'dj'] })
  })
  it('save and load via store', async () => {
    const { getStoredFilter, setStoredFilter } = await import('./store')
    expect(isDefaultFilter(getStoredFilter())).toBe(true)
    setStoredFilter(f({ genres: ['techno'], types: ['dj'] }))
    expect(getStoredFilter()).toEqual(f({ genres: ['techno'], types: ['dj'] }))
  })
  it('invalid stored data falls back to default; empty types = all', () => {
    expect(parseFilter('nonsense')).toEqual(DEFAULT_FILTER)
    expect(parseFilter(JSON.stringify({ types: [], sizes: ['huge'], subtypes: ['x'] }))).toEqual(DEFAULT_FILTER)
  })
})

describe('culture genres (task 076)', () => {
  const horrorFilm = ev('hf', { formats: ['film'], genres: ['horror'] })
  const dramaFilm = ev('df', { formats: ['film'], genres: ['drama'] })
  const dramaPlay = ev('dp', { formats: ['theatre'], genres: ['drama'] })
  const musical = ev('mu', { formats: ['theatre'], genres: ['musical'] })
  const techno = ev('te', { formats: ['dj'], genres: ['hard-techno'] })
  const house = ev('ho', { formats: ['dj'], genres: ['house'] })
  const jazzFilm = ev('jf', { formats: ['film'], genres: ['jazz'] })
  const all = [horrorFilm, dramaFilm, dramaPlay, musical, techno, house, jazzFilm]
  const pass = (fl: EventFilter) => all.filter(e => matchesFilter(e, v1, fl, H)).map(e => e.id).sort()

  it('rows only for selected subtypes that have genres', () => {
    expect(availableCultureGenres(all, [], [], H)).toEqual([])
    expect(availableCultureGenres(all, ['talk'], [], H)).toEqual([])
    const rows = availableCultureGenres(all, ['film'], [], H)
    expect(rows.map(r => r.subtype)).toEqual(['film'])
    expect(rows[0]!.keys.sort()).toEqual(['film:drama', 'film:horror'])
  })
  it('film + theatre = two rows without mixing; drama in film is not drama in theatre', () => {
    const rows = availableCultureGenres(all, ['theatre', 'film'], [], H)
    expect(rows.map(r => r.subtype)).toEqual(['film', 'theatre'])
    expect(rows[0]!.keys.sort()).toEqual(['film:drama', 'film:horror'])
    expect(rows[1]!.keys.sort()).toEqual(['theatre:drama', 'theatre:musical'])
    expect(pass(f({ subtypes: ['film', 'theatre'], cultureGenres: ['film:drama'] }))).toEqual(['df'])
    expect(pass(f({ subtypes: ['film', 'theatre'], cultureGenres: ['theatre:drama'] }))).toEqual(['dp'])
  })
  it('culture genres do not appear in the Žáner section, music genres do not appear in culture rows', () => {
    expect(availableGenres(all, ['concert', 'party', 'dj', 'culture'], [], H).sort()).toEqual(['house', 'techno'])
    expect(availableCultureGenres(all, ['film'], [], H)[0]!.keys).not.toContain('film:jazz')
  })
  it('a music genre does not select a culture event', () => {
    expect(pass(f({ genres: ['jazz'] }))).toEqual([])
    expect(pass(f({ genres: ['techno'] }))).toEqual(['te'])
  })
  it('techno + horror = union (one OR group)', () => {
    expect(pass(f({ subtypes: ['film'], genres: ['techno'], cultureGenres: ['film:horror'] }))).toEqual(['hf', 'te'])
  })
  it('culture genre applies only while its subtype is selected and culture is on; kept otherwise', () => {
    const x = f({ subtypes: [], cultureGenres: ['film:horror'] })
    expect(activeCultureGenres(x)).toEqual([])
    expect(pass(x)).toEqual(all.map(e => e.id).sort())
    expect(isDefaultFilter(x)).toBe(true)
    const off = f({ types: ['dj'], subtypes: ['film'], cultureGenres: ['film:horror'] })
    expect(activeCultureGenres(off)).toEqual([])
    expect(pass(off)).toEqual(['ho', 'te'])
    expect(parseFilter(serializeFilter(x)).cultureGenres).toEqual(['film:horror'])
  })
  it('badge counts culture genres that apply', () => {
    expect(filterBadgeCount(f({ subtypes: ['film'], cultureGenres: ['film:horror', 'film:drama'] }))).toBe(3)
    expect(filterBadgeCount(f({ subtypes: ['film'], genres: ['techno'], cultureGenres: ['film:horror'] }))).toBe(3)
    expect(filterBadgeCount(f({ subtypes: [], cultureGenres: ['film:horror'] }))).toBe(0)
  })
  it('chip counts per subtype:genre', () => {
    const items = all.map(event => ({ event, venue: v1 }))
    const c = filterCounts(items, f({ subtypes: ['film', 'theatre'], cultureGenres: ['film:horror'] }), 'events', H)
    expect(c.cultureGenres.get('film:horror')).toBe(1)
    expect(c.cultureGenres.get('film:drama')).toBe(1)
    expect(c.cultureGenres.get('theatre:drama')).toBe(1)
    expect(c.genres.get('jazz')).toBeUndefined()
    expect(c.total).toBe(1)
  })
  it('a stored filter from task 075 (no cultureGenres) still loads', () => {
    const old = JSON.stringify({ types: ['concert', 'culture'], subtypes: ['film'], genres: ['techno'], characters: [], sizes: [], free: false })
    expect(parseFilter(old)).toEqual(f({ types: ['concert', 'culture'], subtypes: ['film'], genres: ['techno'] }))
    expect(parseFilter(JSON.stringify({ cultureGenres: ['x:horror', 'film', 'film:horror', 3] })).cultureGenres).toEqual(['film:horror'])
  })
})
