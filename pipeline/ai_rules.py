"""
Prompt texts built from docs/ai-rules.md (source of truth, task 058).

Shared by AI classification (classify_ai.py, no web) and AI enrichment
(enrich_ai.py: Claude in one step, Gemini in two steps).  Keep this file in
sync with docs/ai-rules.md; a new rule there = a change here.
"""

from pipeline.genres import FILM_GENRES, MUSIC_GENRES, STAGE_GENRES

FORMATS = ["concert", "dj", "party", "music", "dance", "talk", "comedy", "workshop",
           "theatre", "film", "opening", "quiz", "performance", "other"]

# docs/ai-rules.md B
RULES_TYPE = f"""\
TYPE: formats from {FORMATS}. Exactly ONE primary_format (the main part of the \
event); other formats only as secondary (they stay in formats).
1. The MAIN PERFORMER decides, not the event title and not the venue's label. A \
venue's program category or room name ("Party – Hlavní stage" at Cross Club) is NOT \
a signal for anything.
2. concert: band, singer, rapper live, and ELECTRONIC MUSIC PLAYED LIVE (live set, \
"LIVE" / "(live)" next to the main performer, live band, vocals, instruments; e.g. \
Bonobo, Tinlicker, Modeselektor LIVE, Amphibian Quadrophonic Soundsystem, CREDIT 00 \
(live)).
3. dj: DJs (they present themselves as DJs), many names separated by ☆ / + and a \
night until morning, a genre club night without a headliner (several DJs / live \
sets), a sound system night.
4. Singer / band and DJs after them -> primary concert, dj secondary. A timetable of \
bands ("20:00 X, 21:00 Y") -> concert.
5. party = only a big commercial / mainstream party where people go for the \
atmosphere (commercial clubs, Erasmus / student nights, 80s/90s hits, open bar). In \
a commercial club: a generic night -> primary party; the DJ is the main draw and the \
party is built around him -> primary dj, party secondary; the party itself is the \
draw (theme, format, e.g. Video Oldies Rudy Tučeka, Student Wednesday), even with a \
named DJ -> primary party. Decide mainly from the title and the description. Outside \
commercial clubs only with a clear signal; give the reason in party_reason.
6. Culture by subtype: film, theatre, dance, comedy (stand-up), talk (reading and \
discussion: book launch, poetry, songs + texts, lecture), performance (performative \
piece between theatre and visual art), workshop (also a music / DJ workshop), opening \
(exhibition opening), quiz; otherwise other. music = musical event where concert vs. \
dj cannot be decided (last resort)."""

# Matej's labels (docs/tasks/056/labels-matej.csv) used as examples; the
# measurement marks these events as "in prompt".
EXAMPLE_IDS = [
    "archa-plus-2026-11-20-amphibian-quadrophonic-soundsystem",
    "roxy-2026-11-21-tinlicker",
    "roxy-2027-03-03-modeselektor-live",
    "bike-jesus-2026-11-20-credit-00-live-midirama-raphael-kosmos",
    "cross-club-2026-11-27-drumstation",
    "fuchs2-2026-11-21-family-therapy-present-asher-parashoot-fahell-zecco-millo",
    "epic-2026-11-20-slvl",
    "epic-2026-11-21-video-oldies-ruda-tuceka",   # named in rule B5 (task 059)
    "epic-2026-11-18-student-wednesday",
    "bike-jesus-2026-11-16-bashment-bass-foundation-anniversary-dance-featuring-nomadix",
    "archa-plus-2027-01-27-a-u-set-and-play-w-ursula-sereghy",
    "cross-club-2026-11-19-kavarna-krest-boldrikovo-knihy",
    "fuchs2-2026-11-20-high-speed-fairytales-liia-theya-dj-king-kobra-tmk",
]

