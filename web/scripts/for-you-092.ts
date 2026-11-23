// Task 092: Pre teba counts for culture without subtypes + 2 favourite venues, before and after.
// Usage (from web/): npx vite-node scripts/for-you-092.ts ../site/events.json [score module]
// score module: '../src/core/search.ts' (default, current) or a copy of the 091 version (git show 6bb56e9:web/src/core/search.ts).
import { readFileSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import type { ForYouPrefs } from '../src/core/search'
import { getEventsForPeriod } from '../src/core/period'
import type { Event } from '../src/core/types'

const path = process.argv[2] ?? '../site/events.json'
const mod = process.argv[3] ?? '../src/core/search.ts'
const { forYouScore, forYouTier } = await import(resolve(dirname(fileURLToPath(import.meta.url)), mod)) as typeof import('../src/core/search')
const data = JSON.parse(readFileSync(path, 'utf-8')) as { generated_at: string; events: Event[] }
const sets: Record<string, ForYouPrefs> = {
  'culture (no subtypes), fav MeetFactory+Archa+, no genres': { favorites: new Set(['meetfactory', 'archa-plus']), types: ['culture'], subtypes: [], genres: [] },
}
const upcoming = getEventsForPeriod(data.events, { type: 'anytime' } as never, new Date())
console.log('generated_at', data.generated_at, 'module', mod, 'upcoming', upcoming.length)
for (const [name, p] of Object.entries(sets)) {
  const t = [0, 0, 0]
  const favStar = upcoming.filter(e => forYouTier(forYouScore(e, p)) > 0 && !p.favorites.has(e.venue_id)).length
  for (const e of upcoming) t[forYouTier(forYouScore(e, p))]!++
  console.log(name, { two: t[2], one: t[1], none: t[0], starOutsideFavourites: favStar })
}
