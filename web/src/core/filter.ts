// Filter (task 075, docs/design.md 7b): pure functions, no UI.
// Within a group = OR, between groups = AND. Types are all on by default and
// the user turns them off; the other groups are off by default.
import type { Event, Venue } from './types'
import { getEventType, cultureSubtype, CULTURE_SUBTYPES, type CultureSubtype } from './eventType'
import hierarchyJson from '../../../data/genre_hierarchy.json'

export type FilterType = 'concert' | 'party' | 'dj' | 'culture'
export const FILTER_TYPES: readonly FilterType[] = ['concert', 'party', 'dj', 'culture']
export const VENUE_SIZES = ['small', 'medium', 'large'] as const
export type VenueSize = typeof VENUE_SIZES[number]

export interface EventFilter {
  /** Enabled event types (never empty) */
  types: FilterType[]
  /** Selected culture subtypes; empty = all culture. Kept while culture is off. */
  subtypes: CultureSubtype[]
  /** Selected umbrella music genres (apply to concert, party, DJ only) */
  genres: string[]
  /** Selected culture genres as `subtype:genre` (e.g. `film:horror`, task 076).
   * Apply only while culture is on and their subtype is selected; kept otherwise. */
  cultureGenres: string[]
  /** Selected venue character tags */
  characters: string[]
  /** Selected venue sizes */
  sizes: VenueSize[]
  /** Only events with free === true */
  free: boolean
}

export const DEFAULT_FILTER: EventFilter = {
  types: [...FILTER_TYPES], subtypes: [], genres: [], cultureGenres: [], characters: [], sizes: [], free: false,
}

export type Hierarchy = Record<string, string[]>

/** Subgenre → parents, loaded at build time from data/genre_hierarchy.json. */
export const GENRE_HIERARCHY: Hierarchy = Object.fromEntries(
  Object.entries(hierarchyJson as Record<string, unknown>)
    .filter(([k, v]) => !k.startsWith('_') && Array.isArray(v)),
) as Hierarchy

/** Umbrellas that are also culture subtypes (film, theatre, dance): the subtype
 * chips cover them, so they are not offered as genre chips (task 075). */
const SUBTYPE_UMBRELLAS = new Set<string>(CULTURE_SUBTYPES)

/** Key of a culture genre chip: the same name under two subtypes = two chips. */
export function cultureGenreKey(subtype: string, genre: string): string {
  return `${subtype}:${genre}`
}
function splitCultureGenreKey(key: string): [string, string] {
  const i = key.indexOf(':')
  return i < 0 ? [key, ''] : [key.slice(0, i), key.slice(i + 1)]
}

// ── Types ──────────────────────────────────────────────────────────────────

/** Filter type of an event: `other` belongs to culture (same colour). */
export function filterTypeOf(e: Pick<Event, 'formats' | 'primary_format'>): FilterType {
  const t = getEventType(e.formats, e.primary_format)
  return t === 'other' ? 'culture' : t
}

/** Toggle a type; the last enabled type cannot be turned off (7b). */
export function toggleType(f: EventFilter, t: FilterType): EventFilter {
  const on = f.types.includes(t)
  if (on && f.types.length === 1) return f
  const types = on ? f.types.filter(x => x !== t) : FILTER_TYPES.filter(x => x === t || f.types.includes(x))
  return { ...f, types }
}

export function toggleIn<T>(list: T[], value: T): T[] {
  return list.includes(value) ? list.filter(x => x !== value) : [...list, value]
}

// ── Genres ─────────────────────────────────────────────────────────────────

const umbrellaCache = new WeakMap<Hierarchy, Map<string, string[]>>()

/** Top-level genres of a genre: a genre without parents is its own umbrella;
 * otherwise the roots reached through all its parents (goregrind → metal, punk). */
