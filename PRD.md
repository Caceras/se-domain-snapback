# Product Requirements Document: DropScan

**Owner:** TBD
**Status:** Draft v1
**Last updated:** 2026-05-18
**Codename:** DropScan (current product surface name)

---

## 1. Summary

DropScan is a daily scanner that lists every `.se` and `.nu` domain releasing back into the registry pool, enriched with signals that indicate which ones are worth re‑registering. Today it produces a flat list with one weak signal (Wayback archived page count). This PRD describes the work needed to turn it from a "raw drop list" into a decision tool that a domainer, SEO, or brand‑protection user can rely on to pre‑select targets within minutes each morning.

## 2. Problem

When a `.se`/`.nu` domain expires it goes through quarantine and drops at **04:00 UTC**. The IIS bulk drop list is public, but on a typical day it contains **600–800 domains**. A user who wants to grab the valuable ones has to:

1. Pull the drop list themselves.
2. For each domain, decide whether it's worth registering.
3. Race to the registrar at the drop moment.

Steps 1 and 3 are mechanical. **Step 2 is the real work** and is what the product must do well. Today DropScan only completes step 1, dumps a CSV, and renders an empty "Expiring" page because the only value signal is broken in practice (see §11).

## 3. Goals & non‑goals

### Goals
- Surface the **top ~5%** of each day's drop list in priority order, with enough context to make a register/skip decision in < 10 seconds per domain.
- Be **trustworthy**: every signal shown must be reproducible from a public source linked from the row.
- Be **fast**: full daily scan < 10 min, page load < 1 s on cold cache.
- Be **passive**: a returning user should be able to set a watchlist + alerts and never need to log in unless they want to.

### Non‑goals
- Auto‑registration / sniping at the registrar. Out of scope legally and operationally.
- TLDs other than `.se` and `.nu`. Different drop mechanics, different audience.
- Current‑Whois lookups. IIS rate‑limits hard and the data is also stale for our use case.
- User accounts with passwords. Use email‑only magic link or anonymous device IDs.

## 4. Target users

| Persona | What they want | How they measure success |
|---|---|---|
| **Domainer** | Resellable names with traffic history | $ per drop‑day, registration ROI |
| **SEO operator** | Aged domains with backlinks for PBNs / 301s | Referring domains, archived page count, age |
| **Brand owner** | Catch lookalikes/typos of own brand before squatters | Daily alert hit rate, false positives |
| **Researcher / journalist** | Spot patterns (mass corp failure, sector trends) | Bulk export, history depth |

The **SEO operator** and **brand owner** drive most of the active engagement; the **domainer** drives most of the conversion intent.

## 5. Current state audit

What works:
- IIS fetch for `.se` and `.nu` (`src/fetcher.py`) is solid and handles network errors.
- Daily GitHub Action commits CSV + JSON to `reports/` and republishes static site under `docs/`.
- Flask app and static site render the same data model and share filter primitives.
- Reports are append‑only and form a usable historical dataset.

What's broken or weak:
- **Wayback index check returned 0 for every domain** since 2026‑02‑28 due to a malformed CDX query. Fixed in PR #12 — re‑validate once a fresh report lands.
- **DNS availability** check (`src/availability.py`) reports `available=True` for every row in recent reports, which is implausible — most expiring domains still have NS records pointing at the registrar. Needs investigation (§11.2).
- **Single weak signal**. Wayback page count is a coarse proxy. No backlink data, no age, no name‑quality score, no historical title/snippet.
- **Serial enrichment**. With `SCAN_DELAY_SECONDS=2.5` and ~700 domains, the index step alone takes ~30 minutes.
- **No persistence beyond JSON files**. Trend queries ("show me domains with 50+ pages that have dropped in the last 30 days") require scanning every report.
- **No way to act**. From the site there's no link out to a registrar, no copy‑button, no watchlist.
- **No alerting**. Daily users have to actively visit the site each morning.
- **No analytics**. We don't know which signals users actually look at.

## 6. Roadmap

The work is split into four releases so each one is independently shippable and provides user‑visible value.

### R1 — Trustworthy signals (1–2 weeks)
Make the existing "Expiring" page actually useful.

- **R1.1** Re‑validate Wayback fix on real data. If hit rate is < 3% of daily drops, something is still wrong.
- **R1.2** Fix DNS availability (`§11.2`). At minimum, distinguish `NXDOMAIN`, `NoAnswer`, and `Timeout` in the output instead of collapsing them all to `True`.
- **R1.3** Add **first‑archived date** and **last‑archived date** from Wayback as additional columns. Same CDX query, cheap to add (`from`/`to` fields).
- **R1.4** Add **name‑quality score** (pure local computation, free): length, hyphen count, digit count, dictionary‑word match against a Swedish + English wordlist, vowel/consonant ratio. Combine into a 0–100 score.
- **R1.5** Display a **composite "value score"** that's the user‑adjustable weighted sum of: archived pages (log‑scaled), archive age in years, name‑quality score, has‑MX in last archive. Default weights tuned on the first month of post‑fix data.

