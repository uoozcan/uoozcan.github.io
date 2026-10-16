"""Second design: one long page in the style of the Hugo Academic theme (sticky section nav,
portrait + biography hero, title-left / content-right sections on alternating backgrounds).

Called by build.py after the classic site is built; writes dist/v2/ (English) and dist/v2/tr/
(Turkish) from the same content files. Text that only this design needs is in site.json under "v2".
The pages carry noindex so search engines keep pointing at the classic site.
"""

from __future__ import annotations

import html
from datetime import date
from pathlib import Path

e = html.escape
SECTIONS = ("about", "projects", "publications", "experience", "talks", "contact")


def _svg(body, filled=False):
    paint = 'fill="currentColor"' if filled else 'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
    return f'<svg viewBox="0 0 24 24" {paint} aria-hidden="true">{body}</svg>'


def _badge(text):
    # round/square glyph with letters punched out in the page background colour
    return ('<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="1" y="1" width="22" height="22" rx="{rx}" fill="currentColor"/>'
            '<text x="12" y="16.3" text-anchor="middle" font-size="11.5" font-weight="700" font-family="Arial,sans-serif" '
            'style="fill:var(--bg)">{t}</text></svg>').format(rx=11 if text == "iD" else 4, t=text)


ICON = {
    "email": _svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>'),
    "pin": _svg('<path d="M12 21s-7-6.2-7-11a7 7 0 0 1 14 0c0 4.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>'),
    "cap": _svg('<path d="M12 4 1.5 9 12 14l10.5-5L12 4z"/><path d="M5.5 11v5c0 1.4 2.9 3 6.5 3s6.5-1.6 6.5-3v-5"/><path d="M22.5 9v5"/>'),
    "orcid": _badge("iD"),
    "linkedin": _badge("in"),
    "github": '<svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>',
}

THEME_JS = """(function(){try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t;}catch(e){}})();"""
PAGE_JS = """document.getElementById('theme').addEventListener('click',function(){var d=document.documentElement,
dark=d.dataset.theme?d.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
d.dataset.theme=dark?'light':'dark';try{localStorage.setItem('theme',d.dataset.theme);}catch(e){}});
(function(){var links=[].slice.call(document.querySelectorAll('header.nav nav a'));if(!('IntersectionObserver' in window))return;
var io=new IntersectionObserver(function(es){es.forEach(function(en){if(!en.isIntersecting)return;links.forEach(function(a){
if(a.hash==='#'+en.target.id)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current');});});},
{rootMargin:'-40% 0px -55% 0px'});document.querySelectorAll('main section[id]').forEach(function(s){io.observe(s);});})();"""


