import { useState, useEffect } from 'react'
import { isNightMode, isNightEvent, NIGHT_DAY, resolveSelectedDay } from '../core/night'
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
  const { data, selectedDayRef, setSelectedDay } = opts
  const [showNight, setShowNight] = useState(() => isNightMode(data, new Date()))

  useEffect(() => {
    let wasNight = isNightMode(data, new Date())

    const checkNight = () => {
      const n = new Date()
      const isNight = isNightMode(data, n)
      setShowNight(isNight)
      if (isNight && !wasNight) {
        if (selectedDayRef.current === getToday(n)) {
          setSelectedDay(NIGHT_DAY)
        }
      } else {
        const corrected = resolveSelectedDay(selectedDayRef.current, n, data)
        if (corrected !== selectedDayRef.current) setSelectedDay(corrected)
      }
      wasNight = isNight
    }

    const handleVisChange = () => { if (document.visibilityState === 'visible') checkNight() }
    const handleFocus = () => checkNight()
    document.addEventListener('visibilitychange', handleVisChange)
    window.addEventListener('focus', handleFocus)

    const timer = setInterval(checkNight, 60_000)
    return () => {
      clearInterval(timer)
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
    if (isNightMode(data, n) && pendingSelect.date === getToday(n)) {
      const venue = data.venues.find(v => v.id === pendingSelect.venueId)
      if (venue) {
        const evs = data.events.filter(e => e.venue_id === pendingSelect.venueId && e.date === pendingSelect.date)
        if (evs.some(e => isNightEvent(e, venue.character, venue.closing, n))) dayToSelect = NIGHT_DAY
      }
    }
    setSelectedDay(dayToSelect)
    pendingPanelOpenRef.current = pendingSelect.venueId
    onPendingSelectHandled?.()
  }, [pendingSelect, onPendingSelectHandled, data, pendingPanelOpenRef, setSelectedDay]) // eslint-disable-line react-hooks/exhaustive-deps
}
