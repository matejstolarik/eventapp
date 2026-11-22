// Task 087: Pre teba score stats for model preferences over a local events.json.
// Usage (from web/): npx vite-node scripts/for-you-stats.ts ../site/events.json
import { readFileSync } from 'node:fs'
import { forYouScore, forYouTier, type ForYouPrefs } from '../src/core/search'
import { getEventsForPeriod } from '../src/core/period'
import type { Event } from '../src/core/types'

const path = process.argv[2] ?? '../site/events.json'
const data = JSON.parse(readFileSync(path, 'utf-8')) as { generated_at: string; events: Event[]; venues: { id: string; name: string }[] }
const prefs: ForYouPrefs = {
  favorites: new Set(['fuchs2', 'cross-club']),
  types: ['dj', 'concert'],
  subtypes: [],
  genres: ['techno', 'punk', 'rock'],
}
const now = new Date(process.argv[3] ?? Date.now())
const names = new Map(data.venues.map(v => [v.id, v.name]))

function tally(evts: Event[]) {
  const t = [0, 0, 0]
  for (const e of evts) t[forYouTier(forYouScore(e, prefs))]!++
  return { total: evts.length, two: t[2], one: t[1], none: t[0] }
}

const upcoming = getEventsForPeriod(data.events, { type: 'anytime' } as never, now)
console.log('generated_at', data.generated_at, 'now', now.toISOString())
console.log('Kedykolvek', tally(upcoming))
console.log('Dnes', tally(getEventsForPeriod(data.events, { type: 'today' } as never, now)))
const top = [...upcoming].map(e => ({ e, s: forYouScore(e, prefs) }))
  .sort((a, b) => b.s - a.s || a.e.date.localeCompare(b.e.date) || (a.e.start_time ?? '99').localeCompare(b.e.start_time ?? '99'))
  .slice(0, 10)
for (const { e, s } of top) console.log([s, e.date, e.title, names.get(e.venue_id), e.genres.join(', ')].join(' | '))
