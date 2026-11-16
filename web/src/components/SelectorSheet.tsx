import { useState, useMemo, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import type { Language } from '../core/types'

export interface SheetItem {
  id: string
  label: string
  iconLeft?: React.ReactNode
  rightText?: string
  selected: boolean
  isCalendarTrigger?: boolean
  separator?: boolean
}

interface Props {
  title: string
  items: SheetItem[]
  calendarMode: 'single' | 'interval'
  availableDates?: Set<string>
  now: Date
  lang: Language
  onItemSelect: (id: string) => void
  onCalendarSelect: (from: string, to: string) => void
  onClose: () => void
}

function buildMonthGrid(year: number, month: number) {
  const firstWeekday = (new Date(year, month, 1).getDay() + 6) % 7
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

const WEEK_DAYS_SK = ['Po', 'Ut', 'St', 'Št', 'Pi', 'So', 'Ne']
const WEEK_DAYS_CS = ['Po', 'Út', 'St', 'Čt', 'Pá', 'So', 'Ne']
const WEEK_DAYS_EN = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']

export function SelectorSheet({ title, items, calendarMode, availableDates, now, lang, onItemSelect, onCalendarSelect, onClose }: Props) {
  const [calView, setCalView] = useState(false)
  const [calYear, setCalYear] = useState(now.getFullYear())
  const [calMonth, setCalMonth] = useState(now.getMonth())
  const [pendingFrom, setPendingFrom] = useState<string | null>(null)
  const historyPushedRef = useRef(false)

  useEffect(() => {
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => { document.body.style.overflow = prev }
  }, [])

  // Push a history entry when the sheet opens; popstate = close (Android Back)
  useEffect(() => {
    history.pushState({ sheet: true }, '')
    historyPushedRef.current = true

    function onPopState() {
      if (historyPushedRef.current) {
        historyPushedRef.current = false
        onClose()
      }
    }
    window.addEventListener('popstate', onPopState)
    return () => {
      window.removeEventListener('popstate', onPopState)
      if (historyPushedRef.current) {
        historyPushedRef.current = false
        history.back()
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function handleBackdropClick() {
    if (historyPushedRef.current) {
      historyPushedRef.current = false
      history.back()
    }
    onClose()
  }

  const cells = useMemo(() => buildMonthGrid(calYear, calMonth), [calYear, calMonth])

  const weekHeaders = lang === 'en' ? WEEK_DAYS_EN : lang === 'cs' ? WEEK_DAYS_CS : WEEK_DAYS_SK

  const monthLabel = new Intl.DateTimeFormat(lang === 'en' ? 'en' : lang, {
    month: 'long', year: 'numeric',
  }).format(new Date(calYear, calMonth, 1))

  const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`

  function prevMonth() {
    if (calMonth === 0) { setCalYear(y => y - 1); setCalMonth(11) }
    else setCalMonth(m => m - 1)
  }
  function nextMonth() {
    if (calMonth === 11) { setCalYear(y => y + 1); setCalMonth(0) }
    else setCalMonth(m => m + 1)
  }

  function handleDayClick(date: string) {
    if (calendarMode === 'single') {
      onCalendarSelect(date, date)
      setCalView(false)
    } else {
      if (!pendingFrom) {
        setPendingFrom(date)
      } else {
        const from = pendingFrom <= date ? pendingFrom : date
        const to = pendingFrom <= date ? date : pendingFrom
        onCalendarSelect(from, to)
        setPendingFrom(null)
        setCalView(false)
      }
    }
  }

  function isInRange(date: string): boolean {
    if (!pendingFrom) return false
    return date > pendingFrom
  }

  const rowStyle = (selected: boolean): React.CSSProperties => ({
    display: 'flex', alignItems: 'center', gap: 10,
    height: 48, borderRadius: 24, padding: '0 16px',
    background: selected ? '#F4F2FF' : 'transparent',
    color: selected ? '#111118' : '#F4F2FF',
    fontSize: 16, fontWeight: selected ? 600 : 500,
    fontFamily: "'Outfit', sans-serif",
    cursor: 'pointer', border: 'none', width: '100%', textAlign: 'left',
  })

  return createPortal(
    <>
      <div
        style={{ position: 'fixed', inset: 0, zIndex: 29, background: 'rgba(0,0,0,0.5)' }}
        onClick={handleBackdropClick}
      />
      <div style={{
        position: 'fixed', left: 0, right: 0, bottom: 0,
        background: '#1C1C27', borderRadius: '28px 28px 0 0',
        zIndex: 30, paddingBottom: 'calc(16px + env(safe-area-inset-bottom))', overflow: 'hidden',
        overscrollBehavior: 'contain',
      }}>
        <div style={{ width: 40, height: 4, borderRadius: 2, background: '#3A3848', margin: '10px auto 12px' }} />

        {!calView ? (
          <div style={{ padding: '0 12px 4px' }}>
            <div style={{
              fontFamily: "'Bricolage Grotesque', sans-serif",
              fontSize: 20, fontWeight: 700,
              padding: '0 4px 8px', color: '#F4F2FF',
            }}>
              {title}
            </div>

            {items.map(item => (
              <div key={item.id}>
                {item.separator && (
                  <div style={{ height: 1, background: '#2E2D3C', margin: '2px 0' }} />
                )}
                {!item.separator && (
                  <button
                    style={rowStyle(item.selected)}
                    onClick={() => {
                      if (item.isCalendarTrigger) {
                        setCalView(true)
                      } else {
                        onItemSelect(item.id)
                      }
                    }}
                  >
                    {item.iconLeft}
                    <span>{item.label}</span>
                    {item.rightText !== undefined && (
                      <span style={{
                        marginLeft: 'auto',
                        fontSize: 13, fontWeight: 500,
                        color: item.selected ? '#4A4760' : '#8E8AA6',
                      }}>
                        {item.rightText}
                      </span>
                    )}
                    {item.isCalendarTrigger && (
                      <span style={{ marginLeft: item.rightText !== undefined ? 0 : 'auto' }}>
                        {/* calendar icon handled inline */}
                      </span>
                    )}
                  </button>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div style={{ padding: '0 12px 16px' }}>
            {calendarMode === 'interval' && pendingFrom && (
              <div style={{ padding: '0 4px 8px', fontSize: 13, color: '#8E8AA6', fontFamily: "'Outfit', sans-serif" }}>
                {lang === 'sk' ? 'Vyberte koniec:' : lang === 'cs' ? 'Vyberte konec:' : 'Select end date:'}
              </div>
            )}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 4px 8px' }}>
              <button
                style={{ width: 36, height: 36, borderRadius: 18, border: 'none', background: '#2A2838', color: '#B9B6CC', fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                onClick={prevMonth}
              >‹</button>
              <span style={{ color: '#F4F2FF', fontSize: 16, fontWeight: 600, fontFamily: "'Outfit', sans-serif", textTransform: 'capitalize' }}>
                {monthLabel}
              </span>
              <button
                style={{ width: 36, height: 36, borderRadius: 18, border: 'none', background: '#2A2838', color: '#B9B6CC', fontSize: 18, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                onClick={nextMonth}
              >›</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', padding: '0 0 4px' }}>
              {weekHeaders.map(d => (
                <div key={d} style={{ textAlign: 'center', fontSize: 11, fontWeight: 600, color: '#5D5677', fontFamily: "'Outfit', sans-serif", padding: '4px 0' }}>
                  {d}
                </div>
              ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: 2 }}>
              {cells.map((cell, i) => {
                if (!cell.date) return <div key={`e${i}`} />
                const hasEvent = availableDates ? availableDates.has(cell.date) : true
                const isSelected = cell.date === pendingFrom
                const inRange = isInRange(cell.date)
                const isToday = cell.date === todayStr
                return (
                  <button
                    key={cell.date}
                    disabled={!hasEvent}
                    onClick={() => { if (hasEvent) handleDayClick(cell.date!) }}
                    style={{
                      height: 36, borderRadius: 18, border: 'none',
                      background: isSelected ? '#FF4D8D' : inRange ? '#2A2838' : isToday ? '#2A2838' : 'transparent',
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

            <button
              style={{
                display: 'block', width: '100%', textAlign: 'left',
                padding: '10px 4px', border: 'none', background: 'none',
                fontSize: 15, color: '#7A78A0', cursor: 'pointer',
                fontFamily: "'Outfit', sans-serif", marginTop: 8,
              }}
              onClick={() => { setCalView(false); setPendingFrom(null) }}
            >
              ← {lang === 'en' ? 'Back' : lang === 'cs' ? 'Zpět' : 'Späť'}
            </button>
          </div>
        )}
      </div>
    </>,
    document.body
  )
}

// SVG icons
export const InfinityIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M7 9a3 3 0 1 0 0 6c2 0 3-1.5 5-3s3-3 5-3a3 3 0 1 1 0 6c-2 0-3-1.5-5-3s-3-3-5-3z" />
  </svg>
)

export const CalendarIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <rect x="3" y="5" width="18" height="16" rx="3" />
    <path d="M3 10h18M8 3v4M16 3v4" />
  </svg>
)

export const ChevronDown = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M6 9l6 6 6-6" />
  </svg>
)
