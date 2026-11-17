"""Task 063 part 2 (docs/ai-rules.md F): a description presents facts, never
their absence.  Sentences about missing information are removed one by one
(Czech, before the translation); nothing usable left -> no AI description."""

from pipeline.ai_guards import no_info_sentence, strip_no_info
from pipeline.enrich_ai import _Gemini2, validate
from tests.test_guards_062 import AL, EV, URL, _raw

DIVA = ("O jednotlivých účinkujících se kromě jejich jmen a označení Portera jako britského "
        "interpreta nedochovaly žádné další podrobnosti, stejně jako informace o vydaných "
        "nahrávkách.")
TEXT_APPEAL = "Konkrétní účinkující pro tento večer nejsou zveřejněni."
SEVENTH = "Sedmé jméno zatím ohlášeno nebylo."
REVO = ("O akci REVO: Z Gumy Do Gumy není k dispozici dost informací, které by umožnily popsat "
        "její obsah. Název se nepodařilo spolehlivě spojit s konkrétním interpretem ani s "
        "konkrétním formátem večera. Z dostupných zdrojů vyplývá pouze to, že se akce koná v "
        "termínu 20. listopadu 2026. Podrobnosti o účinkujících, dramaturgii ani programu "
        "nejsou známé.")
BONOBO = ("Na svých koncertech vystupuje s celou živou kapelou, takže jeho vystoupení nejsou "
          "postavená na laptopu, ale na hře hudebníků na pódiu.")
FACT = ("Text-appeal je pravidelný večer umělecké tvorby studentů oboru Tvorba textu a scénáře "
        "Konzervatoře Jaroslava Ježka.")


def test_real_no_info_sentences_detected():
    for s in (DIVA, TEXT_APPEAL, SEVENTH, "Jiní účinkující nejsou uvedeni.",
              "Zbytek hostů bude postupně oznámen.",
              "Podpůrné vystoupení je zatím oznámeno jako TBA.",
              "Večer nese název Unity Rage a představí se i hosté, jejichž jména pořadatelé "
              "zatím nezveřejnili."):
        assert no_info_sentence(s), s


def test_no_false_positives():
    for s in (BONOBO, FACT, "Rezervace míst nejsou možné, kapacita týmů je omezená.",
              "Kapela je známá svými koncerty.",
              "Původní termín byl přesunut a nové datum má být oznámeno do konce roku.",
              "Večer tak stojí na rezidentských DJ setech a na překvapení v podobě "
              "neohlášeného německého hosta."):
        assert not no_info_sentence(s), s


def test_sentences_removed_not_whole_description():
    text, removed = strip_no_info(f"{FACT} {TEXT_APPEAL} {BONOBO}")
    assert removed == [TEXT_APPEAL]
    assert text == f"{FACT} {BONOBO}"


def test_date_inside_sentence_is_not_a_split():
    text, removed = strip_no_info(REVO)
    assert len(removed) == 4 and text is None          # REVO -> no description


def test_bonobo_unchanged():
    assert strip_no_info(BONOBO) == (BONOBO, [])


class _Fake(_Gemini2):
    def __init__(self, cs):
        self.cs, self.translated = cs, []

    def decide(self, ev, venue, page_text, research):
        return {"formats": ["concert"], "descriptions": {"cs": self.cs}}, U

    def translate(self, cs):
        self.translated.append(cs)
        return {"sk": "SK " + cs, "en": "EN " + cs}, U


U = {"input_tokens": 0, "output_tokens": 0, "cached_tokens": 0, "cost_usd": 0.0}
R = {"text": "", "sources": [], "searched": True, "kworb": []}


def test_removed_before_translation():
    prov = _Fake(f"{FACT} {SEVENTH}")
    rec = prov.run_from_research(EV, {}, None, R)
    assert prov.translated == [FACT]                  # translation of the cleaned text
    assert rec["raw"]["descriptions"]["cs"] == FACT
    raw = rec["raw"] | {"description_source_urls": [URL], "type_source_url": URL,
                        "genres": [], "genre_facts": {}}
    out = validate(raw, EV, None, AL)
    assert out["descriptions"]["sk"] == "SK " + FACT
    assert f"description_no_info: {SEVENTH}" in out["dropped"]
    assert not out["needs_review"]


def test_revo_no_description_needs_review():
    prov = _Fake(REVO)
    rec = prov.run_from_research(EV, {}, None, R)
    assert prov.translated == [] and rec["raw"]["descriptions"] is None
    raw = rec["raw"] | {"description_source_urls": [URL], "type_source_url": URL,
                        "genres": [], "genre_facts": {}}
    out = validate(raw, EV, None, AL)
    assert out["descriptions"] is None and out["needs_review"]
    assert any(d.startswith("description_no_info: nothing usable") for d in out["dropped"])


def test_one_step_provider_cleans_cs_and_drops_translations():
    raw = _raw([], {}, descriptions={"cs": f"{FACT} {DIVA}", "sk": "x", "en": "y"},
               description_source_urls=[URL])
    out = validate(raw, EV, None, AL)
    assert out["descriptions"] == {"cs": FACT}
    assert f"description_no_info: {DIVA}" in out["dropped"]
