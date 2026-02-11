"""Fetch dropping domains from Internetstiftelsen (IIS) API."""

import requests
from datetime import datetime, timezone, timedelta
from typing import Literal, Optional

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from config import IIS_SE_URL, IIS_NU_URL, USER_AGENT


def fetch_drop_list(tld: Literal["se", "nu"] = "se") -> list[dict]:
    """
    Fetch the complete drop list for a given TLD.

    Args:
        tld: Either "se" or "nu"

    Returns:
        List of domain entries with 'name' and 'release_at' fields
    """
    url = IIS_NU_URL if tld == "nu" else IIS_SE_URL

    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=30
        )
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"  Warning: Could not connect to {url}. Network may be unavailable.")
        return []
    except requests.exceptions.Timeout:
        print(f"  Warning: Request to {url} timed out.")
        return []
    except requests.exceptions.RequestException as e:
        print(f"  Warning: Failed to fetch .{tld} drop list: {e}")
        return []

    return response.json().get("data", [])


def fetch_dropping_on_date(tld: Literal["se", "nu"] = "se", target_date: Optional[str] = None) -> list[dict]:
    """
    Fetch domains dropping on a specific date for a given TLD.

    Args:
        tld: Either "se" or "nu"
        target_date: Date string in YYYY-MM-DD format, defaults to tomorrow

    Returns:
        List of domain entries releasing on target date
    """
    all_domains = fetch_drop_list(tld)

    if target_date is None:
        # Default to tomorrow (domains drop at 04:00 UTC, we run at 07:00 UTC)
        tomorrow = datetime.now(timezone.utc) + timedelta(days=1)
        target_date = tomorrow.strftime("%Y-%m-%d")

    return [d for d in all_domains if d.get("release_at") == target_date]


def fetch_all_dropping_tomorrow() -> list[dict]:
    """
    Fetch all .se and .nu domains dropping tomorrow.
    This gives ~21 hours advance notice before domains become available.

    Returns:
        Combined list of domains from both TLDs releasing tomorrow
    """
    tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
    return fetch_all_dropping_on_date(tomorrow)


def fetch_all_dropping_on_date(target_date: str) -> list[dict]:
    """
    Fetch all .se and .nu domains dropping on a specific date.

    Args:
        target_date: Date string in YYYY-MM-DD format

    Returns:
        Combined list of domains from both TLDs releasing on target date
    """
    se_domains = fetch_dropping_on_date("se", target_date)
    nu_domains = fetch_dropping_on_date("nu", target_date)

    # Add TLD info to each domain for clarity
    for d in se_domains:
        d["tld"] = "se"
    for d in nu_domains:
        d["tld"] = "nu"

    return se_domains + nu_domains


# Keep backwards compatibility
def fetch_dropping_today(tld: Literal["se", "nu"] = "se") -> list[dict]:
    """
    Fetch domains releasing today (tonight) for a given TLD.
    
    Args:
        tld: Either "se" or "nu"
        
    Returns:
        List of domain entries releasing today
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return fetch_dropping_on_date(tld, today)


def fetch_all_dropping_today() -> list[dict]:
    """
    Fetch all .se and .nu domains releasing today (tonight).
    
    Returns:
        Combined list of domains from both TLDs releasing today
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return fetch_all_dropping_on_date(today)


if __name__ == "__main__":
    # Test the fetcher
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"Fetching domains releasing today ({today})...")
    domains = fetch_all_dropping_today()
    print(f"Found {len(domains)} domains releasing today")

    se_count = sum(1 for d in domains if d.get("tld") == "se")
    nu_count = sum(1 for d in domains if d.get("tld") == "nu")
    print(f"  .se: {se_count}, .nu: {nu_count}")

    for d in domains[:10]:
        print(f"  - {d['name']} (releases: {d['release_at']})")
    if len(domains) > 10:
        print(f"  ... and {len(domains) - 10} more")
