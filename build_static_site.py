#!/usr/bin/env python3
"""
Static site generator for GitHub Pages.

Converts JSON reports into static HTML pages that can be served on GitHub Pages.
Includes dark mode, responsive design, search, sorting, filtering, and more.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

# Configuration
REPORT_DIR = Path("reports")
OUTPUT_DIR = Path("docs")  # GitHub Pages serves from /docs or root
TEMPLATE_DIR = Path("templates")


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


# ── Shared CSS (single source of truth) ──────────────────────────────────────

SHARED_CSS = """\
/* === CSS Custom Properties (Light Theme) === */
:root {
    --bg-primary: #f5f7fa;
    --bg-card: #ffffff;
    --bg-header: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --bg-table-header: #f8f9fa;
    --bg-table-hover: #f0f2f5;
    --bg-input: #ffffff;
    --bg-badge-success: #d4edda;
    --bg-badge-warning: #fff3cd;
    --bg-badge-info: #d1ecf1;
    --bg-chip: #e8eaf6;
    --bg-chip-active: #667eea;
    --bg-footer: #ffffff;
    --text-primary: #1a1a2e;
    --text-secondary: #555;
    --text-muted: #888;
    --text-badge-success: #155724;
    --text-badge-warning: #856404;
    --text-badge-info: #0c5460;
    --text-chip: #444;
    --text-chip-active: #fff;
    --text-on-header: #ffffff;
    --border-color: #e0e0e0;
    --border-input: #d0d0d0;
    --accent: #667eea;
    --accent-hover: #5568d3;
    --accent-light: rgba(102,126,234,0.1);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.1);
    --tld-se: #2196F3;
    --tld-nu: #4CAF50;
    --radius-sm: 6px;
    --radius-md: 10px;
    --transition: 0.25s ease;
}
[data-theme="dark"] {
    --bg-primary: #0f0f1a;
    --bg-card: #1a1a2e;
    --bg-header: linear-gradient(135deg, #434eab 0%, #5a3678 100%);
    --bg-table-header: #16162b;
    --bg-table-hover: #222240;
    --bg-input: #16162b;
    --bg-badge-success: #1a3a2a;
    --bg-badge-warning: #3a3020;
    --bg-badge-info: #1a2a3a;
    --bg-chip: #2a2a4a;
    --bg-chip-active: #667eea;
    --bg-footer: #1a1a2e;
    --text-primary: #e0e0f0;
    --text-secondary: #aab;
    --text-muted: #777;
    --text-badge-success: #7dcc8a;
    --text-badge-warning: #ddc46a;
    --text-badge-info: #6ac5d8;
    --text-chip: #bbb;
    --text-chip-active: #fff;
    --text-on-header: #ffffff;
    --border-color: #2a2a4a;
    --border-input: #3a3a5a;
    --accent: #7b8ff0;
    --accent-hover: #6a7ee0;
    --accent-light: rgba(102,126,234,0.15);
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.3);
    --shadow-lg: 0 8px 24px rgba(0,0,0,0.4);
    --tld-se: #64b5f6;
    --tld-nu: #81c784;
}
* { margin:0; padding:0; box-sizing:border-box; }
html { scroll-behavior:smooth; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height:1.6; color:var(--text-primary); background:var(--bg-primary);
    transition: background var(--transition), color var(--transition);
}
.header {
    background:var(--bg-header); color:var(--text-on-header);
    padding:1.75rem 0; box-shadow:var(--shadow-md);
    position:sticky; top:0; z-index:100;
}
.container { max-width:1280px; margin:0 auto; padding:0 24px; }
.header-row {
    display:flex; align-items:center; justify-content:space-between;
    flex-wrap:wrap; gap:1rem;
}
.header-brand h1 { font-size:1.6rem; font-weight:700; letter-spacing:-0.02em; }
.header-brand .subtitle { opacity:0.85; font-size:0.95rem; margin-top:0.15rem; }
.header-actions { display:flex; align-items:center; gap:0.75rem; }
.nav { display:flex; gap:0.5rem; flex-wrap:wrap; }
.nav a {
    color:white; text-decoration:none; padding:0.45rem 0.9rem;
    background:rgba(255,255,255,0.12); border-radius:var(--radius-sm);
    transition:background var(--transition);
    border:1px solid rgba(255,255,255,0.15); font-size:0.9rem; white-space:nowrap;
}
.nav a:hover { background:rgba(255,255,255,0.22); }
.theme-toggle {
    background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.15);
    color:white; padding:0.45rem 0.65rem; border-radius:var(--radius-sm);
    cursor:pointer; font-size:1.1rem; transition:background var(--transition); line-height:1;
}
.theme-toggle:hover { background:rgba(255,255,255,0.22); }
.content { padding:2rem 0 3rem; }
.card {
    background:var(--bg-card); border-radius:var(--radius-md);
    padding:1.5rem; margin-bottom:1.5rem; box-shadow:var(--shadow-sm);
    transition:background var(--transition), box-shadow var(--transition);
    border:1px solid var(--border-color);
}
.card:hover { box-shadow:var(--shadow-md); }
.card h2 {
    margin-bottom:1rem; color:var(--accent); font-size:1.3rem; font-weight:600;
    display:flex; align-items:center; gap:0.5rem;
}
.card h2 .icon { font-size:1.1rem; }
.stats {
    display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr));
    gap:1rem; margin-bottom:1.5rem;
}
.stat-card {
    background:var(--bg-card); padding:1.25rem 1.5rem; border-radius:var(--radius-md);
    box-shadow:var(--shadow-sm); border:1px solid var(--border-color);
    transition:transform var(--transition), box-shadow var(--transition), background var(--transition);
    position:relative; overflow:hidden;
}
.stat-card::before {
    content:''; position:absolute; top:0; left:0; width:4px; height:100%;
    background:var(--accent); border-radius:4px 0 0 4px;
}
.stat-card:hover { transform:translateY(-2px); box-shadow:var(--shadow-md); }
.stat-value { font-size:2rem; font-weight:700; color:var(--accent); line-height:1.2; }
.stat-label { color:var(--text-secondary); margin-top:0.35rem; font-size:0.9rem; }
.table-wrapper {
    overflow-x:auto; -webkit-overflow-scrolling:touch;
    border-radius:var(--radius-sm); border:1px solid var(--border-color); margin-top:1rem;
}
table { width:100%; border-collapse:collapse; min-width:600px; }
th, td {
    padding:0.7rem 0.85rem; text-align:left;
    border-bottom:1px solid var(--border-color); white-space:nowrap;
}
th {
    background:var(--bg-table-header); font-weight:600; color:var(--text-secondary);
    font-size:0.85rem; text-transform:uppercase; letter-spacing:0.04em;
    position:sticky; top:0; z-index:10;
}
th.sortable { cursor:pointer; user-select:none; transition:background var(--transition); }
th.sortable:hover { background:var(--bg-table-hover); }
th .sort-icon { opacity:0.4; margin-left:0.3rem; font-size:0.75rem; transition:opacity var(--transition); }
th.sorted .sort-icon { opacity:1; color:var(--accent); }
td { font-size:0.92rem; }
tbody tr { transition:background var(--transition); }
tbody tr:hover { background:var(--bg-table-hover); }
tbody tr:last-child td { border-bottom:none; }
.badge {
    display:inline-flex; align-items:center; gap:0.3rem;
    padding:0.2rem 0.55rem; border-radius:50px;
    font-size:0.78rem; font-weight:600; letter-spacing:0.02em;
}
.badge-success { background:var(--bg-badge-success); color:var(--text-badge-success); }
.badge-info { background:var(--bg-badge-info); color:var(--text-badge-info); }
.badge-warning { background:var(--bg-badge-warning); color:var(--text-badge-warning); }
.tld-se { color:var(--tld-se); font-weight:600; }
.tld-nu { color:var(--tld-nu); font-weight:600; }
.btn {
    display:inline-flex; align-items:center; gap:0.4rem;
    padding:0.5rem 1.1rem; background:var(--accent); color:white;
    text-decoration:none; border-radius:var(--radius-sm); border:none;
    cursor:pointer; font-size:0.92rem; font-family:inherit; font-weight:500;
    transition:background var(--transition), transform var(--transition);
}
.btn:hover { background:var(--accent-hover); transform:translateY(-1px); }
.btn:active { transform:translateY(0); }
.btn-secondary {
    background:transparent; color:var(--accent); border:1px solid var(--accent);
}
.btn-secondary:hover { background:var(--accent-light); }
.filter-bar { display:flex; flex-wrap:wrap; align-items:center; gap:0.5rem; margin-bottom:1rem; }
.filter-bar label { font-size:0.85rem; color:var(--text-secondary); font-weight:500; }
.chip {
    display:inline-flex; align-items:center; gap:0.3rem;
    padding:0.3rem 0.75rem; background:var(--bg-chip); color:var(--text-chip);
    border-radius:50px; font-size:0.82rem; font-weight:500; cursor:pointer;
    border:1px solid transparent; transition:all var(--transition); user-select:none;
}
.chip:hover { border-color:var(--accent); }
.chip.active { background:var(--bg-chip-active); color:var(--text-chip-active); border-color:var(--bg-chip-active); }
.chip .count { background:rgba(255,255,255,0.2); padding:0 0.35rem; border-radius:50px; font-size:0.75rem; }
.chip.active .count { background:rgba(255,255,255,0.3); }
.search-box { position:relative; max-width:400px; }
.search-box input {
    width:100%; padding:0.55rem 0.9rem 0.55rem 2.4rem;
    border:1px solid var(--border-input); border-radius:var(--radius-sm);
    font-size:0.92rem; font-family:inherit;
    background:var(--bg-input); color:var(--text-primary);
    transition:border var(--transition), box-shadow var(--transition), background var(--transition);
}
.search-box input:focus { outline:none; border-color:var(--accent); box-shadow:0 0 0 3px var(--accent-light); }
.search-box input::placeholder { color:var(--text-muted); }
.search-box .search-icon { position:absolute; left:0.8rem; top:50%; transform:translateY(-50%); color:var(--text-muted); font-size:0.9rem; pointer-events:none; }
.search-box .clear-btn {
    position:absolute; right:0.6rem; top:50%; transform:translateY(-50%);
    background:none; border:none; color:var(--text-muted); cursor:pointer;
    font-size:1rem; padding:0.2rem; display:none; line-height:1;
}
.search-box .clear-btn.visible { display:block; }
.toolbar { display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:1rem; }
.toolbar-left { display:flex; flex-wrap:wrap; align-items:center; gap:0.75rem; }
.toolbar-right { display:flex; flex-wrap:wrap; align-items:center; gap:0.5rem; }
.result-count { font-size:0.85rem; color:var(--text-muted); padding:0.3rem 0; }
.report-list { list-style:none; }
.report-list li { border-bottom:1px solid var(--border-color); }
.report-list li:last-child { border-bottom:none; }
.report-list a {
    display:flex; align-items:center; gap:0.5rem;
    padding:0.65rem 0.5rem; color:var(--accent); text-decoration:none;
    transition:background var(--transition), padding var(--transition); border-radius:var(--radius-sm);
}
.report-list a:hover { background:var(--accent-light); padding-left:1rem; }
.report-list .report-date { font-weight:500; }
.report-list .report-meta { color:var(--text-muted); font-size:0.82rem; margin-left:auto; }
.empty-state { text-align:center; padding:3rem 1rem; color:var(--text-muted); }
.empty-state .empty-icon { font-size:3rem; margin-bottom:1rem; opacity:0.5; }
.footer {
    background:var(--bg-footer); border-top:1px solid var(--border-color);
    padding:1.5rem 0; margin-top:2rem; transition:background var(--transition);
}
.footer-content {
    display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between;
    gap:1rem; font-size:0.85rem; color:var(--text-muted);
}
.footer a { color:var(--accent); text-decoration:none; }
.footer a:hover { text-decoration:underline; }
.back-to-top {
    position:fixed; bottom:2rem; right:2rem; width:44px; height:44px;
    background:var(--accent); color:white; border:none; border-radius:50%;
    font-size:1.2rem; cursor:pointer; box-shadow:var(--shadow-md);
    opacity:0; transform:translateY(10px);
    transition:opacity var(--transition), transform var(--transition), background var(--transition);
    pointer-events:none; z-index:50; display:flex; align-items:center; justify-content:center;
}
.back-to-top.visible { opacity:1; transform:translateY(0); pointer-events:auto; }
.back-to-top:hover { background:var(--accent-hover); transform:translateY(-2px); }
.report-nav {
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom:1.25rem; flex-wrap:wrap; gap:0.5rem;
}
.download-links { display:flex; flex-wrap:wrap; gap:0.5rem; margin-bottom:1rem; }
@keyframes fadeInUp { from { opacity:0; transform:translateY(12px); } to { opacity:1; transform:translateY(0); } }
.animate-in { animation:fadeInUp 0.4s ease forwards; }
@media (max-width:768px) {
    .header-row { flex-direction:column; align-items:flex-start; }
    .header-brand h1 { font-size:1.3rem; }
    .stats { grid-template-columns:repeat(2,1fr); }
    .stat-value { font-size:1.5rem; }
    .toolbar { flex-direction:column; align-items:stretch; }
    .search-box { max-width:none; }
    .card { padding:1rem; }
    th, td { padding:0.5rem 0.65rem; font-size:0.82rem; }
    .back-to-top { bottom:1rem; right:1rem; }
    .report-nav { flex-direction:column; align-items:stretch; text-align:center; }
}
@media (max-width:480px) {
    .stats { grid-template-columns:1fr; }
    .header-actions { width:100%; justify-content:space-between; }
}
::-webkit-scrollbar { height:6px; width:6px; }
::-webkit-scrollbar-track { background:var(--bg-primary); }
::-webkit-scrollbar-thumb { background:var(--text-muted); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background:var(--text-secondary); }
"""


# ── Shared JavaScript ─────────────────────────────────────────────────────────

SHARED_JS = """\
/* Theme */
function toggleTheme(){
    var h=document.documentElement,c=h.getAttribute('data-theme'),n=c==='dark'?'light':'dark';
    h.setAttribute('data-theme',n);localStorage.setItem('theme',n);updateThemeIcon(n);
}
function updateThemeIcon(t){
    var i=document.querySelector('.theme-icon');
    if(i) i.innerHTML=t==='dark'?'&#9788;':'&#9790;';
}
(function(){
    var s=localStorage.getItem('theme');
    if(s){document.documentElement.setAttribute('data-theme',s);updateThemeIcon(s);}
    else if(window.matchMedia&&window.matchMedia('(prefers-color-scheme:dark)').matches){
        document.documentElement.setAttribute('data-theme','dark');updateThemeIcon('dark');
    }
})();

