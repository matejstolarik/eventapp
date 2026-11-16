import { describe, it, expect } from 'vitest'
import { buildGoogleCalendarUrl } from './calendar'

const venue = {
  name: 'Cross Club',
  address: 'Plynární 1096/23, Praha 7',
  closing: null,
  character: [],
}

describe('buildGoogleCalendarUrl', () => {
  it('normal event with known end', () => {
    const url = buildGoogleCalendarUrl(
      { title: 'Test Party', date: '2026-11-20', start_time: '20:00', end_time: '23:00', formats: ['party'] },
      venue,
      'https://example.com/event/1'
    )
    expect(url).toContain('action=TEMPLATE')
    expect(url).toContain('text=Test+Party')
    expect(url).toContain('20261120T200000%2F20261120T230000')
    expect(url).toContain('ctz=Europe%2FPrague')
    expect(url).toContain('location=Cross+Club')
  })

  it('event crossing midnight (end < start)', () => {
    const url = buildGoogleCalendarUrl(
      { title: 'Night Event', date: '2026-11-20', start_time: '22:00', end_time: '03:00', formats: ['party'] },
      venue,
      'https://example.com/event/2'
    )
    // end should be next day: 20261121T030000
    expect(url).toContain('20261120T220000%2F20261121T030000')
  })

  it('all-day event (no start_time)', () => {
    const url = buildGoogleCalendarUrl(
      { title: 'Festival', date: '2026-11-20', start_time: null, end_time: null, formats: [] },
      venue,
      'https://example.com/event/3'
    )
    // all-day: YYYYMMDD/YYYYMMDD+1 (no time component in dates param)
    expect(url).toContain('20261120%2F20261121')
    expect(url).not.toMatch(/dates=\d{8}T/)
  })

  it('no end_time: uses computed end from eventEndsAt', () => {
    const url = buildGoogleCalendarUrl(
      { title: 'Concert', date: '2026-11-20', start_time: '20:00', end_time: null, formats: ['concert'] },
      { ...venue, character: [] },
      'https://example.com/event/4'
    )
    // concert with no end: start + 3h = 23:00
    expect(url).toContain('20261120T200000%2F20261120T230000')
  })

  it('no venue: empty location', () => {
    const url = buildGoogleCalendarUrl(
      { title: 'Show', date: '2026-11-20', start_time: '20:00', end_time: '22:00', formats: [] },
      undefined,
      'https://example.com/event/5'
    )
    expect(url).toContain('location=')
  })
})
