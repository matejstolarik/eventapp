import { describe, it, expect } from 'vitest'
import { preferenceGenres, togglePrefGenre, togglePrefType, hasMusicType } from './preferences'
import { shouldShowOnboarding, parsePreferences, EMPTY_PREFERENCES, MAX_PREF_GENRES } from './store'
import type { Event } from './types'

const ev = (formats: string[], genres: string[]): Event => ({ formats, genres } as unknown as Event)

describe('shouldShowOnboarding', () => {
  const store = (o: Record<string, string>) => (k: string) => o[k] ?? null
  it('new install → yes', () => expect(shouldShowOnboarding(store({}))).toBe(true))
  it('done flag → no', () => expect(shouldShowOnboarding(store({ onboardingDone: '1' }))).toBe(false))
  it('started but not finished → yes again', () =>
    expect(shouldShowOnboarding(store({ onboardingPending: '1', filter: '{}', eventsLastFetched: '1' }))).toBe(true))
  it.each(['favorites', 'going', 'filter', 'eventsPeriod', 'eventsFilters', 'language', 'eventsLastFetched'])(
    'existing user with %s → no', k => expect(shouldShowOnboarding(store({ [k]: '[]' }))).toBe(false))
})

describe('preferenceGenres', () => {
  it('music umbrellas with events, by count, without culture', () => {
    const events = [
      ev(['dj'], ['techno']), ev(['dj'], ['techno']), ev(['concert'], ['post-punk']),
      ev(['film'], ['horror']), ev(['film'], ['drama']), ev(['film'], ['drama']), ev(['film'], ['drama']),
    ]
    const g = preferenceGenres(events)
    expect(g[0]).toBe('techno')
    expect(g).toContain('punk')
    expect(g).not.toContain('drama')
    expect(g).not.toContain('horror')
    expect(g).not.toContain('film')
  })
})

describe('preference toggles', () => {
  it('genre limit 5', () => {
    let p = EMPTY_PREFERENCES
    for (const g of ['a', 'b', 'c', 'd', 'e', 'f']) p = togglePrefGenre(p, g)
    expect(p.genres).toHaveLength(MAX_PREF_GENRES)
    expect(p.genres).not.toContain('f')
    p = togglePrefGenre(p, 'a')
    expect(p.genres).toHaveLength(4)
  })
  it('culture off clears subtypes', () => {
    const p = togglePrefType({ types: ['culture'], subtypes: ['film'], genres: [] }, 'culture')
    expect(p).toEqual({ types: [], subtypes: [], genres: [] })
  })
  it('genres step only with a music type', () => {
    expect(hasMusicType({ types: ['culture'], subtypes: [], genres: [] })).toBe(false)
    expect(hasMusicType({ types: ['dj'], subtypes: [], genres: [] })).toBe(true)
  })
  it('parse drops junk and caps genres', () => {
    expect(parsePreferences('{"types":["dj","x"],"subtypes":["film","y"],"genres":["a","b","c","d","e","f"]}'))
      .toEqual({ types: ['dj'], subtypes: ['film'], genres: ['a', 'b', 'c', 'd', 'e'] })
    expect(parsePreferences('nope')).toEqual(EMPTY_PREFERENCES)
  })
})
