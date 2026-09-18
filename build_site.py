# -*- coding: utf-8 -*-
"""
Build the personal site.  Run it after any edit:      py build_site.py
Preview it with:                                       py serve.py      (not `py -m http.server`,
                                                       which lets the browser show stale pages)

  pages/*.html            the content of each page (edit these)
  data/publications.json  the publication lists (edit this)
  assets/                 stylesheet, headshot, CV
  --> index.html, research.html, projects.html, publications.html, service.html,
      teaching.html, contact.html            every page gets the same header, tabs and footer
  --> tools/<SLUG>/index.html                the property tax tool, brought in from
                                             ../budget-simulation/dist/school-tax-receipt-a3.html

The tool is copied, not edited by hand.  Five things change on the way in:
  1. the name           -> TOOL_NAME below: the browser title, the site bar, the headline
  2. the colors         -> the site's ledger green and margin red replace the district's slate
                           and crimson; the levy chart colors are left alone because they were
                           validated for colorblind readers as a set
  3. a slim site bar    -> links back to the home page and to Projects
  4. a byline           -> who built it, and that it is not an official district product
  5. one section heading-> "What your tax pays for" would echo the headline, so it becomes
                           "Your bill, service by service"
Nothing about the tool's numbers or behaviour changes.
"""
import hashlib, html, json, os, re, sys

AUTHOR = "Hai (David) Guo"
TOOL_NAME = "What your property tax pays for"
SLUG = "what-your-property-tax-pays-for"            # the folder under tools/, i.e. the web address

LINKS = {
    "KPFC": "https://www.wichita.edu/academics/fairmount_las/hugowall/kpfc/index.php",
    "FS": "https://www.wichita.edu/academics/fairmount_las/hugowall/kpfc/Fiscal-Shocker/",
    "FLC": "https://www.flcities.com/propertytaxstudy/",
    "SCHOLAR": "https://scholar.google.com/citations?user=s0RVzakAAAAJ&amp;hl=en",
}

# file, tab label (None = not a tab), source fragment, <title>, meta description
PAGES = [
    ("index.html", None, "home.html", "Hai (David) Guo | State and Local Public Finance",
     "Hai (David) Guo is the Regents Distinguished Professor of Public Finance at Wichita State University and "
     "Director of the Kansas Public Finance Center. Research, tools, and publications on state and local public finance."),
    ("research.html", "Research", "research.html", "Research | Hai (David) Guo",
     "Three research tracks: property tax and tax limitations; fiscal stress, reserves, and forecasting; "
     "transparency and citizen participation."),
    ("projects.html", "Projects", "projects.html", "Projects and tools | Hai (David) Guo",
     "The Fiscal Shocker, an interactive taxpayer receipt for Wichita Public Schools, and the Florida Property Tax Study."),
    ("publications.html", "Publications", "publications.html", "Publications | Hai (David) Guo",
     "Peer-reviewed articles, book, and reports by Hai (David) Guo on state and local public finance."),
    ("service.html", "Service", "service.html", "Service | Hai (David) Guo",
     "Public service in Kansas and service to the public budgeting and finance profession."),
    ("teaching.html", "Teaching", "teaching.html", "Teaching | Hai (David) Guo",
     "Courses in public budgeting, financial management, public sector economics, and research methods."),
    ("contact.html", "Contact", "contact.html", "Contact | Hai (David) Guo",
     "Contact Hai (David) Guo at the Hugo Wall School of Public Affairs, Wichita State University."),
]

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL_SRC = os.path.normpath(os.path.join(HERE, "..", "budget-simulation", "dist", "school-tax-receipt-a3.html"))
TOOL_OUT = os.path.join(HERE, "tools", SLUG, "index.html")

FONTS = ("https://fonts.googleapis.com/css2?family=Besley:ital,wght@0,500..900;1,500"
         "&family=Public+Sans:wght@400..700&family=IBM+Plex+Mono:wght@400;500&display=swap")