export function umbrellasOf(genre: string, h: Hierarchy = GENRE_HIERARCHY): string[] {
  let cache = umbrellaCache.get(h)
  if (!cache) { cache = new Map(); umbrellaCache.set(h, cache) }
  const hit = cache.get(genre)
  if (hit) return hit
  const out = new Set<string>()
  const seen = new Set<string>()
  const walk = (g: string) => {
    if (seen.has(g)) return
    seen.add(g)
    const parents = h[g]
    if (!parents || parents.length === 0) { out.add(g); return }
    parents.forEach(walk)
  }
  walk(genre)
  const res = [...out]
  cache.set(genre, res)
  return res
}

/** Culture genres of an event (task 076): its genres whose direct parent is the
 * event's own culture subtype (`drama` in a film = `film:drama`). */
export function eventCultureGenres(e: Pick<Event, 'genres' | 'formats' | 'primary_format'>, h: Hierarchy = GENRE_HIERARCHY): string[] {
  const sub = cultureSubtype(e.formats, e.primary_format)
  if (!sub) return []
  const out = new Set<string>()
  for (const g of e.genres) if (h[g]?.includes(sub)) out.add(cultureGenreKey(sub, g))
  return [...out]
}

/** Culture genre keys that currently apply: culture on and their subtype selected. */
export function activeCultureGenres(f: EventFilter): string[] {
  if (!f.types.includes('culture')) return []
  return f.cultureGenres.filter(k => (f.subtypes as string[]).includes(splitCultureGenreKey(k)[0]))
}

/** Umbrella genres of an event that the filter offers (subtype umbrellas excluded). */
export function eventUmbrellas(e: Pick<Event, 'genres'>, h: Hierarchy = GENRE_HIERARCHY): string[] {
  const out = new Set<string>()
  for (const g of e.genres) for (const u of umbrellasOf(g, h)) if (!SUBTYPE_UMBRELLAS.has(u)) out.add(u)
  return [...out]
}

// ── Matching ───────────────────────────────────────────────────────────────

export interface FilterItem { event: Event; venue: Venue | undefined }

type Group = 'type' | 'genre' | 'character' | 'size' | 'free'

interface Prepared {
  item: FilterItem
  type: FilterType
  subtype: CultureSubtype | null
  /** Music umbrellas; only for concert, party, DJ (task 076) */
  umbrellas: string[]
  /** `subtype:genre` keys; only for culture */
  cultureGenres: string[]
  characters: string[]
  size: string | null
}

function prepare(item: FilterItem, h: Hierarchy): Prepared {
  const e = item.event
  const type = filterTypeOf(e)
  return {
    item,
    type,
    subtype: cultureSubtype(e.formats, e.primary_format),
    umbrellas: type === 'culture' ? [] : eventUmbrellas(e, h),
    cultureGenres: type === 'culture' ? eventCultureGenres(e, h) : [],
    characters: item.venue?.character ?? [],
    size: item.venue?.size ?? null,
  }
}

function passes(p: Prepared, f: EventFilter, g: Group): boolean {
  switch (g) {
    case 'type':
      if (!f.types.includes(p.type)) return false
      if (p.type === 'culture' && f.subtypes.length > 0) return p.subtype !== null && f.subtypes.includes(p.subtype)
      return true
    case 'genre': {
      // One OR group: music genres (concert/party/DJ) + active culture genres.
      const cg = activeCultureGenres(f)
      if (f.genres.length === 0 && cg.length === 0) return true
      return p.umbrellas.some(u => f.genres.includes(u)) || p.cultureGenres.some(k => cg.includes(k))
    }
    case 'character': return f.characters.length === 0 || p.characters.some(c => f.characters.includes(c))
    case 'size': return f.sizes.length === 0 || (p.size !== null && (f.sizes as string[]).includes(p.size))
    case 'free': return !f.free || p.item.event.free === true
  }
}

const GROUPS: Group[] = ['type', 'genre', 'character', 'size', 'free']

