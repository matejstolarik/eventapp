import { describe, it, expect } from 'vitest'
import { haversine, formatDistance } from './distance'

describe('haversine', () => {
  it('returns near-zero for same point', () => {
    expect(haversine(50.088, 14.42, 50.088, 14.42)).toBeCloseTo(0, 3)
  })

  it('gives ~1.4 km between Cross Club and Fuchs2 (approximate)', () => {
    // Cross Club: 50.1083, 14.4432
    // Fuchs2 Štvanice area: ~50.1000, 14.4600
    const d = haversine(50.1083, 14.4432, 50.100, 14.460)
    expect(d).toBeGreaterThan(0.5)
    expect(d).toBeLessThan(3)
  })

  it('1 km is roughly 0.009 lat degrees', () => {
    const d = haversine(50.0, 14.4, 50.009, 14.4)
    expect(d).toBeCloseTo(1.0, 0)
  })
})

describe('formatDistance', () => {
  it('shows meters for < 1 km', () => {
    expect(formatDistance(0.3, 'sk')).toBe('300 m')
    expect(formatDistance(0.75, 'en')).toBe('750 m')
  })

  it('shows km with comma for SK/CS', () => {
    expect(formatDistance(1.2, 'sk')).toBe('1,2 km')
    expect(formatDistance(2.5, 'cs')).toBe('2,5 km')
  })

  it('shows km with dot for EN', () => {
    expect(formatDistance(1.2, 'en')).toBe('1.2 km')
  })
})
