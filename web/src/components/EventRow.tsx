// Task 068/069/070: event row in Akcie (design.md part 4, block "Zmena 2026-11-18
// večer po 068") and its pieces: 4:3 image (new + for-you badges), type icon +
// tag row, meta line.
import { useState, type CSSProperties } from 'react'
import type { Event, Language } from '../core/types'
import type { EventIconKey } from '../core/eventType'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK, EVENT_TYPE_TAG_TEXT, eventTags, eventIconKey } from '../core/eventType'
import { joinDot } from '../core/dot'
import { typeIconSvg } from '../map/markers'
import { formatDayLabel, tagLabel } from '../i18n'

const BASE = import.meta.env.BASE_URL

/** Resolve a pipeline-relative image path ("img/events/x.jpg") against the app base. */
export function imgSrc(path: string): string {
  return /^https?:/.test(path) ? path : `${BASE}${path}`
}

/** Type icon from the map pins (same SVG paths and stroke). `bg` = surface under the icon (task 071, workshop). */
export function TypeIcon({ iconKey, color, size, bg }: { iconKey: EventIconKey; color: string; size: number; bg?: string }) {
  return (
    <span
      style={{ display: 'flex', width: size, height: size, lineHeight: 0 }}
      dangerouslySetInnerHTML={{ __html: typeIconSvg(iconKey, color, size, bg) }}
    />
  )
}

/** 4:3 event image; without image a dark type area with a large type icon.
 * Task 069: no type ring; optional "new" badge top-right.
 * Task 070: optional "for you" sparkles top-left (no background, black outline). */
