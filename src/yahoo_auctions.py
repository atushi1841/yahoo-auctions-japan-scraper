import re
import asyncio
from urllib.parse import urljoin, urlsplit, urlunsplit, parse_qsl, urlencode

import httpx
from bs4 import BeautifulSoup


async def fetch_page(client: httpx.AsyncClient, url: str) -> str:
    """Fetch a page with retries on 429/5xx responses and enforce UTF-8 encoding."""
    max_retries = 3
    backoff_base = 1

    for attempt in range(max_retries):
        try:
            response = await client.get(url)
            if response.status_code in (429,) or response.status_code >= 500:
                if attempt == max_retries - 1:
                    response.raise_for_status()
                await asyncio.sleep(backoff_base * (2 ** attempt))
                continue
            response.encoding = "utf-8"
            return response.text
        except (httpx.HTTPError, httpx.TransportError) as exc:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(backoff_base * (2 ** attempt))


def _to_int(value: str | None) -> int | None:
    """Convert a price/bid string like '693,000円' to an int, or None."""
    if value is None:
        return None
    cleaned = re.sub(r"[^\d]", "", value)
    return int(cleaned) if cleaned else None


def list_page(base: str, page: int) -> str:
    """Return the search URL with the given page number (if page > 1)."""
    if page <= 1:
        return base

    parts = urlsplit(base)
    query_pairs = [(k, v) for k, v in parse_qsl(parts.query) if k != "page"]
    query_pairs.append(("page", str(page)))
    new_query = urlencode(query_pairs)
    return urlunsplit(parts._replace(query=new_query))


def parse_page(html: str) -> list[dict]:
    """Parse a Yahoo! Auctions search result page into item records."""
    soup = BeautifulSoup(html, "lxml")
    items = []

    for card in soup.select("li.Product"):
        title_elem = card.select_one(".Product__titleLink")
        if title_elem is None:
            continue

        title = title_elem.get_text(strip=True)
        href = title_elem.get("href")

        detail_url = None
        if href:
            if href.startswith(("http://", "https://")):
                detail_url = href
            else:
                detail_url = urljoin("https://auctions.yahoo.co.jp", href)

        item_id = None
        if detail_url:
            match = re.search(r"/auction/([^/?]+)", detail_url)
            if match:
                item_id = match.group(1)

        # Prices
        price_values = card.select(".Product__priceValue")
        current_price = None
        buy_now_price = None
        if price_values:
            current_price = _to_int(price_values[0].get_text(strip=True))
            if len(price_values) > 1:
                buy_now_price = _to_int(price_values[1].get_text(strip=True))

        # The current price is often marked with .u-textRed
        red_price = card.select_one(".Product__priceValue.u-textRed")
        if red_price is not None:
            current_price = _to_int(red_price.get_text(strip=True))

        # Bid count
        bid_elem = card.select_one(".Product__bid")
        bid_count = 0
        if bid_elem is not None:
            bid_digits = re.findall(r"\d+", bid_elem.get_text(strip=True))
            if bid_digits:
                bid_count = int(bid_digits[0])

        # Time left
        time_elem = card.select_one(".Product__timeWrap")
        time_left = None
        if time_elem is not None:
            time_left = time_elem.get_text(strip=True)

        # Postage
        postage_elem = card.select_one(".Product__postage")
        postage = None
        if postage_elem is not None:
            postage = postage_elem.get_text(strip=True)

        # Image
        img = card.select_one("img")
        image_url = None
        if img is not None:
            image_url = img.get("src")
            if image_url and image_url.startswith("//"):
                image_url = "https:" + image_url

        items.append(
            {
                "itemId": item_id,
                "title": title,
                "currentPrice": current_price,
                "buyNowPrice": buy_now_price,
                "bidCount": bid_count,
                "timeLeft": time_left,
                "postage": postage,
                "imageUrl": image_url,
                "detailUrl": detail_url,
            }
        )

    return items
