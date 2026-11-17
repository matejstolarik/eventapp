import json, re, sys
PAT = {
  "jam": re.compile(r"\bjam\b|jam\s*session|jamsession", re.I),
  "open mic": re.compile(r"open[\s-]*mic", re.I),
  "karaoke": re.compile(r"karaoke", re.I),
  "otevřené pódium": re.compile(r"otev[řr]en[éeá]\s+p[óo]di", re.I),
}
for path in sys.argv[1:]:
    d = json.load(open(path, encoding="utf-8"))
    ev = d["events"]
    print(f"== {path.split('/')[-1]} generated {d.get('generated_at')} events {len(ev)}")
    for k, p in PAT.items():
        hits = [e for e in ev if p.search(e.get("title") or "") or p.search(e.get("description") or "")]
        print(f"  {k}: {len(hits)} (title {sum(1 for e in hits if p.search(e.get('title') or ''))})")
        for e in hits:
            where = "title" if p.search(e.get("title") or "") else "desc"
            url = (e.get("sources") or [{}])[0].get("url")
            print(f"    - {e['title']} | {e['venue_id']} | {e['date']} | {e['formats']} | {where} | {url}")
