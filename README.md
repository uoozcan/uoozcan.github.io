# Academic site: Umut Onur Özcan

Static, bilingual (English `/`, Turkish `/tr/`) academic profile for `https://uoozcan.github.io`.
Built by `build.py`, which uses the Python standard library only. **Not published yet.**

## Edit
- **All text:** `content/site.json`. Every visible string has an `en` and a `tr` version side by side.
- **Publications:** don't edit by hand. Run `python scripts/sync_publications.py`, which pulls the list
  from ORCID (0000-0002-7317-1682) and titles and authors from Crossref. A work appears on the site
  once it is public on ORCID.
- **Style:** `assets/style.css` (light and dark themes; minimal, text-first).

## Preview
`python build.py --serve`, then open http://127.0.0.1:8770

## Rules
- Unpublished projects (ChampHLA, PharmacoProfiler) show **title, aim and status only**: no numbers,
  figures or results until they are published.
- No phone number or private notes. The CV page is built from the CV but deliberately omits them.
- The Turkish text was drafted by Claude. Have a native speaker (you) read it once.

## Publish (when ready)
1. Create the GitHub repository **`uoozcan.github.io`** (it must have exactly this name).
2. `git remote add origin git@github.com:uoozcan/uoozcan.github.io.git && git push -u origin main`
3. Repository → Settings → Pages → Source: **GitHub Actions**.

`.github/workflows/deploy.yml` then builds on every push, and every Monday to pick up new ORCID
entries.
