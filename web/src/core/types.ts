export interface Venue {
  id: string
  name: string
  city: string
  address: string
  lat: number
  lng: number
  web: string
  ra_url: string | null
  instagram: string | null
  facebook?: string | null
  type: string[]
  character: string[]
  music: string[]
  size: string
  capacity?: number | null
  features?: string[] | null
  /** own venue description (task 092): cs main, sk/en translations */
  descriptions?: Partial<Record<Language, string>> | null
  /** pages the description facts come from (not shown in the app) */
  description_sources?: string[] | null
  image_url: string | null
  image_source: string | null
  image_thumb: string | null
  /** 640x480 card, used when an event has no image (task 082) */
  image_card?: string | null
  /** uncropped, longer side <= 1200 px (task 082) */
  image_detail?: string | null
  /** [width, height] of image_detail in px (task 082) */
  image_detail_size?: [number, number] | null
  closing: Record<string, string> | null
  /** day of the venue's first programme load; its events from that day are not "new" (task 086) */
  first_loaded?: string | null
  /** a source of the venue is failing; hidden when it has no future event (task 092) */
  source_failing?: boolean
  sources: VenueSource[]
  active: boolean
  notes?: string | null
}

export interface VenueSource {
  type: string
  url: string
  section?: string
  detail_desc_selector?: string
  strategy?: string
}

export interface Price {
  min: number | null
  max: number | null
  currency: string | null
  kind: 'paid' | 'free' | 'voluntary' | 'free_reservation'
}

export interface Event {
  id: string
  venue_id: string
  title: string
  date: string
  start_time: string | null
  doors_time: string | null
  end_time: string | null
  formats: string[]
  /** Main part of the event from AI or commercial-club rule (task 053); decides the type */
  primary_format?: string | null
  genres: string[]
  character: string[]
  artists: string[]
  price_text: string | null
  /** Structured price (task 058); price_text is the source text and is not shown */
  price?: Price | null
  free: boolean | null
  sold_out: boolean | null
  room: string | null
  ticket_url: string | null
  image_url: string | null
  image_thumb: string | null
  /** Uncropped copy, longer side <= 1200 px (task 066); event page uses it (068) */
  image_detail?: string | null
  /** [width, height] of image_detail in px (task 069) */
  image_detail_size?: [number, number] | null
  description: string | null
  description_source: string | null
  /** AI description in three languages (task 054); cs is the main text */
  descriptions?: Partial<Record<Language, string>> | null
  /** Spotify artist profiles (task 054) */
  artist_links?: { name: string | null; spotify_url: string }[] | null
  sources: EventSource[]
  classification: { method: string; confidence: number } | null
  first_seen: string
  last_seen: string
  status: 'scheduled' | 'cancelled' | 'postponed' | 'gone'
  flags: string[]
}

export interface EventSource {
  type: string
  url: string
  external_id?: string | null
  section?: string | null
}

export interface EventsData {
  schema_version: number
  generated_at: string
  venues: Venue[]
  events: Event[]
}

export type EventType = 'party' | 'dj' | 'concert' | 'culture' | 'other'

export type Language = 'sk' | 'cs' | 'en'
