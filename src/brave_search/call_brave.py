import os
import httpx
from dotenv import load_dotenv

load_dotenv()

class BraveQuery:
    url = "https://api.search.brave.com/res/v1/web/search"
    country = "US"
    search_lang = "en"
    count = 20

    def __init__(self):
        self.api_key = os.getenv("API_KEY_BRAVE", "")
        print(f"k = {self.api_key}") # borrar

    @property
    def headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "x-subscription-token": self.api_key,
        }

    def build_params(self, query: str) -> dict:
        return {
            "q": query,
            "country": self.country,
            "search_lang": self.search_lang,
            "count": self.count,
        }


def search_brave(query: str) -> dict:
    """Search the web using Brave Search API.

    Args:
        query: The search query string.
        api_key: Brave API key. Falls back to API_KEY_BRAVE env var.

    Returns:
        The JSON response from Brave Search.
    """
    bq = BraveQuery()
    response = httpx.get(bq.url, headers=bq.headers, params=bq.build_params(query))
    if not response.is_success:
        raise Exception(f"Brave API error {response.status_code}: {response.text}")
    return response.json()

if __name__ == "__main__":
    q = "Busca información de la empresa coco-cola de méxico"
    print(search_brave(q))
    