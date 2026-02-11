#!/usr/bin/env python3
"""
SE/NU Domain Snapback Scanner

Lists ALL .se and .nu domains that will be released tonight.

Features:
- Fetches official drop lists from Internetstiftelsen (IIS)
- Shows ALL domains releasing tonight (today) by default
- Generates CSV and JSON reports
"""

import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fetcher import fetch_all_dropping_on_date, fetch_drop_list
from src.reporter import generate_report, generate_summary
from config import REPORT_DIR


def main(
    target_date: str = None,
    dry_run: bool = False,
) -> None:
    """
    Main scanner workflow.

    Args:
        target_date: Date to scan (YYYY-MM-DD), defaults to tonight (today)
        dry_run: If True, don't write reports, just print results
    """
    # Default to tonight (today) if no date specified
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if target_date is None:
        target_date = today

    tonight_label = " (tonight)" if target_date == today else ""
    print(f"SE/NU Domain Snapback Scanner")
    print(f"=" * 40)
    print(f"Target release date: {target_date}{tonight_label}")
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()

    # Step 1: Fetch ALL domains releasing on target date
    print(f"Step 1: Fetching ALL domains releasing on {target_date}...")
    domains = fetch_all_dropping_on_date(target_date)

    se_count = sum(1 for d in domains if d.get("tld") == "se")
    nu_count = sum(1 for d in domains if d.get("tld") == "nu")
    print(f"  Found {len(domains)} domains ({se_count} .se, {nu_count} .nu)")

    if not domains:
        print(f"  No domains releasing on {target_date}. Exiting.")
        return

    # Initialize fields - availability is unknown until explicitly checked
    for d in domains:
        d["available"] = None
        d["indexed"] = False
        d["estimated_pages"] = None
        d["index_source"] = None

    # Step 2: Generate report
    print()
    if dry_run:
        print("Step 2: Dry run - not writing reports")
        print()
        print(generate_summary(domains))
    else:
        print("Step 2: Generating reports...")
        # Use target date for report filename
        csv_path, json_path = generate_report(domains, timestamp=target_date)
        print(f"  CSV: {csv_path}")
        print(f"  JSON: {json_path}")

    print()
    print(f"Completed at: {datetime.now(timezone.utc).isoformat()}")

    # Print summary
    if domains:
        print()
        print(generate_summary(domains))


def cli():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="List ALL .se and .nu domains that will be released tonight"
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Target release date (YYYY-MM-DD). Defaults to tonight (today)."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write reports, just print results"
    )

    parser.add_argument(
        "--test-fetch",
        action="store_true",
        help="Only test fetching the drop list (no processing)"
    )

    args = parser.parse_args()

    if args.test_fetch:
        print("Testing drop list fetch...")
        for tld in ["se", "nu"]:
            domains = fetch_drop_list(tld)
            print(f"  .{tld}: {len(domains)} domains in drop list")
        return

    main(
        target_date=args.date,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    cli()
