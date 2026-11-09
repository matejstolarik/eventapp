import { describe, it, expect } from 'vitest'
import { getToday, isTomorrow, isToday, getUpcomingDays } from './day'

describe('getToday', () => {
  it('returns current date when hour >= 5', () => {
    const d = new Date('2026-11-09T10:00:00')
    expect(getToday(d)).toBe('2026-11-09')
  })

  it('returns previous date when hour < 5 (before the 05:00 switch)', () => {
    const d = new Date('2026-11-09T01:00:00')
    expect(getToday(d)).toBe('2026-11-08')
  })

  it('returns current date at exactly 05:00', () => {
    const d = new Date('2026-11-09T05:00:00')
    expect(getToday(d)).toBe('2026-11-09')
  })

  it('still previous day at 04:59', () => {
    const d = new Date('2026-11-09T04:59:00')
    expect(getToday(d)).toBe('2026-11-08')
  })

  it('1:00 AM event belongs to previous day', () => {
    // An event at 2026-11-09 01:00 is conceptually still "yesterday night"
    const now = new Date('2026-11-09T01:00:00')
    expect(getToday(now)).toBe('2026-11-08')
  })
})

describe('isToday / isTomorrow', () => {
  const ref = new Date('2026-11-09T12:00:00')

  it('identifies today correctly', () => {
    expect(isToday('2026-11-09', ref)).toBe(true)
    expect(isToday('2026-11-08', ref)).toBe(false)
  })

  it('identifies tomorrow correctly', () => {
    expect(isTomorrow('2026-11-10', ref)).toBe(true)
    expect(isTomorrow('2026-11-09', ref)).toBe(false)
  })
})

describe('getUpcomingDays', () => {
  const ref = new Date('2026-11-09T12:00:00')

  it('returns N days starting from today', () => {
    const days = getUpcomingDays(3, ref)
    expect(days).toHaveLength(3)
    expect(days[0]).toBe('2026-11-09')
    expect(days[1]).toBe('2026-11-10')
    expect(days[2]).toBe('2026-11-11')
  })

  it('handles month boundary', () => {
    const d = new Date('2026-11-30T12:00:00')
    const days = getUpcomingDays(2, d)
    expect(days[0]).toBe('2026-11-30')
    expect(days[1]).toBe('2026-12-01')
  })
})
