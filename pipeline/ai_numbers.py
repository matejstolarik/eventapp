"""
Report numbers of the AI step from one events.json (task 062).

    python -m pipeline.ai_numbers site/events.json [pipeline_state.json]
"""

import json
import pathlib
import sys


def numbers(data: dict, state: dict | None = None) -> dict:
    evs = data["events"]
    enr = [e for e in evs if (e.get("enrichment") or {}).get("run")]
    ds = [e for e in enr if "deepseek" in str(e["enrichment"]["run"].get("model"))]

    def by(e, k):
        return ((e.get("enrichment") or {}).get(k) or {}).get("by")

    price_ai = [e for e in evs if by(e, "price_text") == "ai_web"]
    n = {
        "events": len(evs),
        "with_ai_run": len(enr),
        "with_ai_run_deepseek": len(ds),
        "type_from_ai": sum(1 for e in evs if (e.get("classification") or {}).get("method")
                            in ("llm", "llm+web")),
        "type_from_ai_web": sum(1 for e in evs
                                if (e.get("classification") or {}).get("method") == "llm+web"),
        "with_genres": sum(1 for e in evs if e.get("genres")),
        "with_price": sum(1 for e in evs if e.get("price_text")),
        "price_from_ai_verified": sum(1 for e in price_ai
                                      if e["enrichment"]["price_text"].get("verified") is not False),
        "price_from_ai_unverified": sum(1 for e in price_ai
                                        if e["enrichment"]["price_text"].get("verified") is False),
        "with_start_time": sum(1 for e in evs if e.get("start_time")),
        "start_time_from_ai": sum(1 for e in evs if by(e, "start_time") == "ai_web"),
        "with_description_ai": sum(1 for e in evs if by(e, "description") == "ai_web"),
        "needs_review": sum(1 for e in enr if e["enrichment"]["run"].get("needs_review")),
        "genre_candidates": sum(len(e["enrichment"].get("genre_candidates") or []) for e in enr),
    }
    if state is not None:
        n["ai_cost"] = state.get("ai_cost")
        n["ai_searches"] = state.get("ai_searches")
    return n


def main() -> None:
    data = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
    state = (json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
             if len(sys.argv) > 2 else None)
    print(f"generated_at: {data.get('generated_at')}")
    for k, v in numbers(data, state).items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
