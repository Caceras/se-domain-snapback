# SE/NU Domain Snapback Scanner

Lists ALL .se and .nu domains that will be released tonight.

🌐 **[View Live Results on GitHub Pages](https://caceras.github.io/se-domain-snapback/)**

## Features

- **Complete Domain Listing**: Shows ALL domains releasing tonight in Swedish TLDs (.se and .nu)
- **Simple & Fast**: No filtering, no checking - just a complete list
- **GitHub Pages**: Published static site with daily updates
- **Web UI**: Beautiful web interface to view all releasing domains
- **Historical Reports**: Tracks all scan results with CSV and JSON exports
- **GitHub Actions Integration**: Automated daily execution

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

- **Dashboard**: View ALL domains releasing tonight
- **Domain Table**: Sortable and searchable table of all domains
- **Historical Reports**: Browse and export past scan results
- **Export**: Download results as CSV or JSON

## Command Line Interface

### Basic Usage

```bash
# List ALL domains releasing tonight (default)
python src/main.py

# List ALL domains releasing on a specific date
python src/main.py --date 2026-02-10

# Dry run (don't save reports)
python src/main.py --dry-run

# Test the drop list fetch
python src/main.py --test-fetch
```

## How It Works

The scanner performs a simple 2-step process:

1. **Fetch Drop Lists**: Retrieves ALL domains releasing on target date from Internetstiftelsen (IIS) API
2. **Generate Reports**: Creates CSV and JSON reports in the `/reports` directory

## Configuration

Edit `config.py` to customize:

- `REPORT_DIR`: Output directory for reports (default: `./reports`)

## GitHub Actions

The scanner runs automatically via GitHub Actions:

- **Schedule**: Daily to capture domains releasing tonight
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
example.se,se,2026-02-10,True,False,,,2026-02-09T07:00:00Z
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
      "indexed": false,
      "estimated_pages": null,
      "index_source": null,
      "checked_at": "2026-02-09T07:00:00Z"
    }
  ]
}
```

## Requirements

- Python 3.12+
- Dependencies listed in `requirements.txt`:
  - requests
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
