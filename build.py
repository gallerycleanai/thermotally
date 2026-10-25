#!/usr/bin/env python3
"""Static site generator for the ThermoTally demand-validation site.
Python 3.8+. Only extra dependency: reportlab (for the 5 printable PDFs).
  pip install reportlab && python3 build.py      -> writes the site into ./docs
If reportlab is missing, the pre-built PDFs in static/downloads/ are copied instead.
All settings live in site.config.json.
"""
import json, os, re, shutil, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CFG = json.loads((ROOT / "site.config.json").read_text())
if os.environ.get("TT_SITE_URL"):          # local testing override
    CFG["SITE_URL"] = os.environ["TT_SITE_URL"]
if os.environ.get("TT_BASE_PATH") is not None:
    CFG["BASE_PATH"] = os.environ["TT_BASE_PATH"]
OUT, SRC, STATIC = ROOT / "docs", ROOT / "src", ROOT / "static"
BRAND = CFG["BRAND"]
SITE_URL = CFG["SITE_URL"].rstrip("/")
BASE = ("/" + CFG.get("BASE_PATH", "").strip("/")) if CFG.get("BASE_PATH", "").strip("/") else ""
FORM = CFG["WAITLIST_FORM_URL"].strip()
FORM_READY = FORM.startswith("http")
GC = CFG.get("GOATCOUNTER_CODE", "").strip()
GC_READY = bool(GC) and GC != "GOATCOUNTER_CODE"
GSV = CFG.get("GOOGLE_SITE_VERIFICATION", "").strip()
GSV_READY = bool(GSV) and GSV != "GOOGLE_SITE_VERIFICATION"
TODAY = datetime.date.today().isoformat()
PATHS = []   # for sitemap

def url(p): return BASE + p
def abs_url(p): return SITE_URL + BASE + p
def waitlist_href(src=""):
    if FORM_READY:
        return FORM + (("&" if "?" in FORM else "?") + "source=" + src if src else "")
    return url("/waitlist/")
def waitlist_attrs(): return ' target="_blank" rel="noopener"' if FORM_READY else ""

def subst(s):
    s = re.sub(r"\{\{WAITLIST:([a-z0-9-]+)\}\}", lambda m: waitlist_href(m.group(1)), s)
    return (s.replace("{{BRAND}}", BRAND).replace("{{BASE}}", BASE)
             .replace("{{WAITLIST}}", waitlist_href()).replace("{{WAITLIST_ATTRS}}", waitlist_attrs())
             .replace("{{SITE}}", SITE_URL + BASE))

def load(folder, prefix):
    items = []
    for f in sorted((SRC / folder).glob("*.html")):
        raw = f.read_text()
        m = re.match(r"<!--META\s*(\{.*?\})\s*-->\s*", raw, re.S)
        meta = json.loads(m.group(1)); meta["body"] = raw[m.end():]
        meta["path"] = f"{prefix}{meta['slug']}/" if prefix else f"/{meta['slug']}/"
        items.append(meta)
    items.sort(key=lambda g: g["order"]); return items

GUIDES = load("guides", "/guides/")
NICHES = load("for", "")
TEMPLATES = load("templates", "/templates/")

LOGO = ('<svg class="mark" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="8" fill="#0f2a24"/>'
        '<rect x="13" y="5" width="6" height="16" rx="3" fill="none" stroke="#e9f5f0" stroke-width="2"/>'
        '<circle cx="16" cy="23" r="4.5" fill="#10b981"/><rect x="15" y="11" width="2" height="9" fill="#10b981"/>'
        '<path d="M22 9h4M22 13h3M22 17h4" stroke="#7dd3b0" stroke-width="1.6" stroke-linecap="round"/></svg>')

DISCLAIMER = (f"{BRAND} is an independent, pre-launch product. The free templates and guides summarize the FDA Food Code for general "
              "information only. They are not legal advice. Your state or local health department's adopted code and its inspectors decide "
              "what applies to you, and local rules can be stricter. We are not affiliated with the FDA or any health department. "
              "Nothing is sold or charged on this site.")

def header():
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="site-header"><div class="wrap">
  <a class="logo" href="{url('/')}">{LOGO}<span>{BRAND}</span></a>
  <nav class="nav" aria-label="Main">
    <a href="{url('/templates/')}">Free templates</a>
    <a href="{url('/guides/')}">Guides</a>
    <a href="{url('/#how')}" class="hide-sm">How it works</a>
    <a class="btn btn-primary" href="{waitlist_href('nav')}"{waitlist_attrs()} data-goatcounter-click="nav-waitlist">Join the waitlist</a>
  </nav>
