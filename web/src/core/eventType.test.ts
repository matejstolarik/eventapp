import { describe, it, expect } from 'vitest'
import { getEventType, eventTags, primaryTypeTag, eventIconKey } from './eventType'

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

describe('eventTags', () => {
  it('returns culture subtypes first, then genres', () => {
    expect(eventTags(['film'], ['jazz', 'classical'])).toEqual(['film', 'jazz', 'classical'])
    expect(eventTags(['talk', 'culture'], ['spoken-word'])).toEqual(['talk', 'spoken-word'])
  })

  it('excludes type formats (party, dj, concert, music)', () => {
    expect(eventTags(['concert'], ['techno', 'minimal'])).toEqual(['techno', 'minimal'])
    expect(eventTags(['party'], ['electronic'])).toEqual(['electronic'])
    expect(eventTags(['dj'], ['techno'])).toEqual(['techno'])
    expect(eventTags(['music'], ['jazz'])).toEqual(['jazz'])
  })

  it('fallback: returns event type string when list would be empty', () => {
    expect(eventTags(['concert'], [])).toEqual(['concert'])
    expect(eventTags(['party'], [])).toEqual(['party'])
    expect(eventTags(['dj'], [])).toEqual(['dj'])
    expect(eventTags([], [])).toEqual(['other'])
  })

  it('culture event without genres falls back to type string', () => {
    expect(eventTags(['film'], [])).toEqual(['film'])
    expect(eventTags(['theatre'], [])).toEqual(['theatre'])
  })

  it('multiple culture subtypes — all included', () => {
    expect(eventTags(['film', 'talk'], ['documentary'])).toEqual(['film', 'talk', 'documentary'])
  })
})

describe('eventIconKey', () => {
  it('party/dj/concert return own key', () => {
    expect(eventIconKey(['party'])).toBe('party')
    expect(eventIconKey(['dj'])).toBe('dj')
    expect(eventIconKey(['concert'])).toBe('concert')
    expect(eventIconKey(['music'])).toBe('concert')
  })

  it('type priority: party > dj > concert', () => {
    expect(eventIconKey(['party', 'film'])).toBe('party')
    expect(eventIconKey(['dj', 'film'])).toBe('dj')
    expect(eventIconKey(['concert', 'film'])).toBe('concert')
  })

  it('culture subtype: film → film', () => {
    expect(eventIconKey(['film'])).toBe('film')
    expect(eventIconKey(['theatre', 'film'])).toBe('film')
  })

  it('culture subtype: comedy → comedy', () => {
    expect(eventIconKey(['comedy'])).toBe('comedy')
  })

  it('culture subtype: dance → dance', () => {
    expect(eventIconKey(['dance'])).toBe('dance')
  })

  it('other culture subtypes → culture (masks)', () => {
    expect(eventIconKey(['theatre'])).toBe('culture')
    expect(eventIconKey(['talk'])).toBe('culture')
    expect(eventIconKey(['opening'])).toBe('culture')
    expect(eventIconKey(['workshop'])).toBe('culture')
    expect(eventIconKey(['quiz'])).toBe('culture')
  })

  it('other/unknown → culture (masks)', () => {
    expect(eventIconKey(['other'])).toBe('culture')
    expect(eventIconKey([])).toBe('culture')
    expect(eventIconKey(['unknown'])).toBe('culture')
  })

  it('film wins over comedy/dance when film appears first in formats', () => {
    expect(eventIconKey(['film', 'comedy'])).toBe('film')
  })

  it('comedy wins when no film', () => {
    expect(eventIconKey(['comedy', 'dance'])).toBe('comedy')
  })
})

describe('primaryTypeTag', () => {
  it('concert/party/dj returns type string', () => {
    expect(primaryTypeTag(['concert'])).toBe('concert')
    expect(primaryTypeTag(['party'])).toBe('party')
    expect(primaryTypeTag(['dj'])).toBe('dj')
    expect(primaryTypeTag(['music'])).toBe('concert')
  })

  it('culture returns first subtype', () => {
    expect(primaryTypeTag(['film'])).toBe('film')
    expect(primaryTypeTag(['talk', 'theatre'])).toBe('talk')
    expect(primaryTypeTag(['workshop'])).toBe('workshop')
  })

  it('other returns null', () => {
    expect(primaryTypeTag([])).toBeNull()
    expect(primaryTypeTag(['unknown'])).toBeNull()
  })

  it('concert/dj/party wins even with culture subtype in formats', () => {
    expect(primaryTypeTag(['concert', 'theatre'])).toBe('concert')
    expect(primaryTypeTag(['dj', 'film'])).toBe('dj')
  })
})
