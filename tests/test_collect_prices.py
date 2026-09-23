import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from collect_prices import SOURCES, extract


class ExtractPricesTest(unittest.TestCase):
    def test_official_page_patterns(self):
        snippets = {
            "cursor-pro": ("Individual For the agent-curious $20 / mo. Pro", 20.0),
            "claude-pro": ("Pro For everyday work $17 Per month with annual subscription discount. $20 if billed monthly.", 20.0),
            "github-copilot-student": ("Copilot Student Free An allowance of credits", 0.0),
            "google-ai-pro": ("Google AI Pro (5 TB) $19.99/mo Get started", 19.99),
        }
        for source in SOURCES:
            snippet, expected = snippets[source["plan_id"]]
            with self.subTest(source["plan_id"]):
                actual, _ = extract(source, f"<html><body>{snippet}</body></html>")
                self.assertEqual(expected, actual)

    def test_conflicting_prices_fail_closed(self):
        source = SOURCES[0]
        html = "Individual For the agent-curious $20 / mo. Pro Individual For the agent-curious $30 / mo. Pro"
        with self.assertRaisesRegex(ValueError, "conflicting prices"):
            extract(source, html)

    def test_missing_plan_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "no price match"):
            extract(SOURCES[1], "<html><body>Page unavailable</body></html>")


if __name__ == "__main__":
    unittest.main()