</div></header>'''

def footer():
    li = lambda items: "".join(f'<li><a href="{url(g["path"])}">{html.escape(g["nav"])}</a></li>' for g in items)
    return f'''<footer class="site-footer"><div class="wrap">
  <div class="cols">
    <div><a class="logo" href="{url('/')}">{LOGO}<span>{BRAND}</span></a>
      <p style="max-width:330px;margin-top:12px">Simple food safety logs for one-location kitchens: temperatures, cooling, deliveries and cleaning, ready for the inspector.</p></div>
    <div><h5>Free templates</h5><ul>{li(TEMPLATES)}</ul></div>
    <div><h5>Guides</h5><ul>{li(GUIDES)}</ul></div>
    <div><h5>Who it's for</h5><ul>{li(NICHES)}<li><a href="{url('/waitlist/')}">Waitlist</a></li><li><a href="{url('/legal/')}">Disclaimer &amp; privacy</a></li></ul></div>
  </div>
  <p class="disclaimer">{DISCLAIMER}<br>© {datetime.date.today().year} {BRAND}.</p>
</div></footer>'''

def analytics():
    if not GC_READY:
        return "<!-- Analytics off: set GOATCOUNTER_CODE in site.config.json -->"
    return f'<script data-goatcounter="https://{GC}.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'

ORG = {"@type": "Organization", "name": BRAND, "url": abs_url("/")}

def breadcrumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": abs_url(p)} for i, (n, p) in enumerate(items)]}

def faq_ld(body):
    faqs = re.findall(r"<details><summary>(.*?)</summary>\s*<p>(.*?)</p></details>", body, re.S)
    if not faqs: return None
    clean = lambda s: html.unescape(re.sub("<.*?>", "", subst(s))).strip()
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": clean(q), "acceptedAnswer": {"@type": "Answer", "text": clean(a)}} for q, a in faqs]}

def page(path, title, desc, body, jsonld=None, og_type="website", index=True, sitemap=True):
    canonical = abs_url(path)
    ld = "".join('<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False) + "</script>\n" for b in (jsonld or []) if b)
    verify = f'<meta name="google-site-verification" content="{html.escape(GSV)}">' if GSV_READY else ""
    t, d = html.escape(title), html.escape(desc)
    doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{'index,follow' if index else 'noindex'}">
{verify}
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{abs_url('/og.png')}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{url('/favicon.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{url('/styles.css')}">
{ld}</head>
<body>
{header()}
<main id="main">
{body}
</main>
{footer()}
{analytics()}
</body>
</html>
'''
    target = OUT / path.lstrip("/") / "index.html" if path.endswith("/") else OUT / path.lstrip("/")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(subst(doc))
    if sitemap and index: PATHS.append(path)

def cta(src, text=None):
    text = text or (f"<strong>Paper logs get lost, skipped and back-filled.</strong> {BRAND} is a phone app that reminds your team when a check is due, "
                    "flags out-of-range temps on the spot, and turns a month of logs into one clean PDF for the inspector. Join the waitlist and tell us what you'd pay.")
    return (f'<div class="inline-cta"><p>{text}</p>'
            f'<a class="btn btn-dark" href="{{{{WAITLIST:{src}}}}}"{{{{WAITLIST_ATTRS}}}} data-goatcounter-click="{src}-waitlist">Join the waitlist →</a></div>')

def tpl_cards(items=None):
    items = items or TEMPLATES
    return "".join(f'''<a class="card tpl" href="{url(t["path"])}"><img src="{url('/img/' + t['pdf'].replace('.pdf', '.png'))}" alt="Preview of the free {html.escape(t["nav"].lower())} PDF" loading="lazy" width="330" height="255"><h3>{html.escape(t["nav"])}</h3><p>{html.escape(t["teaser"])}</p></a>''' for t in items)

def guide_cards(items=None):
    items = items or GUIDES
    return "".join(f'<a class="card" href="{url(g["path"])}"><h3>{html.escape(g["h1"])}</h3><p>{html.escape(g["teaser"])}</p></a>' for g in items)