**Done when:** the Expiring page shows ≥ 20 ranked rows per day with each signal hyperlinked back to the underlying source.

### R2 — Act on a domain (1 week)
Close the gap between "I want this" and "I'm at the registrar."

- **R2.1** Per‑domain detail page (`/d/<domain>`): all signals, Wayback timeline strip, last‑known title from Wayback, similar names from same day's drop list.
- **R2.2** "Register at" outbound links to the top 3 Swedish registrars (Loopia, Binero, Glesys) — clearly labeled as affiliate if monetized later.
- **R2.3** One‑click copy of the bare domain name on every row.
- **R2.4** **Watchlist**: anonymous device‑scoped (localStorage + signed cookie). No login. User can mark up to 100 domains; watchlist persists across visits.

**Done when:** Site Analytics shows ≥ 30% of users who land on `/expiring` either click a registrar link or add to watchlist.

### R3 — Push, don't pull (2 weeks)
Stop requiring users to visit the site daily.

- **R3.1** **Email digest**: one email per day, sent at 07:30 UTC (just after the scan), with the top N domains and the user's watchlist matches. Magic‑link signup, one‑click unsubscribe.
- **R3.2** **RSS / Atom feed** of the top N each day. Free, no signup. Best fit for power users.
- **R3.3** **Webhook integration**: user supplies a Slack/Discord/generic webhook URL, receives a JSON payload after each scan.
- **R3.4** **Public read‑only API** (`/api/v1/...`) with documented schemas. Rate‑limited per IP. Free tier sufficient for a hobbyist; gates premium history depth later.

**Done when:** ≥ 20% of weekly active users consume DropScan without loading the website.

### R4 — Depth (3–4 weeks, can run in parallel with R3)
Make the signals genuinely differentiated from anyone else who can also poll the IIS list.

- **R4.1** **Backlink proxy** from Common Crawl. Pre‑compute referring‑host counts for every `.se`/`.nu` domain monthly, store in a small SQLite DB, join into the daily report.
- **R4.2** **Wayback screenshot thumbnails** — fetch the rendered snapshot once per qualifying domain, cache in `static/thumbs/`. Only do this for domains above a "value score" threshold to keep scan time bounded.
- **R4.3** **Historical title + meta description** extracted from the most recent Wayback snapshot. Often more informative than page count.
- **R4.4** **Trend dashboard** (`/trends`): rolling 30‑/90‑day charts of drop volume, indexed‑rate, average value score. Powered by querying the JSON archive (or the SQLite mirror from R4.1).

**Done when:** A returning user can answer "is this a normal Tuesday, or unusually rich?" without manually comparing reports.

## 7. Functional requirements (R1 detail)

This section is opinionated about R1 because it's the next thing to build. R2–R4 will be expanded into their own briefs before they're started.

### 7.1 Signal definitions

| Field | Source | Type | Notes |
|---|---|---|---|
| `archived_pages` | Wayback CDX, `len(rows)-1` | int ≥ 0 | Existing, post‑fix |
| `archive_first_seen` | Wayback CDX `from=` first row | ISO date | New |
| `archive_last_seen` | Wayback CDX last row timestamp | ISO date | New |
| `archive_age_years` | `(today - first_seen) / 365.25` | float | Derived |
| `name_length` | `len(domain.split('.')[0])` | int | Cheap |
| `name_hyphens` | count of `-` in label | int | Cheap |
| `name_digits` | count of `0–9` in label | int | Cheap |
| `name_dictionary_hits` | longest dict‑word substring match | int | Local wordlist |
| `name_quality_score` | weighted combination (0–100) | int | Reproducible formula in code |
| `value_score` | composite (0–100) | int | Default weights documented |

### 7.2 Display rules
- Default sort on `/expiring`: `value_score` desc, tiebreak `archived_pages` desc.
- Hide rows with `value_score < 20` behind a "show low‑value" toggle.
- Each numeric cell links to the underlying source (Wayback URL, IIS entry).
- Show the explicit `value_score` breakdown on hover.

### 7.3 Backwards compatibility
- The JSON report stays append‑only and additive. New fields are added, no field is renamed or removed in R1.
- The CSV gains new columns at the end — order preserved for existing consumers.
- Static site filter chips are unchanged; new "Quality" chip is additive.

