import type { EventIconKey } from '../core/eventType'

interface IconProps {
  size?: number
  color?: string
  strokeWidth?: number
}

const DEFAULT_STROKE = 2

export function IconConcert({ size = 18, color = 'currentColor', strokeWidth = DEFAULT_STROKE }: IconProps) {
  // Lucide guitar-electric (ISC), scaled 1.12
  const sw = strokeWidth * (2 / DEFAULT_STROKE)
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <g transform="translate(12 12) scale(1.12) translate(-12 -12)" strokeWidth={sw * 0.893}>
        <path d="m12.172 11.828 4.242-4.242"/>
        <path d="M16.414 7.586A2 2 0 0017 6.172V5a2 2 0 011.177-1.823L20.59 2.09a1 1 0 011.32 1.32l-1.088 2.412A2 2 0 0119 7h-1a2 2 0 00-1.586.586"/>
        <path d="m6 16 2 2"/>
        <path d="M8.23 9.85a3 3 0 011.28-1.454 1 1 0 011.496.815 4 4 0 003.783 3.783 1 1 0 01.815 1.496 3 3 0 01-1.454 1.28l-.92.38A2 2 0 0012 18a4 4 0 01-4 4 6 6 0 01-6-6 4 4 0 014-4 2 2 0 001.85-1.23z"/>
      </g>
    </svg>
  )
}

export function IconFilm({ size = 18, color = 'currentColor', strokeWidth = DEFAULT_STROKE }: IconProps) {
  // Lucide clapperboard (ISC)
  const sw = strokeWidth * (2 / DEFAULT_STROKE)
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="m12.296 3.464 3.02 3.956"/>
      <path d="M20.2 6 3 11l-.9-2.4c-.3-1.1.3-2.2 1.3-2.5l13.5-4c1.1-.3 2.2.3 2.5 1.3z"/>
      <path d="M3 11h18v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
      <path d="m6.18 5.276 3.1 3.899"/>
    </svg>
  )
}

export function IconStandUp({ size = 18, color = 'currentColor', strokeWidth = DEFAULT_STROKE }: IconProps) {
  const sw = strokeWidth * (2 / DEFAULT_STROKE)
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth={sw} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="6.5" y="1.5" width="11" height="12.5" rx="5.5"/>
      <path d="M6.8 5.5h5.5M6.5 8.3h5.8M6.8 11.1h5.5"/>
      <path d="M12 14v1.5"/>
      <path d="M9.8 15.5h4.4v2.8h-4.4z"/>
      <path d="M12 18.3v4"/>
    </svg>
  )
}

export function IconDance({ size = 18, color = 'currentColor' }: IconProps) {
  // Filled silhouette — no stroke, fill only (exception from outline style)
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <path fill={color} d="M6.81 22.4C6.63 22.22 6.66 22.07 7.37 19.35C8.35 15.61 8.08 16.14 9.93 14.14C11.12 12.84 11.19 12.76 11.15 12.54C11.11 12.36 11.23 12.59 9.19 8.78C8.22 6.97 7.4 5.39 7.35 5.27C7.27 5.03 7.28 4.69 7.37 4.51C7.61 4.05 9.06 1.59 9.15 1.5C9.36 1.28 9.63 1.33 10.01 1.66C10.32 1.93 10.31 1.98 9.47 3.34L8.79 4.42L8.79 4.67C8.79 4.95 8.91 5.21 9.47 6.15C10.05 7.13 10.07 7.14 11.57 7.12L12.59 7.11L12.83 6.99C13.02 6.9 13.17 6.76 13.68 6.19C14.83 4.89 14.78 4.97 15.46 3.22C16.09 1.6 16.12 1.57 16.72 1.82C17.09 1.98 17.17 2.07 17.19 2.37C17.21 2.59 17.18 2.68 16.81 3.68C16.17 5.38 16.21 5.31 14.88 7.02C13.82 8.39 13.84 8.36 13.84 8.64C13.84 8.9 13.88 8.99 14.64 10.41C15.62 12.25 15.69 12.64 15.34 14.19C15.23 14.69 13.8 20.41 13.49 21.59C13.27 22.43 13.17 22.5 12.28 22.5C11.72 22.5 11.7 22.5 11.6 22.4C11.46 22.26 11.46 22.22 11.81 20.83C12.37 18.56 12.78 16.42 12.92 15.07C12.99 14.45 12.98 14.36 12.9 14.36C12.82 14.36 10.12 17.05 9.99 17.25C9.78 17.58 9.7 17.86 9.19 19.84C8.66 21.86 8.61 22.03 8.48 22.22C8.31 22.45 8.14 22.5 7.49 22.5C6.93 22.5 6.91 22.5 6.81 22.4ZM11.33 6.19C9.93 5.82 9.5 4.0 10.59 3.03C11.68 2.05 13.39 2.66 13.65 4.11C13.88 5.4 12.62 6.54 11.33 6.19Z"/>
    </svg>
  )
}

export function IconParty({ size = 18, color = 'currentColor', strokeWidth = DEFAULT_STROKE }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 4h14l-7 8z" />
      <path d="M12 12v7" />
      <path d="M8 20h8" />
      <path d="M15 7l3-4" />
    </svg>
  )
}

export function IconDJ({ size = 18, color = 'currentColor', strokeWidth = DEFAULT_STROKE }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="4" width="18" height="16" rx="3" />
      <circle cx="11" cy="12" r="5" />
      <circle cx="11" cy="12" r="1" />
      <path d="M18 7v6l-3 2" />
    </svg>
  )
}

