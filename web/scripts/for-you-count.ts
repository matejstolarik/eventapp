// Task 079: how many events are "for you" under given preferences, new rule vs.
// the old rule (favourite venues only). Usage (from web/):
//   npx vite-node scripts/for-you-count.ts <events.json> <favorites,comma> <types,comma> <subtypes,comma> <genres,comma> [YYYY-MM-DD]
import fs from 'fs'
import { isForYou, type ForYouPrefs } from '../src/core/search'
import type { EventsData } from '../src/core/types'
import type { FilterType } from '../src/core/filter'
import type { CultureSubtype } from '../src/core/eventType'

const [file, fav = '', types = '', subtypes = '', genres = '', day] = process.argv.slice(2)
const list = (s: string) => s.split(',').map(x => x.trim()).filter(Boolean)
const data = JSON.parse(fs.readFileSync(file, 'utf-8')) as EventsData
const events = day ? data.events.filter(e => e.date === day) : data.events
const prefs: ForYouPrefs = {
  favorites: new Set(list(fav)),
  types: list(types) as FilterType[],
  subtypes: list(subtypes) as CultureSubtype[],
  genres: list(genres),
}
const old: ForYouPrefs = { favorites: prefs.favorites, types: [], subtypes: [], genres: [] }
const n = (p: ForYouPrefs) => events.filter(e => isForYou(e, p)).length
console.log(JSON.stringify({ generated_at: data.generated_at, day: day ?? 'all', events: events.length, newRule: n(prefs), oldRule: n(old) }))
