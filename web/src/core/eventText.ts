import type { Event, Language } from './types'
import { getDict } from '../i18n'

/** Description shown in the app (task 054): AI text in the app language,
 *  then Czech AI text, then the original description from the source. */
export function eventDescription(ev: Pick<Event, 'descriptions' | 'description'>, lang: Language): string | null {
  const d = ev.descriptions
  return d?.[lang] || d?.cs || ev.description || null
}

/** Spotify button target (design.md part 7): the first artist profile from
 *  artist_links, otherwise a Spotify search for the first artist / title. */
export function spotifyUrl(ev: Pick<Event, 'artist_links' | 'artists' | 'title'>): string {
  const link = ev.artist_links?.find(a => a.spotify_url)?.spotify_url
  if (link) return link
  const query = ev.artists?.[0] ?? ev.title
  return `https://open.spotify.com/search/${encodeURIComponent(query)}`
}

/** Price shown in the app (task 058 part 4): from the structured `price`,
 *  in the app language, without any other text: "350 Kč", "250–350 Kč",
 *  "od 950 Kč" / "from 950 CZK", "20 €", Zdarma, Dobrovolné vstupné,
 *  Zdarma, rezervace.  No `price` -> "free" label if `free`, else null. */
export function priceLabel(ev: Pick<Event, 'price' | 'free'>, lang: Language): string | null {
  const t = getDict(lang).price
  const p = ev.price
  if (!p) return ev.free ? t.free : null
  if (p.kind === 'free') return t.free
  if (p.kind === 'free_reservation') return t.freeReservation
  if (p.kind === 'voluntary') return t.voluntary
  if (p.min == null) return null
  const unit = p.currency === 'EUR' ? '€' : p.currency === 'CZK' ? t.czk : p.currency
  const amount = p.max == null ? `${t.from} ${p.min}`
    : p.max !== p.min ? `${p.min}–${p.max}` : `${p.min}`
  return unit ? `${amount} ${unit}` : amount
}
