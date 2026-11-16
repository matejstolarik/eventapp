import { describe, it, expect } from 'vitest'
import { buildAndroidCalendarIntent } from './calendar'

const venue = {
  name: 'Cross Club',
  address: 'Plynární 1096/23, Praha 7',
  closing: null,
  character: [],
}

describe('buildAndroidCalendarIntent', () => {
  it('normal event produces valid intent URL', () => {
    const url = buildAndroidCalendarIntent(
      { title: 'Test Party', date: '2026-11-20', start_time: '20:00', end_time: '23:00', formats: ['party'] },
      venue,
      'https://example.com/event/1'
    )
    expect(url).toMatch(/^intent:#Intent;action=android\.intent\.action\.INSERT/)
    expect(url).toContain('type=vnd.android.cursor.item%2Fevent')
    expect(url).toContain('S.title=Test%20Party')
    expect(url).toContain('l.beginTime=')
    expect(url).toContain('l.endTime=')
    expect(url).toContain('S.eventLocation=Cross%20Club')
    expect(url).toContain(';end')
  })

  it('all-day event sets B.allDay=true', () => {
    const url = buildAndroidCalendarIntent(
      { title: 'Festival', date: '2026-11-20', start_time: null, end_time: null, formats: [] },
      venue,
      'https://example.com/event/2'
    )
    expect(url).toContain('B.allDay=true')
  })

  it('no venue: no eventLocation extra', () => {
    const url = buildAndroidCalendarIntent(
      { title: 'Show', date: '2026-11-20', start_time: '20:00', end_time: '22:00', formats: [] },
      undefined,
      'https://example.com/event/3'
    )
    expect(url).not.toContain('S.eventLocation')
  })

  it('end time after midnight yields end > begin', () => {
    const url = buildAndroidCalendarIntent(
      { title: 'Night Event', date: '2026-11-20', start_time: '22:00', end_time: '03:00', formats: ['party'] },
      venue,
      'https://example.com/event/4'
    )
    const beginMatch = url.match(/l\.beginTime=(\d+)/)
    const endMatch = url.match(/l\.endTime=(\d+)/)
    expect(beginMatch).not.toBeNull()
    expect(endMatch).not.toBeNull()
    expect(Number(endMatch![1])).toBeGreaterThan(Number(beginMatch![1]))
  })
})