TYPE_EXAMPLES = """\
Examples (decided by the editor):
- "Amphibian Quadrophonic Soundsystem" (Archa+): electronic, close to DJs, but played \
live and they look like a band -> concert.
- "TINLICKER" (Roxy): DJ duo that left Anjunadeep and now performs as a live band \
instead of DJ sets -> concert, dj secondary.
- "Modeselektor LIVE" (Roxy): known as DJs, but play live with vocals -> concert.
- "CREDIT 00 (live), MIDIRAMA & RAPHAEL KOSMOS" (Bike Jesus): explicit (live) at the \
main performer -> concert.
- "DRUMSTATION" (Cross Club, techno / house / acid / breaks live sets): genre night, \
several performers, no headliner -> dj (the venue's "party" label is not taken).
- "FAMILY THERAPY present Asher ☆ Parashoot ☆ Fahell ☆ Zecco ☆ Millo" (Fuchs2): many \
names, into the night, they present themselves as DJs -> dj.
- "SLVL" (EPIC, commercial club): the DJ is the main draw, the party is built around \
him -> dj, party secondary.
- "STUDENT WEDNESDAY" (EPIC): generic commercial night without named DJs -> party.
- "Bashment Bass Foundation Anniversary Dance featuring NOMADIX (UK)" (Bike Jesus): \
sound system night -> dj (not party).
- "A+U: Set and Play w/ Ursula Sereghy" (Archa+): beginners' workshop of electronic \
music production -> workshop.
- "KAVÁRNA KŘEST BOLDRIKOVO KNIHY" (Cross Club): launch of a haiku book with author \
readings and a DJ -> talk, dj secondary.
- "HIGH SPEED FAIRYTALES: LIIA ☆ Theya ☆ DJ King Kobra ☆ tmk" (Fuchs2): singer-songwriter \
and DJs after her -> concert, dj secondary."""

# docs/ai-rules.md C
RULES_GENRES = f"""\
GENRES: ordered from the MAIN genre. Music genres from this list: \
{sorted(MUSIC_GENRES)}; film: {sorted(FILM_GENRES) or "(no list yet)"}; theatre / \
dance / performance: {sorted(STAGE_GENRES)}.
1. Compound names: main genre first ("ambient techno" -> techno, ambient; "mainstage" \
-> edm, electronic; "oldies" -> oldies, + pop only if it fits).
2. Use a list genre only for the same genre or its spelling variant / synonym \
("rap" -> hip-hop). Subgenres on the list stay separate and a parent genre is NOT added \
automatically ("metalcore" is not "metal"). "bass music" is bass-music, not uk-bass \
(only UK artists) and not bassline (a Sheffield style). "hardcore" is its own genre \
(not automatically punk or techno).
3. EVERY genre must be supported by a found fact about the performer (what they play / \
how they describe themselves). No support -> no genre. Give the fact in genre_facts.
4. A genre that is not on the list: put the raw name into genre_candidates (kind \
music | film | stage) instead of forcing a list genre.
5. Genres also for film and theatre."""

# docs/ai-rules.md D, E
RULES_PRICE_TIME = """\
PRICE: only a price explicitly stated for THIS event and THIS date, with \
price_source_url = the page where it is written; the venue page wins over other \
sources. Copy it as written ("BASIC 290 Kč / VIP 500 Kč", "od 950 Kč", "zdarma", \
"dobrovolné vstupné"), all price levels (reduced, presale / at the door, VIP). \
Otherwise null. Ticket shops (GoOut, Ticketmaster, smsticket …) and public Facebook \
events are fine; Instagram and ra.co never.
START TIME: HH:MM only if explicitly stated for this event, with source_url; never \
estimate."""

# docs/ai-rules.md F + approved example (task 054 part 4b)
DESCRIPTION_EXAMPLE = (
    "Švédská kapela Allt z Karlskogy hraje progresivní metalcore a od svého vzniku v roce "
    "2020 si vybudovala pověst skupiny, která staví koncerty jako audiovizuální příběh. Debut "
    "From The New World z roku 2024 je koncepční deska o kolapsu a přežití, ovlivněná zbrojním "
    "průmyslem v jejich rodném městě. Letos vydali u Century Media druhé album Ataraxia a v "
    "MeetFactory, kde v roce 2024 předskakovali Imminence, se teď představí jako hlavní hvězda. "
    "Večer otevřou německá kapela Avralize a švédští Bite Down."
)

