import { useEffect } from 'react'
import type { EventsData, Language } from '../core/types'
import { getDict } from '../i18n'
import { getGoing, pruneGoing, setStoredLanguage, getFavorites } from '../core/store'
import { isNew, isForYou } from '../core/search'
import { EventRow } from '../components/EventRow'
import { isEventFinished } from '../core/events'

interface Props {
  data: EventsData | null
  lang: Language
  onLangChange: (lang: Language) => void
  onEventOpen: (eventId: string) => void
}

export function MyAccountPage({ data, lang, onLangChange, onEventOpen }: Props) {
  const dict = getDict(lang)
  const now = new Date()

  useEffect(() => {
    if (data) pruneGoing(data, now)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const venueMap = data ? new Map(data.venues.map(v => [v.id, v])) : new Map()
  const goingIds = getGoing()
  const favorites = getFavorites()
  const goingEvents = data
    ? data.events
        .filter(e => {
          if (!goingIds.has(e.id)) return false
          const venue = venueMap.get(e.venue_id)
          return !isEventFinished(e, now, venue?.closing ?? null, venue?.character ?? [])
        })
        .sort((a, b) => {
          if (a.date !== b.date) return a.date.localeCompare(b.date)
          if (!a.start_time && !b.start_time) return 0
          if (!a.start_time) return 1
          if (!b.start_time) return -1
          return a.start_time.localeCompare(b.start_time)
        })
    : []

  function handleLangChange(newLang: Language) {
    setStoredLanguage(newLang)
    onLangChange(newLang)
  }

  const languages: Language[] = ['sk', 'cs', 'en']

  return (
    <div style={{
      position: 'absolute', inset: 0, overflowY: 'auto',
      paddingBottom: 110
    }}>
      <div style={{ padding: '56px 16px 0' }}>
        <h1 style={{
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 32, fontWeight: 700, marginBottom: 24
        }}>
          {dict.account.title}
        </h1>

        {/* Going list */}
        <section style={{ marginBottom: 32 }}>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#F4F2FF' }}>
            {dict.account.going}
          </h2>
          {goingEvents.length === 0 ? (
            <p style={{ color: '#B9B6CC', fontSize: 15 }}>{dict.account.noGoing}</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              {goingEvents.map(event => (
                <EventRow
                  key={event.id}
                  event={event}
                  venueName={venueMap.get(event.venue_id)?.name ?? event.venue_id}
                  lang={lang}
                  now={now}
                  isNew={isNew(event, now)}
                  forYou={isForYou(event, favorites)}
                  onClick={() => onEventOpen(event.id)}
                />
              ))}
            </div>
          )}
        </section>

        {/* Language selector */}
        <section>
          <h2 style={{ fontSize: 20, fontWeight: 700, marginBottom: 12, color: '#F4F2FF' }}>
            {dict.account.language}
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {languages.map(l => (
              <button
                key={l}
                style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '14px 0', borderBottom: '1px solid #23232F',
                  background: 'none', cursor: 'pointer',
                  color: l === lang ? '#F4F2FF' : '#B9B6CC',
                  fontSize: 17, fontWeight: l === lang ? 700 : 400
                }}
                onClick={() => handleLangChange(l)}
              >
                {dict.account.languages[l]}
                {l === lang && (
                  <span style={{
                    width: 8, height: 8, borderRadius: 4, background: '#FF4D8D'
                  }} />
                )}
              </button>
            ))}
          </div>
        </section>
      </div>
    </div>
  )
}
