import type { EventType } from '../core/types'

interface IconProps {
  size?: number
  color?: string
  strokeWidth?: number
}

const DEFAULT_STROKE = 2

export function IconConcert({ size = 18, color = 'currentColor', strokeWidth = DEFAULT_STROKE }: IconProps) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color}
      strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <g transform="translate(12 12) scale(1.057) translate(-14.12 -11.09)" strokeWidth={strokeWidth * 0.945}>
        <g transform="rotate(45 12 12)">
          <circle cx="12" cy="5" r="4" />
          <path d="M8.3 6.5h7.4" />
          <path d="M9.6 9.2L10.6 17h2.8l1-7.8" />
        </g>
        <path d="M8.5 15.5C6.6 17.4 6.2 19.6 7.6 20.5c1.4.9 2.9-.5 4.4-2 1.5-1.5 3.6-2 5 0l1 1.5" />
      </g>
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

export function EventTypeIcon({ type, size = 18, color = 'currentColor' }: { type: EventType } & IconProps) {
  if (type === 'party') return <IconParty size={size} color={color} />
  if (type === 'dj') return <IconDJ size={size} color={color} />
  if (type === 'concert') return <IconConcert size={size} color={color} />
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
