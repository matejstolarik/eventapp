import { describe, it, expect } from 'vitest'
import { thumbCandidates, heroCandidates, pickImage } from './eventImage'

const venueImg = { image_card: 'img/venues/card/v.jpg', image_detail: 'img/venues/detail/v.jpg', image_detail_size: [1200, 800] as [number, number] }
const noVenueImg = { image_card: null, image_detail: null, image_detail_size: null }

describe('task 082: venue image as fallback', () => {
  it('event without image + venue with image -> venue image', () => {
    expect(pickImage(thumbCandidates({ image_thumb: null }, venueImg), 0)).toBe('img/venues/card/v.jpg')
  })
  it('event image first', () => {
    expect(pickImage(thumbCandidates({ image_thumb: 'img/events/e.jpg' }, venueImg), 0)).toBe('img/events/e.jpg')
  })
  it('venue without image -> type icon (null)', () => {
    expect(pickImage(thumbCandidates({ image_thumb: null }, noVenueImg), 0)).toBeNull()
    expect(pickImage(thumbCandidates({ image_thumb: null }, undefined), 0)).toBeNull()
  })
  it('load error: event -> venue -> type icon', () => {
    const c = thumbCandidates({ image_thumb: 'img/events/e.jpg' }, venueImg)
    expect(pickImage(c, 1)).toBe('img/venues/card/v.jpg')
    expect(pickImage(c, 2)).toBeNull()
  })
  it('event page: venue image has its own size and no poster button', () => {
    const c = heroCandidates({ image_detail: null, image_detail_size: null, image_url: null }, venueImg)
    expect(c).toEqual([{ src: 'img/venues/detail/v.jpg', size: [1200, 800], poster: false }])
  })
  it('event page: event image with poster, then venue after errors, then icon', () => {
    const c = heroCandidates({ image_detail: 'img/events/detail/e.jpg', image_detail_size: [600, 900], image_url: 'https://x/e.jpg' }, venueImg)
    expect(c.map(x => x.poster)).toEqual([true, true, false])
    expect(c[1].size).toEqual([600, 900])
    expect(pickImage(c, 2)?.src).toBe('img/venues/detail/v.jpg')
    expect(pickImage(c, 3)).toBeNull()
  })
})
