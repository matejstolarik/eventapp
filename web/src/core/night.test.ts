import { describe, it, expect } from 'vitest'
import { isNightTime, isNightEvent } from './night'

describe('isNightTime', () => {
  it('true at 1:30 AM', () => expect(isNightTime(new Date('2026-11-10T01:30:00'))).toBe(true))
  it('true at 4:59 AM', () => expect(isNightTime(new Date('2026-11-10T04:59:00'))).toBe(true))
  it('false at 5:00 AM', () => expect(isNightTime(new Date('2026-11-10T05:00:00'))).toBe(false))
  it('false at noon', () => expect(isNightTime(new Date('2026-11-10T12:00:00'))).toBe(false))
})

describe('isNightEvent', () => {
  const now130 = new Date('2026-11-10T01:30:00')

  it('concert 20:00 without end → no', () => {
    expect(isNightEvent(
      { date: '2026-11-09', start_time: '20:00', end_time: null, formats: ['concert'] },
      ['alternative'],
      now130
    )).toBe(false)
  })

  it('dj 23:00 without end in late-night venue (Fuchs2) → yes', () => {
    expect(isNightEvent(
      { date: '2026-11-09', start_time: '23:00', end_time: null, formats: ['dj'] },
      ['alternative', 'underground', 'queer-friendly', 'late-night'],
      now130
    )).toBe(true)
  })

  it('dj 23:00 without end (no late-night venue) → yes (party/dj type is enough)', () => {
    expect(isNightEvent(
      { date: '2026-11-09', start_time: '23:00', end_time: null, formats: ['dj'] },
      ['alternative'],
      now130
    )).toBe(true)
  })

  it('event 22:00–5:00 spanning midnight → yes', () => {
    expect(isNightEvent(
      { date: '2026-11-09', start_time: '22:00', end_time: '05:00', formats: ['party', 'dj'] },
      ['late-night'],
      now130
    )).toBe(true)
  })

  it('event 22:00–1:00 already ended at 1:30 → no', () => {
    expect(isNightEvent(
      { date: '2026-11-09', start_time: '22:00', end_time: '01:00', formats: ['party', 'dj'] },
      ['late-night'],
      now130
    )).toBe(false)
  })

  it('concert without start_time, without end → no', () => {
    expect(isNightEvent(
      { date: '2026-11-09', start_time: null, end_time: null, formats: ['concert'] },
      [],
      now130
    )).toBe(false)
  })

  it('dj without start_time → no (cannot verify ≥20:00)', () => {
    expect(isNightEvent(
      { date: '2026-11-09', start_time: null, end_time: null, formats: ['dj'] },
      [],
      now130
    )).toBe(false)
  })

  it('at 4:59: event 22:00–5:00 → yes (not yet ended)', () => {
    const now459 = new Date('2026-11-10T04:59:00')
    expect(isNightEvent(
      { date: '2026-11-09', start_time: '22:00', end_time: '05:00', formats: ['party'] },
      ['late-night'],
      now459
    )).toBe(true)
  })

  it('at 5:00: event 22:00–5:00 → no (ended exactly at 5:00)', () => {
    const now500 = new Date('2026-11-10T05:00:00')
    expect(isNightEvent(
      { date: '2026-11-09', start_time: '22:00', end_time: '05:00', formats: ['party'] },
      ['late-night'],
      now500
    )).toBe(false)
  })
})