function passesExcept(p: Prepared, f: EventFilter, skip: Group | null): boolean {
  for (const g of GROUPS) if (g !== skip && !passes(p, f, g)) return false
  return true
}

/** Does one event pass the filter? */
export function matchesFilter(event: Event, venue: Venue | undefined, f: EventFilter, h: Hierarchy = GENRE_HIERARCHY): boolean {
  return passesExcept(prepare({ event, venue }, h), f, null)
}

export function isDefaultFilter(f: EventFilter): boolean {
  return f.types.length === FILTER_TYPES.length && f.subtypes.length === 0 && f.genres.length === 0 &&
    activeCultureGenres(f).length === 0 &&
    f.characters.length === 0 && f.sizes.length === 0 && !f.free
}

/** Badge on the Filter button: selected tags (subtypes, genres, culture genres
 * that apply, characters, sizes, free) + 1 when some types are off. 0 = no badge. */
export function filterBadgeCount(f: EventFilter): number {
  return f.subtypes.length + f.genres.length + activeCultureGenres(f).length + f.characters.length + f.sizes.length + (f.free ? 1 : 0) +
    (f.types.length < FILTER_TYPES.length ? 1 : 0)
}

// ── Counts ─────────────────────────────────────────────────────────────────

/** Map counts venues with a matching event, Akcie counts events. */
export type CountMode = 'events' | 'venues'

export interface FilterCounts {
  total: number
  types: Record<FilterType, number>
  subtypes: Record<string, number>
  genres: Map<string, number>
  /** By `subtype:genre` key */
  cultureGenres: Map<string, number>
  characters: Map<string, number>
  sizes: Record<string, number>
  free: number
}

/** Counts for the panel. The number at a chip is the number of results of that
 * chip under the other groups' current selection (what the chip contributes to
 * the OR within its group); `total` is the current result. Genres and
 * characters are counted for every value present in `items`. */
export function filterCounts(items: FilterItem[], f: EventFilter, mode: CountMode, h: Hierarchy = GENRE_HIERARCHY): FilterCounts {
  const prepared = items.map(it => prepare(it, h))
  const sets = new Map<string, Set<string>>()
  const add = (key: string, p: Prepared) => {
    let s = sets.get(key)
    if (!s) { s = new Set(); sets.set(key, s) }
    s.add(mode === 'venues' ? p.item.event.venue_id : p.item.event.id)
  }
  for (const p of prepared) {
    if (passesExcept(p, f, null)) add('total', p)
    if (passesExcept(p, f, 'type')) {
      const subOk = p.type !== 'culture' || f.subtypes.length === 0 || (p.subtype !== null && f.subtypes.includes(p.subtype))
      if (subOk) add(`t:${p.type}`, p)
      if (p.type === 'culture' && p.subtype) add(`s:${p.subtype}`, p)
    }
    if (passesExcept(p, f, 'genre')) {
      for (const u of p.umbrellas) add(`g:${u}`, p)
      for (const k of p.cultureGenres) add(`k:${k}`, p)
    }
    if (passesExcept(p, f, 'character')) for (const c of p.characters) add(`c:${c}`, p)
    if (passesExcept(p, f, 'size') && p.size) add(`z:${p.size}`, p)
    if (passesExcept(p, f, 'free') && p.item.event.free === true) add('free', p)
  }
  const n = (key: string) => sets.get(key)?.size ?? 0
  const byPrefix = (prefix: string) => {
    const m = new Map<string, number>()
    for (const [k, s] of sets) if (k.startsWith(prefix)) m.set(k.slice(prefix.length), s.size)
    return m
  }
  return {
    total: n('total'),
    types: { concert: n('t:concert'), party: n('t:party'), dj: n('t:dj'), culture: n('t:culture') },
    subtypes: Object.fromEntries(CULTURE_SUBTYPES.map(s => [s, n(`s:${s}`)])),
    genres: byPrefix('g:'),
    cultureGenres: byPrefix('k:'),
    characters: byPrefix('c:'),
    sizes: Object.fromEntries(VENUE_SIZES.map(s => [s, n(`z:${s}`)])),
    free: n('free'),
  }
}

