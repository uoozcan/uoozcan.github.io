"""Build the academic site into dist/ (English at /, Turkish at /tr/). Standard library only.

    python build.py            # build
    python build.py --serve    # build, then serve at http://127.0.0.1:8770

Content: content/site.json (text, en + tr) and content/publications.json (scripts/sync_publications.py).
"""

from __future__ import annotations

import html
import json
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
SITE_URL = "https://uoozcan.github.io"
LANGS = ("en", "tr")
PAGES = ("home", "research", "publications", "cv")
SLUG = {"home": "", "research": "research/", "publications": "publications/", "cv": "cv/"}

C = json.loads((ROOT / "content" / "site.json").read_text(encoding="utf-8"))
P = json.loads((ROOT / "content" / "publications.json").read_text(encoding="utf-8"))
e = html.escape


def t(v, lang):
    """A bilingual value is {"en": ..., "tr": ...}; anything else is language-neutral."""
    return v.get(lang, v.get("en")) if isinstance(v, dict) else v


def url(page, lang):
    return ("/" if lang == "en" else "/tr/") + SLUG[page]


def depth_prefix(page, lang):
    # relative links keep the build working from any folder (file:// preview, a project-page subpath)
    d = (0 if lang == "en" else 1) + (0 if page == "home" else 1)
    return "../" * d or "./"


def href(target, lang, page, cur_lang):
    rel = depth_prefix(page, cur_lang) + (("" if lang == "en" else "tr/") + SLUG[target])
    return rel or "./"


def pub_html(p, lang, short=False):
    a = p["authors"]
    me = p.get("self_index")
    if a:
        shown = list(range(len(a))) if len(a) <= 6 else sorted({0, 1, 2, len(a) - 1} | ({me} if me is not None else set()))
        parts, last = [], -1
        for i in shown:
            if i - last > 1:
                parts.append("…")
            name = e(a[i])
            parts.append(f"<strong>{name}</strong>" if i == me else name)
            last = i
        authors = ", ".join(parts)
        if len(a) > 6:
            authors += f" <span class=muted>({len(a)} {'authors' if lang == 'en' else 'yazar'})</span>"
    else:
        authors = ""
    loc = ""
    if p.get("volume"):
        loc = f" {e(p['volume'])}" + (f"({e(p['issue'])})" if p.get("issue") else "") + (f":{e(p['pages'])}" if p.get("pages") else "")
    doi = f' <a href="https://doi.org/{e(p["doi"])}">doi:{e(p["doi"])}</a>' if p.get("doi") else ""
    return (f'<li class=pub><span class=pub-title>{e(p["title"])}</span><br>'
            f'{authors}{"<br>" if authors else ""}<em>{e(p["venue"])}</em>{loc}, {e(p["year"])}.{doi}</li>')


def page_home(lang):
    lab = C["labels"]
    links = " · ".join(f'<a href="{e(l["url"])}">{e(l["label"])}</a>' for l in C["links"])
    projects = "".join(
        f'<li><strong>{e(p["title"])}</strong>: {e(t(p["aim"], lang))} '
        f'<span class=status>{e(t(p["status"], lang))}</span></li>' for p in C["projects"])
    pubs = "".join(pub_html(p, lang) for p in P["items"][:3])
    return f"""
<section class=intro>
  <div class=monogram aria-hidden=true>UÖ</div>
  <div>
    <h1>{e(C["name"])}</h1>
    <p class=role>{e(t(C["role"], lang))}<br><span class=muted>{e(t(C["location"], lang))}</span></p>
  </div>
</section>
<p class=lede>{e(t(C["statement"], lang))}</p>
<p class=links>{links} · <a href="mailto:{e(C["email"])}">{e(C["email"])}</a></p>
<h2>{e(t(lab["projects"], lang))}</h2>
<ul class=plain>{projects}</ul>
<h2>{e(t(lab["selected"], lang))}</h2>
<ol class=pubs>{pubs}</ol>
<p><a href="{{pubs_href}}">{e(t(lab["all_pubs"], lang))} →</a></p>
"""


def page_research(lang):
    lab = C["labels"]
    cards = "".join(f"""
<article class=project>
  <h3>{e(p["title"])}</h3>
  <p>{e(t(p["aim"], lang))}</p>
  <p class=meta><span class=status>{e(t(lab["status"], lang))}: {e(t(p["status"], lang))}</span> · {e(t(p["role"], lang))}</p>
</article>""" for p in C["projects"])
    earlier = "".join(f'<article class=project><h3>{e(x["title"])}</h3><p>{e(t(x["text"], lang))}</p></article>'
                      for x in C["earlier"])
    return f"""<h1>{e(t(C["nav"]["research"], lang))}</h1>
<p class=lede>{e(t(C["statement"], lang))}</p>
<h2>{e(t(lab["projects"], lang))}</h2>{cards}
<h2>{e(t(lab["earlier"], lang))}</h2>{earlier}"""


def page_publications(lang):
    lab = C["labels"]
    items = "".join(pub_html(p, lang) for p in P["items"])
    return f"""<h1>{e(t(C["nav"]["publications"], lang))}</h1>
<ol class=pubs>{items}</ol>
<p class=muted>{e(t(lab["pubs_source"], lang))} <a href="https://orcid.org/{e(P["orcid"])}">ORCID {e(P["orcid"])}</a> · {e(P["synced"])}</p>"""


