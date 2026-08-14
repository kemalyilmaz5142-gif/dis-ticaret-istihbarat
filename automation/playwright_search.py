from __future__ import annotations

from dataclasses import dataclass

from playwright.async_api import async_playwright


@dataclass(frozen=True)
class RawSearchResult:
    title: str
    url: str
    snippet: str


async def search_with_browser(query: str, limit: int = 10) -> list[RawSearchResult]:
    results: list[RawSearchResult] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.google.com/search?q={query}", wait_until="domcontentloaded")

        items = await page.locator("a").evaluate_all(
            """links => links
                .map(link => ({ title: link.innerText, url: link.href, snippet: "" }))
                .filter(item => item.title && item.url.startsWith("http"))
                .slice(0, 10)
            """
        )
        await browser.close()

    for item in items[:limit]:
        results.append(
            RawSearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("snippet", ""),
            )
        )

    return results

