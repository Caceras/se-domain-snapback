"""Fetch dropping domains from Internetstiftelsen (IIS) API."""

import requests
from datetime import datetime, timezone
from typing import Literal

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

    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=30
    )
    response.raise_for_status()

    return response.json().get("data", [])


def fetch_dropping_today(tld: Literal["se", "nu"] = "se") -> list[dict]:
    """
    Fetch domains dropping today for a given TLD.

    Args:
        tld: Either "se" or "nu"

    Returns:
        List of domain entries releasing today
    """
    all_domains = fetch_drop_list(tld)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    return [d for d in all_domains if d.get("release_at") == today]


def fetch_all_dropping_today() -> list[dict]:
    """
    Fetch all .se and .nu domains dropping today.

    Returns:
        Combined list of domains from both TLDs releasing today
    """
    se_domains = fetch_dropping_today("se")
    nu_domains = fetch_dropping_today("nu")

    # Add TLD info to each domain for clarity
    for d in se_domains:
        d["tld"] = "se"
    for d in nu_domains:
        d["tld"] = "nu"

    return se_domains + nu_domains


if __name__ == "__main__":
    # Test the fetcher
    print("Fetching domains dropping today...")
    domains = fetch_all_dropping_today()
    print(f"Found {len(domains)} domains dropping today")
    for d in domains[:10]:
        print(f"  - {d['name']} (releases: {d['release_at']})")
    if len(domains) > 10:
        print(f"  ... and {len(domains) - 10} more")