SHELL = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="stylesheet" href="{fonts}">
  <link rel="stylesheet" href="assets/site.css">
  <script>
    /* ?theme=light or ?theme=dark pins the page; otherwise it follows the visitor's device */
    (function () {{ try {{ var t = new URLSearchParams(location.search).get('theme');
      if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t); }} catch (e) {{}} }})();
  </script>
</head>
<body>

<header class="col top">
  <a class="brand" href="index.html"{home_current}>{author}</a>
  <nav aria-label="Pages">
{tabs}
  </nav>
</header>

<main>
{body}
</main>

<footer class="col foot">
  <span>&copy; 2026 {author}</span>
  <span>Wichita, Kansas</span>
</footer>

</body>
</html>
"""


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


# ------------------------------------------------------------------ fresh copies
def stamp_assets(page):
    """Add ?v=<fingerprint> to every assets/ file a page uses.  When the stylesheet, the
    headshot or the CV changes, its address changes too, so no browser or web host can go
    on serving the old copy."""
    def stamp(m):
        path = os.path.join(HERE, "assets", m.group(1))
        if not os.path.isfile(path):
            return m.group(0)
        return "assets/%s?v=%s" % (m.group(1), hashlib.sha1(open(path, "rb").read()).hexdigest()[:8])
    return re.sub(r"assets/([A-Za-z0-9._-]+)(?!\?v=)", stamp, page)


# ------------------------------------------------------------------ publications
def pub_item(p):
    e = html.escape
    bits = ['<span class="a">%s</span>' % e(p["authors"]), '<span class="t">%s</span>' % e(p["title"])]
    if p.get("venue"):
        bits.append('<span class="j">%s</span>' % e(p["venue"]))
    if p.get("details"):
        bits.append('<span class="n">%s</span>' % e(p["details"]))
    if p.get("note"):
        bits.append('<span class="n">%s</span>' % e(p["note"]))
    if p.get("doi"):
        bits.append('<a href="https://doi.org/%s">doi.org/%s</a>' % (e(p["doi"], quote=True), e(p["doi"])))
    if p.get("url"):
        bits.append('<a href="%s">%s</a>' % (e(p["url"], quote=True), e(p.get("urlText", "Link"))))
    return '        <li><span class="when">%s</span><span class="what">%s</span></li>' % (e(p["year"]), " ".join(bits))


def publications_fields():
    data = json.load(open(os.path.join(HERE, "data", "publications.json"), encoding="utf-8"))
    return {
        "ARTICLES": "\n".join(pub_item(p) for p in data["articles"]),
        "BOOK": "\n".join(pub_item(p) for p in data["book"]),
        "OTHER": "\n".join(pub_item(p) for p in data["other"]),
        "N_ARTICLES": str(len(data["articles"])),
        "N_OTHER": str(len(data["other"])),
    }


# ------------------------------------------------------------------ pages
def build_pages():
    fields = dict(LINKS, TOOL_NAME=html.escape(TOOL_NAME), TOOL_SLUG=SLUG, **publications_fields())
    for out, label, frag, title, desc in PAGES:
        body = read(os.path.join(HERE, "pages", frag))
        body = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: fields[m.group(1)], body)
        left = re.findall(r"\{\{.*?\}\}", body)
        if left:
            sys.exit("build_site: unfilled placeholders in %s: %s" % (frag, left))
        tabs = "\n".join('    <a href="%s"%s>%s</a>' % (f, ' aria-current="page"' if f == out else "", l)
                         for f, l, _frag, _t, _d in PAGES if l)
        page = SHELL.format(title=html.escape(title), description=html.escape(desc, quote=True), fonts=FONTS,
                            author=html.escape(AUTHOR), tabs=tabs, body=body.rstrip(),
                            home_current=' aria-current="page"' if out == "index.html" else "")
        page = stamp_assets(page)
        write(os.path.join(HERE, out), page)
        print("wrote %-20s %5.1f KB" % (out, len(page.encode("utf-8")) / 1024))


# ------------------------------------------------------------------ the tool
SKIN = """  <style id="site-skin">
    /* the personal site's colors over Design A3's tokens; same three theme scopes, later in
       the document, so they win without touching the tool's own stylesheet */
    :root {
      --heading: #1F4D3A; --brand: #B23A2B; --focus: #1F4D3A; --band: #1F4D3A; --band-ink: #123024;
      --ink: #15211C; --ink-2: #43524A; --ink-3: #66746C; --rule: #D6DED8; --rule-2: #BBC7BF;
      --surface-2: #F1F5F2; --surface-3: #E4ECE6;
    }
    @media (prefers-color-scheme: dark) {
      :root:not([data-theme="light"]) { --heading: #A9D1BE; --brand: #E27B6B; --focus: #A9D1BE; --band: #1B3F31; }
    }
    :root[data-theme="dark"] { --heading: #A9D1BE; --brand: #E27B6B; --focus: #A9D1BE; --band: #1B3F31; }
    .sitebar {
      display: flex; flex-wrap: wrap; justify-content: space-between; gap: 4px 16px;
      max-width: 960px; margin: 0 auto; padding: 11px clamp(16px, 4vw, 32px); font-size: 14px;
    }
    .sitebar a { color: var(--heading); font-weight: 600; text-decoration: none; }
    .sitebar a:hover { text-decoration: underline; text-underline-offset: 3px; }
    .sitebar span { color: var(--ink-3); }
    .sitebar .sep { margin: 0 8px; }
  </style>
"""


def sub1(text, old, new, label):
    if text.count(old) != 1:
        sys.exit("build_site: expected exactly one %r in the tool (%s) -- has Design A3 changed?" % (old[:50], label))
    return text.replace(old, new)


def build_tool():
    if not os.path.exists(TOOL_SRC):
        sys.exit("missing %s\nbuild it first:  py build_standalone.py --design a3   (in budget-simulation)" % TOOL_SRC)
    page = read(TOOL_SRC)
    page, n = re.subn(r"<title>.*?</title>", "<title>%s | %s</title>" % (html.escape(TOOL_NAME), html.escape(AUTHOR)),
                      page, count=1)
    if n != 1:
        sys.exit("build_site: no <title> found in the tool")
    page = sub1(page, "<h1>Where your school property tax goes</h1>", "<h1>%s</h1>" % html.escape(TOOL_NAME), "headline")
    page = sub1(page, '<h2 id="fn-title">What your tax pays for</h2>',
                '<h2 id="fn-title">Your bill, service by service</h2>', "services heading")
    page, n = re.subn(r"mine \? 'What your tax pays for' : 'What this home(?:’|\\u2019)s tax pays for';",
                      "mine ? 'Your bill, service by service' : 'This home\\\\u2019s bill, service by service';",
                      page, count=1)
    if n != 1:
        sys.exit("build_site: services heading script line not found -- has Design A3 changed?")
    page = sub1(page, "</head>", SKIN + "</head>", "skin")
    page = sub1(page, '<div class="wrap">',
                '<div class="wrap">\n  <nav class="sitebar" aria-label="Site"><span>'
                '<a href="../../index.html">&larr; %s</a><span class="sep">/</span>'
                '<a href="../../projects.html">Projects</a></span><span>%s</span></nav>'
                % (html.escape(AUTHOR), html.escape(TOOL_NAME)), "sitebar")
    page = sub1(page, '<div class="notes">',
                '<div class="notes">\n      <p><b>About this tool.</b> Built by %s from the district&rsquo;s published '
                'budget documents. It is not an official product of Wichita Public Schools.</p>'
                % html.escape(AUTHOR), "byline")
    write(TOOL_OUT, page)
    print("wrote %-20s %5.1f KB  as %r" % (os.path.relpath(TOOL_OUT, HERE).replace(os.sep, "/"),
                                           len(page.encode("utf-8")) / 1024, TOOL_NAME))


if __name__ == "__main__":
    build_pages()
    build_tool()
