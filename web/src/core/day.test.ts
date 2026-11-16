import { describe, it, expect } from 'vitest'
import { getToday, getYesterday, isTomorrow, isToday, getUpcomingDays } from './day'

describe('getToday', () => {
  it('returns current calendar date at noon', () => {
    const d = new Date('2026-11-09T10:00:00')
    expect(getToday(d)).toBe('2026-11-09')
  })

  it('returns current calendar date at 1:00 AM (midnight boundary, not 05:00)', () => {
    // Changed 2026-11-16: previously returned 2026-11-08 at 01:00, now returns 2026-11-09
    const d = new Date('2026-11-09T01:00:00')
    expect(getToday(d)).toBe('2026-11-09')
  })

  it('returns current calendar date at midnight', () => {
    const d = new Date('2026-11-09T00:00:00')
    expect(getToday(d)).toBe('2026-11-09')
  })

  it('returns current calendar date at 04:59', () => {
    const d = new Date('2026-11-09T04:59:00')
    expect(getToday(d)).toBe('2026-11-09')
  })
})

describe('getYesterday', () => {
  it('returns previous calendar day at noon', () => {
    expect(getYesterday(new Date('2026-11-09T12:00:00'))).toBe('2026-11-08')
  })

  it('returns previous calendar day at 1:00 AM', () => {
    expect(getYesterday(new Date('2026-11-09T01:00:00'))).toBe('2026-11-08')
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