def build_v2(dist: Path, C: dict, P: dict, t, authors_html) -> int:
    V = C["v2"]
    lab, vlab = C["labels"], V["labels"]

    def section(sid, lang, body, alt):
        return (f'<section id={sid} class="sec{" alt" if alt else ""}"><div class="wrap split">'
                f'<h2 class=sec-title>{e(t(V["nav"][sid], lang))}</h2><div class=sec-body>{body}</div></div></section>')

    def about(lang):
        social = [f'<li><a href="mailto:{e(C["email"])}" aria-label="Email">{ICON["email"]}</a></li>']
        social += [f'<li><a href="{e(l["url"])}" aria-label="{e(l["label"])}">{ICON[l["label"].lower()]}</a></li>'
                   for l in C["links"] if l["label"].lower() in ICON]
        interests = "".join(f"<li>{e(t(x, lang))}</li>" for x in V["interests"])
        edu = "".join(f'<li>{ICON["cap"]}<div><strong>{e(t(x["degree"], lang))}</strong>'
                      f'<span class=muted>{e(t(x["place"], lang))}, {e(x["when"])}</span></div></li>' for x in C["education"])
        return f"""<section id=about class="sec hero"><div class=wrap>
  <div class=profile>
    <div class=avatar aria-hidden=true>UÖ</div>
    <h1>{e(C["name"])}</h1>
    <p class=position>{e(t(V["position"], lang))}</p>
    <p class=org>{e(t(V["org"], lang))}</p>
    <ul class=social>{"".join(social)}</ul>
  </div>
  <div class=bio>
    <h2>{e(t(vlab["biography"], lang))}</h2>
    <p>{e(t(C["statement"], lang))}</p>
    <p>{e(t(V["bio_more"], lang))}</p>
    <div class=cols>
      <div><h3>{e(t(vlab["interests"], lang))}</h3><ul class=interests>{interests}</ul></div>
      <div><h3>{e(t(lab["education"], lang))}</h3><ul class=edu>{edu}</ul></div>
    </div>
  </div>
</div></section>"""

    def projects(lang):
        cur = "".join(f"""<article class=card>
  <p class=card-kicker><span class=chip>{e(t(vlab["current"], lang))}</span> <span class=muted>{e(t(p["role"], lang))}</span></p>
  <h3>{e(p["title"])}</h3><p>{e(t(p["aim"], lang))}</p>
  <p class=status>{e(t(lab["status"], lang))}: {e(t(p["status"], lang))}</p></article>""" for p in C["projects"])
        old = "".join(f"""<article class=card>
  <p class=card-kicker><span class="chip quiet">{e(t(vlab["earlier"], lang))}</span></p>
  <h3>{e(x["title"])}</h3><p>{e(t(x["text"], lang))}</p></article>""" for x in C["earlier"])
        return cur + old

    def publications(lang):
        items = []
        for p in P["items"]:
            loc = ""
            if p.get("volume"):
                loc = f" {e(p['volume'])}" + (f"({e(p['issue'])})" if p.get("issue") else "") + (f":{e(p['pages'])}" if p.get("pages") else "")
            doi = f'<a class=btn href="https://doi.org/{e(p["doi"])}">DOI</a>' if p.get("doi") else ""
            items.append(f"""<article class=pub>
  <p class=pub-authors>{authors_html(p, lang)}</p>
  <p class=pub-title>{e(p["title"])}</p>
  <p class=pub-venue><em>{e(p["venue"])}</em>{loc}, {e(p["year"])}</p>{doi}</article>""")
        note = (f'<p class="muted small">{e(t(lab["pubs_source"], lang))} '
                f'<a href="https://orcid.org/{e(P["orcid"])}">ORCID {e(P["orcid"])}</a></p>')
        return "".join(items) + note

    def experience(lang):
        return "<ol class=timeline>" + "".join(
            f'<li><p class=when>{e(t(x["when"], lang))}</p><h3>{e(t(x["title"], lang))}</h3>'
            f'<p class=muted>{e(t(x["place"], lang))}</p><ul>' + "".join(f"<li>{e(pt)}</li>" for pt in t(x["points"], lang))
            + "</ul></li>" for x in C["experience"]) + "</ol>"

    def talks(lang):
        return "<ul class=talks>" + "".join(
            f'<li><span class=year>{e(x["year"])}</span><span>{e(t(x, lang))}</span></li>' for x in C["talks"]) + "</ul>"

    def contact(lang):
        orcid = next((l for l in C["links"] if l["label"] == "ORCID"), None)
        rows = [f'<li>{ICON["email"]}<a href="mailto:{e(C["email"])}">{e(C["email"])}</a></li>',
                f'<li>{ICON["pin"]}<span>{e(t(V["org"], lang))}<br>{e(t(C["location"], lang))}</span></li>']
        if orcid:
            rows.append(f'<li>{ICON["orcid"]}<a href="{e(orcid["url"])}">{e(C["orcid"])}</a></li>')
        return f'<p>{e(t(vlab["contact_lede"], lang))}</p><ul class=contact>{"".join(rows)}</ul>'

    render = {"projects": projects, "publications": publications, "experience": experience,
              "talks": talks, "contact": contact}

    def page(lang):
        up = "../" if lang == "en" else "../../"
        other = "tr" if lang == "en" else "en"
        other_href = "tr/" if lang == "en" else "../"
        classic = up + ("" if lang == "en" else "tr/")
        nav = "".join(f'<a href="#{s}">{e(t(V["nav"][s], lang))}</a>' for s in SECTIONS)
        body = about(lang) + "".join(section(s, lang, render[s](lang), i % 2 == 1)
                                      for i, s in enumerate(SECTIONS) if s != "about")
        return f"""<!doctype html>
<html lang={lang}>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>{e(C["name"])}</title>
<meta name=description content="{e(t(C["statement"], lang))}">
<meta name=robots content=noindex>
<link rel=icon href="{up}assets/favicon.svg" type="image/svg+xml">
<link rel=stylesheet href="{up}assets/v2.css">
<script>{THEME_JS}</script>
</head>
<body id=top>
<a class=skip href="#main">{e(t(lab["skip"], lang))}</a>
<header class=nav><div class=wrap>
  <a class=brand href="#top">{e(C["name"])}</a>
  <nav aria-label="Sections">{nav}</nav>
  <div class=tools>
    <a href="{other_href}" hreflang={other} lang={other}>{e(t(lab["switch"], lang))}</a>
    <button id=theme type=button aria-label="{e(t(lab["theme"], lang))}">◐</button>
  </div>
</div></header>
<main id=main>
{body}
</main>
<footer class=site><div class=wrap>
  <span>© {date.today().year} {e(C["name"])}</span>
  <a href="{classic}">{e(t(vlab["classic"], lang))}</a>
  <span>{e(t(lab["updated"], lang))}: {date.today().isoformat()}</span>
</div></footer>
<script>{PAGE_JS}</script>
</body>
</html>
"""

    for lang in ("en", "tr"):
        out = dist / "v2" / ("" if lang == "en" else "tr") / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page(lang), encoding="utf-8", newline="\n")
    return 2
