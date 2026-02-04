#!/usr/bin/env python3
"""
Flask web application for SE/NU Domain Snapback Scanner.

Provides a web UI to view scan results and trigger scans.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, render_template, jsonify, request, send_file
import threading

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import main as run_scanner
from config import REPORT_DIR

app = Flask(__name__)

# Store scan status
scan_status = {
    "running": False,
    "message": "",
    "last_scan": None
}


def get_available_reports():
    """Get list of available report files."""
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


@app.route('/')
def index():
    """Home page showing latest scan results."""
    reports = get_available_reports()
    
    # Load the most recent report
    latest_data = None
    if reports:
        latest_data = load_report(reports[0]['date'])
    
    return render_template('index.html', 
                         reports=reports,
                         latest_data=latest_data,
                         scan_status=scan_status)


@app.route('/report/<date>')
def view_report(date):
    """View a specific report by date."""
    reports = get_available_reports()
    report_data = load_report(date)
    
    if not report_data:
        return "Report not found", 404
    
    return render_template('report.html',
                         reports=reports,
                         report_date=date,
                         report_data=report_data,
                         scan_status=scan_status)


@app.route('/api/reports')
def api_reports():
    """API endpoint to get list of reports."""
    reports = get_available_reports()
    return jsonify([r['date'] for r in reports])


@app.route('/api/report/<date>')
def api_report(date):
    """API endpoint to get a specific report."""
    report_data = load_report(date)
    if report_data:
        return jsonify(report_data)
    return jsonify({"error": "Report not found"}), 404


@app.route('/api/report/<date>/csv')
def api_report_csv(date):
    """API endpoint to download a report as CSV."""
    csv_path = REPORT_DIR / f"{date}.csv"
    if csv_path.exists():
        return send_file(csv_path, as_attachment=True, download_name=f"{date}.csv")
    return jsonify({"error": "CSV report not found"}), 404


@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    """Start a new scan."""
    global scan_status
    
    if scan_status["running"]:
        return jsonify({"error": "Scan already running"}), 400
    
    # Get parameters from request
    data = request.get_json() or {}
    target_date = data.get('date')
    
    def run_scan_thread():
        global scan_status
        try:
            scan_status["running"] = True
            scan_status["message"] = f"Scanning domains for {target_date or 'tomorrow'}..."
            
            # Run the scanner
            run_scanner(
                target_date=target_date,
                check_availability=True,
                check_index=True,
                filter_indexed_only=True,
                dry_run=False
            )
            
            scan_status["message"] = "Scan completed successfully"
            scan_status["last_scan"] = datetime.now(timezone.utc).isoformat()
        except Exception as e:
            scan_status["message"] = f"Scan failed: {str(e)}"
        finally:
            scan_status["running"] = False
    
    # Start scan in background thread
    thread = threading.Thread(target=run_scan_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Scan started", "status": scan_status})


@app.route('/api/scan/status')
def scan_status_api():
    """Get current scan status."""
    return jsonify(scan_status)


if __name__ == '__main__':
    # Ensure reports directory exists
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