RULES_DESCRIPTION = f"""\
DESCRIPTIONS (always): descriptions.cs in Czech, 3-5 sentences, factual and in depth: \
who the performer is, where from, what they are known for, what they released, what \
is special about the evening (album launch, comeback, guests). Built from the SAME \
facts as type and genres. No advertising phrases ("nezmeškejte", "legendární", \
"nezapomenutelný", "unikátní zážitek"), no pathos, no exclamation marks, no emoji, no \
price / time / venue address. Only facts from the sources; take facts from the \
original text, never its sentences. Never write about the sources ("podle popisu \
akce"). Genre names are not declined or translated ("techno", "drum and bass", \
"metalcore"; never "technové"). Few facts -> a shorter text, or null. descriptions.sk \
and descriptions.en are translations of the Czech text. description_source_urls = \
pages the facts come from (the event page counts).
Style example (approved): "{DESCRIPTION_EXAMPLE}\""""

# docs/ai-rules.md G, H
RULES_ARTISTS = """\
ARTISTS: names of all performers, main performer first, with artists_source_url.
SPOTIFY: only an open.spotify.com/artist/... URL that appeared in the search results \
and surely is this artist (name AND genre or country match). Otherwise none.
UNSURE: when nothing is found, leave fields empty and set needs_review true. Never \
guess."""

RULES_ALL = "\n\n".join([RULES_TYPE, TYPE_EXAMPLES, RULES_GENRES, RULES_PRICE_TIME,
                         RULES_DESCRIPTION, RULES_ARTISTS])

# Gemini step 1 (research with Google Search) -- docs/ai-rules.md A, G.
# Task 059: at most 3 searches + 1 Spotify search (musicians only), terse facts.
MAX_RESEARCH_SEARCHES = 3
RESEARCH_PROMPT = f"""You research one event at a Prague venue with Google Search. Report only facts you found. Do not decide the event type and do not write prose.

Use AT MOST {MAX_RESEARCH_SEARCHES} searches for the research: determine ALL performers; about every MAIN performer find who it is, where from, how they present themselves (band / DJ / producer / live act / theatre company …), genre, releases; find the page of this event (venue website, public Facebook event, ticket presale) for the price (all price levels) and the start time of THIS date. Combine several performers in one search when you can. Only when the main performer is a musician or DJ (a concert or a DJ night; not theatre, dance, film, talk, exhibition, workshop): one more search "<main performer> spotify". Never use Instagram or ra.co (Resident Advisor).

Answer with short fact lines only (no sentences around them), max ~150 words:
P: <name> | <who / origin> | presents as: <...> | genres: <as the sources say> | releases: <...>
E: url <...> | price <as written> | start <HH:MM>
U: <what you could not find>"""

RESEARCH_RETRY = """IMPORTANT: you did not search. You MUST use Google Search now (at most 3 searches). Facts from memory are not accepted."""

# Gemini step 2 (decision without search)
DECIDE_PROMPT = f"""You decide the data of one event at a Prague venue from RESEARCH FACTS (found with web search, with numbered SOURCES) and the EVENT PAGE TEXT. You do not search. Use only these facts; accuracy matters more than completeness: leave a field empty when the facts do not support it. Every *_source_url must be one of the SOURCES URLs or the event page URL.

{RULES_ALL}

Write ONLY descriptions.cs (Czech); the Slovak and English versions are made later by a separate translation, leave descriptions.sk and descriptions.en out. Keep type_reason to one short sentence. Answer with ONLY one JSON object, no text around it."""

# Gemini step 3 (task 059): translation of the Czech description, cheapest model
TRANSLATE_PROMPT = """Translate the Czech event description into Slovak (sk) and English (en). Keep the facts, names and genre names exactly; do not add or drop anything; no advertising phrases, no exclamation marks. Answer with ONLY a JSON object {"sk": "...", "en": "..."}."""
