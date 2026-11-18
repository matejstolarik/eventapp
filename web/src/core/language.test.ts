import { describe, it, expect } from 'vitest'
import { pickLanguage } from './store'
import { formatDateDMY } from './dot'

describe('pickLanguage (task 072)', () => {
  it('takes the first of cs / sk / en from the whole list, in order', () => {
    expect(pickLanguage(['de-DE', 'cs-CZ'])).toBe('cs')
    expect(pickLanguage(['de', 'sk-SK'])).toBe('sk')
    expect(pickLanguage(['en-US', 'cs-CZ'])).toBe('en')
  })
  it('falls back to English', () => {
    expect(pickLanguage(['de'])).toBe('en')
    expect(pickLanguage([])).toBe('en')
  })
})

describe('formatDateDMY (task 072)', () => {
  it('shows day. month. year', () => {
    expect(formatDateDMY('2026-11-21')).toBe('21. 11. 2026')
    expect(formatDateDMY('2026-12-05')).toBe('5. 12. 2026')
  })
})
