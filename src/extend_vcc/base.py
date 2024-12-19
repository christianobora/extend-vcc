from typing import Dict, List


class ExtendPlatformBrand:
    """Configuration for the Extend platform"""

    def __init__(self, api_base_url: str, headers: Dict[str, str]):
        self.api_base_url = api_base_url
        self.headers = headers


DEFAULT_BRAND = ExtendPlatformBrand(
    api_base_url="https://v.paywithextend.com",
    headers={
        "accept-language": "en-US,en;q=0.7",
        "cache-control": "no-cache",
        "dnt": "1",
        "origin": "https://app.paywithextend.com",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://app.paywithextend.com/",
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "x-extend-app-id": "app.paywithextend.com",
        "x-extend-brand": "br_2F0trP1UmE59x1ZkNIAqsg",
        "x-extend-platform": "web",
        "x-extend-platform-version": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    },
)


class APIError(Exception):
    """API error with details"""

    def __init__(self, message: str, details: List[Dict[str, str]] = None):
        self.message = message
        self.details = details or []
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        message = f"extend: {self.message}"
        for detail in self.details:
            message = (
                f"{message} ({detail.get('field', '')}: {detail.get('error', '')})"
            )
        return message
