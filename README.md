# Hai (David) Guo — personal site

Source for <https://davidkpfc.github.io/>. A small static site: no database, no server code.

| Path | What it is |
|---|---|
| `pages/*.html` | The content of each page. **Edit these.** |
| `data/publications.json` | The publication lists. **Edit this.** |
| `assets/` | Stylesheet, headshot, CV |
| `build_site.py` | Wraps every page in the shared header, tabs and footer; builds the publication lists; brings in the property tax tool |
| `serve.py` | Local preview that never shows a stale copy |
| `*.html`, `tools/` | Built output. Do not edit by hand; run the build |

## Making a change

```bash
py build_site.py      # rebuild after any edit
py serve.py           # preview at http://127.0.0.1:8741/
git add -A && git commit -m "what changed" && git push     # publish; live in about a minute
```

The property tax tool is built in a separate project (`budget-simulation`) and copied in by
`build_site.py`, which renames it, applies this site's colors, and adds a byline. It is an estimate
built from Wichita Public Schools' published budget documents, and not an official district product.
