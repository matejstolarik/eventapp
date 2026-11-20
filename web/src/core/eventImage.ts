// Task 082: image of an event with the venue image as fallback.
// Order: event image -> venue image -> (no candidate left) type icon.
// The data stays as it is (event image_url null); the app does the fallback.
import type { Event, Venue } from './types'

type VenueImages = Pick<Venue, 'image_card' | 'image_detail' | 'image_detail_size'>

/** Thumbnail candidates (4:3 cards, rows, small squares): event image_thumb, venue image_card. */
export function thumbCandidates(event: Pick<Event, 'image_thumb'>, venue?: Partial<VenueImages> | null): string[] {
  return [event.image_thumb, venue?.image_card].filter((x): x is string => !!x)
}

export interface HeroImage {
  src: string
  /** [w, h] reserving the box before load, or null */
  size: [number, number] | null
  /** false for the venue image: no "Plagát" (zoom) button */
  poster: boolean
}

/** Event page image candidates: event image_detail, event image_url, venue image_detail. */
export function heroCandidates(
  event: Pick<Event, 'image_detail' | 'image_detail_size' | 'image_url'>,
  venue?: Partial<VenueImages> | null,
): HeroImage[] {
  const out: HeroImage[] = []
  // image_detail is an uncropped resize of image_url, so its size also reserves
  // the box for the image_url fallback (task 069 / 5cd07ad)
  const evSize = event.image_detail && event.image_detail_size ? event.image_detail_size : null
  if (event.image_detail) out.push({ src: event.image_detail, size: evSize, poster: true })
  if (event.image_url) out.push({ src: event.image_url, size: evSize, poster: true })
  if (venue?.image_detail) out.push({ src: venue.image_detail, size: venue.image_detail_size ?? null, poster: false })
  return out
}

/** Candidate shown after `errors` failed loads, or null (= type icon). */
export function pickImage<T>(candidates: T[], errors: number): T | null {
  return candidates[errors] ?? null
}
