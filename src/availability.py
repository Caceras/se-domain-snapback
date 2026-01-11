"""Check domain availability using DNS lookups."""

import dns.resolver
import dns.exception
from typing import Optional

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
from config import DNS_TIMEOUT_SECONDS


def is_available(domain: str) -> bool:
    """
    Check if a domain is available (not yet registered by someone else).

    Uses DNS lookup as the primary method - if DNS doesn't resolve,
    the domain is likely available.

    Args:
        domain: Full domain name (e.g., "example.se")

    Returns:
        True if domain appears available, False if registered
    """
    resolver = dns.resolver.Resolver()
    resolver.timeout = DNS_TIMEOUT_SECONDS
    resolver.lifetime = DNS_TIMEOUT_SECONDS

    # Try multiple record types
    for record_type in ["A", "AAAA", "NS", "MX"]:
        try:
            resolver.resolve(domain, record_type)
            # If any record exists, domain is registered
            return False
        except dns.resolver.NXDOMAIN:
            # Domain doesn't exist - likely available
            continue
        except dns.resolver.NoAnswer:
            # Domain exists but no records of this type
            return False
        except dns.resolver.NoNameservers:
            # No nameservers - might be available
            continue
        except dns.exception.Timeout:
            # Timeout - can't determine, assume unavailable to be safe
            continue
        except Exception:
            continue

    # If we get here with NXDOMAIN for all types, domain is available
    return True


def check_availability_batch(domains: list[dict]) -> list[dict]:
    """
    Check availability for a batch of domains.

    Args:
        domains: List of domain dicts with 'name' field

    Returns:
        List of available domains with 'available' field added
    """
    available = []

    for domain in domains:
        domain_name = domain["name"]
        domain["available"] = is_available(domain_name)

        if domain["available"]:
            available.append(domain)

    return available


if __name__ == "__main__":
    # Test with some known domains
    test_domains = [
        "google.se",      # Should be registered
        "xyznonexistent123456789.se",  # Should be available
    ]

    for domain in test_domains:
        available = is_available(domain)
        status = "AVAILABLE" if available else "REGISTERED"
        print(f"{domain}: {status}")
