"""
Guards on AI results in code (task 062 part 1, docs/ai-rules.md C2, C3, D, F).

- genre_supported(): a genre stays only when its quote (genre_facts) AND the
  research (step-1 facts + venue page text) contain the genre name, an
  approved alias (data/genre_aliases.json) or a spelling variant, as a whole
  word.  Names of OTHER genres that contain the word are masked first, so a
  parent genre never gets support from a subgenre ("tech house" is no support
  for house, "electronic dance music" none for electronic, "hard techno" none
  for hardcore).
- price_supported(): an AI price stays only when it has an amount or a free /
  voluntary word ("Tba" is no price) and the research or the venue page shows
  that amount / word.
- exclamation marks that are part of the event title or an artist name
  ("FIRE!") are ignored by the description check.
- venue_mentions(): venue / hall names in a description (task 063: counted in
  the log only, no review -- ai-rules F allows them).
- strip_no_info(): sentences about missing information are removed from the
  Czech description (task 063, ai-rules F).
"""

import re
import unicodedata

from pipeline.genres import FILM_GENRES, MUSIC_GENRES, STAGE_GENRES, slug  # noqa: F401
from pipeline.price import parse_price

ALL_GENRES = MUSIC_GENRES | FILM_GENRES | STAGE_GENRES

# Spelling variants not in genre_aliases.json (same word, other spelling /
# Czech spelling of the same word).  Never a different genre.
VARIANTS = {
    "hip-hop": ["hip hop", "hiphop", "rapper", "raper", "raperka", "rapperka"],
    "drum-and-bass": ["drum and bass", "drum n bass", "drumnbass", "dnb", "d and b"],
    "rnb": ["r and b", "rnb", "rn b", "r n b"],
    "electronic": ["elektronick", "electronica", "elektronik"],
    "experimental": ["experimentaln"],
    "industrial": ["industrialn"],
    "uk-garage": ["uk garage", "ukg"],
    "post-punk": ["post punk", "postpunk"],
    # task 065: new genres; "x*" = stem, any ending ("dokumentarn*" ->
    # dokumentární, dokumentárního).  Not a genre: "černobílý" (b/w film).
    "hard-techno": ["hardtechno"],
    "breakbeat": ["break beat"],
    "synthwave": ["synth wave"],
    "post-rock": ["post rock", "postrock"],
    "post-hardcore": ["post hardcore", "posthardcore"],
    "gothic-rock": ["goth rock", "gotick* rock"],
    "classic-rock": ["classic rock", "klasicky rock", "klasickeho rocku", "klasicky rockov*",
                     "dad rock"],
    "pop-punk": ["pop punk", "poppunk"],
    "dance-punk": ["dance punk"],
    "neo-soul": ["neo soul", "neosoul"],
    "psytrance": ["psy trance", "psy-trance"],
    "classical": ["classical music", "vazna hudba", "vazne hudby", "vaznou hudbu",
                  "vazne hudbe", "klasicka hudba", "klasicke hudby", "klasickou hudbu",
                  "klasicke hudbe"],
    "orchestral": ["orchestraln*", "orchestr"],
    "soundtrack": ["soundtracky", "filmova hudba", "filmove hudby", "filmovou hudbu"],
    "chanson": ["sanson", "sansonier*", "sansonov*"],
    "country": ["countryov*"],
    "action": ["akcni*"],
    "adventure": ["dobrodruzn*"],
    "animation": ["animovan*", "animace", "animaci", "animated"],
    "biography": ["biograf*", "zivotopisn*", "biopic"],
    "comedy": ["komedie", "komedii", "komedi", "komediln*"],
    "crime": ["krimi", "kriminaln*"],
    "documentary": ["dokument", "dokumentu", "dokumentarn*", "documentaries"],
    "drama": ["dramatick*", "cinohr*", "cinohern*"],
    "family": ["rodinn*"],
    "history": ["historick*", "historical"],
    "horror": ["horor", "hororov*"],
    "musical": ["muzikal"],
    "mystery": ["mysteriozn*"],
    "romance": ["romanticky film", "romanticke drama", "romantic"],
    "sci-fi": ["sci fi", "scifi", "science fiction", "vedeckofantastick*"],
    "short": ["short film", "short films", "kratkometrazn*", "kratas"],
    "thriller": ["thrilleru", "thrillery"],
    "war": ["valecn*", "war film"],
    "queer": ["lgbt", "lgbtq"],
    "cult-classic": ["cult classic", "cult film", "kultovn*", "kultovk*"],
    "arthouse": ["art house", "artov*", "art film", "artfilm*"],
    "opera": ["opern*"],
    "puppet-theatre": ["puppet theatre", "puppet theater", "loutkov*", "loutkar*"],
    "improv": ["improvizac*", "improvizovan*", "improvisation", "improv comedy"],
    "cabaret": ["kabaret*"],
    "new-circus": ["novy cirkus", "noveho cirkusu", "novem cirkusu", "contemporary circus",
                   "soucasny cirkus", "soucasneho cirkusu"],
    "contemporary-dance": ["contemporary dance", "soucasny tanec", "soucasneho tance",
                           "soucasnem tanci", "soucasnym tancem"],
    "ballet": ["balet*"],
    "dance-theatre": ["dance theatre", "tanecni divadlo", "tanecniho divadla",
                      "tanecnim divadle", "tanztheater"],
}

