#!/usr/bin/env python3
"""
SE/NU Domain Snapback Scanner

Automated daily scanner to find valuable .se and .nu domains that will
drop soon and may be available for registration.

Features:
- Fetches official drop lists from Internetstiftelsen (IIS)
- Scans domains dropping tomorrow (21 hours ahead) by default
- Checks domain availability via DNS (for already-dropped domains)
- Verifies Google/Bing index presence
- Generates CSV and JSON reports
"""

import sys
import argparse
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fetcher import fetch_all_dropping_on_date, fetch_drop_list
from src.availability import check_availability_batch
from src.index_checker import check_index_batch
from src.reporter import generate_report, generate_summary, filter_valuable_domains
from config import REPORT_DIR


def main(
    target_date: str = None,
    check_availability: bool = True,
    check_index: bool = True,
    filter_indexed_only: bool = True,
    dry_run: bool = False,
) -> None:
    """
    Main scanner workflow.

    Args:
        target_date: Date to scan (YYYY-MM-DD), defaults to tomorrow
        check_availability: Whether to check if domains are available
        check_index: Whether to check search engine index status
        filter_indexed_only: Only include indexed domains in final report
        dry_run: If True, don't write reports, just print results
    """
    # Default to tomorrow if no date specified
    if target_date is None:
        target_date = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"SE/NU Domain Snapback Scanner")
    print(f"=" * 40)
    print(f"Target drop date: {target_date}")
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()

    # Step 1: Fetch domains dropping on target date
    print(f"Step 1: Fetching domains dropping on {target_date}...")
    domains = fetch_all_dropping_on_date(target_date)

    se_count = sum(1 for d in domains if d.get("tld") == "se")
    nu_count = sum(1 for d in domains if d.get("tld") == "nu")
    print(f"  Found {len(domains)} domains ({se_count} .se, {nu_count} .nu)")

    if not domains:
        print(f"  No domains dropping on {target_date}. Exiting.")
        return

    # Step 2: Check availability (only useful for already-dropped domains)
    if check_availability:
        print()
        print("Step 2: Checking domain availability via DNS...")
        domains = check_availability_batch(domains)
        available_count = sum(1 for d in domains if d.get("available"))
        print(f"  Checked {len(domains)} domains ({available_count} appear available)")
    else:
        # Mark all as available if not checking (future drops aren't registered yet)
        for d in domains:
            d["available"] = True

    # Step 3: Check search engine index
    if check_index:
        print()
        print("Step 3: Checking search engine index status...")
        print(f"  This may take a while ({len(domains)} domains to check)...")
        domains = check_index_batch(domains, use_fallback=True)

        indexed_count = sum(1 for d in domains if d.get("indexed"))
        print(f"  {indexed_count} domains have indexed pages")

    # Step 4: Filter to valuable domains only
    if filter_indexed_only:
        print()
        print("Step 4: Filtering to indexed domains only...")
        domains = filter_valuable_domains(domains)
        print(f"  {len(domains)} valuable domains remain")

    # Step 5: Generate report
    print()
    if dry_run:
        print("Step 5: Dry run - not writing reports")
        print()
        print(generate_summary(domains))
    else:
        print("Step 5: Generating reports...")
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
        description="Scan for valuable .se and .nu domains dropping soon"
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Target drop date (YYYY-MM-DD). Defaults to tomorrow."
    )

    parser.add_argument(
        "--no-availability-check",
        action="store_true",
        help="Skip DNS availability checking (recommended for future drops)"
    )

    parser.add_argument(
        "--no-index-check",
        action="store_true",
        help="Skip search engine index checking"
    )

    parser.add_argument(
        "--all-domains",
        action="store_true",
        help="Include all domains, not just indexed ones"
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
        check_availability=not args.no_availability_check,
        check_index=not args.no_index_check,
        filter_indexed_only=not args.all_domains,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    cli()
