import asyncio
import logging
import random

from playwright.async_api import ProxySettings, async_playwright
from playwright_stealth import stealth_async
from playwright_stealth.core import StealthConfig, BrowserType
from playwright_stealth.core._options import StealthOptions


logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

PROXIES: list[ProxySettings] = [
    # TODO: replace with your own proxies
    # {
    #     "server": "...",
    #     "username": "...",
    #     "password": "...",
    # },
]

options = StealthOptions(
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    languages=["de-DE", "de", "en-US", "en"],  # Will derive accept_language header automatically
    hardware_concurrency=8,
    webgl_vendor="Apple",
    webgl_renderer="Apple M1, or similar",
    extra_headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    },
)


async def main():
    proxy: ProxySettings | None = random.choice(PROXIES) if PROXIES else None

    async with async_playwright() as playwright, await playwright.chromium.launch(
        headless=False,
    ) as browser:
        context = await browser.new_context(proxy=proxy)
        page = await context.new_page()
        await stealth_async(
            page,
            config=StealthConfig(
                browser_type=BrowserType.CHROME,
                options=options,
            ),
        )

        await page.goto("https://www.bot.sannysoft.com/")
        await page.wait_for_timeout(30000)


if __name__ == "__main__":
    asyncio.run(main())
