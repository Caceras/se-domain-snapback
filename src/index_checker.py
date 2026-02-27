"""Check if domains have archived pages in the Wayback Machine (Internet Archive).

Uses the CDX API — free, no auth, no CAPTCHAs, no rate limits that block bots.
Returns actual archived page counts as a reliable proxy for historical SEO value.
"""

import requests
import time

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from config import SCAN_DELAY_SECONDS


def check_wayback_index(domain: str) -> dict:
    """
    Check if a domain has archived pages in the Wayback Machine.

    Queries the CDX API for unique archived URLs under the domain.
    A non-zero count means the domain had real content and was crawled —
    a strong signal of historical SEO value.

    Args:
        domain: Full domain name (e.g., "example.se")

    Returns:
        Dict with 'indexed' (bool or None), 'estimated_pages' (int or None),
        'source' ("wayback")
    """
    url = "http://web.archive.org/cdx/search/cdx"
    params = {
        "url": f"*.{domain}",
        "matchType": "domain",
        "output": "json",
        "fl": "urlkey",
        "collapse": "urlkey",
        "limit": "500",
    }

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        data = response.json()

        # First row is the header ["urlkey"], rest are results
        page_count = max(0, len(data) - 1)

        if page_count == 0:
            return {"indexed": False, "estimated_pages": 0, "source": "wayback"}

        return {"indexed": True, "estimated_pages": page_count, "source": "wayback"}

    except requests.exceptions.RequestException as e:
        return {"indexed": None, "estimated_pages": None, "source": "wayback", "error": str(e)}


def check_index_batch(domains: list[dict], use_fallback: bool = True) -> list[dict]:
    """
    Check Wayback Machine archive status for a batch of domains.

    Args:
        domains: List of domain dicts with 'name' field
        use_fallback: Unused (kept for API compatibility)

    Returns:
        List of domains with 'indexed', 'estimated_pages', 'source' added
    """
    results = []

    for i, domain in enumerate(domains):
        index_info = check_wayback_index(domain["name"])
        domain.update(index_info)
        results.append(domain)

        if i < len(domains) - 1:
            time.sleep(SCAN_DELAY_SECONDS)

    return results


if __name__ == "__main__":
    test_domains = [
        "google.se",
        "github.com",
        "xyznonexistent123456789.se",
    ]

    for domain in test_domains:
        print(f"Checking {domain}...")
        result = check_wayback_index(domain)
        print(f"  Indexed: {result['indexed']}")
        print(f"  Pages:   {result['estimated_pages']}")
        print(f"  Source:  {result['source']}")
        time.sleep(1)
