import { describe, it, expect } from 'vitest'
import { eventDescription, spotifyUrl } from './eventText'

describe('eventDescription (task 054)', () => {
  const ev = { description: 'Původní popis', descriptions: { cs: 'Český', sk: 'Slovenský', en: 'English' } }
  it('uses the app language', () => {
    expect(eventDescription(ev, 'sk')).toBe('Slovenský')
    expect(eventDescription(ev, 'en')).toBe('English')
  })
  it('falls back to Czech, then the source description', () => {
    expect(eventDescription({ description: 'P', descriptions: { cs: 'Č' } }, 'en')).toBe('Č')
    expect(eventDescription({ description: 'P', descriptions: null }, 'sk')).toBe('P')
    expect(eventDescription({ description: null }, 'cs')).toBeNull()
  })
})

describe('spotifyUrl (task 054)', () => {
  it('opens the artist profile from artist_links', () => {
    const url = 'https://open.spotify.com/artist/5yOvAmpIR7hVxiS6Ls5DPO'
    expect(spotifyUrl({ title: 'Omah Lay', artists: ['Omah Lay'], artist_links: [{ name: 'Omah Lay', spotify_url: url }] })).toBe(url)
  })
  it('falls back to search', () => {
    expect(spotifyUrl({ title: 'Akce X', artists: [], artist_links: null })).toBe('https://open.spotify.com/search/Akce%20X')
    expect(spotifyUrl({ title: 'T', artists: ['Allt'] })).toBe('https://open.spotify.com/search/Allt')
  })
})

import { priceLabel } from './eventText'
describe('priceLabel (task 058)', () => {
  const P = (min: number | null, max: number | null, currency: string | null = 'CZK', kind: 'paid' | 'free' | 'voluntary' | 'free_reservation' = 'paid') =>
    ({ price: { min, max, currency, kind }, free: null })
  it('formats amounts per language', () => {
    expect(priceLabel(P(350, 350), 'cs')).toBe('350 Kč')
    expect(priceLabel(P(250, 350), 'sk')).toBe('250–350 Kč')
    expect(priceLabel(P(950, null), 'cs')).toBe('od 950 Kč')
    expect(priceLabel(P(950, null), 'en')).toBe('from 950 CZK')
    expect(priceLabel(P(20, 20, 'EUR'), 'en')).toBe('20 €')
    expect(priceLabel(P(250, 599, null), 'cs')).toBe('250–599')
  })
  it('free kinds', () => {
    expect(priceLabel(P(null, null, null, 'free'), 'sk')).toBe('Zdarma')
    expect(priceLabel(P(null, null, null, 'free'), 'en')).toBe('Free')
    expect(priceLabel(P(null, null, null, 'voluntary'), 'sk')).toBe('Dobrovoľné vstupné')
    expect(priceLabel(P(null, null, null, 'voluntary'), 'cs')).toBe('Dobrovolné vstupné')
    expect(priceLabel(P(null, null, null, 'voluntary'), 'en')).toBe('Pay what you want')
    expect(priceLabel(P(null, null, null, 'free_reservation'), 'sk')).toBe('Zdarma, rezervácia')
    expect(priceLabel(P(null, null, null, 'free_reservation'), 'cs')).toBe('Zdarma, rezervace')
    expect(priceLabel(P(null, null, null, 'free_reservation'), 'en')).toBe('Free, booking required')
    expect(priceLabel({ price: null, free: null }, 'cs')).toBeNull()
  })
})
