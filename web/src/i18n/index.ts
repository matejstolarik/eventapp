import { sk } from './sk'
import { cs } from './cs'
import { en } from './en'
import type { Language } from '../core/types'

export type Dict = typeof sk

const dicts: Record<Language, Dict> = { sk, cs: cs as unknown as Dict, en: en as unknown as Dict }

export function getDict(lang: Language): Dict {
  return dicts[lang]
}

/** Formats a YYYY-MM-DD date for display in the given language.
 * Uses abbreviated day name + day + dot + month number. */
export function formatDayLabel(dateStr: string, lang: Language, now?: Date): string {
  const dict = getDict(lang)
  const d = new Date(dateStr + 'T12:00:00')
  const today = new Date(now ?? new Date())
  today.setHours(12, 0, 0, 0)
  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
  const tomorrowDate = new Date(today)
  tomorrowDate.setDate(tomorrowDate.getDate() + 1)
  const tomorrowStr = `${tomorrowDate.getFullYear()}-${String(tomorrowDate.getMonth() + 1).padStart(2, '0')}-${String(tomorrowDate.getDate()).padStart(2, '0')}`
  if (dateStr === todayStr) return dict.map.today
  if (dateStr === tomorrowStr) return dict.map.tomorrow
  const dayName = dict.days[d.getDay()]
  if (lang === 'en') {
    return `${dayName} ${dict.months[d.getMonth()]} ${d.getDate()}`
  }
  return `${dayName} ${d.getDate()}. ${d.getMonth() + 1}.`
}

/** Formats a date for the event page header: "Sobota 5. 12." */
export function formatEventDate(dateStr: string, lang: Language): string {
  const dict = getDict(lang)
  const d = new Date(dateStr + 'T12:00:00')
  if (lang === 'en') {
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    return `${days[d.getDay()]} ${dict.months[d.getMonth()]} ${d.getDate()}`
  }
  const daysFull: Record<Language, string[]> = {
    sk: ['Nedeľa', 'Pondelok', 'Utorok', 'Streda', 'Štvrtok', 'Piatok', 'Sobota'],
    cs: ['Neděle', 'Pondělí', 'Úterý', 'Středa', 'Čtvrtek', 'Pátek', 'Sobota'],
    en: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
  }
  return `${daysFull[lang][d.getDay()]} ${d.getDate()}. ${d.getMonth() + 1}.`
}