/* Back to top */
var btt=document.querySelector('.back-to-top');
window.addEventListener('scroll',function(){
    if(btt){if(window.scrollY>400)btt.classList.add('visible');else btt.classList.remove('visible');}
},{passive:true});
function scrollToTop(){window.scrollTo({top:0,behavior:'smooth'});}

/* Sort */
var currentSort={col:-1,asc:true};
function sortTable(ci){
    var t=document.getElementById('domains-table');if(!t)return;
    var tb=t.querySelector('tbody'),rows=Array.from(tb.querySelectorAll('tr')),ths=t.querySelectorAll('th');
    if(currentSort.col===ci)currentSort.asc=!currentSort.asc;
    else{currentSort.col=ci;currentSort.asc=true;}
    ths.forEach(function(h,i){
        h.classList.toggle('sorted',i===ci);
        var ic=h.querySelector('.sort-icon');
        if(ic){ic.innerHTML=i===ci?(currentSort.asc?'&#8593;':'&#8595;'):'&#8693;';}
    });
    rows.sort(function(a,b){
        var at=a.cells[ci].textContent.trim(),bt=b.cells[ci].textContent.trim();
        var an=parseFloat(at),bn=parseFloat(bt),r;
        if(!isNaN(an)&&!isNaN(bn))r=an-bn; else r=at.localeCompare(bt);
        return currentSort.asc?r:-r;
    });
    rows.forEach(function(r){tb.appendChild(r);});
}

