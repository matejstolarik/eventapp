import { useMemo } from 'react'
import { formatDayLabel, getDict } from '../i18n'
import type { Language } from '../core/types'
import { NIGHT_DAY } from '../core/night'
import { getToday, toDateString } from '../core/day'
import { SelectorSheet, CalendarIcon, type SheetItem } from './SelectorSheet'

interface Props {
  days: string[]
  selectedDay: string
  lang: Language
  now: Date
  showNight: boolean
  availableDates: Set<string>
  onSelect: (day: string) => void
  onClose: () => void
}

function formatDayRight(dateStr: string, lang: Language, now: Date): string {
  if (dateStr === NIGHT_DAY) {
    return getDict(lang).events.tillFive
  }
  const today = getToday(now)
  const tomorrowD = new Date(today + 'T12:00:00')
  tomorrowD.setDate(tomorrowD.getDate() + 1)
  const tomorrow = toDateString(tomorrowD)
  if (dateStr !== today && dateStr !== tomorrow) return ''
  const dict = getDict(lang)
  const d = new Date(dateStr + 'T12:00:00')
  const dayName = dict.days[d.getDay()]
  if (lang === 'en') {
    return `${dayName} ${dict.months[d.getMonth()]} ${d.getDate()}`
  }
  return `${dayName} ${d.getDate()}. ${d.getMonth() + 1}.`
}

export function DaySelector({ days, selectedDay, lang, now, showNight, availableDates, onSelect, onClose }: Props) {
  const dict = getDict(lang)
  const visibleDays = days.slice(0, showNight ? 4 : 5)

  const items: SheetItem[] = useMemo(() => {
    const result: SheetItem[] = []

    if (showNight) {
      result.push({
        id: NIGHT_DAY,
        label: dict.map.night,
        rightText: formatDayRight(NIGHT_DAY, lang, now),
        selected: selectedDay === NIGHT_DAY,
      })
    }

    for (const day of visibleDays) {
      result.push({
        id: day,
        label: formatDayLabel(day, lang, now),
        rightText: formatDayRight(day, lang, now),
        selected: day === selectedDay,
      })
    }

    result.push({
      id: '__calendar__',
      label: dict.map.otherDate,
      iconLeft: <CalendarIcon />,
      selected: false,
      isCalendarTrigger: true,
    })

    return result
  }, [days, selectedDay, lang, now, showNight]) // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <SelectorSheet
      title={dict.events.day}
      items={items}
      calendarMode="single"
      availableDates={availableDates}
      now={now}
      lang={lang}
      onItemSelect={onSelect}
      onCalendarSelect={(from) => onSelect(from)}
      onClose={onClose}
    />
  )
}
