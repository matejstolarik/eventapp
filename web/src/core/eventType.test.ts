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
    expect(getEventType(['stand-up'])).toBe('culture')
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
  it('hides culture subtypes carried by the icon, keeps performance and genres (task 071)', () => {
    expect(eventTags(['film'], ['jazz', 'classical'])).toEqual(['jazz', 'classical'])
    expect(eventTags(['talk', 'culture'], ['spoken-word'])).toEqual(['spoken-word'])
    expect(eventTags(['theatre', 'performance'], ['physical-theatre'])).toEqual(['performance', 'physical-theatre'])
    for (const f of ['film', 'stand-up', 'dance', 'theatre', 'talk', 'workshop', 'quiz', 'opening']) {
      expect(eventTags([f], [])).toEqual([])
    }
  })

  it('excludes type formats (party, dj, concert, music)', () => {
    expect(eventTags(['concert'], ['techno', 'minimal'])).toEqual(['techno', 'minimal'])
    expect(eventTags(['party'], ['electronic'])).toEqual(['electronic'])
    expect(eventTags(['dj'], ['techno'])).toEqual(['techno'])
    expect(eventTags(['music'], ['jazz'])).toEqual(['jazz'])
  })

  it('no fallback tag with the type name (task 071)', () => {
    expect(eventTags(['concert'], [])).toEqual([])
    expect(eventTags(['party'], [])).toEqual([])
    expect(eventTags([], [])).toEqual([])
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

  it('culture subtype: stand-up → standup (task 065)', () => {
    expect(eventIconKey(['stand-up'])).toBe('standup')
  })

  it('culture subtype: dance → dance', () => {
    expect(eventIconKey(['dance'])).toBe('dance')
  })

  it('new culture icons: talk, workshop, quiz, opening (task 071)', () => {
    expect(eventIconKey(['talk'])).toBe('talk')
    expect(eventIconKey(['workshop'])).toBe('workshop')
    expect(eventIconKey(['quiz'])).toBe('quiz')
    expect(eventIconKey(['opening'])).toBe('opening')
  })

  it('theatre and performance → culture (masks)', () => {
    expect(eventIconKey(['theatre'])).toBe('culture')
    expect(eventIconKey(['performance'])).toBe('culture')
  })

  it('order film → stand-up → dance → talk → workshop → quiz → opening → masks (task 071)', () => {
    expect(eventIconKey(['opening', 'quiz'])).toBe('quiz')
    expect(eventIconKey(['quiz', 'workshop'])).toBe('workshop')
    expect(eventIconKey(['workshop', 'talk'])).toBe('talk')
    expect(eventIconKey(['talk', 'dance'])).toBe('dance')
    expect(eventIconKey(['theatre', 'opening'])).toBe('opening')
  })

  it('culture primary_format decides the icon (task 071)', () => {
    expect(eventIconKey(['film', 'talk'], 'talk')).toBe('talk')
    expect(eventIconKey(['film', 'theatre'], 'theatre')).toBe('culture')
  })

  it('other/unknown → culture (masks)', () => {
    expect(eventIconKey(['other'])).toBe('culture')
    expect(eventIconKey([])).toBe('culture')
    expect(eventIconKey(['unknown'])).toBe('culture')
  })

  it('film wins over stand-up/dance when film appears first in formats', () => {
    expect(eventIconKey(['film', 'stand-up'])).toBe('film')
  })

  it('stand-up wins when no film', () => {
    expect(eventIconKey(['stand-up', 'dance'])).toBe('standup')
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

describe('getEventType with primary_format (task 053)', () => {
  it('primary_format decides between concert and dj', () => {
    expect(getEventType(['concert', 'dj'], 'concert')).toBe('concert')
    expect(getEventType(['concert', 'dj'], 'dj')).toBe('dj')
    expect(getEventType(['concert', 'dj', 'party'], 'concert')).toBe('concert')
  })
  it('primary_format party', () => {
    expect(getEventType(['dj', 'party'], 'party')).toBe('party')
  })
  it('falls back to priority without primary_format', () => {
    expect(getEventType(['concert', 'dj'], null)).toBe('dj')
    expect(getEventType(['concert', 'dj'], undefined)).toBe('dj')
  })
  it('ignores primary_format that is not among formats', () => {
    expect(getEventType(['concert', 'dj'], 'party')).toBe('dj')
  })
  it('culture primary_format', () => {
    expect(getEventType(['concert', 'film'], 'film')).toBe('culture')
  })
  it('icon and primary tag follow primary_format', () => {
    expect(eventIconKey(['concert', 'dj'], 'concert')).toBe('concert')
    expect(primaryTypeTag(['concert', 'dj'], 'concert')).toBe('concert')
    expect(eventTags(['concert', 'dj'], [], 'concert')).toEqual([])
  })
})

import { tagLabel } from '../i18n'
describe('tagLabel (task 071: always English)', () => {
  it('same English label in every app language', () => {
    for (const lang of ['sk', 'cs', 'en'] as const) {
      expect(tagLabel('talk', lang)).toBe('talk')
      expect(tagLabel('performance', lang)).toBe('performance')
      expect(tagLabel('stand-up', lang)).toBe('stand-up')
      expect(tagLabel('physical-theatre', lang)).toBe('physical theatre')
      expect(tagLabel('puppet-theatre', lang)).toBe('puppet theatre')
      expect(tagLabel('short', lang)).toBe('short film')
      expect(tagLabel('comedy', lang)).toBe('comedy')
    }
    expect(getEventType(['performance'])).toBe('culture')
  })
  it('keeps other codes', () => {
    expect(tagLabel('techno', 'cs')).toBe('techno')
    expect(tagLabel('alternative', 'sk')).toBe('alt')
  })
})
