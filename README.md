# Yahoo! Auctions Japan Scraper

An Apify actor that scrapes product information from Yahoo! Auctions Japan
(`auctions.yahoo.co.jp`) search results.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `searchKeyword` | string | **Required.** The keyword to search for. |
| `maxItems` | integer | Maximum number of items to collect. Defaults to `100`. |
| `maxPages` | integer | Maximum number of search result pages to fetch. Defaults to `5`. |
| `proxyConfiguration` | object | Optional Apify proxy configuration. |

## Usage

1. Provide a search keyword (for example `Honda CB400`).
2. Set optional `maxItems` and `maxPages`.
3. Run the actor.
4. The actor returns a dataset where each record corresponds to one auction product.

## Output fields

| Field | Description |
|-------|-------------|
| `itemId` | Yahoo! Auction product ID |
| `title` | Product title |
| `currentPrice` | Current price in yen (integer) |
| `buyNowPrice` | Buy‑Now price in yen (integer) or `null` |
| `bidCount` | Number of bids |
| `timeLeft` | Remaining time as displayed on the site |
| `postage` | Shipping/postage information |
| `imageUrl` | Main product image URL or `null` |
| `detailUrl` | Full URL to the product detail page |
| `source` | Always `"yahoo_auctions"` |
| `scrapedAt` | ISO timestamp when the record was collected |

## Technical details

- Uses `httpx` for asynchronous HTTP requests with three retries on 429/5xx responses.
- Parses HTML with BeautifulSoup (`lxml` parser).
- Runs on Apify's `apify/actor-python:3.12` Docker image.
