"""Task 067 part 2: film / stage genre facts pass the genre guard."""
import pytest

from pipeline.ai_guards import genre_supported
from pipeline.ai_rules import RESEARCH_PROMPT, RULES_GENRES
from pipeline.deepseek import RESEARCH_PROMPT_DS

RESEARCH = ("F: Ratatouille | Brad Bird, 2007, USA | genres: animated, comedy, family [1]\n"
            "F: Popel | Elfriede Jelinek, Divadlo X | genres: činohra [2]\n"
            "F: Lola | dokumentární film, 2024 [3]\n"
            "F: Ptáci | současný tanec, taneční divadlo [4]")


@pytest.mark.parametrize("genre,quote", [
    ("animation", "animated film by Pixar"),
    ("animation", "animovaný film"),
    ("comedy", "comedy"),
    ("family", "family film"),
    ("documentary", "dokumentární film"),
    ("drama", "činohra"),
    ("contemporary-dance", "současný tanec"),
    ("dance-theatre", "taneční divadlo"),
])
def test_culture_genre_facts_pass(genre, quote):
    ok, why = genre_supported(genre, quote, RESEARCH, None)
    assert ok, why


def test_culture_genre_not_in_research_dropped():
    ok, _ = genre_supported("horror", "horror", RESEARCH, None)
    assert not ok


@pytest.mark.parametrize("prompt", [RESEARCH_PROMPT, RESEARCH_PROMPT_DS])
def test_research_prompt_asks_for_film_and_stage_genres(prompt):
    assert "For a film screening" in prompt and "činohra" in prompt
    assert "F: <film or piece>" in prompt


def test_genre_rule_allows_fact_about_the_film():
    assert "a fact about the film / piece" in RULES_GENRES
