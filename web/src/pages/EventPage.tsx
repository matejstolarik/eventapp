import React, { useState, useEffect, useRef } from 'react'
import type { EventsData, Language } from '../core/types'
import { getEventType, EVENT_TYPE_COLOR, EVENT_TYPE_DARK, EVENT_TYPE_TAG_TEXT, primaryTypeTag, eventIconKey } from '../core/eventType'
import { joinDot, DOT_SEP } from '../core/dot'
import { isGoing, toggleGoing } from '../core/store'
import { haversine, formatDistance } from '../core/distance'
import { getDict, formatEventDate, tagLabel } from '../i18n'
import { isEventLive } from '../core/events'
import { eventDescription, spotifyUrl, priceLabel } from '../core/eventText'
import { isNightMode, NIGHT_DAY } from '../core/night'
import { buildAndroidCalendarIntent, generateICS } from '../core/calendar'
import {
  IconChevronLeft, IconExpand, IconCalendar,
  IconShare, IconSpotify, IconNavigate, IconPin, IconBookmark, EventTypeIcon
} from '../icons'
import { imgSrc } from '../components/EventRow'

interface Props {
  eventId: string
  data: EventsData
  lang: Language
  userLocation: { lat: number; lng: number } | null
  onBack: () => void
  onVenueOpen?: (venueId: string) => void
  onGoToMap?: (venueId: string, date: string) => void
}


