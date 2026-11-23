import { describe, it, expect } from 'vitest'
import { isVenueHidden } from './hiddenVenue'
import type { Event, Venue } from './types'

const v = (o: Partial<Venue> = {}) => ({ id: 'klub-007-strahov', ...o }) as Venue
const e = (date: string, venue_id = 'klub-007-strahov') => ({ venue_id, date }) as Event

describe('isVenueHidden (task 092)', () => {
  it('failing source without future events → hidden', () => {
    expect(isVenueHidden(v({ source_failing: true }), [e('2026-11-22')], '2026-11-23')).toBe(true)
  })
  it('failing source with a kept future event → shown', () => {
    expect(isVenueHidden(v({ source_failing: true }), [e('2026-11-23')], '2026-11-23')).toBe(false)
  })
  it('venue that only has no programme → shown', () => {
    expect(isVenueHidden(v(), [], '2026-11-23')).toBe(false)
  })
})
