#!/usr/bin/env python3
"""
Static site generator for GitHub Pages.

Converts JSON reports into static HTML pages that can be served on GitHub Pages.
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


def generate_index_page(reports):
    """Generate the index.html page."""
    latest_data = None
    if reports:
        latest_data = load_report(reports[0]['date'])
    
    # Generate HTML
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SE/NU Domain Snapback Scanner</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        h1 {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .subtitle {
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        .nav {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .nav a {
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            transition: background 0.2s;
        }
        
        .nav a:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .content {
            padding: 2rem 0;
        }
        
        .card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            margin-bottom: 1rem;
            color: #667eea;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-warning {
            background: #fff3cd;
            color: #856404;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: 600;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            margin-top: 0.5rem;
        }
        
        .report-list {
            list-style: none;
        }
        
        .report-list li {
            padding: 0.5rem;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .report-list a {
            color: #667eea;
            text-decoration: none;
        }
        
        .report-list a:hover {
            text-decoration: underline;
        }
        
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #666;
        }
        
        .tld-se {
            color: #2196F3;
            font-weight: 500;
        }
        
        .tld-nu {
            color: #4CAF50;
            font-weight: 500;
        }
        
        .github-link {
            margin-top: 2rem;
            text-align: center;
            padding: 1rem;
            background: white;
            border-radius: 8px;
        }
        
        .github-link a {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🔍 SE/NU Domain Snapback Scanner</h1>
            <p class="subtitle">Find valuable expiring .se and .nu domains</p>
            <div class="nav">
                <a href="index.html">Latest Results</a>
                <a href="#reports">All Reports</a>
            </div>
        </div>
    </div>
    
    <div class="container content">
"""
    
    if latest_data and reports:
        indexed_count = sum(1 for d in latest_data.get('domains', []) if d.get('indexed'))
        
        html += f"""
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{latest_data.get('total_domains', 0)}</div>
                <div class="stat-label">Valuable Domains Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(reports)}</div>
                <div class="stat-label">Historical Reports</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{indexed_count}</div>
                <div class="stat-label">Indexed Domains</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Latest Scan Results ({reports[0]['date']})</h2>
"""
        
        if latest_data.get('domains'):
            html += """
            <table>
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>TLD</th>
                        <th>Release Date</th>
                        <th>Indexed Pages</th>
                        <th>Source</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            # Show top 50 domains
            for domain in latest_data['domains'][:50]:
                indexed_badge = '<span class="badge badge-success">Indexed</span>' if domain.get('indexed') else '<span class="badge badge-warning">Not Indexed</span>'
                pages = f"<strong>{domain.get('estimated_pages', '-')}</strong>" if domain.get('estimated_pages') else '-'
                tld_class = f"tld-{domain.get('tld', 'se')}"
                
                html += f"""
                    <tr>
                        <td><strong>{domain.get('domain', '')}</strong></td>
                        <td><span class="{tld_class}">.{domain.get('tld', '')}</span></td>
                        <td>{domain.get('release_date', '')}</td>
                        <td>{pages}</td>
                        <td>{domain.get('index_source', '')}</td>
                        <td>{indexed_badge}</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
"""
            
            if len(latest_data['domains']) > 50:
                html += f"""
            <p style="margin-top: 1rem; color: #666;">
                Showing top 50 of {len(latest_data['domains'])} domains. 
                <a href="report-{reports[0]['date']}.html">View full report</a>
            </p>
"""
        else:
            html += """
            <div class="empty-state">
                <p>No domains found in the latest scan.</p>
            </div>
"""
        
        html += """
        </div>
"""
    else:
        html += """
        <div class="card">
            <h2>No Reports Available</h2>
            <div class="empty-state">
                <p>No scan results found yet. Check back soon!</p>
            </div>
        </div>
"""
    
    # Add historical reports section
    if reports:
        html += """
        <div class="card" id="reports">
            <h2>Historical Reports</h2>
            <ul class="report-list">
"""
        for report in reports:
            html += f'                <li><a href="report-{report["date"]}.html">📄 {report["date"]}</a></li>\n'
        
        html += """
            </ul>
        </div>