def page_cv(lang):
    lab = C["labels"]
    edu = "".join(f'<li><strong>{e(t(x["degree"], lang))}</strong>, {e(t(x["place"], lang))} '
                  f'<span class=when>{e(x["when"])}</span><br><span class=muted>{e(t(x["note"], lang))}</span></li>'
                  for x in C["education"])
    exp = "".join(f'<li><strong>{e(t(x["title"], lang))}</strong>, {e(t(x["place"], lang))} '
                  f'<span class=when>{e(t(x["when"], lang))}</span><ul>'
                  + "".join(f"<li>{e(pt)}</li>" for pt in t(x["points"], lang)) + "</ul></li>"
                  for x in C["experience"])
    intern = "".join(f"<li>{e(t(x, lang))}</li>" for x in C["internships"])
    skills = "".join(f"<dt>{e(t(s['area'], lang))}</dt><dd>{e(t(s['items'], lang))}</dd>" for s in C["skills"])
    talks = "".join(f'<li><span class=when>{e(x["year"])}</span> {e(t(x, lang))}</li>' for x in C["talks"])
    pubs = "".join(pub_html(p, lang) for p in P["items"])
    return f"""<h1>{e(t(C["nav"]["cv"], lang))}</h1>
<p>{e(C["name"])} · {e(t(C["location"], lang))} · <a href="mailto:{e(C["email"])}">{e(C["email"])}</a> · <a href="https://orcid.org/{e(C["orcid"])}">ORCID</a></p>
<h2>{e(t(lab["experience"], lang))}</h2><ul class=cv>{exp}</ul>
<h2>{e(t(lab["education"], lang))}</h2><ul class=cv>{edu}</ul>
<h2>{e(t(C["nav"]["publications"], lang))}</h2><ol class=pubs>{pubs}</ol>
<h2>{e(t(lab["talks"], lang))}</h2><ul class=cv>{talks}</ul>
<h2>{e(t(lab["internships"], lang))}</h2><ul class=cv>{intern}</ul>
<h2>{e(t(lab["skills"], lang))}</h2><dl class=skills>{skills}</dl>
<h2>{e(t(lab["languages"], lang))}</h2><p>{e(t(C["spoken"], lang))}</p>"""


RENDER = {"home": page_home, "research": page_research, "publications": page_publications, "cv": page_cv}

THEME_JS = """(function(){try{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t;}catch(e){}})();"""
TOGGLE_JS = """document.getElementById('theme').addEventListener('click',function(){var d=document.documentElement,
dark=d.dataset.theme?d.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
d.dataset.theme=dark?'light':'dark';try{localStorage.setItem('theme',d.dataset.theme);}catch(e){}});"""


def layout(page, lang, body):
    lab, nav = C["labels"], C["nav"]
    other = "tr" if lang == "en" else "en"
    title = C["name"] if page == "home" else f'{t(nav[page], lang)} · {C["name"]}'
    navlinks = "".join(
        f'<a href="{href(p, lang, page, lang)}"{" aria-current=page" if p == page else ""}>{e(t(nav[p], lang))}</a>'
        for p in PAGES)
    alt = "".join(f'<link rel=alternate hreflang={l} href="{SITE_URL}{url(page, l)}">' for l in LANGS)
    body = body.replace("{pubs_href}", href("publications", lang, page, lang))
    css = depth_prefix(page, lang) + "assets/style.css"
    icon = depth_prefix(page, lang) + "assets/favicon.svg"
    return f"""<!doctype html>
<html lang={lang}>
<head>
<meta charset=utf-8>
<meta name=viewport content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name=description content="{e(t(C["statement"], lang))}">
<link rel=canonical href="{SITE_URL}{url(page, lang)}">{alt}
<link rel=alternate hreflang=x-default href="{SITE_URL}{url(page, "en")}">
<meta property=og:title content="{e(title)}">
<meta property=og:description content="{e(t(C["role"], lang))}">
<link rel=icon href="{icon}" type="image/svg+xml">
<link rel=stylesheet href="{css}">
<script>{THEME_JS}</script>
</head>
<body>
<a class=skip href="#main">{e(t(lab["skip"], lang))}</a>
<header class=site>
  <nav aria-label="Main">{navlinks}</nav>
  <div class=tools>
    <a href="{href(page, other, page, lang)}" hreflang={other} lang={other}>{e(t(lab["switch"], lang))}</a>
    <button id=theme type=button aria-label="{e(t(lab["theme"], lang))}">◐</button>
  </div>
</header>
<main id=main>
{body}
</main>
<footer class=site><span>© {date.today().year} {e(C["name"])}</span><span>{e(t(lab["updated"], lang))}: {date.today().isoformat()}</span></footer>
<script>{TOGGLE_JS}</script>
</body>
</html>
"""


def build() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)
    for f in (ROOT / "assets").iterdir():
        shutil.copy2(f, DIST / "assets" / f.name)
    n = 0
    for lang in LANGS:
        for page in PAGES:
            out = DIST / ("" if lang == "en" else "tr") / SLUG[page] / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(layout(page, lang, RENDER[page](lang)), encoding="utf-8", newline="\n")
            n += 1
    (DIST / "404.html").write_text(layout("home", "en", '<h1>404</h1><p>Page not found. <a href="/">Home</a></p>')
                                   .replace('href="./', 'href="/'), encoding="utf-8", newline="\n")
    (DIST / ".nojekyll").write_text("")
    sm = "".join(f"<url><loc>{SITE_URL}{url(p, l)}</loc></url>" for l in LANGS for p in PAGES)
    (DIST / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n', encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"built {n} pages -> {DIST}")
    return 0


if __name__ == "__main__":
    rc = build()
    if "--serve" in sys.argv:
        import functools
        import http.server
        h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
        print("serving http://127.0.0.1:8770 (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8770), h).serve_forever()
    sys.exit(rc)