/* Filter & Search */
var activeFilter='all';
function filterTLD(tld,el){
    activeFilter=tld;
    document.querySelectorAll('.chip').forEach(function(c){c.classList.remove('active');});
    el.classList.add('active');
    applyFilters();
}
function applyFilters(){
    var t=document.getElementById('domains-table');if(!t)return;
    var rows=t.querySelectorAll('tbody tr'),si=document.getElementById('search'),
        term=si?si.value.toLowerCase():'',vc=0;
    rows.forEach(function(r){
        var tld=r.getAttribute('data-tld'),idx=r.getAttribute('data-indexed'),
            txt=r.textContent.toLowerCase(),mf,ms;
        if(activeFilter==='all')mf=true;
        else if(activeFilter==='indexed')mf=idx==='true';
        else mf=tld===activeFilter;
        ms=!term||txt.indexOf(term)>=0;
        var v=mf&&ms;r.style.display=v?'':'none';if(v)vc++;
    });
    var ce=document.getElementById('result-count');
    if(ce)ce.textContent='Showing '+vc+' domains';
}
function clearSearch(){
    var si=document.getElementById('search'),cb=document.getElementById('clear-search');
    if(si){si.value='';if(cb)cb.classList.remove('visible');applyFilters();si.focus();}
}
document.addEventListener('DOMContentLoaded',function(){
    var si=document.getElementById('search'),cb=document.getElementById('clear-search');
    if(si)si.addEventListener('input',function(e){
        var t=e.target.value;
        if(cb)cb.classList.toggle('visible',t.length>0);
        applyFilters();
    });
});
"""


def escape_html(text):
    """Escape HTML special characters."""
    if text is None:
        return ''
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def html_header(title="SE/NU Domain Snapback Scanner"):
    """Generate HTML header with shared styles."""
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(title)}</title>
    <style>{SHARED_CSS}</style>
</head>
<body>"""


