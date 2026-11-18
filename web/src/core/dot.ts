// Task 069 part 5: one way to build "x · y" lines everywhere in the app.
// A plain space before and after the dot, no extra margins. Build the whole
// line as one string: whitespace at the start or end of a flex item is
// dropped by the browser, which made the spacing uneven before.

/** The separator: space, middle dot, space. */
export const DOT_SEP = ' · '

/** Join the non-empty parts with " · " ("Dnes · 20:00 · Archa+"). */
export function joinDot(parts: ReadonlyArray<string | null | undefined | false>): string {
  return parts.filter((p): p is string => typeof p === 'string' && p.trim() !== '').join(DOT_SEP)
}

/** Task 072: "2026-11-21" -> "21. 11. 2026" (same in every language). */
export function formatDateDMY(date: string): string {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(date)
  return m ? `${Number(m[3])}. ${Number(m[2])}. ${m[1]}` : date
}