export function EventImage43({ event, width, height, radius = 12, eager = false, isNew = false, forYou = false, lang = 'sk' }: {
  event: Event; width: number | string; height?: number; radius?: number; eager?: boolean; isNew?: boolean
  forYou?: boolean; lang?: Language
}) {
  const [err, setErr] = useState(false)
  const type = getEventType(event.formats, event.primary_format)
  const hasImg = !!event.image_thumb && !err
  return (
    <div style={{
      width, ...(height ? { height } : { aspectRatio: '4 / 3' }), flexShrink: 0, borderRadius: radius,
      overflow: 'hidden', position: 'relative',
      background: EVENT_TYPE_DARK[type], display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}>
      {hasImg ? (
        <img
          src={imgSrc(event.image_thumb!)} alt="" width={640} height={480} decoding="async"
          loading={eager ? 'eager' : 'lazy'} onError={() => setErr(true)}
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }}
        />
      ) : (
        <TypeIcon iconKey={eventIconKey(event.formats, event.primary_format)} color={EVENT_TYPE_COLOR[type]} size={40} bg={EVENT_TYPE_DARK[type]} />
      )}
      {forYou && (
        <span style={{ position: 'absolute', top: 5, left: 5, zIndex: 2, display: 'flex', lineHeight: 0 }}
          role="img" aria-label={FOR_YOU_LABEL[lang]} title={FOR_YOU_LABEL[lang]}>
          <OutlinedSparkleIcon size={18} color="#FF4D8D" />
        </span>
      )}
      {isNew && (
        // same badge as the pre-068 grid card: white pill, 10/600
        <span style={{ position: 'absolute', top: 5, right: 5, zIndex: 2, height: 18, padding: '0 6px', borderRadius: 9, background: '#F4F2FF', color: '#111118', fontSize: 10, fontWeight: 600, display: 'flex', alignItems: 'center' }}>
          new
        </span>
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

const SPARKLE_PATHS = ['M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z', 'M19 15l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8z']

/** Sparkles on an image (task 070): the same icon drawn twice, a wider black
 * stroke below (round joins and caps = smooth continuous outline, outlinePx
 * per side) and the coloured icon on top. */
export function OutlinedSparkleIcon({ size, color, outlinePx = 1.25 }: { size: number; color: string; outlinePx?: number }) {
  const base = 2.2
  const unit = 24 / size // viewBox units per px
  const pad = Math.ceil(outlinePx * unit)
  return (
    <svg width={size} height={size} viewBox={`${-pad} ${-pad} ${24 + 2 * pad} ${24 + 2 * pad}`} fill="none"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <g stroke="#000" strokeWidth={base + 2 * outlinePx * unit}>{SPARKLE_PATHS.map(d => <path key={d} d={d} />)}</g>
      <g stroke={color} strokeWidth={base}>{SPARKLE_PATHS.map(d => <path key={d} d={d} />)}</g>
    </svg>
  )
}

export const FOR_YOU_LABEL: Record<Language, string> = { sk: 'pre teba', cs: 'pro tebe', en: 'for you' }

/** Type icon pill (task 070): the map pin icon in the type's tag text colour,
 * in a pill like the tags. `background` lets the venue programme keep its own pill colour. */
export function TypeIconPill({ event, height = 20, background = '#2A2838', iconSize = 13 }: {
  event: Event; height?: number; background?: string; iconSize?: number
}) {
  const color = EVENT_TYPE_TAG_TEXT[getEventType(event.formats, event.primary_format)]
  return (
    <span style={{
      flex: 'none', height, padding: `0 ${Math.round(height * 0.3)}px`, borderRadius: height / 2,
      display: 'inline-flex', alignItems: 'center', justifyContent: 'center', boxSizing: 'border-box', background,
    }} aria-hidden="true">
      <TypeIcon iconKey={eventIconKey(event.formats, event.primary_format)} color={color} size={iconSize} bg={background} />
    </span>
  )
}

/** One line of pills: the type icon first (task 070), then the event tags
 * with type-coloured text on #2A2838 (task 069; task 071: no fallback tag, an
 * event without tags shows only the icon pill). Task 072: max 3 tags, only whole tags. */
const MAX_ROW_TAGS = 3

export function BadgeTagRow({ event, lang, height = 20, fontSize = 11, gap = 4 }: {
  event: Event; lang: Language
  height?: number; fontSize?: number; gap?: number
}) {
  const tags = eventTags(event.formats, event.genres, event.primary_format)
  const tagText = EVENT_TYPE_TAG_TEXT[getEventType(event.formats, event.primary_format)]
  const pill: CSSProperties = {
    flex: 'none', height, padding: `0 ${Math.round(height * 0.35)}px`, borderRadius: height / 2,
    fontSize, fontWeight: 500, display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap',
    boxSizing: 'border-box', background: '#2A2838',
  }
  // Task 072: at most 4 pills incl. the icon pill, no fade. flex-wrap with a
  // one-line height hides a tag that does not fit whole: it wraps to the hidden
  // second line, and flex line breaking is in order, so every tag after it too.
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', columnGap: gap, rowGap: gap, height, overflow: 'hidden' }}>
      <TypeIconPill event={event} height={height} />
      {tags.slice(0, MAX_ROW_TAGS).map(tag => (
        <span key={tag} style={{ ...pill, color: tagText }}>{tagLabel(tag, lang)}</span>
      ))}
    </div>
  )
}

/** "date · time · place" on one line; date and time come first, so the
 * ellipsis only ever shortens the place. One string = natural spacing. */
export function MetaLine({ parts, style }: { parts: (string | null | undefined)[]; style?: CSSProperties }) {
  return (
    <div style={{ minWidth: 0, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', ...style }}>
      {joinDot(parts)}
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

/* Row size: task 069 sized the image to the full text block (80 px); task 070
 * (main chat, 4:3) makes row and image 90 px high and the image 120 px wide.
 * The text block (max 80 px) stays vertically centred. */
export const ROW_IMG_H = 90
export const ROW_IMG_W = 120

/** Event row in Akcie: 4:3 image left (fixed size), title / date · time · place /
 * for-you + tags right, vertically centred. Fixed height for every row. */
export function EventRow({ event, venueName, lang, now, isNew, forYou, eager, animIn, onClick }: EventRowProps) {
  return (
    <div
      role="button" tabIndex={0} onClick={onClick} onKeyDown={e => e.key === 'Enter' && onClick()}
      style={{
        display: 'flex', gap: 12, alignItems: 'center', height: ROW_IMG_H, cursor: 'pointer', minWidth: 0,
        ...(animIn ? { animation: 'evCardIn 180ms ease-out both' } : {}),
      }}
    >
      <EventImage43 event={event} width={ROW_IMG_W} height={ROW_IMG_H} radius={8} eager={eager} isNew={isNew} forYou={forYou} lang={lang} />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 4 }}>
        <div style={{
          fontSize: 14, fontWeight: 700, color: '#F4F2FF', lineHeight: 1.25, overflow: 'hidden',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', wordBreak: 'break-word',
        }}>
          {event.title}
        </div>
        <MetaLine
          parts={[formatDayLabel(event.date, lang, now), event.start_time, venueName]}
          style={{ fontSize: 12, fontWeight: 500, color: '#B9B6CC' }}
        />
        <div style={{ marginTop: 2 }}>
          <BadgeTagRow event={event} lang={lang} />
        </div>
      </div>
    </div>
  )
}