export function EventPage({ eventId, data, lang, userLocation, onBack, onVenueOpen, onGoToMap }: Props) {
  const dict = getDict(lang)
  const event = data.events.find(e => e.id === eventId)
  const [going, setGoing] = useState(() => isGoing(eventId))
  const [heroErr, setHeroErr] = useState(0)
  const [showPoster, setShowPoster] = useState(false)
  const posterHistoryRef = useRef(false)
  const [toast, setToast] = useState<string | null>(null)

  useEffect(() => {
    setGoing(isGoing(eventId))
  }, [eventId])

  useEffect(() => {
    if (!showPoster) return
    history.pushState({ poster: true }, '')
    posterHistoryRef.current = true
    function onPopState() {
      if (posterHistoryRef.current) {
        posterHistoryRef.current = false
        setShowPoster(false)
      }
    }
    window.addEventListener('popstate', onPopState)
    return () => {
      window.removeEventListener('popstate', onPopState)
      if (posterHistoryRef.current) {
        posterHistoryRef.current = false
        history.back()
      }
    }
  }, [showPoster]) // eslint-disable-line react-hooks/exhaustive-deps

  function showToast(msg: string) {
    setToast(msg)
    setTimeout(() => setToast(null), 2000)
  }

  if (!event) {
    return (
      <div style={{
        position: 'absolute', inset: 0, background: '#111118',
        display: 'flex', flexDirection: 'column', alignItems: 'center',

        justifyContent: 'center', gap: 16, padding: 24, zIndex: 50
      }}>
        <p style={{ fontSize: 20, fontWeight: 600 }}>{dict.event.notFound}</p>
        <button
          style={{
            height: 48, padding: '0 24px', borderRadius: 24,
            background: '#FF4D8D', color: '#1A0710', fontSize: 16, fontWeight: 700
          }}
          onClick={onBack}
        >
          {dict.event.backToMap}
        </button>
      </div>
    )
  }

  const ev = event
  const venue = data.venues.find(v => v.id === ev.venue_id)
  const eventType = getEventType(ev.formats, ev.primary_format)
  const iconKey = eventIconKey(ev.formats, ev.primary_format)
  const color = EVENT_TYPE_COLOR[eventType]
  const dark = EVENT_TYPE_DARK[eventType]

  const dateLabel = formatEventDate(ev.date, lang)
  const description = eventDescription(ev, lang)
  const price = priceLabel(ev, lang)
  const metaLine = joinDot([dateLabel, ev.start_time])

  const distStr = userLocation && venue
    ? DOT_SEP + formatDistance(haversine(venue.lat, venue.lng, userLocation.lat, userLocation.lng), lang)
    : ''

  const sourceUrl = ev.sources[0]?.url ?? '#'
  const shareUrl = `${window.location.origin}${window.location.pathname}#/akcia/${eventId}`

  function handleTickets() {
    window.open(ev.ticket_url ?? sourceUrl, '_blank', 'noopener')
  }
  function handleGoing() {
    const newState = toggleGoing(eventId)
    setGoing(newState)
    showToast(newState ? dict.event.addedToGoing : dict.event.removedFromGoing)
  }

  function handleGoToMap() {
    if (!venue || !onGoToMap) return
    const now = new Date()
    const isLive = isEventLive(ev, now, venue.closing, venue.character)
    const isNight = isNightMode(data, now)
    onGoToMap(venue.id, isLive && isNight ? NIGHT_DAY : ev.date)
  }
  function downloadIcs() {
    const venueForIcs = venue ? {
      name: venue.name,
      address: venue.address,
      closing: venue.closing,
      character: venue.character,
    } : undefined
    const ics = generateICS(ev, venueForIcs, shareUrl)
    const blob = new Blob([ics], { type: 'text/calendar' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${ev.title.slice(0, 40).replace(/[^a-z0-9]/gi, '-')}.ics`
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleCalendar() {
    if (/Android/i.test(navigator.userAgent)) {
      const intentUrl = buildAndroidCalendarIntent(ev, venue ? {
        name: venue.name,
        address: venue.address,
        closing: venue.closing,
        character: venue.character,
      } : undefined, sourceUrl)
      // Try system calendar via Chrome intent; fall back to .ics after 1.5s if page stays visible
      let opened = false
      function onVisChange() {
        if (document.hidden) { opened = true }
      }
      document.addEventListener('visibilitychange', onVisChange)
      window.location.href = intentUrl
      setTimeout(() => {
        document.removeEventListener('visibilitychange', onVisChange)
        if (!opened) downloadIcs()
      }, 1500)
    } else {
      downloadIcs()
    }
  }
  async function handleShare() {
    if (navigator.share) {
      try { await navigator.share({ title: ev.title, url: shareUrl }) } catch { /* cancelled */ }
    } else {
      try { await navigator.clipboard.writeText(shareUrl) } catch { /* ignore */ }
      showToast(dict.event.linkCopied)
    }
  }
  const spotify = spotifyUrl(ev)
  function handleSpotify() {
    if (spotify) window.open(spotify, '_blank', 'noopener')
  }
  function handleNavigate() {
    if (venue) {
      window.open(`https://www.google.com/maps/dir/?api=1&destination=${venue.lat},${venue.lng}`, '_blank', 'noopener')
    }
  }

  // Task 069: tags exactly as before 068 - first the full-colour type tag
  // (legend of the colours), then culture subtypes and genres with type-coloured text.
  const primaryTag = primaryTypeTag(ev.formats, ev.primary_format)
  const remainingTags = [
    ...ev.formats.filter(f => ['theatre','dance','talk','performance','stand-up','film','opening','workshop','quiz'].includes(f) && f !== primaryTag),
    ...ev.genres,
  ]
  const heroCandidates = [ev.image_detail, ev.image_url].filter((x): x is string => !!x)
  const heroSrc = heroCandidates[heroErr] ? imgSrc(heroCandidates[heroErr]!) : null
  // Task 069: reserve the image box before the image loads (no layout jump).
  // Known size only for image_detail; the image_url fallback sizes itself.
  const heroSize = heroErr === 0 && ev.image_detail && ev.image_detail_size ? ev.image_detail_size : null
  const backButton = (
    <button
      style={{
        position: 'absolute', top: 52, left: 16,
        width: 44, height: 44, borderRadius: 22,
        background: 'rgba(17,17,24,0.7)', color: '#F4F2FF',
        display: 'flex', alignItems: 'center', justifyContent: 'center'
      }}
      onClick={onBack}
      aria-label={dict.event.back}
    >
      <IconChevronLeft size={22} />
    </button>
  )

  return (
    <div style={{
      position: 'absolute', inset: 0, background: '#111118',
      overflowY: 'auto', zIndex: 50
    }}>
      {/* Image (task 068/069): whole image uncropped, max 50 % of the screen
          height, centred on #111118. With image_detail_size the box has its
          final size from the first frame (dark area until the image arrives). */}
      {heroSrc ? (
        <div style={{ position: 'relative', width: '100%', background: '#111118', display: 'flex', justifyContent: 'center' }}>
          <div style={heroSize ? {
            position: 'relative', lineHeight: 0, background: '#1C1C27',
            width: `min(100%, calc(50vh * ${heroSize[0]} / ${heroSize[1]}))`,
            aspectRatio: `${heroSize[0]} / ${heroSize[1]}`,
          } : { position: 'relative', lineHeight: 0, maxWidth: '100%' }}>
            <img
              src={heroSrc} alt=""
              onError={() => setHeroErr(e => e + 1)}
              style={heroSize
                ? { display: 'block', width: '100%', height: '100%' }
                : { display: 'block', maxWidth: '100%', maxHeight: '50vh', width: 'auto', height: 'auto' }}
            />
            <button
              style={{
                position: 'absolute', bottom: 12, right: 12,
                height: 36, padding: '0 12px', borderRadius: 18,
                background: 'rgba(17,17,24,0.7)', color: '#F4F2FF',
                display: 'flex', alignItems: 'center', gap: 6,
                fontSize: 13, fontWeight: 600, lineHeight: 1
              }}
              onClick={() => setShowPoster(true)}
              aria-label={dict.event.poster}
            >
              <IconExpand size={16} />
              {dict.event.poster}
            </button>
          </div>
          {backButton}
        </div>
      ) : (
        <div style={{ position: 'relative', width: '100%', paddingTop: '100%' }}>
          <div style={{ position: 'absolute', inset: 0, background: color, overflow: 'hidden' }}>
            <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <EventTypeIcon iconKey={iconKey} size={80} color={dark} />
            </div>
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(180deg, rgba(17,17,24,0) 55%, #111118 100%)' }} />
          </div>
          {backButton}
        </div>
      )}

      {/* Content */}
      <div style={{ padding: '0 16px 100px' }}>
        {/* Title */}
        <h1 style={{
          margin: '16px 0 8px',
          fontFamily: "'Bricolage Grotesque', sans-serif",
          fontSize: 28, fontWeight: 700,
          lineHeight: 1.08, letterSpacing: '-0.02em'
        }}>
          {ev.title}
        </h1>

        {/* Venue */}
        <p style={{ fontSize: 17, fontWeight: 700, marginBottom: 6 }}>
          {venue && onVenueOpen ? (
            <span
              onClick={() => onVenueOpen(venue.id)}
              style={{ cursor: 'pointer', borderBottom: '1px solid #5D5677' }}
            >
              {venue.name}
            </span>
          ) : (
            venue?.name ?? ev.venue_id
          )}
          {distStr && <span style={{ color: '#B9B6CC', fontWeight: 400 }}>{distStr}</span>}
        </p>

        {/* Meta */}
        <p style={{ fontSize: 15, color: '#B9B6CC', marginBottom: 12 }}>
          {metaLine}
        </p>

        {/* Tags row — with bookmark on right when no price and no sold_out (case c) */}
        {(primaryTag || remainingTags.length > 0) && (
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: 6, marginBottom: 12 }}>
            <div style={{ flex: 1, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {primaryTag && (
                <span style={{
                  height: 24, padding: '0 10px', borderRadius: 12,
                  background: color, color: dark, fontSize: 12, fontWeight: 600,
                  display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap'
                }}>{tagLabel(primaryTag, lang)}</span>
              )}
              {remainingTags.map(tag => (
                <span key={tag} style={{
                  height: 24, padding: '0 10px', borderRadius: 12,
                  background: '#2A2838', color: EVENT_TYPE_TAG_TEXT[eventType], fontSize: 12, fontWeight: 600,
                  display: 'inline-flex', alignItems: 'center', whiteSpace: 'nowrap'
                }}>{tagLabel(tag, lang)}</span>
              ))}
            </div>
            {/* Case (c): no price, no sold_out → bookmark on tag row */}
            {!price && !ev.sold_out && (
              <button
                style={{
                  width: 40, height: 40, borderRadius: 20, flexShrink: 0, marginTop: -8,
                  background: going ? '#FF4D8D' : '#1C1C27',
                  border: going ? 'none' : '1.5px solid #5D5677',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  WebkitTapHighlightColor: 'transparent',
                }}
                onClick={handleGoing}
                aria-label={going ? dict.event.removedFromGoing : dict.event.addedToGoing}
              >
                <IconBookmark size={18} color={going ? '#1A0710' : '#F4F2FF'} filled={going} />
              </button>
            )}
          </div>
        )}

        {/* Case (a): has price → price + bookmark row */}
        {price && (
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20, minHeight: 40 }}>
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                fontSize: 17, fontWeight: 600,
                color: ev.sold_out ? '#5D5677' : '#F4F2FF',
                textDecoration: ev.sold_out ? 'line-through' : 'none'
              }}>
                {price}
              </span>
              {ev.sold_out && (
                <span style={{
                  padding: '2px 8px', borderRadius: 10,
                  background: '#3A1420', color: '#FF8FB0',
                  fontSize: 12, fontWeight: 600
                }}>
                  {dict.event.soldOut}
                </span>
              )}
            </div>
            <button
              style={{
                width: 40, height: 40, borderRadius: 20, flexShrink: 0,
                background: going ? '#FF4D8D' : '#1C1C27',
                border: going ? 'none' : '1.5px solid #5D5677',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                WebkitTapHighlightColor: 'transparent',
              }}
              onClick={handleGoing}
              aria-label={going ? dict.event.removedFromGoing : dict.event.addedToGoing}
            >
              <IconBookmark size={18} color={going ? '#1A0710' : '#F4F2FF'} filled={going} />
            </button>
          </div>
        )}

        {/* Case (b): no price, sold_out → sold_out row + bookmark */}
        {!price && ev.sold_out && (
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: 20, minHeight: 32 }}>
            <div style={{ flex: 1 }}>
              <span style={{
                padding: '2px 8px', borderRadius: 10,
                background: '#3A1420', color: '#FF8FB0',
                fontSize: 12, fontWeight: 600
              }}>
                {dict.event.soldOut}
              </span>
            </div>
            <button
              style={{
                width: 40, height: 40, borderRadius: 20, flexShrink: 0,
                background: going ? '#FF4D8D' : '#1C1C27',
                border: going ? 'none' : '1.5px solid #5D5677',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                WebkitTapHighlightColor: 'transparent',
              }}
              onClick={handleGoing}
              aria-label={going ? dict.event.removedFromGoing : dict.event.addedToGoing}
            >
              <IconBookmark size={18} color={going ? '#1A0710' : '#F4F2FF'} filled={going} />
            </button>
          </div>
        )}

        {/* Main CTA */}
        <button
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            width: '100%', height: 54, borderRadius: 27,
            background: '#FF4D8D', color: '#1A0710',
            fontSize: 17, fontWeight: 700, marginBottom: 12
          }}
          onClick={handleTickets}
        >
          {ev.ticket_url ? dict.event.tickets : dict.event.website}
        </button>

        {/* Secondary actions: Spotify (only with a verified link) · Kalendár · Zdieľať · Na mape · Navigovať */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          {([
            ...(spotify ? [{ label: dict.event.spotify, onClick: handleSpotify, icon: <IconSpotify size={18} /> }] : []),
            { label: dict.event.calendar, onClick: handleCalendar, icon: <IconCalendar size={18} color="#F4F2FF" /> },
            { label: dict.event.share, onClick: handleShare, icon: <IconShare size={18} color="#F4F2FF" /> },
            ...(venue && onGoToMap ? [{ label: dict.event.onMap, onClick: handleGoToMap, icon: <IconPin size={18} color="#F4F2FF" /> }] : []),
            ...(venue ? [{ label: dict.event.navigate, onClick: handleNavigate, icon: <IconNavigate size={18} color="#F4F2FF" /> }] : []),
          ] as { label: string; onClick: () => void; icon: React.ReactNode }[]).map(({ label, onClick, icon }) => (
            <button
              key={label}
              style={{
                flex: 1, height: 64, borderRadius: 18,
                background: '#1C1C27', color: '#F4F2FF',
                display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'center', gap: 4,
                fontSize: 11, fontWeight: 600, border: 'none', cursor: 'pointer',
                WebkitTapHighlightColor: 'transparent',
              }}
              onClick={onClick}
            >
              {icon}
              {label}
            </button>
          ))}
        </div>

        {/* Description */}
        {description && (
          <p style={{ fontSize: 14, lineHeight: 1.5, color: '#B9B6CC' }}>
            {description}
          </p>
        )}
      </div>

      {/* Full-screen poster overlay */}
      {showPoster && ev.image_url && (
        <div
          style={{
            position: 'fixed', inset: 0, background: '#000', zIndex: 200,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}
          onClick={() => setShowPoster(false)}
        >
          <img src={ev.image_url} alt={ev.title}
            style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }} />
          <button
            style={{
              position: 'absolute', top: 52, left: 16,
              width: 44, height: 44, borderRadius: 22,
              background: 'rgba(0,0,0,0.6)', color: '#fff',
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}
            onClick={() => setShowPoster(false)}
            aria-label={dict.event.back}
          >
            <IconChevronLeft size={22} />
          </button>
        </div>
      )}

      {/* Toast */}
      {toast && (
        <div style={{
          position: 'fixed', bottom: 120, left: '50%', transform: 'translateX(-50%)',
          background: '#2A2838', color: '#F4F2FF', padding: '10px 20px',
          borderRadius: 20, fontSize: 14, fontWeight: 600, zIndex: 300,
          whiteSpace: 'nowrap', boxShadow: '0 4px 20px rgba(0,0,0,0.5)'
        }}>
          {toast}
        </div>
      )}
    </div>
  )
}
