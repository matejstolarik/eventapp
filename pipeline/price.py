"""
Structured price from a price text (task 058 part 4).

    parse_price("BASIC: 250,-kč | VIP: 400,-kč")
        -> {"min": 250, "max": 400, "currency": "CZK", "kind": "paid"}

`price` = {min, max, currency, kind}; kind: paid | free | voluntary |
free_reservation.  Several prices (reduced, presale / at the door, BASIC /
VIP) -> range min-max.  Only "od X" (from X) -> min without max.  Another
currency is kept.  A text without a recognisable amount or free/voluntary word
-> None (nothing is guessed).  Numbers that are not attached to a currency
(dates, times, "2. vlna", "Praha 5") are ignored; a text that is only numbers
("250–599") is taken as amounts without currency.
"""

import re
import unicodedata

_CUR = r"(?P<cur>kč|kc|czk|eur|€|,-)"
_NUM = r"\d{1,3}(?:[  .,]\d{3})+(?:[.,]\d{2})?(?!\d)|\d+(?:[.,]\d{1,2})?"
# number [– number] currency   |   € number
_AMOUNT_RE = re.compile(
    rf"(?<![\d.,])(?P<a>{_NUM})(?:\s*(?:[–-]|až|to)\s*(?P<b>{_NUM}))?\s*(?:,-\s*)?{_CUR}"
    rf"|(?P<cur2>€|eur)\s*(?P<c>{_NUM})", re.I)
_ONLY_NUMS_RE = re.compile(rf"^\s*(?P<a>{_NUM})(?:\s*[–-]\s*(?P<b>{_NUM}))?\s*$")
_FROM_RE = re.compile(r"(?:^|\s|\()(od|from|ab)\s+\d", re.I)
_FREE_RE = re.compile(r"zdarma|zadarmo|free|volný|volny|gratis|bez vstupného", re.I)
_VOLUNTARY_RE = re.compile(r"dobrovoln|pay what you|dobrovoľn", re.I)
_RESERVATION_RE = re.compile(r"rezervac|rezervác|reservation|booking", re.I)
_NO_RESERVATION_RE = re.compile(r"(don't|do not|no|bez|nepřijímáme)\s+\w*\s*reserv|bez rezerv", re.I)


def _num(s: str) -> float:
    s = s.replace(" ", " ")
    m = re.match(r"^(\d{1,3}(?:[ .,]\d{3})+)(?:[.,](\d{2}))?$", s)
    if m:
        return float(re.sub(r"[ .,]", "", m.group(1)))
    return float(s.replace(",", "."))


def _int(x: float):
    return int(x) if x == int(x) else round(x, 2)


def _currency(raw: str | None) -> str | None:
    if not raw:
        return None
    raw = raw.lower()
    if raw in ("€", "eur"):
        return "EUR"
    return "CZK"   # kč, kc, czk, ",-"


def parse_price(text) -> dict | None:
    if not isinstance(text, str) or not text.strip():
        return None
    t = unicodedata.normalize("NFC", text).strip()
    amounts: list[float] = []
    currency = None
    for m in _AMOUNT_RE.finditer(t):
        if m.group("c"):
            vals, cur = [m.group("c")], m.group("cur2")
        else:
            vals, cur = [m.group("a")] + ([m.group("b")] if m.group("b") else []), m.group("cur")
        amounts += [_num(v) for v in vals]
        currency = currency or _currency(cur)
    if not amounts:
        m = _ONLY_NUMS_RE.match(t)
        if m:
            amounts = [_num(m.group("a"))] + ([_num(m.group("b"))] if m.group("b") else [])
    paid = [a for a in amounts if a > 0]
    if paid:
        lo, hi = min(paid), max(paid)
        if _FROM_RE.search(t) and len(set(paid)) == 1:
            return {"min": _int(lo), "max": None, "currency": currency, "kind": "paid"}
        # single price: min == max; max None only for "od X" (from X)
        return {"min": _int(lo), "max": _int(hi), "currency": currency, "kind": "paid"}
    if _VOLUNTARY_RE.search(t):
        return {"min": None, "max": None, "currency": None, "kind": "voluntary"}
    if _FREE_RE.search(t) or amounts:
        kind = ("free_reservation" if _RESERVATION_RE.search(t) and not _NO_RESERVATION_RE.search(t)
                else "free")
        return {"min": None, "max": None, "currency": None, "kind": kind}
    return None