def html_site_header(nav_links):
    """Generate the site header/nav bar."""
    nav = ''.join(f'<a href="{href}">{label}</a>' for label, href in nav_links)
    return f"""
    <div class="header">
        <div class="container">
            <div class="header-row">
                <div class="header-brand">
                    <h1>SE/NU Domain Snapback Scanner</h1>
                    <p class="subtitle">Find valuable expiring .se and .nu domains</p>
                </div>
                <div class="header-actions">
                    <div class="nav">{nav}</div>
                    <button class="theme-toggle" onclick="toggleTheme()" title="Toggle dark mode" aria-label="Toggle dark mode">
                        <span class="theme-icon">&#9790;</span>
                    </button>
                </div>
            </div>
        </div>
    </div>"""


def html_footer():
    """Generate footer, back-to-top button, and shared JS."""
    return f"""
    <footer class="footer">
        <div class="container">
            <div class="footer-content">
                <span>Data sourced from <a href="https://www.internetstiftelsen.se" target="_blank" rel="noopener">Internetstiftelsen (IIS)</a></span>
                <span><a href="https://github.com/Caceras/se-domain-snapback" target="_blank" rel="noopener">View on GitHub</a></span>
            </div>
        </div>
    </footer>
    <button class="back-to-top" onclick="scrollToTop()" title="Back to top" aria-label="Back to top">&#8593;</button>
    <script>{SHARED_JS}</script>
</body>
</html>"""


