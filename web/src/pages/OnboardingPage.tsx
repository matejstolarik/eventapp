import { useEffect, useMemo, useRef, useState } from 'react'
import type { EventsData, Language } from '../core/types'
import { getDict } from '../i18n'
import { pressClass } from '../core/motion'
import { EVENT_TYPE_COLOR } from '../core/eventType'
import { getPreferences, setPreferences, setOnboardingDone, setStoredPeriod, type Preferences } from '../core/store'
import { preferenceGenres, hasMusicType, stepHasPick, type PickStep } from '../core/preferences'
import { useForYouPrefs } from '../core/useForYouPrefs'
import {
  TypeCircle, PlaceSearch, PlacesList, placesFor, TypesPicker, GenresPicker, GenreCounter, PREF_TYPE_ORDER, reducedMotion,
} from '../components/PrefPickers'
import { ForYouChip } from '../components/ForYouChip'
import { FilterButton } from '../components/FilterButton'
import { OutlinedSparkleIcon } from '../components/EventRow'

// Onboarding on a new install (docs/design.md 7c, task 079).

type Step = 'welcome' | 'places' | 'types' | 'genres' | 'done'
const PICK_STEPS: Step[] = ['places', 'types', 'genres']
const PINK = '#FF4D8D'
const FONT = "'Outfit', sans-serif"
const HEAD = "'Bricolage Grotesque', sans-serif"

interface Props {
  data: EventsData
  lang: Language
  /** Called once the overlay is gone; skipped = the welcome Skip was confirmed */
  onClose: (skipped: boolean) => void
}

const primaryBtn: React.CSSProperties = {
  width: '100%', height: 52, borderRadius: 26, border: 0, background: PINK, color: '#1A0710',
  fontFamily: FONT, fontSize: 16, fontWeight: 700, cursor: 'pointer', flex: 'none',
}
const textBtn: React.CSSProperties = {
  height: 44, border: 0, background: 'transparent', color: '#B9B6CC', padding: '0 4px',
  fontFamily: FONT, fontSize: 15, fontWeight: 600, cursor: 'pointer', flex: 'none',
}

function Title({ title, sub, right }: { title: string; sub: string; right?: React.ReactNode }) {
  return (
    <div style={{ flex: 'none' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <h1 style={{ margin: 0, flex: 1, fontFamily: HEAD, fontSize: 28, fontWeight: 700, lineHeight: 1.15, color: '#F4F2FF' }}>{title}</h1>
        {right}
      </div>
      <p style={{ margin: '6px 0 0', fontSize: 15, color: '#B9B6CC' }}>{sub}</p>
    </div>
  )
}

/** Skeleton event row for the done-screen previews (task 080): image in the type
 * colour (optional ✦ badge top left, like the real row), two grey text bars.
 * Identical in both cards. */
function MiniRow({ color, sparkle = false }: { color: string; sparkle?: boolean }) {
  return (
    <div data-testid="onb-mini-row" style={{ display: 'flex', alignItems: 'center', gap: 8, height: 22 }}>
      <span style={{ position: 'relative', width: 30, height: 22, borderRadius: 5, background: color, flex: 'none' }}>
        {sparkle && (
          <span data-testid="onb-mini-sparkle" style={{ position: 'absolute', top: 2, left: 2, display: 'flex', lineHeight: 0 }}>
            <OutlinedSparkleIcon size={10} color={PINK} outlinePx={1} />
          </span>
        )}
      </span>
      <span style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 4 }}>
        <span style={{ height: 5, width: '75%', borderRadius: 3, background: '#3A3A50' }} />
        <span style={{ height: 4, width: '50%', borderRadius: 2, background: '#2E2D3C' }} />
      </span>
    </div>
  )
}

const ROW_GAP = 7
const FOR_YOU_ROWS = [EVENT_TYPE_COLOR.dj, EVENT_TYPE_COLOR.concert, EVENT_TYPE_COLOR.culture, EVENT_TYPE_COLOR.party]
// Filter: 4 rows -> the 2 rows of one type (same colours as on the left)
const FILTER_ROWS = [EVENT_TYPE_COLOR.dj, EVENT_TYPE_COLOR.concert, EVENT_TYPE_COLOR.dj, EVENT_TYPE_COLOR.culture]
const FILTER_KEPT = [EVENT_TYPE_COLOR.dj, EVENT_TYPE_COLOR.dj]
/** Same left column in both done cards; the control is centred in it. */
const DONE_LEFT_COL = 116

