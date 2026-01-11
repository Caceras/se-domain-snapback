#!/usr/bin/env python3
"""
SE/NU Domain Snapback Scanner

Automated daily scanner to find valuable .se and .nu domains that have
just dropped and are available for immediate registration.

Features:
- Fetches official drop lists from Internetstiftelsen (IIS)
- Filters to domains dropping today
- Checks domain availability via DNS
- Verifies Google/Bing index presence
- Generates CSV and JSON reports
"""

import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fetcher import fetch_all_dropping_today, fetch_drop_list
from src.availability import check_availability_batch
from src.index_checker import check_index_batch
from src.reporter import generate_report, generate_summary, filter_valuable_domains
from config import REPORT_DIR


def main(
    check_availability: bool = True,
    check_index: bool = True,
    filter_indexed_only: bool = True,
    dry_run: bool = False,
    lookahead_days: int = 0,
) -> None:
    """
    Main scanner workflow.

    Args:
        check_availability: Whether to check if domains are available
        check_index: Whether to check search engine index status
        filter_indexed_only: Only include indexed domains in final report
        dry_run: If True, don't write reports, just print results
        lookahead_days: Also include domains dropping in next N days
    """
    print(f"SE/NU Domain Snapback Scanner")
    print(f"=" * 40)
    print(f"Started at: {datetime.now(timezone.utc).isoformat()}")
    print()

    # Step 1: Fetch today's dropping domains
    print("Step 1: Fetching drop lists from Internetstiftelsen...")
    domains = fetch_all_dropping_today()
    print(f"  Found {len(domains)} domains dropping today")

    if not domains:
        print("  No domains dropping today. Exiting.")
        return

    # Step 2: Check availability (filter out already-registered)
    if check_availability:
        print()
        print("Step 2: Checking domain availability via DNS...")
        domains = check_availability_batch(domains)
        print(f"  {len(domains)} domains are still available")

        if not domains:
            print("  All domains have been registered. Exiting.")
            return
    else:
        # Mark all as available if not checking
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
        csv_path, json_path = generate_report(domains)
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
        description="Scan for valuable dropped .se and .nu domains"
    )

    parser.add_argument(
        "--no-availability-check",
        action="store_true",
        help="Skip DNS availability checking"
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
        check_availability=not args.no_availability_check,
        check_index=not args.no_index_check,
        filter_indexed_only=not args.all_domains,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    cli()