def generate_stat_cards(cards):
    """Generate stat cards HTML from a list of (value, label) tuples."""
    html = '<div class="stats">\n'
    for value, label in cards:
        html += f"""    <div class="stat-card">
        <div class="stat-value">{value}</div>
        <div class="stat-label">{escape_html(label)}</div>
    </div>\n"""
    html += '</div>\n'
    return html


def generate_domain_row(domain):
    """Generate a single table row for a domain."""
    tld = domain.get('tld', 'se')
    indexed = domain.get('indexed', False)
    pages = domain.get('estimated_pages')
    pages_html = f'<strong>{pages}</strong>' if pages else '<span style="color:var(--text-muted);">-</span>'
    badge = '<span class="badge badge-success">Indexed</span>' if indexed else '<span class="badge badge-warning">Not Indexed</span>'
    return f"""<tr data-tld="{escape_html(tld)}" data-indexed="{'true' if indexed else 'false'}">
    <td><strong>{escape_html(domain.get('domain', ''))}</strong></td>
    <td><span class="tld-{escape_html(tld)}">.{escape_html(tld)}</span></td>
    <td>{escape_html(domain.get('release_date', ''))}</td>
    <td>{pages_html}</td>
    <td>{escape_html(domain.get('index_source', ''))}</td>
    <td>{badge}</td>
</tr>"""


