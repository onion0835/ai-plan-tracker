# AI Plan Tracker

Open, source-linked pricing and promotion data for AI subscriptions and coding plans, maintained by [AIPlanWise](https://aiplanwise.com/).

Every active record includes an official source, a verification date, and an evidence level. Expired offers are archived instead of silently removed.

## Files

- [`data/plans.json`](data/plans.json) — current machine-readable dataset
- [`data/plans.csv`](data/plans.csv) — spreadsheet-friendly export
- [`data/archive.json`](data/archive.json) — expired and discontinued offers
- [`data/changes.json`](data/changes.json) — structured change history
- [`data/price-history/`](data/price-history/) — automated daily observations from official pages (unreviewed)
- [`schema/plans.schema.json`](schema/plans.schema.json) — JSON Schema
- [`CHANGELOG.md`](CHANGELOG.md) — human-readable release history

## Evidence levels

- `official`: published directly by the provider
- `calculated`: derived by AIPlanWise using a documented method
- `reported`: reported by a third party and not yet fully confirmed on an official pricing page

Official facts and calculated estimates are stored separately. A calculated value must never be interpreted as a provider-published limit.

## Automated price observations

A [daily GitHub Actions workflow](.github/workflows/collect-prices.yml) collects public USD monthly prices for Cursor Pro, Claude Pro, GitHub Copilot Student, and Google AI Pro. You can also run it from the Actions tab with **Run workflow**. The collector refuses ambiguous matches and never changes the curated `data/plans.json` automatically. See the [history notes](data/price-history/README.md) for limitations and fields.

## Citation

Recommended citation:

> AI coding plan pricing data from AIPlanWise, verified September 22, 2026. https://aiplanwise.com/data/

Markdown:

```md
Source: [AIPlanWise AI Plan Tracker](https://aiplanwise.com/data/)
```

## License

The original dataset structure and AIPlanWise-authored annotations are available under [CC BY 4.0](LICENSE.md). Provider names, trademarks, and source material remain the property of their respective owners. Always verify a price on the linked provider page before purchasing.

