"""Configuration constants for the domain snapback scanner."""

from pathlib import Path

# API URLs
IIS_SE_URL = "https://data.internetstiftelsen.se/bardate_domains.json"
IIS_NU_URL = "https://data.internetstiftelsen.se/bardate_domains_nu.json"

# Rate limiting
SCAN_DELAY_SECONDS = 2.5  # Delay between Google index checks
DNS_TIMEOUT_SECONDS = 3   # Timeout for DNS lookups

# Filtering
MIN_INDEXED_PAGES = 1     # Minimum pages to include in report

# Output
REPORT_DIR = Path(__file__).parent / "reports"

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
