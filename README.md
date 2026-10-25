# ThermoTally: zero-cost demand test for a food-safety log app

<div dir="rtl">

## סיכום בעברית

**מה זה:** אתר SEO סטטי ומוכן לפריסה, שבודק תוך 2–8 שבועות ובלי שקל אחד אם בעלי עסקי מזון קטנים בארה"ב (מסעדה בודדת, פודטראק, בית קפה/מאפייה) מחפשים, מורידים ונרשמים לאפליקציית יומני בטיחות מזון במחיר 19–39$ לחודש לסניף.

**המיצוב:** "יומני בטיחות מזון שהצוות באמת ממלא – למטבח עם סניף אחד". רישום טמפרטורה בטלפון בכ־10 שניות, תזכורת כשבדיקה מתפספסת, ו־PDF מסודר למפקח בלחיצה. מחיר קבוע מחודש לחודש: בלי חומרה, בלי דמי הקמה ובלי חוזה שנתי. זה בדיוק מה שלקוחות של Jolt, Trail ו־ComplianceMate מתלוננים עליו.

**השם הזמני:** ThermoTally. הדומיין thermotally.com פנוי (נבדק ב־RDAP ב־25.10.2026), ולא נמצא סימן מסחרי מתנגש. כדאי לבדוק שוב ב־USPTO לפני רכישה.

**ממצאים עיקריים:**
- הביקוש הוא "זנב ארוך": עשרות וריאציות של "temperature log sheet pdf / template / for restaurant".
- בתוצאות החיפוש שולטים קובצי PDF של משרדי בריאות מקומיים, עם SEO חלש. אפשר לנצח אותם.
- נישת האפליקציות הזולות מתחילה להתמלא (SafePlate בחינם, LogChill ב־18$). לכן היתרון צריך להגיע מהפצה דרך SEO ותבניות חינמיות, ומפוקוס על פודטראקים ובתי קפה.
- כדאי להתחיל בארה"ב. בבריטניה המחירים נמוכים מאוד ויש חבילה ממשלתית חינמית (SFBB).
- פירוט מלא ב־`RESEARCH.md`.

**מה יש באתר:** 20 עמודים:
- דף בית
- 3 דפי נישה: מסעדות, פודטראקים, בתי קפה/מאפיות
- 6 מאמרים
- 5 דפי תבנית, כל אחד עם PDF להורדה חינמית
- דף רשימת המתנה
- עמוד משפטי ו־404

כל עמוד כולל title, meta, canonical, JSON-LD, sitemap ו־robots. כל הורדה נספרת כאירוע ב־GoatCounter.

**מה אתה עושה בעצמך (כ־60 דקות, הכול בחינם):**
1. פותח טופס Tally עם השאלות שלמטה, ומדביק את הקישור ב־`site.config.json`.
2. פותח חשבון GoatCounter ומדביק את הקוד.
3. מעלה את האתר ל־GitHub Pages או ל־Firebase Hosting.
4. מחבר את האתר ל־Google Search Console ושולח את ה־sitemap.

**החלטה:** בשבוע 2 בודקים שהכול עובד. בשבוע 8 מחליטים GO או KILL לפי טבלת הניקוד שלמטה.

</div>

---

## What's in this folder
| Path | What |
|---|---|
| `site.config.json` | **The only file you edit.** Brand, URL, form link, analytics, verification |
| `build.py` | Generator → writes the site into `docs/` (`pip install reportlab` once, then `python3 build.py`) |
| `make_pdfs.py` | Generates the 5 printable PDFs (footer shows your site URL) |
| `src/` | Page content: `home.html`, `for/` (3 niche pages), `guides/` (6 articles), `templates/` (5 template pages), `legal.html` |
| `static/` | CSS, favicon, OG image, PDF preview images, fallback PDFs |
| `docs/` | **Built site** (deploy this folder) |
| `firebase.json`, `.firebaserc` | Firebase Hosting config (public = `docs`) |
| `.github/workflows/pages.yml` | GitHub Pages auto-deploy |
| `RESEARCH.md` | 41 keywords in clusters, SERP notes, competitor table and quotes, gaps, positioning, name check |
| `home.png` | Screenshot of the home page |

Pages: `/`, `/restaurants/`, `/food-trucks/`, `/cafes-bakeries/`, `/templates/` + 5 (`fridge-freezer-temperature-log`, `hot-cold-holding-temperature-log`, `food-cooling-log`, `receiving-log`, `kitchen-cleaning-schedule`), `/guides/` + 6 (`fridge-temperature-log`, `haccp-temperature-log`, `food-cooling-log-2-hour-6-hour-rule`, `hot-and-cold-holding-temperatures`, `restaurant-cleaning-schedule`, `paper-vs-digital-temperature-logs`), `/waitlist/`, `/legal/`, `404.html`. PDFs are served from `/downloads/*.pdf`.

## Step 1: Waitlist form in Tally (free, ~15 min)
Create a free form at tally.so. **Add a hidden field named `source`**: the site appends `?source=hero`, `?source=tpl-food-cooling-log`, etc., so you'll see which page converts.