/** Umbrella music genres offered in the panel: those with events of the enabled
 * music types (concert, party, DJ) in `events` (all loaded data, so a chip can
 * be chosen for another day), plus the selected ones. */
export function availableGenres(events: Event[], types: FilterType[], selected: string[], h: Hierarchy = GENRE_HIERARCHY): string[] {
  const out = new Set<string>()
  for (const e of events) {
    const t = filterTypeOf(e)
    if (t === 'culture' || !types.includes(t)) continue
    for (const u of eventUmbrellas(e, h)) out.add(u)
  }
  for (const g of selected) out.add(g)
  return [...out]
}

/** Culture genre rows (task 076): for each selected subtype (in subtype order)
 * that has genres in `events` or a selected one, its `subtype:genre` keys. */
export function availableCultureGenres(events: Event[], subtypes: CultureSubtype[], selected: string[], h: Hierarchy = GENRE_HIERARCHY): { subtype: CultureSubtype; keys: string[] }[] {
  const bySub = new Map<string, Set<string>>()
  const put = (k: string) => {
    const s = splitCultureGenreKey(k)[0]
    let set = bySub.get(s)
    if (!set) { set = new Set(); bySub.set(s, set) }
    set.add(k)
  }
  for (const e of events) for (const k of eventCultureGenres(e, h)) put(k)
  for (const k of selected) put(k)
  return CULTURE_SUBTYPES
    .filter(s => subtypes.includes(s) && (bySub.get(s)?.size ?? 0) > 0)
    .map(s => ({ subtype: s, keys: [...bySub.get(s)!] }))
}

/** Genre name of a `subtype:genre` key. */
export function cultureGenreName(key: string): string {
  return splitCultureGenreKey(key)[1]
}

/** Venue character tags offered in the panel (all venues with events) plus the selected ones. */
export function availableCharacters(venues: Venue[], selected: string[]): string[] {
  const out = new Set<string>()
  for (const v of venues) for (const c of v.character ?? []) out.add(c)
  for (const c of selected) out.add(c)
  return [...out]
}

/** Order by count (most first, 0 at the end), ties by name. Used once when the
 * panel opens; the order then stays while the user taps (7b). */
export function orderByCount(values: string[], counts: Map<string, number>): string[] {
  return [...values].sort((a, b) => (counts.get(b) ?? 0) - (counts.get(a) ?? 0) || a.localeCompare(b))
}

// ── Storage format ─────────────────────────────────────────────────────────

/** Parse a stored filter; anything invalid falls back to the default. */
export function parseFilter(raw: string | null): EventFilter {
  if (!raw) return DEFAULT_FILTER
  try {
    const o = JSON.parse(raw) as Partial<Record<keyof EventFilter, unknown>>
    const strs = (v: unknown): string[] => Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : []
    const types = strs(o.types).filter((t): t is FilterType => (FILTER_TYPES as readonly string[]).includes(t))
    return {
      types: types.length > 0 ? FILTER_TYPES.filter(t => types.includes(t)) : [...FILTER_TYPES],
      subtypes: strs(o.subtypes).filter((s): s is CultureSubtype => (CULTURE_SUBTYPES as readonly string[]).includes(s)),
      genres: strs(o.genres),
      cultureGenres: strs(o.cultureGenres).filter(k => {
        const [s, g] = splitCultureGenreKey(k)
        return (CULTURE_SUBTYPES as readonly string[]).includes(s) && g !== ''
      }),
      characters: strs(o.characters),
      sizes: strs(o.sizes).filter((s): s is VenueSize => (VENUE_SIZES as readonly string[]).includes(s)),
      free: o.free === true,
    }
  } catch { return DEFAULT_FILTER }
}

export function serializeFilter(f: EventFilter): string {
  return JSON.stringify(f)
}
