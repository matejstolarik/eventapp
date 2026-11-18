// Task 068: shared event row "A3" (design.md part 4, block 2026-11-18) and
// its pieces: type ring (same icons as the map pins), 4:3 image, badge + tag row.
import { useState, type CSSProperties } from 'react'
import type { Event, Language } from '../core/types'
import type { EventIconKey } from '../core/eventType'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK, eventTags, eventIconKey } from '../core/eventType'
import { typeIconSvg } from '../map/markers'
import { formatDayLabel, tagLabel } from '../i18n'

const BASE = import.meta.env.BASE_URL

/** Resolve a pipeline-relative image path ("img/events/x.jpg") against the app base. */
export function imgSrc(path: string): string {
  return /^https?:/.test(path) ? path : `${BASE}${path}`
}

/** Type icon from the map pins (same SVG paths and stroke). */
export function TypeIcon({ iconKey, color, size }: { iconKey: EventIconKey; color: string; size: number }) {
  return (
    <span
      style={{ display: 'flex', width: size, height: size, lineHeight: 0 }}
      dangerouslySetInnerHTML={{ __html: typeIconSvg(iconKey, color, size) }}
    />
  )
}

/** Type ring: type colour fill, dark icon, 2 px #111118 outline. */
export function TypeRing({ event, size = 28, icon = 16, style }: {
  event: Event; size?: number; icon?: number; style?: CSSProperties
}) {
  const type = getEventType(event.formats, event.primary_format)
  return (
    <span
      aria-hidden="true"
      style={{
        position: 'absolute', zIndex: 2, width: size, height: size, borderRadius: '50%',
        boxSizing: 'border-box', border: '2px solid #111118', background: EVENT_TYPE_COLOR[type],
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        ...style,
      }}
    >
      <TypeIcon iconKey={eventIconKey(event.formats, event.primary_format)} color={EVENT_TYPE_DARK[type]} size={icon} />
    </span>
  )
}

/** 4:3 event image with the type ring top-left; without image a dark type
 * area with a large type icon (no ring). */
export function EventImage43({ event, width, eager = false, ringSize = 28, ringIcon = 16 }: {
  event: Event; width: number | string; eager?: boolean; ringSize?: number; ringIcon?: number
}) {
  const [err, setErr] = useState(false)
  const type = getEventType(event.formats, event.primary_format)
  const hasImg = !!event.image_thumb && !err
  return (
    <div style={{
      width, aspectRatio: '4 / 3', flexShrink: 0, borderRadius: 12, overflow: 'hidden', position: 'relative',
      background: EVENT_TYPE_DARK[type], display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      {hasImg ? (
        <>
          <img
            src={imgSrc(event.image_thumb!)} alt="" width={640} height={480} decoding="async"
            loading={eager ? 'eager' : 'lazy'} onError={() => setErr(true)}
            style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }}
          />
          <TypeRing event={event} size={ringSize} icon={ringIcon} style={{ top: 6, left: 6 }} />
        </>
      ) : (
        <TypeIcon iconKey={eventIconKey(event.formats, event.primary_format)} color={EVENT_TYPE_COLOR[type]} size={40} />
      )}
    </div>
  )
}

export function SparkleIcon({ size = 16, color = 'currentColor' }: { size?: number; color?: string }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z" />
      <path d="M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z" />
    </svg>
  )
}

const FOR_YOU_LABEL: Record<Language, string> = { sk: 'pre teba', cs: 'pro tebe', en: 'for you' }

/** One line of pills: "new" (white, first), "for you" (sparkles), then grey
 * event tags. Tags that do not fit drop off the end (wrap into a hidden
 * second line); badges come first so they stay. Nothing when empty. */
export function BadgeTagRow({ event, lang, isNew, forYou, height = 20, fontSize = 11, gap = 4 }: {
  event: Event; lang: Language; isNew: boolean; forYou: boolean
  height?: number; fontSize?: number; gap?: number
}) {
  const tags = eventTags(event.formats, event.genres, event.primary_format)
  if (!tags.length && !isNew && !forYou) return null
  const pill: CSSProperties = {
    flex: 'none', height, padding: `0 ${Math.round(height * 0.35)}px`, borderRadius: height / 2,
    fontSize, fontWeight: 500, display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap',
    boxSizing: 'border-box',
  }
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap, height, overflow: 'hidden' }}>
      {isNew && <span style={{ ...pill, background: '#F4F2FF', color: '#111118' }}>new</span>}
      {forYou && (
        <span style={{ ...pill, background: '#2A2838', padding: `0 ${Math.round(height * 0.3)}px` }} aria-label={FOR_YOU_LABEL[lang]} title={FOR_YOU_LABEL[lang]}>
          <SparkleIcon size={Math.round(height * 0.65)} color="#FF4D8D" />
        </span>
      )}
      {tags.map(tag => (
        <span key={tag} style={{ ...pill, background: '#2A2838', color: '#E4DEFF' }}>{tagLabel(tag, lang)}</span>
      ))}
    </div>
  )
}

/** "date · time · place" on one line; only the place is shortened with "…". */
export function MetaLine({ parts, place, style }: { parts: string[]; place?: string | null; style?: CSSProperties }) {
  const head = parts.filter(Boolean).join(' · ')
  return (
    <div style={{ display: 'flex', minWidth: 0, whiteSpace: 'nowrap', ...style }}>
      <span style={{ flexShrink: 0 }}>{head}{place && head ? ' · ' : ''}</span>
      {place && <span style={{ minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis' }}>{place}</span>}
    </div>
  )
}

interface EventRowProps {
  event: Event
  venueName?: string | null
  lang: Language
  now: Date
  isNew: boolean
  forYou: boolean
  eager?: boolean
  animIn?: boolean
  onClick: () => void
}

/** Row A3: 4:3 image (45 %) left, title / date · time · place / badges + tags right. */
export function EventRow({ event, venueName, lang, now, isNew, forYou, eager, animIn, onClick }: EventRowProps) {
  return (
    <div
      role="button" tabIndex={0} onClick={onClick} onKeyDown={e => e.key === 'Enter' && onClick()}
      style={{
        display: 'flex', gap: 12, alignItems: 'center', cursor: 'pointer', minWidth: 0,
        ...(animIn ? { animation: 'evCardIn 180ms ease-out both' } : {}),
      }}
    >
      <EventImage43 event={event} width="45%" eager={eager} />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div style={{
          fontSize: 14, fontWeight: 700, color: '#F4F2FF', lineHeight: 1.25, overflow: 'hidden',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', wordBreak: 'break-word',
        }}>
          {event.title}
        </div>
        <MetaLine
          parts={[formatDayLabel(event.date, lang, now), event.start_time ?? '']}
          place={venueName}
          style={{ fontSize: 12, fontWeight: 500, color: '#B9B6CC' }}
        />
        <div style={{ marginTop: 2 }}>
          <BadgeTagRow event={event} lang={lang} isNew={isNew} forYou={forYou} />
        </div>
      </div>
    </div>
  )
}
