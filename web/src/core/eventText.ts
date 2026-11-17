import type { Event, Language } from './types'
import { getDict } from '../i18n'

/** Description shown in the app (task 054): AI text in the app language,
 *  then Czech AI text, then the original description from the source. */
export function eventDescription(ev: Pick<Event, 'descriptions' | 'description'>, lang: Language): string | null {
  const d = ev.descriptions
  return d?.[lang] || d?.cs || ev.description || null
}

/** Spotify button target (design.md part 7, task 060): only the verified
 *  artist profile artist_links[0].spotify_url (from data/manual.json);
 *  null = no Spotify button (no Spotify search). */
export function spotifyUrl(ev: Pick<Event, 'artist_links'>): string | null {
  return ev.artist_links?.[0]?.spotify_url || null
}

/** Price shown in the app (task 058 part 4): from the structured `price`,
 *  in the app language, without any other text: "350 Kč", "250–350 Kč",
 *  "od 950 Kč" / "from 950 CZK", "20 €", Zdarma, Dobrovolné vstupné,
 *  Zdarma, rezervace.  No `price` -> "free" label if `free`, else null
 *  (price_text only for older data without the `price` key). */
export function priceLabel(ev: Pick<Event, 'price' | 'free' | 'price_text'>, lang: Language): string | null {
  const t = getDict(lang).price
  const p = ev.price
  // data from before task 058 has no `price` key yet: keep showing price_text
  if (p === undefined && ev.price_text) return ev.price_text
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
