import { describe, it, expect } from 'vitest'
import { parseHash, tabOfRoute } from './App'
import { TAB_ORDER } from './components/BottomNav'

describe('parseHash — tab navigation (task 079: Akcie first)', () => {
  it('empty hash → events (start page)', () => {
    expect(parseHash('')).toEqual({ page: 'events' })
    expect(parseHash('#/')).toEqual({ page: 'events' })
    expect(parseHash('#')).toEqual({ page: 'events' })
  })

  it('map has its own hash', () => {
    expect(parseHash('#/mapa')).toEqual({ page: 'map' })
  })

  it('old events hash still works', () => {
    expect(parseHash('#/akcie')).toEqual({ page: 'events' })
  })

  it('places tab hash → places', () => {
    expect(parseHash('#/miesta')).toEqual({ page: 'places' })
  })

  it('account tab hash → account', () => {
    expect(parseHash('#/ucet')).toEqual({ page: 'account' })
  })

  it('preferences overlay', () => {
    expect(parseHash('#/preferencie')).toEqual({ page: 'preferences' })
    expect(tabOfRoute({ page: 'preferences' })).toBe('account')
  })

  it('event overlay hash → event with id', () => {
    expect(parseHash('#/akcia/roxy-123')).toEqual({ page: 'event', eventId: 'roxy-123' })
  })

  it('venue overlay hash → venue with id', () => {
    expect(parseHash('#/miesto/cross-club')).toEqual({ page: 'venue', venueId: 'cross-club' })
  })

  it('unknown hash → events fallback', () => {
    expect(parseHash('#/unknown-path')).toEqual({ page: 'events' })
  })

  it('start tab is events; deep links open events tab underneath', () => {
    expect(tabOfRoute(parseHash(''))).toBe('events')
    expect(tabOfRoute(parseHash('#/akcia/x'))).toBe('events')
    expect(tabOfRoute(parseHash('#/mapa'))).toBe('map')
  })
})

describe('bottom nav order (task 079)', () => {
  it('Akcie, Mapa, Miesta, Môj účet', () => {
    expect(TAB_ORDER).toEqual(['events', 'map', 'places', 'account'])
  })
})
