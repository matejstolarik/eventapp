"""Cancellation / postponement / sold-out marks, shared by all sources (task 067).

Only short markers are checked, never a long description: a title prefix or
suffix ("ZRUŠENO: X", "X (cancelled)"), a short label or a standalone line
("Zrušeno", "Akce zrušena", "Cancelled"), and schema.org metadata
(eventStatus, offers.availability).  A cancellation word inside a sentence
("nic se neruší", "after the cancelled tour ...") or inside a band/show name
("SPITFIRE COMPANY & PAST ►CANCEL") is not a mark.

Results:
  "cancelled"   – the source states the event is cancelled
  "postponed"   – moved/postponed without a new date
  "rescheduled" – moved to a new date: the source usually changed the date
                  already, so the caller only logs it (status stays scheduled)
"""

import re

_CANCEL = r"zru[šs]en[aáoéyý]?|ru[šs][íi]\s+se|odpad[áa]|cancell?ed"
_POSTPONE = r"p[řr]esunut[oaáéý]?|p[řr]elo[žz]en[oaáéý]?|odlo[žz]en[oaáéý]?|postponed"
_RESCHEDULE = r"rescheduled|nov[ýy]\s+term[íi]n"
_SOLD_OUT = r"vyprod[áa]n[oaéý]?|vypredan[éýáo]|sold[\s-]?out"

_WORD = rf"(?P<word>{_CANCEL}|{_POSTPONE}|{_RESCHEDULE}|{_SOLD_OUT})"
_WORD_RE = {
    "cancelled": re.compile(rf"^(?:{_CANCEL})$", re.I),
    "postponed": re.compile(rf"^(?:{_POSTPONE})$", re.I),
    "rescheduled": re.compile(rf"^(?:{_RESCHEDULE})$", re.I),
    "sold_out": re.compile(rf"^(?:{_SOLD_OUT})$", re.I),
}

# Prefix: the word, then a separator (":", "!", "-", "–", "|", "/") or the end.
# "ZRUŠENO Koncert" (no separator) is only accepted when the word is in
# capitals, so a band called "Postponed Dreams" is not a mark.
_PREFIX_RE = re.compile(
    rf"^\s*[\[(]?\s*{_WORD}\s*[\])]?\s*(?P<sep>[:!|/–—\-]+\s*|$)", re.I)
# "[ZRUŠENO] X", "(CANCELLED) X": the brackets are the separator
_PREFIX_BRACKET_RE = re.compile(
    rf"^\s*[\[(]\s*{_WORD}\s*[!.]*\s*[\])]\s*", re.I)
_PREFIX_CAPS_RE = re.compile(
    rf"^\s*{_WORD}\s+(?=\S)", re.I)
# Suffix: "(cancelled)", "[ZRUŠENO]", " - ZRUŠENO", " | cancelled"
_SUFFIX_RE = re.compile(
    rf"(?:\s*[(\[]\s*{_WORD.replace('word', 'w1')}\s*[!.]*\s*[)\]]"
    rf"|\s+[|/–—\-]+\s*{_WORD.replace('word', 'w2')}\s*[!.]*)\s*$", re.I)

# Short label / standalone line: the whole text is the mark, optionally with a
# noun ("Akce zrušena", "Koncert se ruší", "Event cancelled", "ZRUŠENO!").
_NOUN = (r"akce|koncert|koncertu|představení|predstavenie|event|show|concert|"
         r"program|večer|party|termín|se")
_LABEL_RE = re.compile(
    rf"^(?:(?:{_NOUN})\s+)?{_WORD}(?:\s+(?:{_NOUN}))?$", re.I)
_LABEL_MAX = 40
_DATE_RE = re.compile(r"\b\d{1,2}\.\s*\d{1,2}\.|\b\d{4}-\d{2}-\d{2}\b")


def _kind(word: str) -> str:
    word = re.sub(r"\s+", " ", word.strip())
    for kind, rx in _WORD_RE.items():
        if rx.match(word):
            return kind
    return ""


def _status_of(kind: str, rest: str = "") -> str:
    """Map a word kind to a status; a postponement naming a date = rescheduled."""
    if kind == "postponed" and _DATE_RE.search(rest or ""):
        return "rescheduled"
    return kind


