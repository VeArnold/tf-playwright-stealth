# -*- coding: utf-8 -*-
from playwright.async_api import Page as AsyncPage
from playwright.sync_api import Page as SyncPage
from playwright_stealth.core import StealthConfig
from playwright_stealth.properties import Properties, BrowserType


def combine_scripts(properties: Properties, config: StealthConfig):
    """Combines the scripts for the page based on the properties and config."""

    scripts = []

    for script in (config or StealthConfig()).enabled_scripts(properties):
        scripts.append(script)
    return "\n".join(scripts)


def generate_stealth_headers_sync(
    properties: Properties,
    page: SyncPage,
    config: StealthConfig = None,
):
    """Generates the stealth headers for the page."""
    base_headers = properties.header.as_dict()

    if config and config.options and config.options.extra_headers:
        base_headers.update(config.options.extra_headers)

    page.set_extra_http_headers(base_headers)


async def generate_stealth_headers_async(
    properties: Properties,
    page: AsyncPage,
    config: StealthConfig = None,
):
    """Generates the stealth headers for the page."""
    base_headers = properties.header.as_dict()

    if config and config.options and config.options.extra_headers:
        base_headers.update(config.options.extra_headers)

    await page.set_extra_http_headers(base_headers)


def stealth_sync(page: SyncPage, config: StealthConfig = None):
    """teaches synchronous playwright Page to be stealthy like a ninja!"""
    properties = Properties(browser_type=config.browser_type if config else BrowserType.CHROME)
    combined_script = combine_scripts(properties, config)
    generate_stealth_headers_sync(properties, page, config)

    page.add_init_script(combined_script)


async def stealth_async(page: AsyncPage, config: StealthConfig = None):
    """teaches asynchronous playwright Page to be stealthy like a ninja!"""
    properties = Properties(browser_type=config.browser_type if config else BrowserType.CHROME)
    combined_script = combine_scripts(properties, config)
    await generate_stealth_headers_async(properties, page, config)

    await page.add_init_script(combined_script)
