import { describe, it, expect } from 'vitest'
import { getPeriodRange, getEventsForPeriod, formatPeriodShortLabel, formatPeriodRangeText } from './period'
import type { Event } from './types'

// Sunday 2026-11-15 18:00 (after 5am → "today" = 2026-11-15)
const SUN = new Date('2026-11-15T18:00:00')
// Monday 2026-11-16 10:00
const MON = new Date('2026-11-16T10:00:00')
// Friday 2026-11-20 20:00
const FRI = new Date('2026-11-20T20:00:00')
// Saturday 2026-11-21 20:00
const SAT = new Date('2026-11-21T20:00:00')
// Sunday at 1:30 (before 5am → "today" = 2026-11-15)
const SUN_NIGHT = new Date('2026-11-15T01:30:00')

const SK_DAYS = ['Ne', 'Po', 'Ut', 'St', 'Št', 'Pi', 'So'] as const

describe('getPeriodRange', () => {
  it('today', () => {
    expect(getPeriodRange({ type: 'today' }, SUN)).toEqual({ from: '2026-11-15', to: '2026-11-15' })
  })

  it('tomorrow', () => {
    expect(getPeriodRange({ type: 'tomorrow' }, SUN)).toEqual({ from: '2026-11-16', to: '2026-11-16' })
  })

  it('weekend on Sunday → today until this Sunday', () => {
    const r = getPeriodRange({ type: 'weekend' }, SUN)
    expect(r.from).toBe('2026-11-15')
    expect(r.to).toBe('2026-11-15')  // Sunday is both start and end
  })

  it('weekend on Saturday → today until Sunday', () => {
    const r = getPeriodRange({ type: 'weekend' }, SAT)
    expect(r.from).toBe('2026-11-21')  // today=Sat
    expect(r.to).toBe('2026-11-22')   // Sunday
  })

  it('weekend on Friday → today until Sunday', () => {
    const r = getPeriodRange({ type: 'weekend' }, FRI)
    expect(r.from).toBe('2026-11-20')  // today=Fri
    expect(r.to).toBe('2026-11-22')   // Sunday
  })

  it('weekend on Monday → next Fri–Sun', () => {
    const r = getPeriodRange({ type: 'weekend' }, MON)
    // Mon 16 Nov → Fri 20 – Sun 22 Nov
    expect(r.from).toBe('2026-11-20')
    expect(r.to).toBe('2026-11-22')
  })

  it('next7 from Sunday', () => {
    const r = getPeriodRange({ type: 'next7' }, SUN)
    expect(r.from).toBe('2026-11-15')
    expect(r.to).toBe('2026-11-21')
  })

  it('next30 from Sunday', () => {
    const r = getPeriodRange({ type: 'next30' }, SUN)
    expect(r.from).toBe('2026-11-15')
    expect(r.to).toBe('2026-12-14')
  })

  it('anytime', () => {
    const r = getPeriodRange({ type: 'anytime' }, SUN)
    expect(r.from).toBe('2026-11-15')
    expect(r.to).toBeNull()
  })

  it('custom', () => {
    const r = getPeriodRange({ type: 'custom', from: '2026-11-20', to: '2026-11-24' }, SUN)
    expect(r).toEqual({ from: '2026-11-20', to: '2026-11-24' })
  })

  it('today at 1:30 night → today = 2026-11-15 (calendar midnight, not 05:00)', () => {
    const r = getPeriodRange({ type: 'today' }, SUN_NIGHT)
    // Calendar midnight boundary: 01:30 on Nov 15 → today = Nov 15
    expect(r.from).toBe('2026-11-15')
    expect(r.to).toBe('2026-11-15')
  })
})

