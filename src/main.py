import asyncio
import json
import sys
from datetime import datetime, timezone
from urllib.parse import quote

import httpx

try:
    from apify import Actor
except Exception:
    Actor = None

from .yahoo_auctions import fetch_page, list_page, parse_page


async def _process(user_input: dict) -> None:
    use_actor = Actor is not None and Actor.is_at_home()

    search_keyword = (user_input.get("searchKeyword") or "").strip()
    if not search_keyword:
        if use_actor:
            await Actor.fail(status_message="Missing searchKeyword in actor input")
        else:
            print("Missing searchKeyword in actor input")
        return

    max_items = int(user_input.get("maxItems", 100))
    max_pages = int(user_input.get("maxPages", 5))
    proxy_config = user_input.get("proxyConfiguration") or {}

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ja,en;q=0.9",
    }

    proxy_url = None
    if proxy_config and use_actor:
        try:
            proxy_url = await Actor.create_proxy_url(proxy_config)
        except Exception as exc:
            Actor.log.warning(f"Could not create proxy URL: {exc}")

    client_kwargs = {
        "headers": headers,
        "timeout": 30,
        "follow_redirects": True,
    }
    if proxy_url:
        client_kwargs["proxy"] = proxy_url

    collected_items = []

    base_url = (
        "https://auctions.yahoo.co.jp/search/search?"
        f"p={quote(search_keyword)}"
        "&auccat=&tab_ex=commerce"
    )

    async with httpx.AsyncClient(**client_kwargs) as client:
        for page in range(1, max_pages + 1):
            url = list_page(base_url, page)
            if use_actor:
                Actor.log.info(f"Fetching page {page}: {url}")
            else:
                print(f"Fetching page {page}: {url}")

            try:
                html = await fetch_page(client, url)
            except Exception as exc:
                if use_actor:
                    Actor.log.warning(f"Failed to fetch page {page}: {exc}")
                else:
                    print(f"WARNING: Failed to fetch page {page}: {exc}")
                break

            items = parse_page(html)
            if use_actor:
                Actor.log.info(f"Found {len(items)} items on page {page}")
            else:
                print(f"Found {len(items)} items on page {page}")

            for item in items:
                item["source"] = "yahoo_auctions"
                item["scrapedAt"] = datetime.now(timezone.utc).isoformat()
                collected_items.append(item)
                if use_actor:
                    await Actor.push_data(item)

                if len(collected_items) >= max_items:
                    break

            if len(collected_items) >= max_items or not items:
                break

    if use_actor:
        Actor.log.info(f"Collected {len(collected_items)} items")
    else:
        print(f"Collected {len(collected_items)} items")

    if not use_actor:
        print(json.dumps(collected_items, ensure_ascii=False, indent=2))


async def main() -> None:
    if Actor is None or not Actor.is_at_home():
        if not sys.stdin.isatty():
            try:
                user_input = json.load(sys.stdin)
            except Exception:
                user_input = {}
        else:
            user_input = {}
        await _process(user_input)
    else:
        async with Actor:
            user_input = await Actor.get_input() or {}
            await _process(user_input)


if __name__ == "__main__":
    asyncio.run(main())
