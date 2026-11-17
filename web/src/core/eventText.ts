import type { Event, Language } from './types'

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
