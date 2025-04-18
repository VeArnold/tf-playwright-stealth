import json
from dataclasses import dataclass
from typing import Dict
import os
from playwright_stealth.core._options import StealthOptions
from playwright_stealth.properties import Properties, BrowserType


def from_file(name) -> str:
    """Read script from ./js directory"""
    filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), "js", name)
    with open(filename, encoding="utf-8") as f:
        return f.read()


SCRIPTS: Dict[str, str] = {
    "chrome_csi": from_file("chrome.csi.js"),
    "chrome_app": from_file("chrome.app.js"),
    "chrome_runtime": from_file("chrome.runtime.js"),
    "chrome_load_times": from_file("chrome.load.times.js"),
    "generate_magic_arrays": from_file("generate.magic.arrays.js"),
    "iframe_content_window": from_file("iframe.contentWindow.js"),
    "media_codecs": from_file("media.codecs.js"),
    "navigator_vendor": from_file("navigator.vendor.js"),
    "navigator_plugins": from_file("navigator.plugins.js"),
    "navigator_permissions": from_file("navigator.permissions.js"),
    "navigator_languages": from_file("navigator.languages.js"),
    "navigator_user_agent": from_file("navigator.userAgent.js"),
    "navigator_hardware_concurrency": from_file("navigator.hardwareConcurrency.js"),
    "outerdimensions": from_file("window.outerdimensions.js"),
    "utils": from_file("utils.js"),
    "webdriver": from_file("navigator.webdriver.js"),
    "webgl_vendor": from_file("webgl.vendor.js"),
}


@dataclass
class StealthConfig:
    """
    Playwright stealth configuration that applies stealth strategies to playwright page objects.
    The stealth strategies are contained in ./js package and are basic javascript scripts that are executed
    on every page.goto() called.
    Note:
        All init scripts are combined by playwright into one script and then executed this means
        the scripts should not have conflicting constants/variables etc. !
        This also means scripts can be extended by overriding enabled_scripts generator:
        ```
        @property
        def enabled_scripts():
            yield 'console.log("first script")'
            yield from super().enabled_scripts()
            yield 'console.log("last script")'
        ```
    """

    # Script toggles
    webdriver: bool = True
    webgl_vendor: bool = True
    chrome_app: bool = True
    chrome_csi: bool = True
    chrome_load_times: bool = True
    chrome_runtime: bool = True
    iframe_content_window: bool = True
    media_codecs: bool = True
    navigator_languages: bool = True
    navigator_permissions: bool = True
    navigator_plugins: bool = True
    navigator_user_agent: bool = True
    navigator_vendor: bool = True
    outerdimensions: bool = True

    browser_type: BrowserType = BrowserType.CHROME
    options: StealthOptions = None

    def _apply_options(self, properties: Properties):
        """Apply custom options to the properties, while attempting to preserve consistency."""

        opts = self.options
        if opts.user_agent:
            self._apply_user_agent_properties(properties, opts.user_agent)

        self._apply_language_settings(properties)
        if opts.platform and not opts.user_agent:
            properties.navigator.platform = opts.platform

        if opts.vendor and not opts.user_agent:
            properties.navigator.vendor = opts.vendor

        self._apply_hardware_specs(properties)
        self._apply_webgl_settings(properties)

        if opts.run_on_insecure_origins is not None:
            properties.runOnInsecureOrigins = opts.run_on_insecure_origins

    def _apply_user_agent_properties(self, properties: Properties, user_agent: str):
        """Apply user agent and related derivative properties."""

        properties.navigator.userAgent = user_agent
        properties.header.user_agent = user_agent
        properties.navigator.appVersion = properties.navigator._generate_app_version(user_agent)
        properties.navigator.platform = (
            self.options.platform or properties.navigator._generate_platform(user_agent)
        )
        properties.navigator.vendor = self.options.vendor or properties.navigator._generate_vendor(
            user_agent
        )

    def _apply_language_settings(self, properties: Properties):
        """Apply language-related settings."""

        if languages := self.options.derive_navigator_languages():
            properties.navigator.languages = languages

        if accept_lang := self.options.derive_accept_language_header():
            properties.header.accept_language = accept_lang

    def _apply_hardware_specs(self, properties: Properties):
        """Apply hardware specification settings."""

        if self.options.hardware_concurrency is not None:
            properties.navigator.hardwareConcurrency = self.options.hardware_concurrency

        if self.options.device_memory is not None:
            properties.navigator.deviceMemory = self.options.device_memory

    def _apply_webgl_settings(self, properties: Properties):
        """Apply WebGL-related settings."""

        if self.options.webgl_vendor:
            properties.webgl.vendor = self.options.webgl_vendor

        if self.options.webgl_renderer:
            properties.webgl.renderer = self.options.webgl_renderer

    def enabled_scripts(self, properties: Properties):
        """Generate the scripts to be executed."""

        if self.options:
            self._apply_options(properties)

        opts = json.dumps(properties.as_dict())

        # defined options constant
        yield f"const opts = {opts}"
        # init utils and generate_magic_arrays helper
        yield SCRIPTS["utils"]
        yield SCRIPTS["generate_magic_arrays"]

        if self.chrome_app:
            yield SCRIPTS["chrome_app"]
        if self.chrome_csi:
            yield SCRIPTS["chrome_csi"]
        if self.chrome_load_times:
            yield SCRIPTS["chrome_load_times"]
        if self.chrome_runtime:
            yield SCRIPTS["chrome_runtime"]
        if self.iframe_content_window:
            yield SCRIPTS["iframe_content_window"]
        if self.media_codecs:
            yield SCRIPTS["media_codecs"]
        if self.navigator_languages:
            yield SCRIPTS["navigator_languages"]
        if self.navigator_permissions:
            yield SCRIPTS["navigator_permissions"]
        if self.navigator_plugins:
            yield SCRIPTS["navigator_plugins"]
        if self.navigator_user_agent:
            yield SCRIPTS["navigator_user_agent"]
        if self.navigator_vendor:
            yield SCRIPTS["navigator_vendor"]
        if self.webdriver:
            yield SCRIPTS["webdriver"]
        if self.outerdimensions:
            yield SCRIPTS["outerdimensions"]
        if self.webgl_vendor:
            yield SCRIPTS["webgl_vendor"]
