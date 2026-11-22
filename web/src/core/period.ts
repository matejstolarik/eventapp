import type { Event } from './types'
import { getToday, getYesterday, toDateString } from './day'
import { isEventFinished } from './events'
import { haversine } from './distance'

export type Period =
  | { type: 'today' }
  | { type: 'tomorrow' }
  | { type: 'night' }
  | { type: 'weekend' }
  | { type: 'next7' }
  | { type: 'next30' }
  | { type: 'anytime' }
  | { type: 'custom'; from: string; to: string }

export interface DateRange {
  from: string
  to: string | null
}

export function getPeriodRange(period: Period, now: Date): DateRange {
  const today = getToday(now)

  switch (period.type) {
    case 'today':
      return { from: today, to: today }

    case 'night':
      return { from: getYesterday(now), to: getYesterday(now) }

    case 'tomorrow': {
      const d = new Date(today + 'T12:00:00')
      d.setDate(d.getDate() + 1)
      const tom = toDateString(d)
      return { from: tom, to: tom }
    }

    case 'weekend': {
      const todayD = new Date(today + 'T12:00:00')
      const dow = todayD.getDay() // 0=Sun,1=Mon…5=Fri,6=Sat
      // Mon-Thu: nearest upcoming Fri–Sun; Fri-Sun: today until this Sunday
      let fridayOffset: number
      if (dow === 5) fridayOffset = 0
      else if (dow === 6) fridayOffset = -1
      else if (dow === 0) fridayOffset = -2
      else fridayOffset = 5 - dow  // Mon=1..Thu=4

      let sundayOffset: number
      if (dow === 0) sundayOffset = 0
      else if (dow === 6) sundayOffset = 1
      else if (dow === 5) sundayOffset = 2
      else sundayOffset = 7 - dow  // Mon=1..Thu=4

      const fri = new Date(todayD)
      fri.setDate(fri.getDate() + fridayOffset)
      const sun = new Date(todayD)
      sun.setDate(sun.getDate() + sundayOffset)

      const from = (dow === 5 || dow === 6 || dow === 0) ? today : toDateString(fri)
      return { from, to: toDateString(sun) }
    }

    case 'next7': {
      const d = new Date(today + 'T12:00:00')
      d.setDate(d.getDate() + 6)
      return { from: today, to: toDateString(d) }
    }

    case 'next30': {
      const d = new Date(today + 'T12:00:00')
      d.setDate(d.getDate() + 29)
      return { from: today, to: toDateString(d) }
    }

    case 'anytime':
      return { from: today, to: null }

    case 'custom':
      return { from: period.from, to: period.to }
  }
}

export function getEventsForPeriod(events: Event[], period: Period, now: Date): Event[] {
  const range = getPeriodRange(period, now)
  const today = getToday(now)
  return events.filter(e => {
    if (e.status === 'cancelled' || e.status === 'gone') return false
    if (e.date < range.from) return false
    if (range.to !== null && e.date > range.to) return false
    if (e.date === today && isEventFinished(e, now)) return false
    return true
  })
}

/** 'match' = Best match (task 087): offered only while Pre teba is on. */
export type SortMode = 'date' | 'distance' | 'size' | 'match'

/** Sort after the Pre teba chip is toggled (task 087): on → Best match, the current
 * sort is remembered; off → back to the remembered sort if the sort is still Best match,
 * otherwise the user's manual choice stays. Distance falls back to date on multi-day periods. */
export function sortAfterForYouToggle(
  turningOn: boolean, sort: SortMode, remembered: SortMode, singleDay: boolean,
): { sort: SortMode; remembered: SortMode } {
  if (turningOn) return { sort: 'match', remembered: sort === 'match' ? remembered : sort }
  if (sort !== 'match') return { sort, remembered }
  const back = remembered === 'match' || (remembered === 'distance' && !singleDay) ? 'date' : remembered
  return { sort: back, remembered }
}

function compareDatetime(a: Event, b: Event): number {
  if (a.date !== b.date) return a.date.localeCompare(b.date)
  const aTime = a.start_time ?? '99:99'
  const bTime = b.start_time ?? '99:99'
  return aTime.localeCompare(bTime)
}

export function sortEvents(
  events: Event[],
  venueLocations: Map<string, { lat: number; lng: number }>,
  sort: SortMode,
  userLocation: { lat: number; lng: number } | null,
  venueCapacities?: Map<string, number | null | undefined>,
  scoreOf?: (e: Event) => number,
): Event[] {
  const sorted = [...events]
  if (sort === 'match' && scoreOf) {
    // Score descending, ties by start (task 087)
    const scores = new Map(sorted.map(e => [e.id, scoreOf(e)]))
    sorted.sort((a, b) => (scores.get(b.id)! - scores.get(a.id)!) || compareDatetime(a, b))
  } else if (sort === 'size') {
    // Venue capacity descending, ties by start; venues without capacity last
    sorted.sort((a, b) => {
      const aCap = venueCapacities?.get(a.venue_id) ?? null
      const bCap = venueCapacities?.get(b.venue_id) ?? null
      if (aCap !== bCap) {
        if (aCap === null) return 1
        if (bCap === null) return -1
        return bCap - aCap
      }
      return compareDatetime(a, b)
    })
  } else if (sort === 'distance' && userLocation) {
    sorted.sort((a, b) => {
      const aLoc = venueLocations.get(a.venue_id)
      const bLoc = venueLocations.get(b.venue_id)
      const aDist = aLoc ? haversine(userLocation.lat, userLocation.lng, aLoc.lat, aLoc.lng) : Infinity
      const bDist = bLoc ? haversine(userLocation.lat, userLocation.lng, bLoc.lat, bLoc.lng) : Infinity
      if (aDist !== bDist) return aDist - bDist
      return compareDatetime(a, b)
    })
  } else {
    sorted.sort(compareDatetime)
  }
  return sorted
}

