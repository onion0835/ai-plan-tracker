"""Collect US-dollar plan prices from public, official pages.

This creates dated observations only. It never changes the curated plans.json.
When a page changes unexpectedly, the run fails instead of recording a guess.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "data" / "price-history"
SOURCES = (
    {
        "plan_id": "cursor-pro",
        "url": "https://cursor.com/pricing",
        "pattern": r"Individual\s+For the agent-curious\s+\$([\d,.]+)\s*/\s*mo\.\s+Pro\b",
    },
    {
        "plan_id": "claude-pro",
        "url": "https://claude.com/pricing",
        "pattern": r"\bPro\s+For everyday work\b.{0,240}?\$([\d,.]+)\s+if billed monthly\b",
    },
    {
        "plan_id": "github-copilot-student",
        "url": "https://docs.github.com/en/copilot/get-started/plans",
        "pattern": r"\bCopilot Student\s+Free\b",
        "free": True,
    },
    {
        "plan_id": "google-ai-pro",
        "url": "https://one.google.com/about/plans",
        "pattern": r"\bGoogle AI Pro\s+\([^)]{1,60}\)\s+\$([\d,.]+)\s*/\s*mo\b",
    },
)


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def extract(plan: dict, html: str) -> tuple[float, str]:
    parser = VisibleText()
    parser.feed(html)
    visible = re.sub(r"\s+", " ", " ".join(parser.parts))
    matches = list(re.finditer(plan["pattern"], visible, re.IGNORECASE))
    if not matches:
        raise ValueError(f"{plan['plan_id']}: no price match")
    prices = {Decimal("0") if plan.get("free") else Decimal(m.group(1).replace(",", "")) for m in matches}
    if len(prices) != 1:
        raise ValueError(f"{plan['plan_id']}: conflicting prices found: {sorted(prices)}")
    match = matches[0]
    price = prices.pop()
    if price < 0 or price > 10000 or (price == 0 and not plan.get("free")):
        raise ValueError(f"{plan['plan_id']}: implausible price {price}")
    excerpt = visible[max(0, match.start() - 45) : min(len(visible), match.end() + 45)]
    return float(price), excerpt


def collect(plan: dict, fetched_at: str) -> dict:
    request = Request(plan["url"], headers={"User-Agent": "Mozilla/5.0 (compatible; AIPlanWisePriceTracker/1.0; +https://aiplanwise.com/data/)"})
    with urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(f"{plan['plan_id']}: HTTP {response.status}")
        final_url = response.url
        if final_url.split("/")[2] != plan["url"].split("/")[2]:
            raise ValueError(f"{plan['plan_id']}: unexpected redirect to {final_url}")
        raw = response.read(3_000_001)
        if len(raw) > 3_000_000:
            raise ValueError(f"{plan['plan_id']}: page too large")
    price, excerpt = extract(plan, raw.decode("utf-8", "replace"))
    return {
        "plan_id": plan["plan_id"],
        "monthly_price": price,
        "currency": "USD",
        "market": "US / public English page",
        "source_url": final_url,
        "fetched_at": fetched_at,
        "evidence_excerpt": excerpt,
        "review_status": "unreviewed",
    }


def main() -> int:
    cli = argparse.ArgumentParser()
    cli.add_argument("--dry-run", action="store_true", help="Fetch and validate without writing files")
    args = cli.parse_args()
    now = datetime.now(timezone.utc)
    fetched_at = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    observations = []
    errors = []
    for plan in SOURCES:
        try:
            observation = collect(plan, fetched_at)
            observations.append(observation)
            print(f"{plan['plan_id']}: USD {observation['monthly_price']}/month")
        except Exception as exc:
            errors.append(str(exc))
            print(f"ERROR {plan['plan_id']}: {exc}", file=sys.stderr)
    if errors:
        print("No observations saved: all sources must parse successfully.", file=sys.stderr)
        return 1
    if args.dry_run:
        return 0
    HISTORY.mkdir(parents=True, exist_ok=True)
    destination = HISTORY / f"{now.date().isoformat()}.json"
    payload = {"observed_on": now.date().isoformat(), "observations": observations}
    destination.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {destination.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
