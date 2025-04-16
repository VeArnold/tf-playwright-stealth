from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class StealthOptions:

    user_agent: Optional[str] = None  # Affects: navigator.userAgent, headers, appVersion, etc.
    accept_language: Optional[str] = None  # Will be parsed into navigator.languages and header
    languages: Optional[List[str]] = None
    platform: Optional[str] = None
    vendor: Optional[str] = None
    hardware_concurrency: Optional[int] = None
    device_memory: Optional[int] = None
    viewport: Optional[Tuple[int, int]] = None
    webgl_vendor: Optional[str] = None
    webgl_renderer: Optional[str] = None
    run_on_insecure_origins: Optional[bool] = None
    extra_headers: Dict[str, str] = field(default_factory=dict)

    def derive_navigator_languages(self) -> Optional[List[str]]:
        """Derive navigator.languages from either languages or accept_language."""

        if self.languages:
            return self.languages
        if not self.accept_language:
            return None

        languages_with_quality = self.accept_language.split(",")
        languages = [lang.split(";")[0].strip() for lang in languages_with_quality]
        return languages

    def derive_accept_language_header(self) -> Optional[str]:
        """Derive Accept-Language header from either accept_language or languages."""

        if self.accept_language:
            return self.accept_language
        if not self.languages:
            return None

        if len(self.languages) == 1:
            return self.languages[0]
        else:
            result = self.languages[0]
            for i, lang in enumerate(self.languages[1:], 1):
                quality = max(0.1, 1.0 - (i * 0.1))
                result += f", {lang};q={quality:.1f}"
            return result

    def get_all_headers(self) -> Dict[str, str]:
        """Get all HTTP headers including derived ones."""

        headers = {}
        if self.user_agent:
            headers["User-Agent"] = self.user_agent

        accept_lang = self.derive_accept_language_header()
        if accept_lang:
            headers["Accept-Language"] = accept_lang
        headers.update(self.extra_headers)

        return headers
