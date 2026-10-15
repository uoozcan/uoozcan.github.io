"""Refresh content/publications.json from ORCID (the list) and Crossref (titles, authors, venues).

Run: python scripts/sync_publications.py
Only works ORCID lists publicly are included. A work without a DOI keeps its ORCID metadata.
Standard library only.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date
from pathlib import Path

ORCID = "0000-0002-7317-1682"
OUT = Path(__file__).resolve().parent.parent / "content" / "publications.json"
UA = {"User-Agent": "academic-site-sync (mailto:umut.ozcan@helsinki.fi)", "Accept": "application/json"}


def get(url: str) -> dict:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)


def short_name(a: dict) -> str:
    given = a.get("given", "")
    initials = "".join(p[0] for p in given.replace("-", " ").split() if p)
    return f"{a.get('family', '')} {initials}".strip()


def main() -> int:
    works = get(f"https://pub.orcid.org/v3.0/{ORCID}/works").get("group", [])
    pubs = []
    for g in works:
        s = g["work-summary"][0]
        ids = g.get("external-ids", {}).get("external-id", [])
        doi = next((i["external-id-value"] for i in ids if i["external-id-type"] == "doi"), None)
        item = {"title": s["title"]["title"]["value"], "venue": (s.get("journal-title") or {}).get("value", ""),
                "year": ((s.get("publication-date") or {}).get("year") or {}).get("value", ""),
                "type": s.get("type", ""), "doi": doi, "authors": [], "self_index": None}
        if doi:
            m = get(f"https://api.crossref.org/works/{doi}")["message"]
            item["title"] = (m.get("title") or [item["title"]])[0]
            item["venue"] = (m.get("container-title") or [item["venue"]])[0]
            parts = (m.get("published-print") or m.get("issued") or {}).get("date-parts", [[None]])[0]
            item["year"] = str(parts[0] or item["year"])
            item["volume"], item["issue"], item["pages"] = m.get("volume", ""), m.get("issue", ""), m.get("page", "")
            item["authors"] = [short_name(a) for a in m.get("author", [])]
            item["self_index"] = next((i for i, a in enumerate(m.get("author", []))
                                       if a.get("family", "").lower() in ("özcan", "ozcan")), None)
        pubs.append(item)
    pubs.sort(key=lambda p: (p["year"], p["title"]), reverse=True)
    OUT.write_text(json.dumps({"synced": date.today().isoformat(), "orcid": ORCID, "items": pubs},
                              ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"{len(pubs)} publications -> {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
