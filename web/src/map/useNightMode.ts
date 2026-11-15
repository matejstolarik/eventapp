import { useState, useEffect } from 'react'
import { isNightTime, isNightEvent, NIGHT_DAY, resolveSelectedDay } from '../core/night'
import { getToday } from '../core/day'
import type { EventsData } from '../core/types'

interface NightModeOptions {
  data: EventsData
  selectedDayRef: React.MutableRefObject<string>
  pendingPanelOpenRef: React.MutableRefObject<string | null>
  setSelectedDay: (day: string) => void
  onPendingSelectHandled?: () => void
}

export function useNightMode(opts: NightModeOptions) {
  const [showNight, setShowNight] = useState(() => isNightTime(new Date()))
  const { selectedDayRef, setSelectedDay } = opts

  // Auto-switch at midnight and 5:00, also on visibility/focus restore
  useEffect(() => {
    let wasNight = isNightTime(new Date())

    const checkNight = () => {
      const n = new Date()
      const isNight = isNightTime(n)
      setShowNight(isNight)
      if (isNight && !wasNight) {
        if (selectedDayRef.current === getToday(n)) {
          setSelectedDay(NIGHT_DAY)
        }
      } else {
        const corrected = resolveSelectedDay(selectedDayRef.current, n)
        if (corrected !== selectedDayRef.current) setSelectedDay(corrected)
      }
      wasNight = isNight
    }

    const handleVisChange = () => { if (document.visibilityState === 'visible') checkNight() }
    const handleFocus = () => checkNight()
    document.addEventListener('visibilitychange', handleVisChange)
    window.addEventListener('focus', handleFocus)

    const scheduleNext = () => {
      const n = new Date()
      const h = n.getHours()
      let targetMs: number
      if (h >= 5) {
        const midnight = new Date(n)
        midnight.setDate(midnight.getDate() + 1)
        midnight.setHours(0, 0, 10, 0)
        targetMs = midnight.getTime() - n.getTime()
      } else {
        const five = new Date(n)
        five.setHours(5, 0, 10, 0)
        targetMs = five.getTime() - n.getTime()
      }
      return setTimeout(() => { checkNight(); scheduleNext() }, Math.max(targetMs, 1000))
    }

    const timer = scheduleNext()
    return () => {
      clearTimeout(timer)
      document.removeEventListener('visibilitychange', handleVisChange)
      window.removeEventListener('focus', handleFocus)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  return showNight
}

// Handle external "Na mape" selection with night mode awareness
export function usePendingSelect(
  pendingSelect: { venueId: string; date: string } | null | undefined,
  data: EventsData,
  pendingPanelOpenRef: React.MutableRefObject<string | null>,
  setSelectedDay: (day: string) => void,
  onPendingSelectHandled?: () => void,
) {
  useEffect(() => {
    if (!pendingSelect) return
    const n = new Date()
    let dayToSelect = pendingSelect.date
    if (isNightTime(n) && pendingSelect.date === getToday(n)) {
      const venue = data.venues.find(v => v.id === pendingSelect.venueId)
      if (venue) {
        const evs = data.events.filter(e => e.venue_id === pendingSelect.venueId && e.date === pendingSelect.date)
        if (evs.some(e => isNightEvent(e, venue.character, n))) dayToSelect = NIGHT_DAY
      }
    }
    setSelectedDay(dayToSelect)
    pendingPanelOpenRef.current = pendingSelect.venueId
    onPendingSelectHandled?.()
  }, [pendingSelect, onPendingSelectHandled, data, pendingPanelOpenRef, setSelectedDay]) // eslint-disable-line react-hooks/exhaustive-deps
}
