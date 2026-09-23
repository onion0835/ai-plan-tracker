# Price observation history

The daily `YYYY-MM-DD.json` files are automated observations from public English-language official pages. They are **not** independently reviewed prices, and the `review_status` field is `unreviewed`. Historical records start when this workflow is enabled; earlier dates are not backfilled.

Each record includes the plan ID, observed USD monthly price, source URL, UTC fetch time, and a short evidence excerpt. A run fails without writing a partial daily file if any source cannot be fetched or parsed. The collector never changes the curated `data/plans.json`; a maintainer must review observations before publishing price changes there.

Prices can vary by country, tax, billing cycle, eligibility, and promotion. This first version monitors Cursor Pro, Claude Pro, GitHub Copilot Student, and Google AI Pro on their public English-language pages.