def title_marks(title: str) -> dict:
    """Marks at the start or end of an event title.

    Returns {"status": cancelled|postponed|rescheduled|None,
             "sold_out": True|None, "title": title without a postponed
             prefix/suffix, "mark": the matched text or None}.
    Only the postponed mark is removed from the title (data-model.md);
    cancelled and sold-out titles stay as the source gives them.
    """
    out = {"status": None, "sold_out": None, "title": title, "mark": None}
    if not title:
        return out
    rest = title
    for _ in range(2):          # e.g. "VYPRODÁNO: ZRUŠENO: X" – at most two marks
        m = _PREFIX_RE.match(rest) or _PREFIX_BRACKET_RE.match(rest)
        if not m:
            m2 = _PREFIX_CAPS_RE.match(rest)
            m = m2 if m2 and m2.group("word").isupper() else None
        if not m:
            break
        kind = _kind(m.group("word"))
        after = rest[m.end():]
        _apply(out, kind, after, m.group(0).strip())
        if kind == "postponed" and out["status"] == "postponed":
            out["title"] = after.strip()
        rest = after
    m = _SUFFIX_RE.search(rest)
    if m:
        word = m.group("w1") or m.group("w2")
        kind = _kind(word)
        _apply(out, kind, "", m.group(0).strip())
        if kind == "postponed" and out["status"] == "postponed":
            out["title"] = rest[:m.start()].strip()
    return out


def _apply(out: dict, kind: str, rest: str, mark: str) -> None:
    if kind == "sold_out":
        out["sold_out"] = True
        out["mark"] = out["mark"] or mark
        return
    status = _status_of(kind, rest)
    # cancelled wins over postponed, postponed over rescheduled
    order = {"cancelled": 3, "postponed": 2, "rescheduled": 1}
    if status in order and order[status] > order.get(out["status"], 0):
        out["status"] = status
        out["mark"] = mark


def label_marks(labels) -> dict:
    """Marks from short labels / standalone lines (each label checked whole).

    Returns {"status": ..., "sold_out": True|None, "mark": text|None}.
    Labels longer than 40 characters (sentences, descriptions) are ignored.
    """
    out = {"status": None, "sold_out": None, "title": None, "mark": None}
    for label in labels or []:
        kind, text = label_kind(label)
        if kind:
            _apply(out, kind, text, text)
    return out


def label_kind(label) -> "tuple[str, str]":
    """(kind, cleaned text) if the whole label is a mark, else ("", text)."""
    if not isinstance(label, str):
        return "", ""
    text = re.sub(r"\s+", " ", label).strip()
    text = text.strip(" !.*►▶»«•–—-:")
    if not text or len(text) > _LABEL_MAX:
        return "", text
    # "Zrušeno / Cancelled": every part must be a mark of the same kind
    parts = [p.strip() for p in re.split(r"\s*[/|]\s*", text) if p.strip()]
    kinds = set()
    for p in parts:
        m = _LABEL_RE.match(p)
        if not m:
            return "", text
        kinds.add(_kind(m.group("word")))
    if len(kinds) != 1:
        return "", text
    return kinds.pop(), text


def ld_status(event_status) -> "str | None":
    """schema.org eventStatus -> cancelled | postponed | rescheduled | None."""
    if not isinstance(event_status, str):
        return None
    s = event_status.lower()
    if "cancel" in s:
        return "cancelled"
    if "postpon" in s:
        return "postponed"
    if "reschedul" in s:
        return "rescheduled"
    return None


def ld_sold_out(offers) -> "bool | None":
    """True if any schema.org offer has availability SoldOut, else None.

    InStock is not taken as "tickets on sale": the CMSs of our venues write it
    by default (Čitárna Unijazz has InStock with an empty price in USD).
    """
    if isinstance(offers, dict):
        offers = [offers]
    if not isinstance(offers, list):
        return None
    for o in offers:
        if isinstance(o, dict) and "soldout" in str(o.get("availability", "")).lower():
            return True
    return None


def page_status(lines: list, title: str, ld_items: "list | None" = None) -> dict:
    """Status marks on an event page.

    Checks schema.org eventStatus of the first Event item, and the short lines
    near the event title (8 lines before, 15 after the first line that
    contains the title), so a "ZRUŠENO" of another event further down the page
    ("další akce") is not taken.  Without the title on the page only the
    metadata is used.
    """
    out = {"status": None, "sold_out": None, "title": None, "mark": None}
    for item in ld_items or []:
        st = ld_status(item.get("eventStatus"))
        if st:
            _apply(out, st, "", f"eventStatus {item.get('eventStatus')}")
        if ld_sold_out(item.get("offers")):
            out["sold_out"] = True
        break
    key = _fold(title)
    if not key:
        return out
    # every line with the title (the <title> of the page, the heading, ...),
    # at most three
    hits = [i for i, line in enumerate(lines) if key in _fold(line)][:3]
    for idx in hits:
        window = lines[max(0, idx - 8):idx + 16]
        marks = label_marks(window)
        if marks["status"]:
            _apply(out, marks["status"], "", marks["mark"])
        if marks["sold_out"]:
            out["sold_out"] = True
        tm = title_marks(lines[idx])
        if tm["status"]:
            _apply(out, tm["status"], "", tm["mark"])
    return out


def _fold(text) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().casefold()
