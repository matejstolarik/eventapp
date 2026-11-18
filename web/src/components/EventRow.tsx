// Task 068/069: event row in Akcie (design.md part 4, block "Zmena 2026-11-18
// večer po 068") and its pieces: 4:3 image, for-you + tag row, meta line.
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

/** Type icon from the map pins (same SVG paths and stroke). */
export function TypeIcon({ iconKey, color, size }: { iconKey: EventIconKey; color: string; size: number }) {
  return (
    <span
      style={{ display: 'flex', width: size, height: size, lineHeight: 0 }}
      dangerouslySetInnerHTML={{ __html: typeIconSvg(iconKey, color, size) }}
    />
  )
}

/** 4:3 event image; without image a dark type area with a large type icon.
 * Task 069: no type ring; optional "new" badge top-right. */
export function EventImage43({ event, width, height, radius = 12, eager = false, isNew = false }: {
  event: Event; width: number | string; height?: number; radius?: number; eager?: boolean; isNew?: boolean
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
        <TypeIcon iconKey={eventIconKey(event.formats, event.primary_format)} color={EVENT_TYPE_COLOR[type]} size={40} />
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

const FOR_YOU_LABEL: Record<Language, string> = { sk: 'pre teba', cs: 'pro tebe', en: 'for you' }

/** One line of pills: "for you" (pink sparkles) first, then the event tags
 * with type-coloured text on #2A2838 (task 069; without tags one tag with the
 * type, eventTags fallback). No wrapping: the line fades out on the right. */
export function BadgeTagRow({ event, lang, forYou, height = 20, fontSize = 11, gap = 4 }: {
  event: Event; lang: Language; forYou: boolean
  height?: number; fontSize?: number; gap?: number
}) {
  const tags = eventTags(event.formats, event.genres, event.primary_format)
  const tagText = EVENT_TYPE_TAG_TEXT[getEventType(event.formats, event.primary_format)]
  const pill: CSSProperties = {
    flex: 'none', height, padding: `0 ${Math.round(height * 0.35)}px`, borderRadius: height / 2,
    fontSize, fontWeight: 500, display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap',
    boxSizing: 'border-box', background: '#2A2838',
  }
  return (
    <div style={{
      display: 'flex', gap, height, overflow: 'hidden',
      WebkitMaskImage: 'linear-gradient(to right, black calc(100% - 24px), transparent)',
      maskImage: 'linear-gradient(to right, black calc(100% - 24px), transparent)',
    }}>
      {forYou && (
        <span style={{ ...pill, padding: `0 ${Math.round(height * 0.3)}px` }} aria-label={FOR_YOU_LABEL[lang]} title={FOR_YOU_LABEL[lang]}>
          <SparkleIcon size={Math.round(height * 0.65)} color="#FF4D8D" />
        </span>
      )}
      {tags.map(tag => (
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

/* Row size (task 069, design.md part 4 block "večer po 068"): the text block
 * of a full row = 2 title lines (14 px x line-height 1.25 = 2 x 17.5) + gap 4
 * + meta line (12 px Outfit, line-height normal = META_LINE_H) + gap 4
 * + tag row (margin 2 + 20). The image has that height and 4:3 width. */
const META_LINE_H = 15
export const ROW_IMG_H = 2 * 17.5 + 4 + META_LINE_H + 4 + 2 + 20
export const ROW_IMG_W = ROW_IMG_H * 4 / 3

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
      <EventImage43 event={event} width={ROW_IMG_W} height={ROW_IMG_H} radius={8} eager={eager} isNew={isNew} />
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
          <BadgeTagRow event={event} lang={lang} forYou={forYou} />
        </div>
      </div>
    </div>
  )
}
