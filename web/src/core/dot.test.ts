import { describe, it, expect } from 'vitest'
import { joinDot, DOT_SEP } from './dot'

describe('joinDot (task 069)', () => {
  it('puts one plain space before and after the dot', () => {
    expect(DOT_SEP).toBe(' · ')
    expect(joinDot(['Dnes', '20:00', 'Archa+'])).toBe('Dnes · 20:00 · Archa+')
  })
  it('skips empty parts without doubled separators', () => {
    expect(joinDot(['Dnes', null, '', 'Archa+'])).toBe('Dnes · Archa+')
    expect(joinDot([undefined, '20:00', false])).toBe('20:00')
    expect(joinDot([])).toBe('')
  })
})
