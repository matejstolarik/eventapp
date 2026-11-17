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
