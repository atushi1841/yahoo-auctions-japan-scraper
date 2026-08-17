# Yahoo Auctions Japan Scraper — Used Item Price Research & Resale Sourcing

Scrape **Yahoo! Auctions Japan** (`auctions.yahoo.co.jp`) by keyword — or by **multiple keywords at once** — and get structured price / bid / availability data for JDM used items. Built for reseller sourcing, price arbitrage, and market monitoring.

## Output Sample

```json
{
  "itemId": "u1240525087",
  "title": "中古美品 a7iv ボディ ILCE-7M4",
  "currentPrice": 196500,
  "buyNowPrice": null,
  "bidCount": 9,
  "timeLeft": "5時間",
  "postage": "＋送料810円",
  "imageUrl": "https://auc-pctr.c.yimg.jp/...",
  "detailUrl": "https://auctions.yahoo.co.jp/jp/auction/u1240525087",
  "source": "yahoo_auctions",
  "scrapedAt": "2026-08-17T08:50:42Z"
}
```

## What You Can Build With This

- **Resaler sourcing** — keyword lists for whole product categories in one run. `bidCount` flags high-demand items; low `buyNowPrice` marks buyable sourcing candidates.
- **Price arbitrage** — compare Yahoo Auctions buy-now prices against Mercari / Amazon market rates (scrape the other side separately) to spot margin.
- **Price monitoring** — schedule daily/hourly runs to track JDM used-item market movement over time.
- **Market research** — snapshot what Japanese auction sellers are listing and at what price.

## Input

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `searchKeywords` | array | **List of keywords**, each searched independently and combined into one dataset. Use for multi-category research. | — |
| `searchKeyword` | string | Single keyword (backward compatible; ignored if `searchKeywords` is set). | — |
| `maxItems` | integer | Max total items across all keywords. | `100` |
| `maxPages` | integer | Max result pages fetched **per keyword**. | `5` |
| `webhookUrl` | string | Optional. POST a JSON summary to this URL on completion (Slack / Discord / n8n / Zapier). | `""` |
| `proxyConfiguration` | object | Optional Apify proxy configuration. | — |

> At least one keyword (`searchKeywords` or `searchKeyword`) is required.

## Pricing

- Actors charge **$0.00005 per run** (Actor Start) + **$0.002 per dataset item**.
- A typical 100-item single-keyword run costs **~$0.20 total**.
- Every result returns **11 fields** (item id, title, both prices, bid count, time left, postage, image, URL, source, timestamp) — no hidden charges.

## Limitations

- Scrapes Yahoo! Auctions **search results** (public listing pages). Login-gated data and sellers' private information are **not** collected.
- The site is **not** rate-limit-free — keep `maxPages` modest for frequent scheduled runs.
- Prices are **live** at scrape time; fixed-price buy-now listings are returned as-is.

## FAQ

**How fresh is the data?** As fresh as the moment of the run — each record is timestamped with `scrapedAt`.

**Can I run this daily on a schedule?** Yes — use the **Schedule** tab in the Apify console to run it hourly/daily, ideal for price tracking dashboards.

**Can a keyword return zero items?** Yes, if nothing currently matches. The actor reports what it finds; missing keywords simply contribute no rows.

**Is there a related actor for the buy-side marketplace?** This covers auctions side. Pair it with a Mercari / e-commerce scraper if you need cross-market arbitrage.

## Integrations

This actor supports **Apify MCP Connectors** — send run results to Slack, Notion, Supabase, or GitHub without sharing credentials. Look for the **Connectors** tab on the run screen.

You can also receive a **JSON completion summary** at any URL by passing a `webhookUrl` in the input — useful with Slack, Discord, n8n, or Zapier.

### Example: Post Results to Slack (Webhook)

1. Create a Slack webhook: `https://api.slack.com/apps` → Create New App → Incoming Webhooks.
2. Copy the Webhook URL and pass it as `webhookUrl` when running the actor.
3. On completion the actor POSTs `{"event":"actor_completed","itemCount":N,"keywords":[...],"datasetUrl":"..."}` to your Slack channel.

### Example: Scheduled Price Alerts to Slack

1. Run the actor once. On the run screen, open the **Connectors** tab and connect **Slack** (one-time authorization).
2. Go to the **Schedule** tab → create a daily schedule.
3. Set `searchKeywords` to your watchlist.
4. Each scheduled run delivers a fresh price snapshot for your categories to Slack automatically.

### Scheduled Multi-Category Research

1. **Schedule** tab → create a daily/hourly schedule.
2. Set `searchKeywords` (`["SONY α7 IV", "POKEMON カード 未開封", "PS5 中古"]`) for cross-category sourcing research.
3. Combine `maxItems` to cap total collection volume per run.

## Changelog

- **2026-08-17** — Added `searchKeywords` (multi-keyword) support for cross-category resale research; fixed `maxItems` cap across keywords. Added webhook delivery. Optimized Store SEO. Added local resale-research tool & cross-market margin analyzer.
- **2026-08-13** — Initial release.

## Technical Details

- `httpx` async HTTP with 3 retries on 429/5xx.
- BeautifulSoup (`lxml`) parsing.
- Sequential keyword search on a shared client (gentle on rate limits).
- Runs on Apify's `apify/actor-python:3.12` image.

## Local Resale Research & Margin Analysis (self-use)

Two companion scripts under `research/` build the resale pipeline locally (Japan IP):

```bash
# 1. Daily research over a watchlist -> flags high-demand (bid>=5) & sourcing
#    candidates, writes timestamped JSON+CSV to data/research/
python3 -m research.research_locally --config research/watchlist.json
python3 -m research.research_locally --keywords "SONY α7 IV" --keywords "POKEMON カード"

# 2. Cross-market margin: Yahoo sourcing vs Suruga-ya resale prices
#    Tag each Suruga-ya JSON with its keyword so it only matches same-keyword
#    candidates; require matching SKU (ILCE-xxx) to avoid cross-model hits.
python3 -m research.margin_analyzer \
  --yahoo data/research/items_YYYYMMDD.csv \
  --suruga "SONY α7 IV=/path/to/suruga.json" \
  --min-margin-rate 0.20
```

The analyzer is **advisory only** — it never places orders. Real resale is always
manual (fees: Yahoo 8.8% + shipping, Mercari 10%; returns/fakes risk apply).

