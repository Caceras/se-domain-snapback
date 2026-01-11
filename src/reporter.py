"""Generate reports in CSV and JSON formats."""

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from config import REPORT_DIR, MIN_INDEXED_PAGES


def filter_valuable_domains(domains: list[dict]) -> list[dict]:
    """
    Filter domains to only include those meeting value criteria.

    Args:
        domains: List of domain dicts with index information

    Returns:
        Filtered list of valuable domains
    """
    valuable = []

    for domain in domains:
        # Must be indexed
        if not domain.get("indexed"):
            continue

        # Must meet minimum page threshold (if we have count)
        pages = domain.get("estimated_pages")
        if pages is not None and pages < MIN_INDEXED_PAGES:
            continue

        valuable.append(domain)

    return valuable


def generate_report(
    domains: list[dict],
    output_dir: Optional[Path] = None,
    timestamp: Optional[str] = None
) -> tuple[Path, Path]:
    """
    Generate CSV and JSON reports for the given domains.

    Args:
        domains: List of domain dicts with all collected data
        output_dir: Directory to save reports (defaults to config REPORT_DIR)
        timestamp: Date string for filename (defaults to today)

    Returns:
        Tuple of (csv_path, json_path)
    """
    if output_dir is None:
        output_dir = REPORT_DIR

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Ensure output directory exists
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Prepare data with consistent fields
    report_data = []
    checked_at = datetime.now(timezone.utc).isoformat()

    for domain in domains:
        report_data.append({
            "domain": domain.get("name", ""),
            "tld": domain.get("tld", ""),
            "release_date": domain.get("release_at", ""),
            "available": domain.get("available", True),
            "indexed": domain.get("indexed", False),
            "estimated_pages": domain.get("estimated_pages"),
            "index_source": domain.get("source", ""),
            "checked_at": checked_at,
        })

    # Sort by estimated pages (highest first), then by domain name
    report_data.sort(
        key=lambda x: (-(x.get("estimated_pages") or 0), x.get("domain", ""))
    )

    # Generate CSV
    csv_path = output_dir / f"{timestamp}.csv"
    fieldnames = [
        "domain", "tld", "release_date", "available",
        "indexed", "estimated_pages", "index_source", "checked_at"
    ]

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)

    # Generate JSON
    json_path = output_dir / f"{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": checked_at,
            "total_domains": len(report_data),
            "domains": report_data
        }, f, indent=2)

    return csv_path, json_path


def generate_summary(domains: list[dict]) -> str:
    """
    Generate a text summary of the scan results.

    Args:
        domains: List of processed domain dicts

    Returns:
        Summary string
    """
    total = len(domains)
    indexed = sum(1 for d in domains if d.get("indexed"))
    with_pages = [d for d in domains if d.get("estimated_pages")]

    lines = [
        f"Domain Scan Summary",
        f"==================",
        f"Total domains scanned: {total}",
        f"Indexed in search engines: {indexed}",
        f"With page count data: {len(with_pages)}",
    ]

    if with_pages:
        max_pages = max(d.get("estimated_pages", 0) for d in with_pages)
        lines.append(f"Highest page count: {max_pages}")

    # Top domains
    if domains:
        lines.append(f"\nTop domains by indexed pages:")
        sorted_domains = sorted(
            domains,
            key=lambda x: -(x.get("estimated_pages") or 0)
        )[:5]
        for d in sorted_domains:
            pages = d.get("estimated_pages", "?")
            lines.append(f"  - {d.get('name', '?')}: {pages} pages")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test with sample data
    sample_domains = [
        {
            "name": "example.se",
            "tld": "se",
            "release_at": "2026-01-11",
            "available": True,
            "indexed": True,
            "estimated_pages": 150,
            "source": "google"
        },
        {
            "name": "test.nu",
            "tld": "nu",
            "release_at": "2026-01-11",
            "available": True,
            "indexed": True,
            "estimated_pages": 42,
            "source": "bing"
        },
    ]

    csv_path, json_path = generate_report(sample_domains, Path("/tmp"))
    print(f"Generated: {csv_path}")
    print(f"Generated: {json_path}")
    print()
    print(generate_summary(sample_domains))