def niche_cards():
    return "".join(f'<a class="card niche" href="{url(n["path"])}"><span class="emoji" aria-hidden="true">{n["icon"]}</span><h3>{html.escape(n["nav"])}</h3><p>{html.escape(n["teaser"])}</p></a>' for n in NICHES)

def expand(body):
    return (body.replace("{{TEMPLATE_CARDS}}", tpl_cards()).replace("{{GUIDE_CARDS}}", guide_cards())
                .replace("{{NICHE_CARDS}}", niche_cards()))

def build_home():
    body = expand((SRC / "home.html").read_text())
    app_ld = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": BRAND, "applicationCategory": "BusinessApplication",
              "operatingSystem": "iOS, Android, Web", "description": "Planned phone app for food safety logs (fridge, freezer, hot/cold holding, cooling, receiving, cleaning) for single-location restaurants, food trucks, cafés and bakeries. Waitlist open.",
              "url": abs_url("/"), "publisher": ORG}
    site_ld = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": abs_url("/")}
    page("/", f"Food Safety Log App & Free Temperature Log Sheets | {BRAND}",
         "Log fridge, hot-holding, cooling and cleaning checks on your phone in seconds, get reminders for missed checks, and print an inspector-ready PDF. Free printable logs.",
         body, [site_ld, app_ld, faq_ld(body)])

def build_niches():
    for n in NICHES:
        body = expand(n["body"]).replace("{{CTA}}", cta(n["slug"]))
        page(n["path"], n["title"], n["description"], body,
             [{"@context": "https://schema.org", "@type": "WebPage", "name": n["h1"], "description": n["description"], "url": abs_url(n["path"]), "publisher": ORG},
              breadcrumbs([("Home", "/"), (n["nav"], n["path"])]), faq_ld(n["body"])])

def sidebar(cur):
    cur_attr = ' aria-current="page"'
    a = lambda items: "".join(f'<li><a href="{url(g["path"])}"{cur_attr if g["path"] == cur else ""}>{html.escape(g["nav"])}</a></li>' for g in items)
    return f'<aside class="sidebar"><h4>Free templates</h4><ul>{a(TEMPLATES)}</ul><h4>Guides</h4><ul>{a(GUIDES)}</ul></aside>'

def dl_button(t, where):
    return (f'<a class="btn btn-primary dl" href="{url("/downloads/" + t["pdf"])}" download data-goatcounter-click="dl-{t["slug"]}-{where}" '
            f'data-goatcounter-title="Download {html.escape(t["nav"])} ({where})">⬇ Download the free PDF</a>')

def build_guides():
    for g in GUIDES:
        rel = [x for x in GUIDES if x["slug"] in g.get("related", [])]
        reltpl = [x for x in TEMPLATES if x["slug"] in g.get("templates", [])]
        b = g["body"]
        for t in TEMPLATES:
            b = b.replace("{{DL:" + t["slug"] + "}}", dl_button(t, "guide-" + g["slug"]))
        body = f'''<div class="wrap doc">
{sidebar(g["path"])}
<article class="prose">
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Home</a> / <a href="{url('/guides/')}">Guides</a> / {html.escape(g["nav"])}</nav>
<h1>{html.escape(g["h1"])}</h1>
<p class="meta">Updated {TODAY} · {g.get("minutes", 6)} min read · Based on the FDA Food Code</p>
{b}
{cta("guide-" + g["slug"])}
{('<div class="related"><h3>Free printable templates for this</h3><div class="grid g3">' + tpl_cards(reltpl) + '</div></div>') if reltpl else ''}
<div class="related"><h3>Related guides</h3><ul>{"".join(f'<li><a href="{url(x["path"])}">{html.escape(x["h1"])}</a></li>' for x in rel)}</ul></div>
<p class="legal-note">This guide is general information based on the FDA Food Code, not legal advice. Check your local health department's adopted code.</p>
</article></div>'''
        art = {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["description"], "dateModified": TODAY,
               "datePublished": g.get("published", TODAY), "author": ORG, "publisher": ORG, "mainEntityOfPage": abs_url(g["path"])}
        page(g["path"], g["title"], g["description"], body, [art, breadcrumbs([("Home", "/"), ("Guides", "/guides/"), (g["nav"], g["path"])]), faq_ld(b)], og_type="article")

