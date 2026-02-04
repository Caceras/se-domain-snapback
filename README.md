# SE/NU Domain Snapback Scanner

Automated daily scanner to find valuable .se and .nu domains that will drop soon and may be available for registration.

🌐 **[View Live Results on GitHub Pages](https://caceras.github.io/se-domain-snapback/)**

## Features

- **Automated Scanning**: Daily scans of domains dropping in Swedish TLDs (.se and .nu)
- **Search Engine Verification**: Checks Google/Bing to identify domains with indexed pages (indicating past traffic/value)
- **DNS Availability Check**: Verifies if domains are already available for registration
- **GitHub Pages**: Published static site with daily updates showing latest scan results
- **Web UI**: Beautiful web interface to view scan results and trigger manual scans
- **Historical Reports**: Tracks all scan results with CSV and JSON exports
- **GitHub Actions Integration**: Automated daily execution at 07:00 UTC

## Web Interface

### Starting the Web UI

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
python app.py
```

The web interface will be available at `http://localhost:5000`

### Web UI Features

- **Dashboard**: View latest scan results with statistics
- **Domain Table**: Sortable and searchable table of valuable domains
- **Historical Reports**: Browse and export past scan results
- **Manual Scan**: Trigger new scans on-demand
- **Export**: Download results as CSV or JSON

## Command Line Interface

### Basic Usage

```bash
# Run a scan for tomorrow's drops (default)
python src/main.py

# Scan for a specific date
python src/main.py --date 2026-02-10

# Skip availability checking (recommended for future drops)
python src/main.py --no-availability-check

# Include all domains, not just indexed ones
python src/main.py --all-domains

# Dry run (don't save reports)
python src/main.py --dry-run

# Test the drop list fetch
python src/main.py --test-fetch
```

## How It Works

The scanner performs a 5-step process:

1. **Fetch Drop Lists**: Retrieves domains dropping on target date from Internetstiftelsen (IIS) API
2. **Check Availability**: Verifies via DNS if domains are already available
3. **Check Search Engine Index**: Queries Google/Bing to see if domains have indexed pages
4. **Filter Valuable Domains**: Keeps only indexed domains with traffic history
5. **Generate Reports**: Creates CSV and JSON reports in the `/reports` directory

## Configuration

Edit `config.py` to customize:

- `SCAN_DELAY_SECONDS`: Delay between Google index checks (default: 2.5s)
- `DNS_TIMEOUT_SECONDS`: Timeout for DNS lookups (default: 3s)
- `MIN_INDEXED_PAGES`: Minimum pages to include in report (default: 1)
- `REPORT_DIR`: Output directory for reports (default: `./reports`)

## GitHub Actions

The scanner runs automatically via GitHub Actions:

- **Schedule**: Daily at 07:00 UTC (21 hours before domains drop at 04:00 UTC)
- **Manual Trigger**: Use the "Run workflow" button in the Actions tab
- **Auto-commit**: Reports are automatically committed to the repository

## GitHub Pages

The results are automatically published to GitHub Pages:

- **Live Site**: https://caceras.github.io/se-domain-snapback/
- **Updates**: Site rebuilds automatically after each daily scan
- **Build Script**: `build_static_site.py` generates static HTML from JSON reports
- **Deployment**: `.github/workflows/deploy-pages.yml` handles the deployment

The static site includes:
- Latest scan results with statistics
- Sortable table of valuable domains
- Historical reports archive
- Download links for CSV and JSON data

## Output Format

### CSV Format
```csv
domain,tld,release_date,available,indexed,estimated_pages,index_source,checked_at
example.se,se,2026-02-10,true,true,150,google,2026-02-09T07:00:00Z
```

### JSON Format
```json
{
  "generated_at": "2026-02-09T07:00:00Z",
  "total_domains": 1,
  "domains": [
    {
      "domain": "example.se",
      "tld": "se",
      "release_date": "2026-02-10",
      "available": true,
      "indexed": true,
      "estimated_pages": 150,
      "index_source": "google",
      "checked_at": "2026-02-09T07:00:00Z"
    }
  ]
}
```

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`:
  - requests
  - dnspython
  - httpx
  - beautifulsoup4
  - flask

## Installation

```bash
# Clone the repository
git clone https://github.com/Caceras/se-domain-snapback.git
cd se-domain-snapback

# Install dependencies
pip install -r requirements.txt

# Run the scanner
python src/main.py

# Or start the web UI
python app.py
```

## License

This project is for educational and research purposes.

## API Sources

- **Domain Drop Lists**: Internetstiftelsen (IIS) - https://data.internetstiftelsen.se/
- **Search Engine Data**: Google and Bing search indices
