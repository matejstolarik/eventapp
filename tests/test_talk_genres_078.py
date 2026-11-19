"""Task 078: talk genres from phrases (ai-rules C10)."""

from pipeline.enrich_ai import apply_talk_genres, genres_from_raw
from pipeline.genres import (STAGE_GENRES, TALK_GENRES, UMBRELLAS, load_aliases, load_hierarchy,
                             talk_genres_from_text)

AL = load_aliases()


def test_lists_and_hierarchy():
    assert TALK_GENRES <= STAGE_GENRES
    assert "talk" in UMBRELLAS
    h = load_hierarchy()
    for g in TALK_GENRES:
        assert h[g] == ["talk"]


def test_phrases():
    f = lambda *t: talk_genres_from_text(list(t), AL)
    assert f("CROSS SLAM 2026", "genres: slam poetry, poetry") == ["slam-poetry"]
    assert f("CROSS SLAM 2026 - open mic") == []            # 'slam' alone is never mapped
    assert f("Poetry Slam v Praze") == ["slam-poetry"]
    assert f("KAVÁRNA KŘEST BOLDRIKOVO KNIHY") == ["book-launch"]
    assert f("křest první knihy haiku") == ["book-launch"]
    assert f("KŘEST KNIHY") == ["book-launch"]
    assert f("Hraní, čtení, výstava") == ["reading"]
    assert f("čtených scénářů") == []
    assert f("Přednáška o jazzu") == ["lecture"]
    assert f("performer, creator, lecturer") == []          # whole words only
    assert f("full list of all Talks/panel participants") == ["discussion"]
    assert f("Diskuse a debata") == ["discussion"]
    assert f("panelák") == []


def _ev(id_, formats, genres, title, primary=None, enr=None):
    return {"id": id_, "formats": formats, "primary_format": primary or formats[0],
            "genres": genres, "title": title, "description": None,
            "enrichment": enr if enr is not None else {"formats": {"by": "ai_web", "model": "m",
                                                                   "checked_at": "2026-11-19"}}}


def test_apply_talk_genres():
    slam = _ev("a", ["talk", "dj"], ["techno"], "CROSS SLAM", enr={"genres": {"by": "ai_web"}})
    talk2 = _ev("b", ["concert", "talk"], [], "Koncert a čtení")
    theatre = _ev("c", ["theatre"], ["drama", "discussion"], "Hra a diskuse")
    manual = _ev("d", ["talk"], ["jazz"], "Přednáška", enr={"genres": {"by": "manual"}})
    research = {"a": {"facts": "genres: slam poetry"}}
    changed = apply_talk_genres([slam, talk2, theatre, manual], research, AL)
    assert slam["genres"] == ["slam-poetry", "techno"]       # primary talk: first
    assert talk2["genres"] == ["reading"]
    assert talk2["enrichment"]["genres"]["by"] == "ai_web"   # provenance copied from formats
    assert theatre["genres"] == ["drama"]                    # not a talk event
    assert manual["genres"] == ["jazz"]
    assert changed == ["a", "b", "c"]
    assert apply_talk_genres([slam], research, AL) == []     # idempotent


def test_model_talk_genres_dropped():
    dropped = []
    gens, cands = genres_from_raw([], [{"raw": "slam poetry", "kind": "stage"},
                                       {"raw": "panel", "kind": "stage"}],
                                  {}, "stage", "slam poetry panel", AL, dropped)
    assert gens == [] and cands == []
    assert len(dropped) == 2
