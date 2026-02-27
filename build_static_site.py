#!/usr/bin/env python3
"""
Static site generator for GitHub Pages.

Converts JSON reports into static HTML pages with:
- PWA support (manifest, service worker, standalone mode)
- Favicon (SVG)
- Dark mode with system preference detection
- Responsive mobile-first design with app-like feel
- Structured data (JSON-LD) for search engine crawlers
- Open Graph / Twitter Card meta tags
- Search, sort, filter on every page
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

# Configuration
_HERE = Path(__file__).parent
REPORT_DIR = _HERE / "reports"
OUTPUT_DIR = _HERE / "docs"
TEMPLATE_DIR = _HERE / "templates"
SITE_NAME = "DropScan — .SE/.NU Domain Scanner"
SITE_DESCRIPTION = "Find valuable expiring .se and .nu domains before they drop. Daily snapback scanner with Wayback Machine data."
GITHUB_URL = "https://github.com/Caceras/se-domain-snapback"


def load_reports():
    """Load all available reports."""
    reports = []
    if REPORT_DIR.exists():
        for json_file in sorted(REPORT_DIR.glob("*.json"), reverse=True):
            if json_file.name != ".gitkeep":
                reports.append({
                    "date": json_file.stem,
                    "path": json_file
                })
    return reports


def load_report(report_date):
    """Load a specific report by date."""
    json_path = REPORT_DIR / f"{report_date}.json"
    if json_path.exists():
        with open(json_path, 'r') as f:
            return json.load(f)
    return None


# ── Shared CSS ────────────────────────────────────────────────────────────────

SHARED_CSS = """\
:root{
    --bg:#F5F5F7;--surface:#fff;--surface-2:#F5F5F7;--surface-3:#E8E8ED;
    --label:#1D1D1F;--label-2:#6E6E73;--label-3:#AEAEB2;
    --sep:rgba(0,0,0,0.08);--fill:rgba(0,0,0,0.04);--fill-2:rgba(0,0,0,0.08);
    --blue:#0071E3;--blue-h:#0077ED;--blue-t:rgba(0,113,227,0.1);
    --green:#28CD41;--green-t:rgba(40,205,65,0.1);
    --red:#FF3B30;--red-t:rgba(255,59,48,0.1);
    --tld-se:#0071E3;--tld-nu:#28CD41;
    --r:12px;--r-sm:8px;--r-lg:18px;
    --shadow:0 1px 3px rgba(0,0,0,0.04),0 4px 16px rgba(0,0,0,0.06);
    --shadow-sm:0 1px 2px rgba(0,0,0,0.04);
    --nav-h:52px;--safe-top:env(safe-area-inset-top,0px);--safe-bot:env(safe-area-inset-bottom,0px);
}
[data-theme="dark"]{
    --bg:#000;--surface:#1C1C1E;--surface-2:#2C2C2E;--surface-3:#3A3A3C;
    --label:#fff;--label-2:#98989D;--label-3:#636366;
    --sep:rgba(255,255,255,0.1);--fill:rgba(255,255,255,0.06);--fill-2:rgba(255,255,255,0.12);
    --blue:#0A84FF;--blue-h:#1A8FFF;--blue-t:rgba(10,132,255,0.15);
    --green:#30D158;--green-t:rgba(48,209,88,0.15);
    --red:#FF453A;--red-t:rgba(255,69,58,0.15);
    --tld-se:#0A84FF;--tld-nu:#30D158;
    --shadow:0 1px 3px rgba(0,0,0,0.3),0 4px 16px rgba(0,0,0,0.4);
    --shadow-sm:0 1px 2px rgba(0,0,0,0.3);
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:16px;scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
    font-family:-apple-system,BlinkMacSystemFont,"Helvetica Neue","Segoe UI",sans-serif;
    font-size:15px;line-height:1.5;color:var(--label);background:var(--bg);
    -webkit-tap-highlight-color:transparent;overscroll-behavior-y:none;
    padding-top:calc(var(--nav-h) + var(--safe-top));
    transition:background .2s,color .2s;
}
.navbar{
    position:fixed;top:0;left:0;right:0;z-index:200;
    height:calc(var(--nav-h) + var(--safe-top));padding-top:var(--safe-top);
    background:rgba(255,255,255,.85);
    backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);
    border-bottom:.5px solid var(--sep);
}
[data-theme="dark"] .navbar{background:rgba(28,28,30,.85);}
.navbar-inner{
    max-width:1100px;margin:0 auto;padding:0 20px;height:var(--nav-h);
    display:flex;align-items:center;justify-content:space-between;gap:12px;
}
.navbar-brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--label);}
.navbar-logo{width:28px;height:28px;border-radius:7px;}
.navbar-title{font-size:17px;font-weight:700;letter-spacing:-.03em;}
.nav-links{display:none;align-items:center;gap:4px;}
.nav-links a{
    font-size:14px;font-weight:500;color:var(--label-2);
    text-decoration:none;padding:6px 12px;border-radius:var(--r-sm);
    transition:color .15s,background .15s;
}
.nav-links a:hover{color:var(--label);background:var(--fill);}
.nav-links a.on{color:var(--blue);}
.btn-theme{
    width:36px;height:36px;border-radius:50%;background:var(--fill);border:none;
    cursor:pointer;display:flex;align-items:center;justify-content:center;
    font-size:15px;color:var(--label-2);transition:background .15s;
}
.btn-theme:hover{background:var(--fill-2);}
main{max-width:1100px;margin:0 auto;padding:24px 16px 40px;}
.page-title{font-size:26px;font-weight:700;letter-spacing:-.04em;margin-bottom:4px;}
.page-subtitle{font-size:14px;color:var(--label-2);margin-bottom:20px;}
.card{background:var(--surface);border-radius:var(--r-lg);padding:20px;margin-bottom:16px;box-shadow:var(--shadow);}
.card-title{font-size:17px;font-weight:600;letter-spacing:-.02em;margin-bottom:14px;}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:20px;}
.stat-card{
    background:var(--surface);border-radius:var(--r);padding:14px 16px;
    box-shadow:var(--shadow-sm);transition:transform .15s;
}
.stat-card::before{content:'';position:absolute;top:0;left:0;width:4px;height:100%;background:var(--accent);border-radius:4px 0 0 4px}
.stat-card:active{transform:scale(.97)}
.stat-value{font-size:28px;font-weight:700;letter-spacing:-.04em;line-height:1.1}
.stat-label{font-size:11px;font-weight:600;color:var(--label-2);margin-top:4px;text-transform:uppercase;letter-spacing:.05em}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:0 -20px;padding:0}
table{width:100%;border-collapse:collapse;min-width:560px}
th{padding:8px 12px;text-align:left;font-size:11px;font-weight:600;letter-spacing:.06em;text-transform:uppercase;color:var(--label-3);border-bottom:.5px solid var(--sep);white-space:nowrap;background:var(--surface);position:sticky;top:0;z-index:1}
td{padding:10px 12px;font-size:14px;border-bottom:.5px solid var(--sep);white-space:nowrap;vertical-align:middle}
th.sort{cursor:pointer;user-select:none}
th.sort:hover{color:var(--label-2)}
th.asc,th.desc{color:var(--blue)}
.si{margin-left:3px;opacity:.5;font-size:9px}
th.asc .si,th.desc .si{opacity:1}
td{font-size:.85rem}
tbody tr{transition:background var(--transition)}
tbody tr:hover{background:var(--bg-table-hover)}
tbody tr:active{background:var(--bg-table-hover)}
tbody tr{transition:background .1s}
tbody tr:hover{background:var(--fill)}
tbody tr:active{background:var(--fill-2)}
tbody tr:last-child td{border-bottom:none}
.tld{display:inline-block;font-size:12px;font-weight:600;padding:2px 7px;border-radius:5px}
.tld-se{background:var(--blue-t);color:var(--tld-se)}
.tld-nu{background:var(--green-t);color:var(--tld-nu)}
.pill{display:inline-flex;align-items:center;gap:3px;padding:3px 8px;border-radius:20px;font-size:12px;font-weight:500}
.pill-g{background:var(--green-t);color:var(--green)}
.pill-r{background:var(--red-t);color:var(--red)}
.pill-m{background:var(--fill);color:var(--label-3)}
.badge{display:inline-flex;align-items:center;padding:2px 8px;border-radius:20px;font-size:11px;font-weight:600}
.badge-blue{background:var(--blue-t);color:var(--blue)}
.badge-muted{background:var(--fill);color:var(--label-3)}
.btn{
    display:inline-flex;align-items:center;justify-content:center;gap:6px;
    padding:9px 18px;border-radius:20px;border:none;
    font:600 14px/1 -apple-system,sans-serif;cursor:pointer;
    transition:opacity .15s,transform .1s;text-decoration:none;white-space:nowrap;
}
.btn:active{transform:scale(.96)}
.btn-primary{background:var(--blue);color:#fff}
.btn-primary:hover{opacity:.88}
.btn-ghost{background:var(--fill);color:var(--label-2)}
.btn-ghost:hover{background:var(--fill-2);color:var(--label)}
.btn-tinted{background:var(--blue-t);color:var(--blue)}
.btn-tinted:hover{opacity:.8}
.chip-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px}
.chip{
    display:inline-flex;align-items:center;gap:4px;
    padding:5px 12px;background:var(--fill);color:var(--label-2);
    border:none;border-radius:20px;font:500 13px/1 inherit;
    cursor:pointer;transition:background .15s,color .15s;white-space:nowrap;
}
.chip:hover{background:var(--fill-2);color:var(--label)}
.chip.on{background:var(--blue);color:#fff}
.chip .n{font-size:11px;opacity:.75}
.chip.on .n{opacity:.85}
.search-wrap{position:relative;margin-bottom:12px}
.search-input{
    width:100%;padding:10px 36px;background:var(--fill);border:none;border-radius:10px;
    font:15px/1.4 inherit;color:var(--label);-webkit-appearance:none;appearance:none;outline:none;
    transition:background .15s,box-shadow .15s;
}
.search-input::placeholder{color:var(--label-3)}
.search-input:focus{background:var(--fill-2);box-shadow:0 0 0 3px var(--blue-t)}
.search-clear{
    position:absolute;right:8px;top:50%;transform:translateY(-50%);
    background:var(--label-3);border:none;border-radius:50%;width:18px;height:18px;
    display:none;align-items:center;justify-content:center;
    cursor:pointer;color:var(--surface);font-size:10px;transition:background .15s;
}
.search-clear.on{display:flex}
.toolbar{display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:10px;flex-wrap:wrap}
.rcount{font-size:12px;color:var(--label-3)}
.breadcrumb{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--label-2);margin-bottom:16px}
.breadcrumb a{color:var(--blue);text-decoration:none}
.report-list{list-style:none}
.report-list li+li{border-top:.5px solid var(--sep)}
.report-list a{
    display:flex;align-items:center;justify-content:space-between;
    padding:12px 0;color:var(--label);text-decoration:none;gap:8px;
}
.report-list a:hover .rd{color:var(--blue)}
.rd{font-size:15px;font-weight:500;transition:color .15s}
.rc{color:var(--label-3);font-size:12px;flex-shrink:0}
.empty{text-align:center;padding:48px 24px;color:var(--label-2)}
.empty .ei{font-size:40px;margin-bottom:12px;opacity:.4}
.empty p{font-size:15px;margin-bottom:16px}
.footer{border-top:.5px solid var(--sep);padding:20px 0;margin-top:32px}
.footer-content{max-width:1100px;margin:0 auto;padding:0 20px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px;font-size:13px;color:var(--label-2)}
.footer a{color:var(--blue);text-decoration:none}
.footer a:hover{text-decoration:underline}
@keyframes fadeUp{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.fup{animation:fadeUp .3s ease forwards}
@media(min-width:700px){
    .nav-links{display:flex}
    main{padding:32px 24px 56px}
    .stats{grid-template-columns:repeat(4,1fr)}
    .stat-value{font-size:32px}
    .stat-card:hover{transform:translateY(-2px);box-shadow:var(--shadow)}
}
::-webkit-scrollbar{height:4px;width:4px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--text-muted);border-radius:2px}
@media(display-mode:standalone){
    .header{padding-top:calc(1rem + var(--safe-top))}
    .footer{padding-bottom:calc(1.25rem + var(--safe-bottom))}
}
"""


# ── Shared JavaScript ─────────────────────────────────────────────────────────

SHARED_JS = """\
/* Theme */
function applyTheme(t){document.documentElement.setAttribute('data-theme',t);var i=document.getElementById('theme-ico');if(i)i.textContent=t==='dark'?'🌙':'☀️';}
function toggleTheme(){var n=document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark';applyTheme(n);localStorage.setItem('theme',n);}
(function(){var s=localStorage.getItem('theme');if(s){applyTheme(s);return;}if(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches)applyTheme('dark');})();

/* Sort */
var _s={col:-1,asc:true};
function sortBy(ci){
    var t=document.getElementById('tbl');if(!t)return;
    var tb=t.querySelector('tbody'),rows=Array.from(tb.querySelectorAll('tr')),ths=t.querySelectorAll('th');
    if(_s.col===ci)_s.asc=!_s.asc;else{_s.col=ci;_s.asc=true;}
    ths.forEach(function(h,i){
        h.classList.remove('asc','desc');
        var si=h.querySelector('.si');
        if(i===ci){h.classList.add(_s.asc?'asc':'desc');if(si)si.textContent=_s.asc?'↑':'↓';}
        else if(si)si.textContent='⇅';
    });
    rows.sort(function(a,b){var at=a.cells[ci]?a.cells[ci].textContent.trim():'',bt=b.cells[ci]?b.cells[ci].textContent.trim():'',an=parseFloat(at),bn=parseFloat(bt),r;if(!isNaN(an)&&!isNaN(bn))r=an-bn;else r=at.localeCompare(bt);return _s.asc?r:-r;});
    rows.forEach(function(r){tb.appendChild(r);});
}

/* Filter & Search */
var _tld='all';
function setTLD(v,el){
    _tld=v;document.querySelectorAll('.chip-row .chip').forEach(function(c){c.classList.remove('on');});el.classList.add('on');applyFilters();
}
function applyFilters(){
    var t=document.getElementById('tbl');if(!t)return;
    var rows=t.querySelectorAll('tbody tr'),si=document.getElementById('search'),term=si?si.value.toLowerCase():'',n=0;
    rows.forEach(function(r){
        var tld=r.getAttribute('data-tld'),indexed=r.getAttribute('data-indexed'),txt=r.textContent.toLowerCase();
        var m=(_tld==='all'||(_tld==='indexed'&&indexed==='yes')||tld===_tld)&&(!term||txt.includes(term));
        r.style.display=m?'':'none';if(m)n++;
    });
    var rc=document.getElementById('rcount');if(rc)rc.textContent=n+' domains';
}
function clearSearch(){
    var si=document.getElementById('search'),cb=document.getElementById('search-clear');
    if(si){si.value='';if(cb)cb.classList.remove('on');applyFilters();si.focus();}
}
document.addEventListener('DOMContentLoaded',function(){
    var si=document.getElementById('search'),cb=document.getElementById('search-clear');
    if(si)si.addEventListener('input',function(e){if(cb)cb.classList.toggle('on',e.target.value.length>0);applyFilters();});
    document.querySelectorAll('.stat-card,.card').forEach(function(el,i){el.classList.add('fup');el.style.animationDelay=(i*.04)+'s';});
});

/* Service Worker */
if('serviceWorker' in navigator){navigator.serviceWorker.register('sw.js').catch(function(){});}
"""


def escape_html(text):
    """Escape HTML special characters."""
    if text is None:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def json_ld(obj):
    """Serialize a dict to a JSON-LD script tag."""
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False) + '</script>'


def html_head(title=SITE_NAME, description=SITE_DESCRIPTION, extra_ld=None):
    """Generate <head> with meta tags, favicon, PWA, structured data."""
    ld_blocks = [json_ld({
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": SITE_NAME,
        "description": SITE_DESCRIPTION,
        "url": "index.html",
        "applicationCategory": "UtilitiesApplication",
        "operatingSystem": "Any",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@type": "Organization", "name": SITE_NAME}
    })]
    if extra_ld:
        for obj in extra_ld:
            ld_blocks.append(json_ld(obj))

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{escape_html(title)}</title>
    <meta name="description" content="{escape_html(description)}">
    <meta name="robots" content="index, follow">
    <meta property="og:type" content="website">
    <meta property="og:title" content="{escape_html(title)}">
    <meta property="og:description" content="{escape_html(description)}">
    <meta property="og:site_name" content="DropScan">
    <link rel="icon" type="image/svg+xml" href="favicon.svg">
    <link rel="apple-touch-icon" href="favicon.svg">
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme:light)">
    <meta name="theme-color" content="#000000" media="(prefers-color-scheme:dark)">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="DropScan">
    <meta name="mobile-web-app-capable" content="yes">
    {''.join(ld_blocks)}
    <style>{SHARED_CSS}</style>
</head>
<body>"""


def html_site_header(active="latest"):
    """Generate the frosted glass navbar."""
    return f"""
<header class="navbar">
    <div class="navbar-inner">
        <a href="index.html" class="navbar-brand">
            <img src="favicon.svg" class="navbar-logo" alt="DropScan">
            <span class="navbar-title">DropScan</span>
        </a>
        <nav class="nav-links" aria-label="Main">
            <a href="index.html" class="{'on' if active=='latest' else ''}">Latest</a>
            <a href="#reports-section" class="{'on' if active=='reports' else ''}">History</a>
        </nav>
        <div>
            <button class="btn-theme" onclick="toggleTheme()" aria-label="Toggle dark mode">
                <span id="theme-ico">☀️</span>
            </button>
        </div>
    </div>
</header>"""


def html_footer():
    """Generate footer and shared JS."""
    return f"""
<footer class="footer">
    <div class="footer-content">
        <span>Data from <a href="https://www.internetstiftelsen.se" target="_blank" rel="noopener">Internetstiftelsen</a></span>
        <span><a href="{GITHUB_URL}" target="_blank" rel="noopener">GitHub</a></span>
    </div>
</footer>
<script>{SHARED_JS}</script>
</body>
</html>"""


# ── Component Generators ──────────────────────────────────────────────────────

def generate_stat_cards(cards):
    html = '<div class="stats fup">\n'
    for value, label in cards:
        html += f'<div class="stat-card"><div class="stat-value">{escape_html(str(value))}</div><div class="stat-label">{escape_html(label)}</div></div>\n'
    html += '</div>\n'
    return html


def generate_domain_row(domain):
    tld = domain.get('tld', 'se')
    available = domain.get('available')
    if available is None:
        avail_cell = '<span class="pill pill-m">&mdash;</span>'
    elif available:
        avail_cell = '<span class="pill pill-g">&#10003; Free</span>'
    else:
        avail_cell = '<span class="pill pill-r">&#10007; Taken</span>'
    indexed = domain.get('indexed')
    if indexed is None:
        index_cell = '<span class="pill pill-m">&mdash;</span>'
    elif indexed:
        index_cell = '<span class="pill pill-g">&#10003; Yes</span>'
    else:
        index_cell = '<span class="pill pill-m">No</span>'
    pages = domain.get('estimated_pages')
    pages_cell = f'<span style="color:var(--label-2)">{escape_html(str(pages))}</span>' if pages else '<span style="color:var(--label-3)">&mdash;</span>'
    return (f'<tr data-tld="{escape_html(tld)}" data-indexed="{"yes" if indexed else "no"}">'
            f'<td><strong>{escape_html(domain.get("domain", ""))}</strong></td>'
            f'<td><span class="tld tld-{escape_html(tld)}">.{escape_html(tld)}</span></td>'
            f'<td style="color:var(--label-2)">{escape_html(domain.get("release_date", ""))}</td>'
            f'<td>{avail_cell}</td>'
            f'<td>{index_cell}</td>'
            f'<td>{pages_cell}</td>'
            f'</tr>')


def generate_domains_table(domains, table_id="tbl"):
    cols = [("Domain", 0), ("TLD", 1), ("Release", 2), ("Avail", 3), ("Indexed", 4), ("Pages", 5)]
    hdr = ''.join(
        f'<th class="sort" onclick="sortBy({i})">{n} <span class="si">&#8645;</span></th>'
        for n, i in cols
    )
    rows = '\n'.join(generate_domain_row(d) for d in domains)
    return f'<div class="table-wrap"><table id="{table_id}"><thead><tr>{hdr}</tr></thead><tbody>{rows}</tbody></table></div>'


def generate_filter_bar(domains):
    total = len(domains)
    se = sum(1 for d in domains if d.get('tld') == 'se')
    nu = sum(1 for d in domains if d.get('tld') == 'nu')
    indexed = sum(1 for d in domains if d.get('indexed'))
    return f"""<div class="search-wrap">
    <input class="search-input" id="search" type="text" placeholder="Search domains\u2026" autocomplete="off">
    <button class="search-clear" id="search-clear" onclick="clearSearch()">&#10005;</button>
</div>
<div class="chip-row">
    <button class="chip on" onclick="setTLD('all',this)">All <span class="n">{total}</span></button>
    <button class="chip" onclick="setTLD('se',this)">.se <span class="n">{se}</span></button>
    <button class="chip" onclick="setTLD('nu',this)">.nu <span class="n">{nu}</span></button>
    <button class="chip" onclick="setTLD('indexed',this)">Indexed <span class="n">{indexed}</span></button>
</div>
<div class="toolbar"><span class="rcount" id="rcount">{total} domains</span></div>"""


def generate_report_list(reports, current_date=None):
    html = '<ul class="report-list">\n'
    for i, report in enumerate(reports):
        d = report['date']
        badge = ''
        if d == current_date:
            badge = ' <span class="badge badge-blue">Current</span>'
        elif current_date is None and i == 0:
            badge = ' <span class="badge badge-blue">Latest</span>'
        html += f'<li><a href="report-{d}.html"><span class="rd">{d}{badge}</span><span class="rc">&#8250;</span></a></li>\n'
    html += '</ul>\n'
    return html


# ── Page Generators ───────────────────────────────────────────────────────────

def generate_index_page(reports):
    latest_data = None
    if reports:
        latest_data = load_report(reports[0]['date'])

    description = SITE_DESCRIPTION
    extra_ld = []
    if latest_data and reports:
        total = latest_data.get('total_domains', 0)
        description = f"Today's scan found {total} valuable expiring .se and .nu domains. Daily updated domain snapback scanner."
        extra_ld.append({
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": f"SE/NU Expiring Domain Report - {reports[0]['date']}",
            "description": f"{total} valuable expiring .se and .nu domains found on {reports[0]['date']}.",
            "temporalCoverage": reports[0]['date'],
            "creator": {"@type": "Organization", "name": SITE_NAME}
        })

    html = html_head(title=SITE_NAME, description=description, extra_ld=extra_ld)
    html += html_site_header(active="latest")
    html += '\n<main>\n'

    if latest_data and reports:
        domains = latest_data.get('domains', [])
        se = sum(1 for d in domains if d.get('tld') == 'se')
        indexed = sum(1 for d in domains if d.get('indexed'))

        html += f'<p class="page-title">Tonight\'s Drops</p>\n'
        html += f'<p class="page-subtitle">{reports[0]["date"]} &middot; {len(domains)} domains &middot; {indexed} indexed</p>\n'

        html += generate_stat_cards([
            (latest_data.get('total_domains', 0), "Total"),
            (se, ".se"),
            (len(domains) - se, ".nu"),
            (indexed, "Indexed"),
        ])

        html += '<div class="card fup">\n'
        html += f'<div class="toolbar"><span class="card-title" style="margin-bottom:0">Domains</span>'
        if reports:
            html += f'<a href="report-{reports[0]["date"]}.html" class="btn btn-tinted" style="font-size:13px;padding:7px 14px">Full Report</a>'
        html += '</div>\n'

        if domains:
            display = domains[:50]
            html += generate_filter_bar(domains)
            html += generate_domains_table(display)
            if len(domains) > 50:
                html += f'<div style="text-align:center;margin-top:16px"><a href="report-{reports[0]["date"]}.html" class="btn btn-tinted">View all {len(domains)} domains</a></div>'
        else:
            html += '<div class="empty"><div class="ei">&#128269;</div><p>No domains found in the latest scan.</p></div>'
        html += '\n</div>\n'
    else:
        html += '<div class="card fup"><div class="empty"><div class="ei">&#128640;</div><p>No scan results found yet. Check back soon!</p></div></div>'

    if reports:
        html += f'<div class="card fup" id="reports-section"><p class="card-title">History</p>\n{generate_report_list(reports)}</div>'

    html += '\n</main>'
    html += html_footer()
    return html


def generate_report_page(report_date, report_data, reports):
    domains = report_data.get('domains', [])
    total = report_data.get('total_domains', 0)
    se = sum(1 for d in domains if d.get('tld') == 'se')
    nu = sum(1 for d in domains if d.get('tld') == 'nu')

    dates = [r['date'] for r in reports]
    try:
        idx = dates.index(report_date)
    except ValueError:
        idx = -1
    prev_date = dates[idx - 1] if idx > 0 else None
    next_date = dates[idx + 1] if 0 <= idx < len(dates) - 1 else None

    title = f"Report {report_date} - {SITE_NAME}"
    description = f"ALL {total} .se/.nu domains releasing on {report_date}."
    extra_ld = [
        {
            "@context": "https://schema.org",
            "@type": "Dataset",
            "name": f"SE/NU Domain Release List - {report_date}",
            "description": description,
            "temporalCoverage": report_date,
            "datePublished": report_data.get("generated_at", ""),
            "creator": {"@type": "Organization", "name": SITE_NAME},
            "variableMeasured": [
                {"@type": "PropertyValue", "name": "Total Domains", "value": str(total)}
            ]
        },
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": "index.html"},
                {"@type": "ListItem", "position": 2, "name": f"Report {report_date}", "item": f"report-{report_date}.html"}
            ]
        }
    ]

    html = html_head(title=title, description=description, extra_ld=extra_ld)
    html += html_site_header(active="reports")
    html += '\n<main>\n'

    # Breadcrumb
    html += f'<nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Latest</a> <span>/</span> <span>Report {report_date}</span></nav>\n'

    html += f'<p class="page-title">Report: {report_date}</p>\n'
    indexed = sum(1 for d in domains if d.get('indexed'))
    html += f'<p class="page-subtitle">{total} domains &middot; {se} .se &middot; {nu} .nu &middot; {indexed} indexed</p>\n'

    html += generate_stat_cards([
        (total, "Total"), (se, ".se"), (nu, ".nu"), (indexed, "Indexed")
    ])

    # Prev/Next nav + export buttons
    html += '<div class="toolbar fup" style="margin-bottom:16px">\n'
    html += '  <div style="display:flex;gap:8px;align-items:center">\n'
    html += f'  <a href="report-{next_date}.html" class="btn btn-ghost" style="font-size:13px;padding:7px 14px">&larr; {next_date}</a>\n' if next_date else ''
    html += f'  <a href="report-{prev_date}.html" class="btn btn-ghost" style="font-size:13px;padding:7px 14px">{prev_date} &rarr;</a>\n' if prev_date else ''
    html += '  </div>\n'
    html += '  <div style="display:flex;gap:8px;align-items:center">\n'
    html += f'  <a href="../reports/{report_date}.json" download class="btn btn-ghost" style="font-size:13px;padding:7px 14px">JSON</a>\n'
    html += f'  <a href="../reports/{report_date}.csv" download class="btn btn-ghost" style="font-size:13px;padding:7px 14px">CSV</a>\n'
    html += '  </div>\n'
    html += '</div>\n'

    html += '<div class="card fup">\n'
    html += f'<p class="card-title">Domains</p>\n'
    html += f'<p style="color:var(--label-3);font-size:12px;margin-bottom:12px">Generated: {escape_html(report_data.get("generated_at", "N/A"))}</p>\n'

    if domains:
        html += generate_filter_bar(domains)
        html += generate_domains_table(domains)
    else:
        html += '<div class="empty"><div class="ei">&#128269;</div><p>No domains found in this report.</p></div>\n'

    html += '</div>\n'

    html += f'<div class="card fup"><p class="card-title">Other Reports</p>\n{generate_report_list(reports, current_date=report_date)}</div>'

    html += '\n</main>'
    html += html_footer()
    return html


def main():
    """Generate static site."""
    print("Building static site for GitHub Pages...")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    reports = load_reports()
    print(f"Found {len(reports)} reports")

    # Copy static assets that need to live at docs/ root
    # (favicon.svg, manifest.json, sw.js are written by this script or committed separately)

    print("Generating index.html...")
    with open(OUTPUT_DIR / "index.html", 'w') as f:
        f.write(generate_index_page(reports))

    for report in reports:
        print(f"Generating report-{report['date']}.html...")
        report_data = load_report(report['date'])
        if report_data:
            with open(OUTPUT_DIR / f"report-{report['date']}.html", 'w') as f:
                f.write(generate_report_page(report['date'], report_data, reports))

    print(f"Static site generated in {OUTPUT_DIR}/")
    print(f"To test: cd {OUTPUT_DIR} && python -m http.server 8000")


if __name__ == "__main__":
    main()