export function IconCulture({ size = 18, color = 'currentColor', strokeWidth = DEFAULT_STROKE }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 5h9v6a4.5 4.5 0 0 1-9 0z" />
      <path d="M11 10h9v5a4.5 4.5 0 0 1-9 0" />
      <path d="M6.5 8.5h.01M10.5 8.5h.01M14 13h.01M17.5 13h.01" />
    </svg>
  )
}

export function EventTypeIcon({ iconKey, size = 18, color = 'currentColor' }: { iconKey: EventIconKey } & IconProps) {
  if (iconKey === 'party') return <IconParty size={size} color={color} />
  if (iconKey === 'dj') return <IconDJ size={size} color={color} />
  if (iconKey === 'concert') return <IconConcert size={size} color={color} />
  if (iconKey === 'film') return <IconFilm size={size} color={color} />
  if (iconKey === 'standup') return <IconStandUp size={size} color={color} />
  if (iconKey === 'dance') return <IconDance size={size} color={color} />
  return <IconCulture size={size} color={color} />
}

export function IconMap({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M9 4L3 6v14l6-2 6 2 6-2V4l-6 2z" />
      <path d="M9 4v14M15 6v14" />
    </svg>
  )
}

export function IconList({ size = 22, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.1" strokeLinecap="round" aria-hidden="true">
      <path d="M8 6h12M8 12h12M8 18h12" />
      <circle cx="4" cy="6" r="1" />
      <circle cx="4" cy="12" r="1" />
      <circle cx="4" cy="18" r="1" />
    </svg>
  )
}

export function IconBuilding({ size = 22, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.1" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 21V9l8-5 8 5v12" />
      <path d="M9 21v-6h6v6" />
    </svg>
  )
}

export function IconPerson({ size = 22, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.1" strokeLinecap="round" aria-hidden="true">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21a8 8 0 0 1 16 0" />
    </svg>
  )
}

export function IconChevronDown({ size = 16, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M6 9l6 6 6-6" />
    </svg>
  )
}

export function IconChevronLeft({ size = 22, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M15 6l-6 6 6 6" />
    </svg>
  )
}

export function IconFilter({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.4" strokeLinecap="round" aria-hidden="true">
      <path d="M4 7h10M18 7h2M4 17h4M12 17h8" />
      <circle cx="16" cy="7" r="2" />
      <circle cx="10" cy="17" r="2" />
    </svg>
  )
}

export function IconLocation({ size = 22, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" aria-hidden="true">
      <circle cx="12" cy="12" r="4" />
      <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
    </svg>
  )
}

export function IconHeart({ size = 15, color = 'currentColor', filled = false }: IconProps & { filled?: boolean }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24"
      fill={filled ? color : 'none'} stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M19.5 12.6L12 20l-7.5-7.4A5 5 0 1 1 12 6a5 5 0 1 1 7.5 6.6z" />
    </svg>
  )
}

export function IconCheck({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 12l5 5 9-10" />
    </svg>
  )
}

export function IconCalendar({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="5" width="18" height="16" rx="3" />
      <path d="M3 10h18M8 3v4M16 3v4" />
    </svg>
  )
}

export function IconShare({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 3v13M7 8l5-5 5 5" />
      <path d="M5 14v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5" />
    </svg>
  )
}

export function IconInstagram({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="3" y="3" width="18" height="18" rx="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="1" />
    </svg>
  )
}

export function IconExpand({ size = 16, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />
    </svg>
  )
}

export function IconSpotify({ size = 20 }: { size?: number }) {
  // Official Spotify "play" icon (simplified circular mark, brand-compliant)
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="12" fill="#1DB954" />
      <path d="M17.9 10.9C14.7 9 9.35 8.8 6.3 9.75c-.5.15-1-.15-1.15-.6-.15-.5.15-1 .6-1.15C9.65 6.8 15.5 7 19.1 9.15c.45.25.6.85.35 1.3-.25.35-.85.5-1.3.2-.05-.1-.1-.2-.25-.25zM17.75 13.65c-.2.3-.6.4-.9.2-2.6-1.6-6.55-2.1-9.6-1.1-.35.1-.75-.1-.85-.45-.1-.35.1-.75.45-.85 3.5-1.1 7.85-.55 10.8 1.3.3.15.4.6.1.9zM16.6 16.4c-.15.25-.5.3-.75.15-2.25-1.4-5.1-1.7-8.45-.9-.3.05-.6-.1-.65-.4-.05-.3.1-.6.4-.65 3.65-.8 6.8-.45 9.3 1.05.3.1.3.5.15.75z" fill="white" />
    </svg>
  )
}

export function IconNavigate({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 2l9 20-9-4-9 4z" />
    </svg>
  )
}

export function IconGlobe({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  )
}

export function IconPin({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  )
}

export function IconPlusCircle({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="16" />
      <line x1="8" y1="12" x2="16" y2="12" />
    </svg>
  )
}

export function IconCheckCircle({ size = 20, color = 'currentColor' }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <circle cx="12" cy="12" r="10" />
      <polyline points="9 12 11 14 15 10" />
    </svg>
  )
}

export function IconBookmark({ size = 20, color = 'currentColor', filled = false }: IconProps & { filled?: boolean }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24"
      fill={filled ? color : 'none'} stroke={color}
      strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 3h14a1 1 0 0 1 1 1v17l-8-4-8 4V4a1 1 0 0 1 1-1z" />
    </svg>
  )
}