# Czech / Slovak endings after a genre word ("rockový", "punku", "jazzová")
# (text is compared after plain(): no diacritics, so "rockových" -> "rockovych");
# English plural "s" ("electronics")
_SUFFIX = r"(?:ov(?:a|e|y|ou|ych|eho|ym|ymi|i|u|ej|emu|ich|im)?|u|e|em|y|a|i|ie|s)?"


def plain(s) -> str:
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    s = s.replace("&", " and ")
    s = re.sub(r"['’`]", "", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def _plain_term(v: str) -> str:
    """plain() that keeps the stem marker '*' at word ends."""
    return " ".join(plain(w) + ("*" if w.endswith("*") else "") for w in v.split())


def _term_re(term: str, czech: bool = True) -> re.Pattern:
    if "*" in term:
        # task 065: explicit stems ("dokumentarn*", "romantick* komedi*")
        parts = [re.escape(w[:-1]) + r"[a-z]*" if w.endswith("*") else re.escape(w)
                 for w in term.split()]
        return re.compile(r"(?<![a-z0-9])" + " ".join(parts) + r"(?![a-z0-9])")
    suffix = _SUFFIX if czech else ""
    # Czech stems ("elektronick") take any ending
    if term.endswith(("ick", "aln", "nik")):
        suffix = r"[a-z]*"
    body = re.escape(term)
    if czech and term.endswith("o") and " " not in term and len(term) >= 5:
        # declension of -o words: "techna", "technu", "technem" (Czech)
        body = re.escape(term[:-1]) + r"(?:o|a|u|em|ech)"
        suffix = r"(?:ov(?:a|e|y|ou|ych|eho|ym|i|u|ej|emu)?)?"
    return re.compile(rf"(?<![a-z0-9]){body}{suffix}(?![a-z0-9])")


def genre_terms(genre: str, aliases: dict | None) -> list[str]:
    terms = {plain(genre.replace("-", " "))}
    terms.update(_plain_term(v) for v in VARIANTS.get(genre, []))
    for raw, target in (aliases or {}).items():
        targets = target if isinstance(target, list) else [target]
        if genre in targets:
            terms.add(plain(raw))
    return sorted(t for t in terms if t)


def _other_phrases(genre: str, aliases: dict | None) -> list[str]:
    """Names / aliases of other genres (not mapping to `genre`)."""
    out = []
    for g in ALL_GENRES:
        if g != genre:
            out += [plain(g.replace("-", " "))] + [_plain_term(v) for v in VARIANTS.get(g, [])]
    for raw, target in (aliases or {}).items():
        targets = target if isinstance(target, list) else [target]
        if genre not in targets:
            out.append(plain(raw))
    return out


def _supports(text: str, genre: str, aliases: dict | None) -> bool:
    text = plain(text)
    if not text:
        return False
    terms = genre_terms(genre, aliases)
    # mask longer names of other genres that contain one of our terms
    for ph in sorted(set(_other_phrases(genre, aliases)), key=len, reverse=True):
        if any(_term_re(t, False).search(ph) for t in terms) and ph not in terms:
            text = _term_re(ph, False).sub(" ", text)
    return any(_term_re(t).search(text) for t in terms)


def genre_supported(genre: str, quote: str | None, research_text: str | None,
                    aliases: dict | None) -> tuple[bool, str]:
    if not quote:
        return False, "no genre_facts quote"
    if not _supports(quote, genre, aliases):
        return False, "genre name not in its quote"
    if research_text is not None and not _supports(research_text, genre, aliases):
        return False, "genre name not in the research facts / venue page"
    return True, "ok"


_FREE_RE = re.compile(r"zdarma|zadarmo|free|volny vstup|vstup volny|dobrovoln|bez vstupneho|gratis")


def price_supported(price: str, support_text: str | None) -> tuple[bool, str]:
    p = parse_price(price)
    if not p:
        return False, "no amount and no free / voluntary word"
    if support_text is None:
        return True, "ok"
    text = plain(support_text)
    if p["min"] is not None:
        digits = re.sub(r"(?<=\d) (?=\d{3}\b)", "", text)
        amounts = {str(int(v)) for v in (p["min"], p["max"]) if v is not None}
        missing = [a for a in amounts if not re.search(rf"(?<!\d){a}(?!\d)", digits)]
        if missing:
            return False, f"amount {missing} not in research facts / venue page"
        return True, "ok"
    if not _FREE_RE.search(text):
        return False, "free / voluntary word not in research facts / venue page"
    return True, "ok"


def strip_names(text: str, names: list[str]) -> str:
    """Remove '!' that belongs to a name: words with '!' from the title / an
    artist name (FIRE!), and any '!' inside a sentence -- followed by a
    lower-case word, a comma etc. -- which is part of a title ("alba Exit! a
    Testament", "Hello Mom!, Happy Birthday! i ...").  A '!' that ends a
    sentence (end of text or a capital letter after it) stays."""
    for name in names:
        for word in re.findall(r"\S*!\S*", name or ""):
            word = word.strip(".,;:()[]\"'“”„")
            if word:
                text = re.sub(re.escape(word), " ", text, flags=re.I)
    return re.sub(r"(?<=\w)!+(?=[\"'“”„)]?\s*(?:[,;:)]|[a-zà-ž0-9]))", "", text)


_HALL_RE = re.compile(r"(?<![a-z])(sal[ae]?|salu|salem|stage|hall|mistnost\w*|miestnost\w*|"
                      r"citarn\w*)(?![a-z])")


def venue_mentions(text: str, venue: dict, extra_names: list[str] | None = None) -> list[str]:
    """Venue / hall names found in a description (-> needs_review)."""
    t = plain(text)
    hits = []
    names = [venue.get("name")] + list(extra_names or [])
    for n in names:
        n = plain(n)
        # "Palác Akropolis" -> also "akropolis"; very short words are skipped
        parts = [n] + [w for w in n.split() if len(w) >= 5]
        for p in parts:
            if p and _term_re(p).search(t):
                hits.append(p)
                break
    m = _HALL_RE.search(t)
    if m:
        hits.append(m.group(0))
    return hits


# ---------------------------------------------------------------------------
# Task 063 (docs/ai-rules.md F): a description presents facts, never their
# absence.  Sentences about what was not found / is not known / not published
# or announced, or about the search itself, are removed one by one (Czech,
# before the translation).  Patterns run on plain() text (no diacritics).
# ---------------------------------------------------------------------------

_NEG = r"(?:nejsou|neni|nebyl[aiy]?|nebylo|nebudou)"
_MISSING = (r"(?:zverejnen\w*|uveden\w*|ohlasen\w*|oznamen\w*|k dispozici|dostupn\w*|"
            r"dolozen\w*|jmenovan\w*|popsan\w*|specifikovan\w*|upresnen\w*|potvrzen\w*)")
_NO_INFO = [re.compile(p) for p in (
    rf"\b{_NEG}(?: \w+){{0,8}} {_MISSING}",          # "nejsou ... zveřejněni"
    rf"\b{_MISSING}(?: \w+){{0,3}} {_NEG}\b",        # "ohlášeno nebylo"
    rf"\b{_NEG}(?: \w+){{0,2}} znam[aeyo]?\b",       # "nejsou známé", "není známo"
    r"\bne(?:zverejnil|uvedl|ohlasil|oznamil|upresnil|potvrdil)\w*",
    r"\b(?:nepodarilo|nedochoval\w*|nenasl\w*|nelze (?:dohledat|zjistit|dolozit))",
    r"\b(?:tba|tbc)\b",
    r"\bdostupn\w* (?:zdroj|informac|material|podklad)\w*",   # about the search
    r"\bzustava\w* otevren\w*|\bteprve v priprave\b|\boznamen\w* pozdeji\b",
    r"\b(?:budou|bude|maji byt|ma byt)(?: \w+){0,2} (?:oznamen|ohlasen|zverejnen|upresnen)\w*",
    r"\bstejn\w* (?:jmen|nazv|nazev)\w*",              # other performers with the same name
)]
_SENT_SPLIT = re.compile(r"(?<=[.?!…])\s+(?=[\"„“(]?[A-ZÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ])")
MIN_USABLE_CHARS = 60


# a moved / cancelled event is a fact, even with "new date to be announced"
_KEEP = re.compile(r"\b(?:presun\w*|preloz\w*|zrusen\w*|odlozen\w*)")


def no_info_sentence(sentence: str) -> bool:
    t = plain(sentence)
    return not _KEEP.search(t) and any(p.search(t) for p in _NO_INFO)


def strip_no_info(text: str | None) -> tuple[str | None, list[str]]:
    """Remove sentences about missing information -> (text or None, removed).
    None = nothing usable left (rule H: no AI description)."""
    if not text or not text.strip():
        return None, []
    sents = [s.strip() for s in _SENT_SPLIT.split(text.strip()) if s.strip()]
    removed = [s for s in sents if no_info_sentence(s)]
    if not removed:
        return text, []
    kept = " ".join(s for s in sents if s not in removed)
    return (kept if len(kept) >= MIN_USABLE_CHARS else None), removed
