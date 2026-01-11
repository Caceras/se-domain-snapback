"""Check if domains have pages indexed in Google."""

import re
import time
import requests
from typing import Optional
from urllib.parse import quote_plus

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from config import SCAN_DELAY_SECONDS, USER_AGENT


def check_google_index(domain: str) -> dict:
    """
    Check if a domain has pages indexed in Google using site: search.

    Args:
        domain: Full domain name (e.g., "example.se")

    Returns:
        Dict with 'indexed' (bool) and 'estimated_pages' (int or None)
    """
    query = f"site:{domain}"
    url = f"https://www.google.com/search?q={quote_plus(query)}"

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "DNT": "1",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        # Check for "No results found" or similar indicators
        no_results_patterns = [
            "did not match any documents",
            "No results found",
            "didn't match any documents",
        ]

        for pattern in no_results_patterns:
            if pattern.lower() in html.lower():
                return {"indexed": False, "estimated_pages": 0}

        # Try to extract result count
        # Pattern: "About X results" or "X results"
        count_patterns = [
            r'About ([\d,]+) results',
            r'([\d,]+) results',
            r'result-stats[^>]*>About ([\d,]+)',
            r'result-stats[^>]*>([\d,]+)',
        ]

        for pattern in count_patterns:
            match = re.search(pattern, html)
            if match:
                count_str = match.group(1).replace(",", "")
                try:
                    count = int(count_str)
                    return {"indexed": True, "estimated_pages": count}
                except ValueError:
                    pass

        # If we got a response but couldn't parse count, assume indexed
        # (Google sometimes changes their HTML structure)
        if "search" in html.lower() and len(html) > 5000:
            return {"indexed": True, "estimated_pages": None}

        return {"indexed": False, "estimated_pages": 0}

    except requests.exceptions.RequestException as e:
        # On error, return unknown status
        return {"indexed": None, "estimated_pages": None, "error": str(e)}


def check_bing_index(domain: str) -> dict:
    """
    Fallback: Check if a domain has pages indexed in Bing.
    Bing is often more lenient with automated queries.

    Args:
        domain: Full domain name (e.g., "example.se")

    Returns:
        Dict with 'indexed' (bool) and 'estimated_pages' (int or None)
    """
    query = f"site:{domain}"
    url = f"https://www.bing.com/search?q={quote_plus(query)}"

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html = response.text

        # Check for no results
        if "No results found" in html or "There are no results for" in html:
            return {"indexed": False, "estimated_pages": 0}

        # Try to extract result count from Bing
        count_patterns = [
            r'([\d,]+) results',
            r'sb_count[^>]*>([\d,]+)',
        ]

        for pattern in count_patterns:
            match = re.search(pattern, html)
            if match:
                count_str = match.group(1).replace(",", "")
                try:
                    count = int(count_str)
                    return {"indexed": True, "estimated_pages": count}
                except ValueError:
                    pass

        # Check if there are any search results
        if 'class="b_algo"' in html:
            return {"indexed": True, "estimated_pages": None}

        return {"indexed": False, "estimated_pages": 0}

    except requests.exceptions.RequestException as e:
        return {"indexed": None, "estimated_pages": None, "error": str(e)}


def check_index_with_fallback(domain: str) -> dict:
    """
    Check domain index status, falling back to Bing if Google fails.

    Args:
        domain: Full domain name

    Returns:
        Dict with index status and source used
    """
    # Try Google first
    result = check_google_index(domain)

    if result.get("indexed") is None and "error" in result:
        # Google failed, try Bing
        result = check_bing_index(domain)
        result["source"] = "bing"
    else:
        result["source"] = "google"

    return result


def check_index_batch(domains: list[dict], use_fallback: bool = True) -> list[dict]:
    """
    Check index status for a batch of domains with rate limiting.

    Args:
        domains: List of domain dicts with 'name' field
        use_fallback: Whether to fallback to Bing if Google fails

    Returns:
        List of domains with index information added
    """
    results = []

    for i, domain in enumerate(domains):
        domain_name = domain["name"]

        if use_fallback:
            index_info = check_index_with_fallback(domain_name)
        else:
            index_info = check_google_index(domain_name)

        domain.update(index_info)
        results.append(domain)

        # Rate limiting - don't hit on the last iteration
        if i < len(domains) - 1:
            time.sleep(SCAN_DELAY_SECONDS)

    return results


if __name__ == "__main__":
    # Test with some known domains
    test_domains = [
        "google.se",      # Should be indexed
        "github.com",     # Should be indexed
    ]

    for domain in test_domains:
        print(f"Checking {domain}...")
        result = check_index_with_fallback(domain)
        print(f"  Indexed: {result['indexed']}")
        print(f"  Pages: {result['estimated_pages']}")
        print(f"  Source: {result.get('source', 'unknown')}")
        time.sleep(2)
