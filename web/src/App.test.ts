import { describe, it, expect } from 'vitest'
import { parseHash } from './App'

describe('parseHash — tab navigation', () => {
  it('empty hash → map', () => {
    expect(parseHash('')).toEqual({ page: 'map' })
    expect(parseHash('#/')).toEqual({ page: 'map' })
    expect(parseHash('#')).toEqual({ page: 'map' })
  })

  it('map tab hash → map', () => {
    expect(parseHash('#/')).toEqual({ page: 'map' })
  })

  it('places tab hash → places', () => {
    expect(parseHash('#/miesta')).toEqual({ page: 'places' })
  })

  it('event overlay hash → event with id', () => {
    expect(parseHash('#/akcia/roxy-123')).toEqual({ page: 'event', eventId: 'roxy-123' })
  })

  it('venue overlay hash → venue with id', () => {
    expect(parseHash('#/miesto/cross-club')).toEqual({ page: 'venue', venueId: 'cross-club' })
  })

  // Tab transition: each tab from each other
  describe('tab transitions from map', () => {
    it('map → places', () => {
      expect(parseHash('#/miesta')).toMatchObject({ page: 'places' })
    })
    it('map → events (hash stays as map if no event hash)', () => {
      // events tab doesn't change hash — stays at map hash
      expect(parseHash('#/')).toMatchObject({ page: 'map' })
    })
    it('map → account (hash stays as map if no account hash)', () => {
      expect(parseHash('#/')).toMatchObject({ page: 'map' })
    })
  })

  describe('tab transitions from places', () => {
    it('places → map', () => {
      expect(parseHash('#/')).toMatchObject({ page: 'map' })
    })
    it('places → events', () => {
      expect(parseHash('#/')).toMatchObject({ page: 'map' }) // events doesn't set a unique hash
    })
    it('places → account', () => {
      expect(parseHash('#/')).toMatchObject({ page: 'map' }) // account doesn't set a unique hash
    })
  })

  describe('overlay routes do not affect tabs', () => {
    it('event overlay keeps page="event"', () => {
      const r = parseHash('#/akcia/some-event-id')
      expect(r.page).toBe('event')
    })
    it('venue overlay keeps page="venue"', () => {
      const r = parseHash('#/miesto/kasarna-karlin')
      expect(r.page).toBe('venue')
    })
    it('unknown hash → map fallback', () => {
      expect(parseHash('#/unknown-path')).toEqual({ page: 'map' })
    })
  })
})