## 8. Non‑functional requirements

| Area | Target |
|---|---|
| **Scan duration** | < 10 min P95 for the full daily run (currently ~30 min). Achieved by parallelizing Wayback queries with a bounded worker pool + per‑host concurrency cap. |
| **Site load** | First contentful paint < 1 s on a cold cache (static site, already close). |
| **Availability** | 99% — site is static on GitHub Pages, only the scanner can fail. |
| **Reproducibility** | Every signal must be regenerable from the raw IIS drop list + a stable code revision. Daily reports are immutable once committed. |
| **Accessibility** | WCAG 2.1 AA: keyboard navigation on the filter bar, focus rings, alt text on the new thumbnails. |
| **Privacy** | No PII collected pre‑R3. Watchlist is local‑only. Email digest stores `email + hashed_token + preferences`, nothing else. |
| **Cost** | $0 hosting through R3 (GitHub Pages + Actions). R3 email may need a transactional provider (~$10/mo for low volume). R4 backlink data may need ~$5/mo of object storage. |

## 9. Technical changes implied

- Move `reports/` history into a small SQLite mirror (built on the fly from JSON, kept in `docs/data.sqlite`) so the site can do range queries without shipping every JSON to the client.
- Introduce a `src/signals/` package, one module per signal, each with a `compute(domain) -> dict` contract. Makes unit testing per signal trivial and lets parallel workers fan out cleanly.
- Replace the manual `time.sleep(SCAN_DELAY_SECONDS)` loop with a `concurrent.futures.ThreadPoolExecutor` + per‑host token bucket (10 rps to archive.org is well within their published limits).
- Add a thin `web/` module that's used by both the Flask app and `build_static_site.py` for shared row/filter rendering — avoid the current copy‑paste between `templates/` and `build_static_site.py`.

## 10. Success metrics

Tracked from R2 onward (we need analytics first).

| Metric | R2 target | R3 target | R4 target |
|---|---|---|---|
| Daily uniques | 50 | 200 | 500 |
| Click‑through to a registrar | 5% | 10% | 15% |
| Watchlist adds per visitor | 0.3 | 0.5 | 0.8 |
| Email digest open rate | — | 35% | 40% |
| Median session time on `/expiring` | 60 s | 90 s | 120 s |
| Scanner P95 runtime | 10 min | 8 min | 6 min |
| % of indexed drops registered within 7 days (proxy: NS comes back) | baseline | +20% | +50% |

## 11. Known issues & open questions

### 11.1 Wayback hit rate after the fix
PR #12 fixes the CDX URL format. We need one or two real daily reports under the new code before we can size R1.5's value‑score weights. If the hit rate is still suspiciously low (< 3% of drops), something else is wrong (rate limit, IP block) and R1.1 becomes a blocker.

### 11.2 Availability check always returns True
Every recent report has `available=True` for every domain. Three possibilities, in order of likelihood:
1. DNS lookups time out from GitHub Actions runners and the timeout path returns `available=True` (it currently does).
2. Most pre‑drop domains have genuinely had their NS records pulled.
3. The resolver is misconfigured.

Investigation: run `is_available()` from a local machine against a sample of 50 domains from yesterday's report and compare to a Whois lookup. If (1), tighten the timeout semantics — a timeout is *unknown*, not *available*.

### 11.3 .DS_Store committed
Minor housekeeping but real — `.DS_Store` is in the repo. Add to `.gitignore` and delete.

### 11.4 Monetization
Affiliate links to registrars are the only path with zero user friction. Email digest is a natural place to upsell a "Pro" plan (deeper history, no rate limit, private watchlist sync). Defer the decision until R3 metrics exist.

### 11.5 Legal
Showing third‑party Wayback thumbnails is fine under archive.org's terms. Showing the live current site of a still‑registered‑but‑expiring domain is **not**. Stick to historical snapshots only.

## 12. Rollout plan

- **R1** ships behind no flag — it's strictly additive to existing reports and pages.
- **R2** ships the detail page first, then watchlist behind a `localStorage` flag for a week of friends‑and‑family.
- **R3** ships RSS first (no signup), then email (needs signup flow + double opt‑in).
- **R4** ships the trend dashboard first, then thumbnails (slow, expensive), then backlinks (needs the SQLite mirror).

Each release ends with: docs updated, a `CHANGELOG` entry, and one short blog post on the static site to drive returning traffic.

---

**Next action:** wait for PR #12 to land, then write the R1.1 + R1.2 issues and pick whichever has the higher signal‑per‑hour to start.