def build_templates():
    for t in TEMPLATES:
        b = t["body"].replace("{{DL}}", dl_button(t, "page"))
        others = [x for x in TEMPLATES if x["slug"] != t["slug"]]
        body = f'''<div class="wrap doc">
{sidebar(t["path"])}
<article class="prose">
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url('/')}">Home</a> / <a href="{url('/templates/')}">Free templates</a> / {html.escape(t["nav"])}</nav>
<h1>{html.escape(t["h1"])}</h1>
<div class="tpl-hero"><img src="{url('/img/' + t['pdf'].replace('.pdf', '.png'))}" alt="Preview of the {html.escape(t["nav"].lower())} printable PDF" width="660" height="510">
<div><p class="lede">{t["lede"]}</p>{dl_button(t, "hero")}<p class="fine">Free PDF · US Letter, landscape · no email required · {t.get("format", "1 page")}</p></div></div>
{b}
{cta("tpl-" + t["slug"], f"<strong>Want this log on your phone instead?</strong> {BRAND} will remind your team when this check is due, flag out-of-range readings, and give you the same log as a clean PDF for any date range. Tell us what you'd pay.")}
<div class="related"><h3>More free logs</h3><div class="grid g2">{tpl_cards(others)}</div></div>
<p class="legal-note">Template based on the FDA Food Code. Not legal advice; your local health department may require a specific form or stricter limits.</p>
</article></div>'''
        doc_ld = {"@context": "https://schema.org", "@type": "DigitalDocument", "name": t["h1"], "description": t["description"], "encodingFormat": "application/pdf",
                  "url": abs_url("/downloads/" + t["pdf"]), "isAccessibleForFree": True, "publisher": ORG, "dateModified": TODAY}
        page(t["path"], t["title"], t["description"], body, [doc_ld, breadcrumbs([("Home", "/"), ("Free templates", "/templates/"), (t["nav"], t["path"])]), faq_ld(b)])

def build_indexes():
    body = f'''<section><div class="wrap"><p class="eyebrow">Free printables</p><h1 class="h2">Free food safety log templates (PDF)</h1>
<p class="sub">Five printable logs built on the FDA Food Code limits: fridge and freezer, hot and cold holding, cooling, receiving and cleaning. Print them, hang them on a clipboard, no email needed.</p>
<div class="grid g3">{tpl_cards()}</div>{cta("templates-index")}</div></section>'''
    page("/templates/", f"Free Food Safety Log Templates: Temperature, Cooling, Receiving, Cleaning (PDF) | {BRAND}",
         "Download 5 free printable food safety logs: fridge/freezer temperature log, hot & cold holding log, food cooling log, receiving log and kitchen cleaning schedule.",
         body, [breadcrumbs([("Home", "/"), ("Free templates", "/templates/")])])
    body = f'''<section><div class="wrap"><p class="eyebrow">Guides</p><h1 class="h2">Food safety logs, explained in plain English</h1>
<p class="sub">What to record, how often, the temperatures that matter, and what inspectors look for, based on the FDA Food Code.</p>
<div class="grid g2">{guide_cards()}</div></div></section>'''
    page("/guides/", f"Food Safety Log Guides for Small Kitchens | {BRAND}",
         "Plain-English guides to temperature logs, cooling logs, hot and cold holding, cleaning schedules and digital vs paper records, based on the FDA Food Code.",
         body, [breadcrumbs([("Home", "/"), ("Guides", "/guides/")])])

def build_waitlist():
    if FORM_READY:
        embed = FORM
        if "tally.so/r/" in FORM:
            embed = FORM.replace("tally.so/r/", "tally.so/embed/") + ("&" if "?" in FORM else "?") + "alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1"
        elif "docs.google.com/forms" in FORM and "embedded=true" not in FORM:
            embed = FORM + ("&" if "?" in FORM else "?") + "embedded=true"
        form = (f'<p><a class="btn btn-dark" href="{FORM}" target="_blank" rel="noopener" data-goatcounter-click="waitlist-open">Open the form in a new tab →</a></p>'
                f'<iframe class="form-frame" src="{embed}" title="Waitlist form" loading="lazy"></iframe>')
    else:
        form = ('<div class="placeholder"><strong>Form not connected yet.</strong> The site owner still needs to set '
                '<code>WAITLIST_FORM_URL</code> in <code>site.config.json</code>. Please check back soon.</div>')
    body = f'''<div class="wrap doc one"><article class="prose narrow">
<p class="eyebrow">Early access</p><h1>Join the {BRAND} waitlist</h1>
<p class="lede">We're building the simplest food safety log for one-location kitchens. Answer 8 quick questions (about 90 seconds) and you'll get early access, plus a founding-member price if you're one of the first 100.</p>
<ul><li>No payment, no card. Nothing is sold yet.</li><li>We only use your email to tell you about {BRAND}. Unsubscribe any time.</li>
<li>Your answers decide what we build first: which logs, which alerts, and the price.</li></ul>
{form}
<p>Prefer paper for now? The <a href="{url('/templates/')}">free printable logs</a> stay free.</p>
</article></div>'''
    page("/waitlist/", f"Join the waitlist | {BRAND} food safety log app",
         "Get early access to a simple food safety log app for restaurants, food trucks, cafés and bakeries. Free to join, no card.", body,
         [breadcrumbs([("Home", "/"), ("Waitlist", "/waitlist/")])])

