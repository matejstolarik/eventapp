import { describe, it, expect } from 'vitest'
import { getEventType } from './eventType'

describe('getEventType', () => {
  it('party wins over all others', () => {
    expect(getEventType(['dj', 'party'])).toBe('party')
    expect(getEventType(['concert', 'party'])).toBe('party')
    expect(getEventType(['party'])).toBe('party')
  })

  it('dj wins when no party', () => {
    expect(getEventType(['dj'])).toBe('dj')
    expect(getEventType(['dj', 'concert'])).toBe('dj')
  })

  it('concert wins over culture and other', () => {
    expect(getEventType(['concert'])).toBe('concert')
    expect(getEventType(['concert', 'theatre'])).toBe('concert')
  })

  it('music is treated as concert', () => {
    expect(getEventType(['music'])).toBe('concert')
    expect(getEventType(['music', 'theatre'])).toBe('concert')
  })

  it('culture formats', () => {
    expect(getEventType(['theatre'])).toBe('culture')
    expect(getEventType(['dance'])).toBe('culture')
    expect(getEventType(['talk'])).toBe('culture')
    expect(getEventType(['comedy'])).toBe('culture')
    expect(getEventType(['film'])).toBe('culture')
    expect(getEventType(['opening'])).toBe('culture')
    expect(getEventType(['workshop'])).toBe('culture')
    expect(getEventType(['quiz'])).toBe('culture')
  })

  it('other formats fall back to other', () => {
    expect(getEventType(['other'])).toBe('other')
    expect(getEventType([])).toBe('other')
    expect(getEventType(['unknown'])).toBe('other')
  })
})