describe('getEventsForPeriod', () => {
  const makeEvent = (id: string, date: string, start_time: string | null = null, end_time: string | null = null, status: 'scheduled' | 'cancelled' | 'gone' = 'scheduled'): Event => ({
    id, venue_id: 'v1', title: id, date, start_time, end_time, doors_time: null,
    formats: [], genres: [], character: [], artists: [],
    price_text: null, free: null, sold_out: null, room: null,
    ticket_url: null, image_url: null, image_thumb: null,
    description: null, description_source: null,
    sources: [], classification: null,
    first_seen: date, last_seen: date,
    status, flags: []
  })

  it('filters cancelled and gone', () => {
    const events = [
      makeEvent('ok', '2026-11-15'),
      makeEvent('cancelled', '2026-11-15', null, null, 'cancelled'),
      makeEvent('gone', '2026-11-15', null, null, 'gone'),
    ]
    const result = getEventsForPeriod(events, { type: 'today' }, SUN)
    expect(result.map(e => e.id)).toEqual(['ok'])
  })

  it('filters finished events on today', () => {
    // Event that ended at 17:00, now is 18:00
    const events = [
      makeEvent('finished', '2026-11-15', '15:00', '17:00'),
      makeEvent('ok', '2026-11-15', '20:00'),
    ]
    const result = getEventsForPeriod(events, { type: 'today' }, SUN)
    expect(result.map(e => e.id)).toEqual(['ok'])
  })

  it('includes all days in next7', () => {
    const events = [
      makeEvent('d0', '2026-11-15'),
      makeEvent('d6', '2026-11-21'),
      makeEvent('d7', '2026-11-22'),  // outside range
    ]
    const result = getEventsForPeriod(events, { type: 'next7' }, SUN)
    expect(result.map(e => e.id)).toEqual(['d0', 'd6'])
  })

  it('anytime has no upper bound', () => {
    const events = [
      makeEvent('d0', '2026-11-15'),
      makeEvent('d100', '2027-02-23'),
    ]
    const result = getEventsForPeriod(events, { type: 'anytime' }, SUN)
    expect(result.map(e => e.id)).toEqual(['d0', 'd100'])
  })
})

describe('formatPeriodShortLabel', () => {
  it('today sk', () => expect(formatPeriodShortLabel({ type: 'today' }, 'sk')).toBe('Dnes'))
  it('weekend cs', () => expect(formatPeriodShortLabel({ type: 'weekend' }, 'cs')).toBe('Víkend'))
  it('next7 en', () => expect(formatPeriodShortLabel({ type: 'next7' }, 'en')).toBe('7 days'))
  it('anytime sk', () => expect(formatPeriodShortLabel({ type: 'anytime' }, 'sk')).toBe('Kedykoľvek'))
  it('custom same month', () => {
    expect(formatPeriodShortLabel({ type: 'custom', from: '2026-11-20', to: '2026-11-24' }, 'sk')).toBe('20.–24. 11.')
  })
  it('custom diff month', () => {
    expect(formatPeriodShortLabel({ type: 'custom', from: '2026-11-28', to: '2026-12-02' }, 'sk')).toBe('28. 11.–2. 12.')
  })
})

describe('formatPeriodRangeText', () => {
  it('today sk → "Ne 15. 11."', () => {
    expect(formatPeriodRangeText({ type: 'today' }, 'sk', SK_DAYS, SUN)).toBe('Ne 15. 11.')
  })
  it('tomorrow sk → "Po 16. 11."', () => {
    expect(formatPeriodRangeText({ type: 'tomorrow' }, 'sk', SK_DAYS, SUN)).toBe('Po 16. 11.')
  })
  it('weekend on Monday sk → "Pi 20.–Ne 22. 11."', () => {
    expect(formatPeriodRangeText({ type: 'weekend' }, 'sk', SK_DAYS, MON)).toBe('Pi 20.–Ne 22. 11.')
  })
  it('next7 sk → "15.–21. 11."', () => {
    expect(formatPeriodRangeText({ type: 'next7' }, 'sk', SK_DAYS, SUN)).toBe('15.–21. 11.')
  })
  it('next30 sk → "15. 11.–14. 12."', () => {
    expect(formatPeriodRangeText({ type: 'next30' }, 'sk', SK_DAYS, SUN)).toBe('15. 11.–14. 12.')
  })
  it('anytime → ""', () => {
    expect(formatPeriodRangeText({ type: 'anytime' }, 'sk', SK_DAYS, SUN)).toBe('')
  })
})
