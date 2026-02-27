"""Tests for the SE/NU Domain Snapback Scanner."""

import json
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import main
from src.fetcher import fetch_drop_list, fetch_all_dropping_on_date
from src.reporter import generate_report, generate_summary
from app import app


class TestFetcherErrorHandling(unittest.TestCase):
    """Test that the fetcher handles network errors gracefully."""

    @patch('src.fetcher.requests.get')
    def test_fetch_drop_list_connection_error(self, mock_get):
        """fetch_drop_list returns [] on ConnectionError."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("No network")
        result = fetch_drop_list("se")
        self.assertEqual(result, [])

    @patch('src.fetcher.requests.get')
    def test_fetch_drop_list_timeout(self, mock_get):
        """fetch_drop_list returns [] on Timeout."""
        import requests
        mock_get.side_effect = requests.exceptions.Timeout("Timed out")
        result = fetch_drop_list("nu")
        self.assertEqual(result, [])

    @patch('src.fetcher.requests.get')
    def test_fetch_drop_list_success(self, mock_get):
        """fetch_drop_list returns data on success."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": [{"name": "test.se", "release_at": "2026-01-11"}]}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = fetch_drop_list("se")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "test.se")

    @patch('src.fetcher.requests.get')
    def test_fetch_all_dropping_on_date_with_errors(self, mock_get):
        """fetch_all_dropping_on_date returns [] when both TLDs fail."""
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError("No network")
        result = fetch_all_dropping_on_date("2026-01-11")
        self.assertEqual(result, [])


class TestMainFunction(unittest.TestCase):
    """Test the main scanner function."""

    @patch('src.main.fetch_all_dropping_on_date')
    def test_main_signature_no_unused_params(self, mock_fetch):
        """main() only accepts target_date and dry_run."""
        import inspect
        sig = inspect.signature(main)
        param_names = list(sig.parameters.keys())
        self.assertEqual(param_names, ['target_date', 'dry_run'])

    @patch('src.main.fetch_all_dropping_on_date')
    def test_main_tomorrow_label_default(self, mock_fetch):
        """main() prints '(tomorrow)' when using default (tomorrow) date."""
        mock_fetch.return_value = []
        captured = StringIO()
        with patch('sys.stdout', captured):
            main(dry_run=True)
        output = captured.getvalue()
        self.assertIn("(tomorrow)", output)

    @patch('src.main.fetch_all_dropping_on_date')
    def test_main_no_tomorrow_label_custom_date(self, mock_fetch):
        """main() doesn't print '(tomorrow)' for a custom non-tomorrow date."""
        mock_fetch.return_value = []
        captured = StringIO()
        with patch('sys.stdout', captured):
            main(target_date="2020-01-01", dry_run=True)
        output = captured.getvalue()
        self.assertNotIn("(tomorrow)", output)
        self.assertIn("2020-01-01", output)

    @patch('src.main.check_index_batch')
    @patch('src.main.check_availability_batch')
    @patch('src.main.fetch_all_dropping_on_date')
    def test_main_sets_available_none(self, mock_fetch, mock_avail, mock_index):
        """main() initialises available=None before running checks."""
        domain = {"name": "test.se", "tld": "se", "release_at": "2026-01-11"}
        mock_fetch.return_value = [domain]
        # Capture the domains list *before* availability check overwrites it
        def capture_then_return(domains):
            self.assertIsNone(domains[0]["available"])
            return domains
        mock_avail.side_effect = capture_then_return
        mock_index.side_effect = lambda domains: domains
        captured = StringIO()
        with patch('sys.stdout', captured):
            main(target_date="2026-01-11", dry_run=True)


class TestReporter(unittest.TestCase):
    """Test report generation."""

    def test_generate_report_creates_files(self):
        """generate_report creates CSV and JSON files."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            domains = [
                {"name": "test.se", "tld": "se", "release_at": "2026-01-11",
                 "available": None, "indexed": False, "estimated_pages": None,
                 "source": ""}
            ]
            csv_path, json_path = generate_report(domains, Path(tmpdir), "test")
            self.assertTrue(csv_path.exists())
            self.assertTrue(json_path.exists())

            with open(json_path) as f:
                data = json.load(f)
            self.assertEqual(data["total_domains"], 1)
            self.assertEqual(data["domains"][0]["domain"], "test.se")


class TestFlaskApp(unittest.TestCase):
    """Test Flask web application."""

    def setUp(self):
        self.client = app.test_client()

    def test_home_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

    def test_report_page_exists(self):
        resp = self.client.get('/report/2026-01-11')
        self.assertEqual(resp.status_code, 200)

    def test_report_page_not_found(self):
        resp = self.client.get('/report/9999-99-99')
        self.assertEqual(resp.status_code, 404)

    def test_api_reports(self):
        resp = self.client.get('/api/reports')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)

    def test_api_report(self):
        resp = self.client.get('/api/report/2026-01-11')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn('domains', data)
        self.assertIn('total_domains', data)

    def test_api_csv(self):
        resp = self.client.get('/api/report/2026-01-11/csv')
        self.assertEqual(resp.status_code, 200)


class TestBuildStaticSite(unittest.TestCase):
    """Test static site builder consistency."""

    def test_generated_html_has_6_column_table(self):
        """Static site should generate 6-column tables matching Flask templates."""
        from build_static_site import generate_domains_table
        domains = [
            {"domain": "test.se", "tld": "se", "release_date": "2026-01-11",
             "available": True, "indexed": True, "estimated_pages": 50},
        ]
        html = generate_domains_table(domains)
        self.assertIn("Domain", html)
        self.assertIn("TLD", html)
        self.assertIn("Release Date", html)
        self.assertIn("Available", html)
        self.assertIn("Indexed", html)
        self.assertIn("Est. Pages", html)

    def test_generated_row_has_availability_and_index(self):
        """Static site rows should render available/indexed fields."""
        from build_static_site import generate_domain_row
        domain = {"domain": "test.se", "tld": "se", "release_date": "2026-01-11",
                  "available": True, "indexed": True, "estimated_pages": 42}
        html = generate_domain_row(domain)
        self.assertIn("4caf50", html)   # green check for indexed
        self.assertIn("42", html)       # estimated pages shown

    def test_filter_bar_no_indexed_chip(self):
        """Static site filter bar should not have Indexed chip."""
        from build_static_site import generate_filter_bar
        domains = [
            {"domain": "test.se", "tld": "se"},
            {"domain": "test.nu", "tld": "nu"},
        ]
        html = generate_filter_bar(domains)
        self.assertNotIn("Indexed", html)
        self.assertIn("All", html)
        self.assertIn(".se", html)
        self.assertIn(".nu", html)


if __name__ == "__main__":
    unittest.main()
