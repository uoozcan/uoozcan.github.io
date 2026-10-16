# Academic site: Umut Onur Özcan

Static, bilingual (English `/`, Turkish `/tr/`) academic profile for `https://uoozcan.github.io`.
Built by `build.py`, which uses the Python standard library only. **Live since 2026-10-16**: every
push to `main` redeploys within about a minute.

## Edit
- **All text:** `content/site.json`. Every visible string has an `en` and a `tr` version side by side.
- **Publications:** don't edit by hand. Run `python scripts/sync_publications.py`, which pulls the list
  from ORCID (0000-0002-7317-1682) and titles and authors from Crossref. A work appears on the site
  once it is public on ORCID.
- **Style:** `assets/style.css` (light and dark themes; minimal, text-first).

## Second design (`/v2/`)
`v2.py` renders the same content as one long page in the style of the Hugo Academic theme
(portrait + biography, interests, education, then projects, publications, experience, talks, contact).
`build.py` calls it, writing `dist/v2/` and `dist/v2/tr/`; its stylesheet is `assets/v2.css` and the
text only it uses is under `"v2"` in `content/site.json`. The pages are `noindex`, so search engines keep
the classic site. To make it the main design, render it at `/` instead and drop the noindex.

## Preview
`python build.py --serve`, then open http://127.0.0.1:8770

## Rules
- Unpublished projects (ChampHLA, PharmacoProfiler) show **title, aim and status only**: no numbers,
  figures or results until they are published.
- No phone number or private notes. The CV page is built from the CV but deliberately omits them.
- The Turkish text was drafted by Claude. Have a native speaker (you) read it once.

## Publish
Repository: `github.com/uoozcan/uoozcan.github.io` (public; Pages source: GitHub Actions). Push from
WSL over SSH: `git -c safe.directory=/mnt/d/projects/academic-site push`. Windows SSH has no GitHub host
key, and HTTPS is refused because the gh token lacks the `workflow` scope.

`.github/workflows/deploy.yml` builds on every push, and every Monday to pick up new ORCID entries.