def build_legal():
    page("/legal/", f"Disclaimer & privacy | {BRAND}", f"Disclaimer, sources and privacy notes for the {BRAND} pre-launch site.",
         (SRC / "legal.html").read_text(), [breadcrumbs([("Home", "/"), ("Disclaimer & privacy", "/legal/")])])

def build_404():
    body = f'''<section><div class="wrap"><h1 class="h2">Page not found</h1><p class="sub">That page doesn't exist. Try the <a href="{url('/templates/')}">free templates</a>, the <a href="{url('/guides/')}">guides</a> or the <a href="{url('/')}">home page</a>.</p></div></section>'''
    page("/404.html", f"Not found | {BRAND}", "Page not found.", body, index=False, sitemap=False)

def build_sitemap():
    pr = {"/": "1.0", "/templates/": "0.9", "/guides/": "0.8"}
    xs = "".join(f"<url><loc>{abs_url(p)}</loc><lastmod>{TODAY}</lastmod><priority>{pr.get(p, '0.7')}</priority></url>\n" for p in PATHS)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + xs + "</urlset>\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {abs_url('/sitemap.xml')}\n")

def build_pdfs():
    dl = OUT / "downloads"; dl.mkdir(parents=True, exist_ok=True)
    footer_url = (CFG.get("CUSTOM_DOMAIN") or "").strip() or (SITE_URL + BASE).replace("https://", "")
    if "YOUR-" in footer_url: footer_url = ""   # placeholder config: PDFs show brand only
    try:
        import make_pdfs
        make_pdfs.make_all(dl, BRAND, footer_url)
        prebuilt = STATIC / "downloads"; prebuilt.mkdir(exist_ok=True)
        for f in dl.glob("*.pdf"): shutil.copy(f, prebuilt / f.name)   # keep fallback copies fresh
        return "generated"
    except ImportError:
        for f in (STATIC / "downloads").glob("*.pdf"): shutil.copy(f, dl / f.name)
        return "copied pre-built (pip install reportlab to regenerate with your URL)"

def main():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir()
    for f in STATIC.rglob("*"):
        if f.is_file() and "downloads" not in f.parts:
            dest = OUT / f.relative_to(STATIC); dest.parent.mkdir(parents=True, exist_ok=True)
            if f.suffix == ".css": dest.write_text(subst(f.read_text()))
            else: shutil.copy(f, dest)
    (OUT / ".nojekyll").write_text("")
    if CFG.get("CUSTOM_DOMAIN", "").strip(): (OUT / "CNAME").write_text(CFG["CUSTOM_DOMAIN"].strip() + "\n")
    how = build_pdfs()
    build_home(); build_niches(); build_indexes(); build_templates(); build_guides(); build_waitlist(); build_legal(); build_404(); build_sitemap()
    warn = []
    if not FORM_READY: warn.append("WAITLIST_FORM_URL is still a placeholder (buttons go to /waitlist/)")
    if not GC_READY: warn.append("GOATCOUNTER_CODE not set (analytics + download tracking off)")
    if not GSV_READY: warn.append("GOOGLE_SITE_VERIFICATION not set")
    if "YOUR-GITHUB-USERNAME" in SITE_URL: warn.append("SITE_URL still has the placeholder")
    print(f"Built {sum(1 for _ in OUT.rglob('*.html'))} HTML pages, {len(list((OUT/'downloads').glob('*.pdf')))} PDFs ({how}) into {OUT}")
    for w in warn: print("  ! " + w)

if __name__ == "__main__":
    main()
