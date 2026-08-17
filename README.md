# Yahoo! Auctions Japan Scraper

An Apify actor that scrapes product information from Yahoo! Auctions Japan
(`auctions.yahoo.co.jp`) search results. Supports **multi-keyword** searches —
ideal for resale (せどり) research across many product categories in a single run.

## Input

| Field | Type | Description |
|-------|------|-------------|
| `searchKeywords` | array | **One of the two.** List of keywords. Each is searched independently and results are combined into one dataset. |
| `searchKeyword` | string | Single keyword (backward compatible; ignored if `searchKeywords` given). |
| `maxItems` | integer | Maximum total items to collect across all keywords. Defaults to `100`. |
| `maxPages` | integer | Maximum pages to fetch **per keyword**. Defaults to `5`. |
| `proxyConfiguration` | object | Optional Apify proxy configuration. |

At least one keyword (either `searchKeywords` or `searchKeyword`) is required.

## Usage

1. Provide search keywords, e.g. `["Honda CB400", "YAMAHA R3 中古", "SONY α7 IV"]`.
2. Set optional `maxItems` and `maxPages`.
3. Run the actor.
4. The actor returns one dataset where each record is a single auction product,
   with each record tagged by its search keyword via the searched title.

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
- Searches keywords sequentially with a shared client (gentle on rate limits).
- Parses HTML with BeautifulSoup (`lxml` parser).
- Runs on Apify's `apify/actor-python:3.12` Docker image.