export function isSingleDayPeriod(period: Period): boolean {
  if (period.type === 'today' || period.type === 'tomorrow' || period.type === 'night') return true
  if (period.type === 'custom' && period.from === period.to) return true
  return false
}

/** Short button label for the period (e.g. "Dnes", "7 dní", "20.–24. 11.") */
export function formatPeriodShortLabel(period: Period, lang: string): string {
  const labels: Record<string, Record<Period['type'], string>> = {
    sk: { today: 'Dnes', tomorrow: 'Zajtra', night: 'V noci', weekend: 'Víkend', next7: '7 dní', next30: '30 dní', anytime: 'Kedykoľvek', custom: '' },
    cs: { today: 'Dnes', tomorrow: 'Zítra', night: 'V noci', weekend: 'Víkend', next7: '7 dní', next30: '30 dní', anytime: 'Kdykoli', custom: '' },
    en: { today: 'Today', tomorrow: 'Tomorrow', night: 'Late night', weekend: 'Weekend', next7: '7 days', next30: '30 days', anytime: 'Anytime', custom: '' },
  }
  const l = labels[lang] ?? labels.cs
  if (period.type === 'custom') {
    return formatCustomShort(period.from, period.to)
  }
  return l[period.type]
}

/** Format custom range short: "20.–24. 11." or "20. 11.–4. 12." */
function formatCustomShort(from: string, to: string): string {
  if (from === to) {
    const d = new Date(from + 'T12:00:00')
    return `${d.getDate()}. ${d.getMonth() + 1}.`
  }
  const dFrom = new Date(from + 'T12:00:00')
  const dTo = new Date(to + 'T12:00:00')
  if (dFrom.getMonth() === dTo.getMonth()) {
    return `${dFrom.getDate()}.–${dTo.getDate()}. ${dTo.getMonth() + 1}.`
  }
  return `${dFrom.getDate()}. ${dFrom.getMonth() + 1}.–${dTo.getDate()}. ${dTo.getMonth() + 1}.`
}

/** Right-side date range text shown in the period selector panel */
export function formatPeriodRangeText(period: Period, lang: string, days: readonly string[], now: Date): string {
  if (period.type === 'anytime' || period.type === 'night') return ''
  if (period.type === 'custom') {
    return formatRangeText(period.from, period.to, lang, days)
  }
  const range = getPeriodRange(period, now)
  const { from, to } = range
  if (!to) return ''

  if (period.type === 'today' || period.type === 'tomorrow') {
    return formatDateShort(from, lang, days)
  }
  if (period.type === 'weekend') {
    return formatWeekendRange(from, to, lang, days)
  }
  // next7, next30
  return formatRangeText(from, to, lang, days)
}

function formatDateShort(dateStr: string, lang: string, days: readonly string[]): string {
  const d = new Date(dateStr + 'T12:00:00')
  const dayName = days[d.getDay()]
  if (lang === 'en') {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return `${dayName} ${months[d.getMonth()]} ${d.getDate()}`
  }
  return `${dayName} ${d.getDate()}. ${d.getMonth() + 1}.`
}

function formatWeekendRange(from: string, to: string, lang: string, days: readonly string[]): string {
  const dFrom = new Date(from + 'T12:00:00')
  const dTo = new Date(to + 'T12:00:00')
  const dayFrom = days[dFrom.getDay()]
  const dayTo = days[dTo.getDay()]
  if (lang === 'en') {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if (dFrom.getMonth() === dTo.getMonth()) {
      return `${dayFrom} ${dFrom.getDate()}–${dayTo} ${dTo.getDate()} ${months[dTo.getMonth()]}`
    }
    return `${dayFrom} ${dFrom.getDate()} ${months[dFrom.getMonth()]}–${dayTo} ${dTo.getDate()} ${months[dTo.getMonth()]}`
  }
  if (dFrom.getMonth() === dTo.getMonth()) {
    return `${dayFrom} ${dFrom.getDate()}.–${dayTo} ${dTo.getDate()}. ${dTo.getMonth() + 1}.`
  }
  return `${dayFrom} ${dFrom.getDate()}. ${dFrom.getMonth() + 1}.–${dayTo} ${dTo.getDate()}. ${dTo.getMonth() + 1}.`
}

function formatRangeText(from: string, to: string, lang: string, _days: readonly string[]): string {
  const dFrom = new Date(from + 'T12:00:00')
  const dTo = new Date(to + 'T12:00:00')
  if (lang === 'en') {
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    if (dFrom.getMonth() === dTo.getMonth()) {
      return `${dFrom.getDate()}–${dTo.getDate()} ${months[dTo.getMonth()]}`
    }
    return `${dFrom.getDate()} ${months[dFrom.getMonth()]}–${dTo.getDate()} ${months[dTo.getMonth()]}`
  }
  if (dFrom.getMonth() === dTo.getMonth()) {
    return `${dFrom.getDate()}.–${dTo.getDate()}. ${dTo.getMonth() + 1}.`
  }
  return `${dFrom.getDate()}. ${dFrom.getMonth() + 1}.–${dTo.getDate()}. ${dTo.getMonth() + 1}.`
}