def generate_domains_table(domains, table_id="domains-table"):
    """Generate a full domains table with sortable headers."""
    columns = [
        ("Domain", 0), ("TLD", 1), ("Release Date", 2),
        ("Indexed Pages", 3), ("Source", 4), ("Status", 5),
    ]
    header_cells = ''.join(
        f'<th class="sortable" onclick="sortTable({i})" tabindex="0" role="button" '
        f'onkeypress="if(event.key===\'Enter\')sortTable({i})">'
        f'{name} <span class="sort-icon">&#8693;</span></th>'
        for name, i in columns
    )
    rows = '\n'.join(generate_domain_row(d) for d in domains)
    return f"""<div class="table-wrapper">
<table id="{table_id}">
    <thead><tr>{header_cells}</tr></thead>
    <tbody>{rows}</tbody>
</table>
</div>"""


def generate_filter_bar(domains):
    """Generate a filter bar with TLD and indexed chips."""
    total = len(domains)
    se_count = sum(1 for d in domains if d.get('tld') == 'se')
    nu_count = sum(1 for d in domains if d.get('tld') == 'nu')
    indexed_count = sum(1 for d in domains if d.get('indexed'))
    return f"""<div class="toolbar">
    <div class="toolbar-left">
        <div class="search-box">
            <span class="search-icon">&#128269;</span>
            <input type="text" id="search" placeholder="Search domains..." aria-label="Search domains">
            <button class="clear-btn" id="clear-search" onclick="clearSearch()" aria-label="Clear search">&#10005;</button>
        </div>
    </div>
    <div class="toolbar-right">
        <div class="filter-bar">
            <label>Filter:</label>
            <button class="chip active" onclick="filterTLD('all',this)">All <span class="count">{total}</span></button>
            <button class="chip" onclick="filterTLD('se',this)">.se <span class="count">{se_count}</span></button>
            <button class="chip" onclick="filterTLD('nu',this)">.nu <span class="count">{nu_count}</span></button>
            <button class="chip" onclick="filterTLD('indexed',this)">Indexed <span class="count">{indexed_count}</span></button>
        </div>
    </div>
</div>
<div class="result-count" id="result-count">Showing {total} domains</div>"""


def generate_report_list(reports, current_date=None):
    """Generate the historical reports list."""
    html = '<ul class="report-list">\n'
    for report in reports:
        date = report['date']
        style = ' style="font-weight:bold;background:var(--accent-light);"' if date == current_date else ''
        badge = ' <span class="badge badge-info">Current</span>' if date == current_date else ''
        if current_date is None and report == reports[0]:
            badge = ' <span class="badge badge-info">Latest</span>'
        html += f'<li><a href="report-{date}.html"{style}><span class="report-date">{date}</span>{badge}</a></li>\n'
    html += '</ul>\n'
    return html


# ── Page Generators ───────────────────────────────────────────────────────────

def generate_index_page(reports):
    """Generate the index.html page."""
    latest_data = None
    if reports:
        latest_data = load_report(reports[0]['date'])

    html = html_header()
    html += html_site_header([
        ("Latest Results", "index.html"),
        ("All Reports", "#reports"),
    ])

    html += '\n    <div class="container content">\n'

    if latest_data and reports:
        domains = latest_data.get('domains', [])
        indexed_count = sum(1 for d in domains if d.get('indexed'))
        se_count = sum(1 for d in domains if d.get('tld') == 'se')
        nu_count = sum(1 for d in domains if d.get('tld') == 'nu')

        html += generate_stat_cards([
            (latest_data.get('total_domains', 0), "Valuable Domains Found"),
            (len(reports), "Historical Reports"),
            (indexed_count, "Indexed Domains"),
            (se_count, ".se Domains"),
        ])

        html += f'\n<div class="card">\n'
        html += f'    <h2><span class="icon">&#128202;</span> Latest Scan Results ({reports[0]["date"]})</h2>\n'

        if domains:
            display_domains = domains[:50]
            html += generate_filter_bar(display_domains)
            html += generate_domains_table(display_domains)

            if len(domains) > 50:
                html += f"""
    <p style="margin-top:1rem;text-align:center;">
        <a href="report-{reports[0]['date']}.html" class="btn btn-secondary">View all {len(domains)} domains</a>
    </p>"""
        else:
            html += """
    <div class="empty-state">
        <div class="empty-icon">&#128269;</div>
        <p>No domains found in the latest scan.</p>
    </div>"""

        html += '\n</div>\n'
    else:
        html += """
<div class="card">
    <h2>No Reports Available</h2>
    <div class="empty-state">
        <div class="empty-icon">&#128640;</div>
        <p>No scan results found yet. Check back soon!</p>
    </div>
</div>"""

    if reports:
        html += f"""
<div class="card" id="reports">
    <h2><span class="icon">&#128197;</span> Historical Reports</h2>
{generate_report_list(reports)}
</div>"""

    html += '\n    </div>'  # close .container .content
    html += html_footer()
    return html