Questions (keep them in this order; mark 1, 2 and 7 as required):
1. **Email** (required)
2. **What do you run?** Restaurant (1 location) / Restaurant (2–5 locations) / Food truck or trailer / Café or coffee shop / Bakery / Home or cottage baker / Caterer / Other (required)
3. **Where are you?** US state + county or city (short text). Use "Country" if outside the US.
4. **How do you keep food safety logs today?** Paper sheets / Binder from health dept / Spreadsheet / An app (which?) / We don't really keep them
5. **Which logs do you need?** (multi-select) Fridge/freezer temps / Hot & cold holding / Cooling / Receiving / Cleaning schedule / HACCP plan records / Date labels / Other
6. **What would you rather do?** Type readings on my phone / Keep paper and snap a photo at closing / Wireless sensors / Not sure
7. **What would you pay per location, per month, for an app that reminds your team, flags bad temps and prints the inspector report?** $0, I'd only use a free app / $10 / $19 / $29 / $39 / $49+ (required)
8. **When is your next health inspection (roughly)?** Within 1 month / 1–3 months / 3–12 months / Don't know
9. **Biggest pain with logs today?** (long text, optional)
10. **Want to be a beta tester and talk for 15 min?** Yes / No

Publish, copy the share link (`https://tally.so/r/XXXX`) and paste it into `WAITLIST_FORM_URL`. The waitlist page embeds it automatically.

## Step 2: GoatCounter analytics + download tracking (free, ~5 min)
Sign up at goatcounter.com and choose a code, e.g. `thermotally` (your dashboard becomes `thermotally.goatcounter.com`). Put just the code in `GOATCOUNTER_CODE`.
- Every download button has `data-goatcounter-click="dl-<template>-<where>"`, so downloads show in the dashboard as events starting with `dl-`. **Template downloads = sum of all `dl-*` events.**
- Waitlist clicks appear as `*-waitlist` events.

## Step 3: Deploy (pick one)
Before either option, edit `site.config.json`, then run `pip install reportlab && python3 build.py`. The build prints warnings for any placeholder still left.

**A. GitHub Pages (simplest)**
1. Create a public repo, e.g. `thermotally`, and push this folder to `main`.
2. Repo → Settings → Pages → Source: **GitHub Actions**. The included workflow builds and deploys on every push.
3. Config: `SITE_URL = https://<user>.github.io`, `BASE_PATH = /thermotally`.
   With a custom domain: `SITE_URL = https://thermotally.com`, `BASE_PATH = ""`, `CUSTOM_DOMAIN = thermotally.com`, plus the DNS records GitHub shows you.

**B. Firebase Hosting (free Spark plan)**
1. `npm i -g firebase-tools && firebase login`
2. Create a project in the console and put its ID in `.firebaserc`.
3. Config: `SITE_URL = https://<project-id>.web.app` (or your domain), `BASE_PATH = ""`.
4. `python3 build.py && firebase deploy --only hosting`

A domain is optional for the test. The free `github.io` / `web.app` URL is fine, and buying `thermotally.com` (~$10) can wait for a GO.

## Step 4: Google Search Console (free, ~10 min)
1. Add a **URL-prefix** property for your exact `SITE_URL + BASE_PATH/`.
2. Choose the *HTML tag* method, copy the `content="..."` value into `GOOGLE_SITE_VERIFICATION`, rebuild, deploy, then click Verify.
3. Sitemaps → submit `sitemap.xml`.
4. URL Inspection → *Request indexing* for the home page, `/templates/` and the 5 template pages.
5. Optional, free and no outreach: add the site to Bing Webmaster Tools (it can import from GSC).

## Local preview
```bash
TT_SITE_URL=http://localhost:8000 TT_BASE_PATH="" python3 build.py
cd docs && python3 -m http.server 8000
npx linkinator@6 http://localhost:8000/ --recurse      # expect 0 broken
```
Rebuild without the env vars before deploying.

## Validation scoreboard
Track weekly in a sheet. Sources: Search Console (impressions, clicks, pages indexed), GoatCounter (`dl-*` events, `*-waitlist` events), Tally (signups, price answers).

| Week | Impressions (GSC, cumulative) | Pages indexed | Template downloads | Waitlist signups | Signups choosing ≥ $19 |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| … | | | | | |
| 8 | | | | | |

**Week 2: feasibility check** (is the machine working? No business decision yet)
- [ ] Site live, the sitemap shows *Success* in GSC
- [ ] ≥ 10 pages indexed (or "Discovered", with indexing requested)
- [ ] First impressions appear in GSC (any number > 0)
- [ ] GoatCounter records page views and at least one test `dl-*` event (click a download yourself)
- [ ] A test Tally submission arrives with the `source` hidden field filled

If any box fails, fix it before the clock for week 8 counts.

**Week 8: GO / KILL decision**
| Metric (cumulative, weeks 1–8) | **GO** | Extend 4 weeks | **KILL** |
|---|---|---|---|
| GSC impressions | ≥ 3,000 | 500–3,000 | < 500 |
| Template downloads (`dl-*`) | ≥ 100 | 25–100 | < 25 |
| Waitlist signups | ≥ 30 | 8–30 | < 8 |
| Signups choosing **≥ $19**/location/month | ≥ 10 | 3–10 | < 3 |

- **GO** = all four at GO, or 3 at GO and the price metric ≥ 10. Next step: build the MVP (Firebase: logs + reminders + PDF), email the waitlist, and buy the domain.
- **KILL** = any metric in the KILL column, or price answers mostly "$0". Reuse the engine for the next compliance niche.
- **Extend** otherwise: add 2 articles a week targeting the clusters with the most GSC impressions, then decide at week 12.
- Price signal beats volume: 10 people saying "$29" is worth more than 200 downloads.

## Notes and limits
- All content summarizes the FDA Food Code 2022 (temperature limits unchanged in the 2026 edition) with a "not legal advice; check your local health department" disclaimer on every page and every PDF.
- Nothing on the site sells, charges or collects payment.
- Competitor prices in `RESEARCH.md` were gathered on Oct 25, 2026 from public pages and review sites, and change often.