"""
    
    # Add GitHub link
    html += """
        <div class="github-link">
            <p>📊 Data updated daily via <a href="https://github.com/Caceras/se-domain-snapback" target="_blank">GitHub Actions</a></p>
            <p style="margin-top: 0.5rem;">⭐ <a href="https://github.com/Caceras/se-domain-snapback" target="_blank">View on GitHub</a></p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


def generate_report_page(report_date, report_data, reports):
    """Generate a report page for a specific date."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Domain Report - {report_date}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        h1 {{
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        
        .subtitle {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .nav {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .nav a {{
            color: white;
            text-decoration: none;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .nav a:hover {{
            background: rgba(255,255,255,0.2);
        }}
        
        .content {{
            padding: 2rem 0;
        }}
        
        .card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            margin-bottom: 1rem;
            color: #667eea;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        th, td {{
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #555;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .tld-se {{
            color: #2196F3;
            font-weight: 500;
        }}
        
        .tld-nu {{
            color: #4CAF50;
            font-weight: 500;
        }}
        
        .download-links {{
            margin-top: 1rem;
        }}
        
        .download-links a {{
            display: inline-block;
            margin-right: 1rem;
            padding: 0.5rem 1rem;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
        
        .download-links a:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="container">
            <h1>🔍 SE/NU Domain Snapback Scanner</h1>
            <p class="subtitle">Report for {report_date}</p>
            <div class="nav">
                <a href="index.html">← Back to Latest</a>
            </div>
        </div>
    </div>
    
    <div class="container content">
        <div class="card">
            <h2>Domain Report - {report_date}</h2>
            <p><strong>Total Domains:</strong> {report_data.get('total_domains', 0)}</p>
            <p><strong>Generated:</strong> {report_data.get('generated_at', 'N/A')}</p>
            
            <div class="download-links">
                <a href="../reports/{report_date}.json" download>📥 Download JSON</a>
                <a href="../reports/{report_date}.csv" download>📥 Download CSV</a>
            </div>
"""
    
    if report_data.get('domains'):
        html += """
            <table>
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>TLD</th>
                        <th>Release Date</th>
                        <th>Indexed Pages</th>
                        <th>Source</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for domain in report_data['domains']:
            indexed_badge = '<span class="badge badge-success">Indexed</span>' if domain.get('indexed') else '<span class="badge badge-warning">Not Indexed</span>'
            pages = f"<strong>{domain.get('estimated_pages', '-')}</strong>" if domain.get('estimated_pages') else '-'
            tld_class = f"tld-{domain.get('tld', 'se')}"
            
            html += f"""
                    <tr>
                        <td><strong>{domain.get('domain', '')}</strong></td>
                        <td><span class="{tld_class}">.{domain.get('tld', '')}</span></td>
                        <td>{domain.get('release_date', '')}</td>
                        <td>{pages}</td>
                        <td>{domain.get('index_source', '')}</td>
                        <td>{indexed_badge}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
"""
    else:
        html += """
            <p style="margin-top: 1rem;">No domains found in this report.</p>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    return html


def main():
    """Generate static site."""
    print("🏗️  Building static site for GitHub Pages...")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load all reports
    reports = load_reports()
    print(f"📊 Found {len(reports)} reports")
    
    # Generate index page
    print("📄 Generating index.html...")
    index_html = generate_index_page(reports)
    with open(OUTPUT_DIR / "index.html", 'w') as f:
        f.write(index_html)
    
    # Generate individual report pages
    for report in reports:
        print(f"📄 Generating report-{report['date']}.html...")
        report_data = load_report(report['date'])
        if report_data:
            report_html = generate_report_page(report['date'], report_data, reports)
            with open(OUTPUT_DIR / f"report-{report['date']}.html", 'w') as f:
                f.write(report_html)
    
    print(f"✅ Static site generated in {OUTPUT_DIR}/")
    print(f"🌐 To test locally: cd {OUTPUT_DIR} && python -m http.server 8000")


if __name__ == "__main__":
    main()
