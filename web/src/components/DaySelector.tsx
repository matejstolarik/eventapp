import { useState, useMemo } from 'react'
import { formatDayLabel, getDict } from '../i18n'
import type { Language } from '../core/types'
import { NIGHT_DAY } from '../core/night'

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

/** Build the day grid for a given month: { dateStr | null, inMonth } × N */
function buildMonthGrid(year: number, month: number) {
  const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7 // 0=Mon
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const cells: Array<{ date: string | null }> = []
  for (let i = 0; i < firstWeekday; i++) cells.push({ date: null })
  for (let d = 1; d <= daysInMonth; d++) {
    cells.push({
      date: `${year}-${String(month + 1).padStart(2, '0')}-${String(d).padStart(2, '0')}`,
    })
  }
  return cells
}

export function DaySelector({ days, selectedDay, lang, now, showNight, availableDates, onSelect, onClose }: Props) {
  const dict = getDict(lang)
  const [calView, setCalView] = useState(false)
  const [calYear, setCalYear] = useState(now.getFullYear())
  const [calMonth, setCalMonth] = useState(now.getMonth())

  const cells = useMemo(() => buildMonthGrid(calYear, calMonth), [calYear, calMonth])

  // How many day rows fit without scrolling: estimate based on viewport height
  // Sheet max is 70vh; handle+padding ≈ 56px; night ≈ 50px; otherDate ≈ 50px; each day ≈ 50px
  const maxDays = Math.max(3, Math.floor((window.innerHeight * 0.7 - 56 - (showNight ? 50 : 0) - 50) / 50))
  const visibleDays = days.slice(0, maxDays)

  const monthLabel = new Intl.DateTimeFormat(lang === 'en' ? 'en' : lang, {
    month: 'long', year: 'numeric',
  }).format(new Date(calYear, calMonth, 1))

  // Mo–Su headers for the calendar (locale-aware)
  const weekHeaders = [...dict.days.slice(1), dict.days[0]]

  function prevMonth() {
    if (calMonth === 0) { setCalYear(y => y - 1); setCalMonth(11) }
    else setCalMonth(m => m - 1)
  }
  function nextMonth() {
    if (calMonth === 11) { setCalYear(y => y + 1); setCalMonth(0) }
    else setCalMonth(m => m + 1)
  }

  const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  const itemStyle = (active: boolean): React.CSSProperties => ({
    display: 'block', width: '100%', textAlign: 'left',
    padding: '14px 24px', border: 'none', background: 'none',
    fontSize: 17, fontWeight: active ? 700 : 400,
    color: active ? '#F4F2FF' : '#B9B6CC',
    cursor: 'pointer', letterSpacing: '-0.01em',
    fontFamily: "'Outfit', sans-serif",
  })

  return (
    <>
      {/* Backdrop */}
      <div
        style={{ position: 'absolute', inset: 0, zIndex: 29, background: 'rgba(0,0,0,0.5)' }}
        onClick={onClose}
      />
      {/* Sheet */}
      <div style={{
        position: 'absolute', left: 0, right: 0, bottom: 0,
        background: '#1C1C27', borderRadius: '28px 28px 0 0',
        zIndex: 30, paddingBottom: 'max(28px, env(safe-area-inset-bottom))',
        overflow: 'hidden',
      }}>
        {/* Handle */}
        <div style={{
          width: 40, height: 4, borderRadius: 2, background: '#3A3A50',
          margin: '12px auto 0'
        }} />

        {!calView ? (
          /* ── List view ── */
          <div style={{ padding: '8px 0 4px' }}>
            {showNight && (
              <button
                style={itemStyle(selectedDay === NIGHT_DAY)}
                onClick={() => onSelect(NIGHT_DAY)}
              >
                {dict.map.night}
              </button>
            )}

            {visibleDays.map(day => (
              <button
                key={day}
                style={itemStyle(day === selectedDay)}
                onClick={() => onSelect(day)}
              >
                {formatDayLabel(day, lang, now)}
              </button>
            ))}

            <button
              style={{
                ...itemStyle(false),
                color: '#7A78A0',
                fontSize: 15,
                paddingTop: 10, paddingBottom: 10,
              }}
              onClick={() => setCalView(true)}
            >
              {dict.map.otherDate} ›
            </button>
          </div>
        ) : (
          /* ── Calendar view ── */
          <div style={{ padding: '8px 0 16px' }}>
            {/* Month navigation */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '4px 16px 8px',
            }}>
              <button
                style={{ width: 36, height: 36, borderRadius: 18, border: 'none', background: '#2A2838', color: '#B9B6CC', fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                onClick={prevMonth}
                aria-label="Predchádzajúci mesiac"
              >‹</button>
              <span style={{ color: '#F4F2FF', fontSize: 16, fontWeight: 600, fontFamily: "'Outfit', sans-serif", textTransform: 'capitalize' }}>
                {monthLabel}
              </span>
              <button
                style={{ width: 36, height: 36, borderRadius: 18, border: 'none', background: '#2A2838', color: '#B9B6CC', fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                onClick={nextMonth}
                aria-label="Nasledujúci mesiac"
              >›</button>
            </div>

            {/* Week day headers */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', padding: '0 12px 4px' }}>
              {weekHeaders.map(d => (
                <div key={d} style={{ textAlign: 'center', fontSize: 11, fontWeight: 600, color: '#5D5677', fontFamily: "'Outfit', sans-serif", padding: '4px 0' }}>
                  {d}
                </div>
              ))}
            </div>

            {/* Day grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', padding: '0 12px', gap: 2 }}>
              {cells.map((cell, i) => {
                if (!cell.date) return <div key={`e${i}`} />
                const hasEvent = availableDates.has(cell.date)
                const isSelected = cell.date === selectedDay
                const isToday = cell.date === todayStr
                return (
                  <button
                    key={cell.date}
                    disabled={!hasEvent}
                    onClick={() => { onSelect(cell.date!); setCalView(false) }}
                    style={{
                      height: 36, borderRadius: 18, border: 'none',
                      background: isSelected ? '#FF4D8D' : isToday ? '#2A2838' : 'transparent',
                      color: isSelected ? '#1A0710' : hasEvent ? '#F4F2FF' : '#3A3A50',
                      fontSize: 14, fontWeight: isSelected ? 700 : 400,
                      cursor: hasEvent ? 'pointer' : 'default',
                      fontFamily: "'Outfit', sans-serif",
                      outline: isToday && !isSelected ? '1px solid #3A3A50' : 'none',
                    }}
                  >
                    {parseInt(cell.date.slice(8))}
                  </button>
                )
              })}
            </div>

            {/* Back to list */}
            <button
              style={{ ...itemStyle(false), color: '#7A78A0', fontSize: 15, marginTop: 8 }}
              onClick={() => setCalView(false)}
            >
              ← {lang === 'en' ? 'Days' : lang === 'cs' ? 'Dny' : 'Dni'}
            </button>
          </div>
        )}
      </div>
    </>
  )
}