function DoneCard({ control, preview, text, testId }: { control: React.ReactNode; preview: React.ReactNode; text: string; testId: string }) {
  return (
    <div data-testid={testId} style={{ background: '#1C1C27', borderRadius: 16, padding: 14, display: 'flex', flexDirection: 'column', gap: 12 }}>
      <div style={{ display: 'grid', gridTemplateColumns: `${DONE_LEFT_COL}px minmax(0, 1fr)`, columnGap: 14, alignItems: 'center' }}>
        <div data-testid="onb-done-control" style={{ display: 'flex', justifyContent: 'center' }}>{control}</div>
        <div style={{ minWidth: 0 }}>{preview}</div>
      </div>
      <p style={{ margin: 0, fontSize: 14, lineHeight: 1.4, color: '#E4E2EE' }}>{text}</p>
    </div>
  )
}

export function OnboardingPage({ data, lang, onClose }: Props) {
  const dict = getDict(lang)
  const t = dict.onboarding
  const [step, setStep] = useState<Step>('welcome')
  const [dir, setDir] = useState<1 | -1>(1)
  const [confirmSkip, setConfirmSkip] = useState(false)
  const [prefs, setPrefsState] = useState<Preferences>(getPreferences)
  const [query, setQuery] = useState('')
  const { favorites } = useForYouPrefs()
  const [reduced] = useState(reducedMotion)
  const [shake, setShake] = useState(0)

  const genres = useMemo(() => preferenceGenres(data.events), [data.events])
  const places = useMemo(() => placesFor(data.venues, query), [data.venues, query])

  function changePrefs(p: Preferences) { setPrefsState(p); setPreferences(p) }

  function nextOf(s: Step): Step {
    if (s === 'welcome') return 'places'
    if (s === 'places') return 'types'
    if (s === 'types') return hasMusicType(prefs) ? 'genres' : 'done'
    return 'done'
  }
  function prevOf(s: Step): Step {
    if (s === 'done') return hasMusicType(prefs) ? 'genres' : 'types'
    if (s === 'genres') return 'types'
    if (s === 'types') return 'places'
    return 'welcome'
  }
  function go(s: Step, d: 1 | -1) { setDir(d); setShake(0); setStep(s) }

  // Task 080: Next without a pick shakes (~300 ms) and vibrates gently; no step change.
  function next() {
    if (!stepHasPick(step as PickStep, prefs, favorites)) {
      setShake(n => n + 1)
      try { navigator.vibrate?.(30) } catch { /* not supported */ }
      return
    }
    go(nextOf(step), 1)
  }

  // System Back: previous step; on the welcome screen like Skip (design 7c).
  const stateRef = useRef({ step, confirmSkip })
  stateRef.current = { step, confirmSkip }
  const closingRef = useRef(false)
  useEffect(() => {
    history.pushState({ onboarding: true }, '', window.location.href)
    function onPop() {
      if (closingRef.current) return
      history.pushState({ onboarding: true }, '', window.location.href)
      const { step: s, confirmSkip: c } = stateRef.current
      if (c) setConfirmSkip(false)
      else if (s === 'welcome') setConfirmSkip(true)
      else go(prevOf(s), -1)
    }
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  function finish(skipped: boolean) {
    if (closingRef.current) return
    closingRef.current = true
    setOnboardingDone()
    setStoredPeriod({ type: 'today' })
    // Drop our history entry, then hand over to the app.
    let done = false
    const end = () => { if (done) return; done = true; window.removeEventListener('popstate', end); onClose(skipped) }
    window.addEventListener('popstate', end)
    history.back()
    setTimeout(end, 400)
  }

  const anim = reduced ? undefined : `onbIn${dir > 0 ? 'R' : 'L'} 200ms cubic-bezier(.2,.8,.2,1)`
  const pickIdx = PICK_STEPS.indexOf(step)

  const topBar = (
    <div style={{ position: 'relative', height: 44, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', flex: 'none' }}>
      <div style={{ position: 'absolute', left: 0, right: 0, display: 'flex', justifyContent: 'center', gap: 8, pointerEvents: 'none' }}>
        {PICK_STEPS.map((s, i) => (
          <span key={s} style={{
            width: i === pickIdx ? 22 : 8, height: 8, borderRadius: 4,
            background: i === pickIdx ? PINK : i < pickIdx ? '#B9B6CC' : '#3A3A50',
            transition: reduced ? 'none' : 'width 200ms',
          }} />
        ))}
      </div>
      <button data-testid="onb-step-skip" style={textBtn} onClick={() => go(nextOf(step), 1)}>{t.skip}</button>
    </div>
  )
  const footer = (label: string, onClick: () => void, testId: string, shakeN = 0) => (
    <div style={{ flex: 'none', padding: '12px 0 calc(16px + env(safe-area-inset-bottom))' }}>
      <button key={shakeN} data-testid={testId} data-shake={shakeN > 0 ? shakeN : undefined} className={pressClass()} style={{
        ...primaryBtn, animation: shakeN > 0 && !reduced ? 'onbShake 300ms ease-in-out' : undefined,
      }} onClick={onClick}>{label}</button>
    </div>
  )

  let body: React.ReactNode
  if (step === 'welcome') {
    body = (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', gap: 18 }}>
        <div style={{ display: 'flex', gap: 12 }}>
          {PREF_TYPE_ORDER.map(type => <TypeCircle key={type} type={type} size={52} filled />)}
        </div>
        <h1 style={{ margin: '10px 0 0', fontFamily: HEAD, fontSize: 34, fontWeight: 700, lineHeight: 1.1, color: '#F4F2FF' }}>{t.welcomeTitle}</h1>
        <p style={{ margin: 0, maxWidth: 320, fontSize: 16, lineHeight: 1.45, color: '#B9B6CC' }}>{t.welcomeText}</p>
      </div>
    )
  } else if (step === 'places') {
    body = (
      <>
        {topBar}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14, padding: '8px 0 10px', flex: 'none' }}>
          <Title title={t.placesTitle} sub={t.placesSub} />
          <PlaceSearch value={query} placeholder={dict.places.search} onChange={setQuery} />
        </div>
        <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', overscrollBehavior: 'contain' }}>
          <PlacesList venues={places} favorites={favorites} />
        </div>
      </>
    )
  } else if (step === 'types') {
    body = (
      <>
        {topBar}
        <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', overscrollBehavior: 'contain', padding: '8px 0 4px', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Title title={t.typesTitle} sub={t.typesSub} />
          <TypesPicker lang={lang} prefs={prefs} onChange={changePrefs} />
        </div>
      </>
    )
  } else if (step === 'genres') {
    body = (
      <>
        {topBar}
        <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', overscrollBehavior: 'contain', padding: '8px 0 4px', display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Title title={t.genresTitle} sub={t.genresSub} right={<GenreCounter n={prefs.genres.length} />} />
          <GenresPicker lang={lang} genres={genres} prefs={prefs} onChange={changePrefs} />
        </div>
      </>
    )
  } else {
    body = (
      <div style={{ flex: 1, minHeight: 0, overflowY: 'auto', padding: '40px 0 4px', display: 'flex', flexDirection: 'column', gap: 14 }}>
        <h1 style={{ margin: '0 0 4px', fontFamily: HEAD, fontSize: 32, fontWeight: 700, color: '#F4F2FF' }}>{t.doneTitle}</h1>
        <DoneCard
          testId="onb-done-for-you"
          control={<ForYouChip active label={dict.events.forYou} inert />}
          preview={<div style={{ display: 'flex', flexDirection: 'column', gap: ROW_GAP }}>
            {FOR_YOU_ROWS.map((c, i) => <MiniRow key={i} color={c} sparkle={i === 0 || i === 2} />)}
          </div>}
          text={t.doneForYou}
        />
        <DoneCard
          testId="onb-done-filter"
          control={<div style={{ pointerEvents: 'none' }} aria-hidden="true"><FilterButton badge={0} label={dict.map.filter} onClick={() => {}} /></div>}
          preview={<div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: ROW_GAP }}>{FILTER_ROWS.map((c, i) => <MiniRow key={i} color={c} />)}</div>
            <svg data-testid="onb-filter-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8E8AA6" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ flex: 'none' }}><path d="M5 12h14M13 6l6 6-6 6" /></svg>
            <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: ROW_GAP }}>
              {FILTER_KEPT.map((c, i) => <MiniRow key={i} color={c} />)}
            </div>
          </div>}
          text={t.doneFilter}
        />
        <p style={{ margin: '2px 0 0', fontSize: 14, lineHeight: 1.4, color: '#8E8AA6' }}>{t.doneAccount}</p>
      </div>
    )
  }

  return (
    <div data-testid="onboarding" style={{
      position: 'fixed', inset: 0, zIndex: 200, background: '#111118', color: '#F4F2FF', fontFamily: FONT,
      overflow: 'hidden',
    }}>
      <style>{`
        @keyframes onbInR { from { opacity: 0; transform: translateX(28px) } to { opacity: 1; transform: none } }
        @keyframes onbInL { from { opacity: 0; transform: translateX(-28px) } to { opacity: 1; transform: none } }
        @keyframes onbFade { from { opacity: 0 } to { opacity: 1 } }
        @keyframes onbShake { 0%, 100% { transform: none } 20% { transform: translateX(-8px) } 40% { transform: translateX(7px) } 60% { transform: translateX(-5px) } 80% { transform: translateX(3px) } }
        @media (prefers-reduced-motion: reduce) { [data-testid="onb-next"] { animation: none !important } }
        @media (prefers-reduced-motion: reduce) { [data-onb-anim] { animation: none !important } }
      `}</style>
      <div key={step} data-onb-anim data-testid={`onb-step-${step}`} style={{
        position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column',
        padding: 'calc(12px + env(safe-area-inset-top)) 20px 0', boxSizing: 'border-box', animation: anim,
      }}>
        {body}
        {step === 'welcome' && (
          <div style={{ flex: 'none', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4, padding: '12px 0 calc(12px + env(safe-area-inset-bottom))' }}>
            <button data-testid="onb-start" className={pressClass()} style={primaryBtn} onClick={() => go('places', 1)}>{t.start}</button>
            <button data-testid="onb-skip" style={textBtn} onClick={() => setConfirmSkip(true)}>{t.skip}</button>
          </div>
        )}
        {(step === 'places' || step === 'types' || step === 'genres') && footer(t.next, next, 'onb-next', shake)}
        {step === 'done' && footer(t.doneButton, () => finish(false), 'onb-finish')}
      </div>

      {confirmSkip && (
        <>
          <div onClick={() => setConfirmSkip(false)} style={{
            position: 'absolute', inset: 0, background: 'rgba(8,8,12,0.6)', zIndex: 1,
            animation: reduced ? undefined : 'onbFade 200ms',
          }} />
          <div role="dialog" aria-label={t.skipTitle} data-testid="onb-skip-confirm" style={{
            position: 'absolute', left: 0, right: 0, bottom: 0, zIndex: 2,
            background: '#1C1C27', borderRadius: '28px 28px 0 0', borderTop: '1px solid #2E2D3C',
            padding: '24px 20px calc(12px + env(safe-area-inset-bottom))',
            display: 'flex', flexDirection: 'column', gap: 8,
            animation: reduced ? undefined : 'onbInUp 220ms cubic-bezier(.2,.8,.2,1)',
          }}>
            <style>{'@keyframes onbInUp { from { transform: translateY(100%) } to { transform: none } }'}</style>
            <h2 style={{ margin: 0, fontFamily: HEAD, fontSize: 24, fontWeight: 700 }}>{t.skipTitle}</h2>
            <p style={{ margin: '0 0 12px', fontSize: 15, lineHeight: 1.4, color: '#B9B6CC' }}>{t.skipText}</p>
            <button data-testid="onb-skip-setup" className={pressClass()} style={primaryBtn} onClick={() => { setConfirmSkip(false); go('places', 1) }}>{t.skipSetUp}</button>
            <button data-testid="onb-skip-confirm-btn" style={{ ...textBtn, alignSelf: 'center' }} onClick={() => finish(true)}>{t.skipConfirm}</button>
          </div>
        </>
      )}
    </div>
  )
}
