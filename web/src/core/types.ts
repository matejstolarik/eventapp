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
  description: string | null
  description_url: string | null
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

export interface Event {
  id: string
  venue_id: string
  title: string
  date: string
  start_time: string | null
  doors_time: string | null
  end_time: string | null
  formats: string[]
  genres: string[]
  character: string[]
  artists: string[]
  price_text: string | null
  free: boolean | null
  sold_out: boolean | null
  room: string | null
  ticket_url: string | null
  image_url: string | null
  description: string | null
  description_source: string | null
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
