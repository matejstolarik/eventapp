import { Fragment, useMemo, useState } from 'react'
import type { EventsData, Language } from '../core/types'
import { getDict } from '../i18n'
import { getPreferences, setPreferences, type Preferences } from '../core/store'
import { preferenceGenres, hasMusicType, PREF_SECTION_ORDER } from '../core/preferences'
import { useForYouPrefs } from '../core/useForYouPrefs'
import { PlaceSearch, PlacesList, placesFor, TypesPicker, GenresPicker, GenreCounter } from '../components/PrefPickers'

// My account → Event preferences (docs/design.md 7c, tasks 079, 080): the onboarding's
// three pickers one under another (types, genres, places); every change is saved at once.

interface Props {
  data: EventsData
  lang: Language
  onBack: () => void
}

function SectionTitle({ title, sub, right }: { title: string; sub: string; right?: React.ReactNode }) {
  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <h2 style={{ margin: 0, flex: 1, fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: 22, fontWeight: 700, color: '#F4F2FF' }}>{title}</h2>
        {right}
      </div>
      <p style={{ margin: '4px 0 0', fontSize: 14, color: '#B9B6CC' }}>{sub}</p>
    </div>
  )
}

const sectionStyle: React.CSSProperties = { display: 'flex', flexDirection: 'column', gap: 16 }

export function PreferencesPage({ data, lang, onBack }: Props) {
  const dict = getDict(lang)
  const t = dict.onboarding
  const [prefs, setPrefsState] = useState<Preferences>(getPreferences)
  const [query, setQuery] = useState('')
  const { favorites } = useForYouPrefs()
  const genres = useMemo(() => preferenceGenres(data.events), [data.events])
  const places = useMemo(() => placesFor(data.venues, query), [data.venues, query])

  function change(p: Preferences) { setPrefsState(p); setPreferences(p) }

  const showGenres = prefs.types.length === 0 || hasMusicType(prefs)

  return (
    <div data-testid="preferences-page" style={{
      position: 'absolute', inset: 0, overflowY: 'auto', overscrollBehaviorY: 'contain',
      fontFamily: "'Outfit', sans-serif", color: '#F4F2FF',
    }}>
      {/* Header scrolls with the page; the tick closes it like Back (every change is already saved, task 080) */}
      <div style={{ padding: '12px 16px 0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 4 }}>
        <button onClick={onBack} aria-label={dict.prefs.back} style={{
          width: 44, height: 44, marginLeft: -10, border: 0, background: 'transparent', color: '#F4F2FF',
          display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
        }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6" /></svg>
        </button>
        <button data-testid="preferences-done" onClick={onBack} aria-label={dict.prefs.done} style={{
          width: 44, height: 44, borderRadius: 22, border: 0, background: '#23232F', color: '#F4F2FF', flex: 'none',
          display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer',
        }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 12l5 5 9-10" /></svg>
        </button>
      </div>
      <div style={{ padding: '4px 16px 40px', display: 'flex', flexDirection: 'column', gap: 40 }}>
        <h1 style={{ margin: '0 0 -20px', fontFamily: "'Bricolage Grotesque', sans-serif", fontSize: 32, fontWeight: 700 }}>{dict.prefs.title}</h1>
        {PREF_SECTION_ORDER.map(sec => (
          <Fragment key={sec}>
            {sec === 'types' && (
              <section data-testid="pref-section-types" style={sectionStyle}>
                <SectionTitle title={t.typesTitle} sub={t.typesSub} />
                <TypesPicker lang={lang} prefs={prefs} onChange={change} keepOne />
              </section>
            )}
            {sec === 'genres' && showGenres && (
              <section data-testid="pref-section-genres" style={sectionStyle}>
                <SectionTitle title={t.genresTitle} sub={t.genresSub} right={<GenreCounter n={prefs.genres.length} />} />
                <GenresPicker lang={lang} genres={genres} prefs={prefs} onChange={change} />
              </section>
            )}
            {sec === 'places' && (
              <section data-testid="pref-section-places" style={sectionStyle}>
                <SectionTitle title={t.placesTitle} sub={t.placesSub} />
                <PlaceSearch value={query} placeholder={dict.places.search} onChange={setQuery} />
                <PlacesList venues={places} favorites={favorites} />
              </section>
            )}
          </Fragment>
        ))}
      </div>
    </div>
  )
}