def generate_report_page(report_date, report_data, reports):
    """Generate a report page for a specific date."""
    domains = report_data.get('domains', [])
    indexed_count = sum(1 for d in domains if d.get('indexed'))
    se_count = sum(1 for d in domains if d.get('tld') == 'se')
    nu_count = sum(1 for d in domains if d.get('tld') == 'nu')

    # Figure out prev/next
    dates = [r['date'] for r in reports]
    try:
        idx = dates.index(report_date)
    except ValueError:
        idx = -1
    prev_date = dates[idx - 1] if idx > 0 else None
    next_date = dates[idx + 1] if 0 <= idx < len(dates) - 1 else None

    html = html_header(f"Report: {report_date} - SE/NU Domain Snapback Scanner")
    html += html_site_header([
        ("&larr; Back to Latest", "index.html"),
    ])

    html += '\n    <div class="container content">\n'

    # Prev/Next navigation
    html += '<div class="report-nav">\n'
    if next_date:
        html += f'    <a href="report-{next_date}.html" class="btn btn-secondary">&larr; {next_date}</a>\n'
    else:
        html += '    <span></span>\n'
    html += f'    <a href="index.html" class="btn btn-secondary">Back to Latest</a>\n'
    if prev_date:
        html += f'    <a href="report-{prev_date}.html" class="btn btn-secondary">{prev_date} &rarr;</a>\n'
    else:
        html += '    <span></span>\n'
    html += '</div>\n'

    html += '<div class="card">\n'
    html += f'    <h2><span class="icon">&#128202;</span> Domain Report: {report_date}</h2>\n'
    html += f'    <p style="color:var(--text-muted);margin-bottom:1rem;font-size:0.9rem;">'
    html += f'Generated at: {escape_html(report_data.get("generated_at", "N/A"))}</p>\n'

    html += generate_stat_cards([
        (report_data.get('total_domains', 0), "Total Domains"),
        (indexed_count, "Indexed Domains"),
        (se_count, ".se Domains"),
        (nu_count, ".nu Domains"),
    ])

    html += generate_filter_bar(domains)

    # Download links
    html += f"""<div class="download-links">
    <a href="../reports/{report_date}.json" download class="btn btn-secondary">Export JSON</a>
    <a href="../reports/{report_date}.csv" download class="btn btn-secondary">Export CSV</a>
</div>\n"""

    if domains:
        html += generate_domains_table(domains)
    else:
        html += '<p style="margin-top:1rem;">No domains found in this report.</p>\n'

    html += '</div>\n'

    # Other reports card
    html += f"""
<div class="card">
    <h2><span class="icon">&#128197;</span> Other Reports</h2>
{generate_report_list(reports, current_date=report_date)}
</div>"""

    html += '\n    </div>'  # close .container .content
    html += html_footer()
    return html


def main():
    """Generate static site."""
    print("Building static site for GitHub Pages...")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load all reports
    reports = load_reports()
    print(f"Found {len(reports)} reports")

    # Generate index page
    print("Generating index.html...")
    index_html = generate_index_page(reports)
    with open(OUTPUT_DIR / "index.html", 'w') as f:
        f.write(index_html)

    # Generate individual report pages
    for report in reports:
        print(f"Generating report-{report['date']}.html...")
        report_data = load_report(report['date'])
        if report_data:
            report_html = generate_report_page(report['date'], report_data, reports)
            with open(OUTPUT_DIR / f"report-{report['date']}.html", 'w') as f:
                f.write(report_html)

    print(f"Static site generated in {OUTPUT_DIR}/")
    print(f"To test locally: cd {OUTPUT_DIR} && python -m http.server 8000")


if __name__ == "__main__":
    main()
