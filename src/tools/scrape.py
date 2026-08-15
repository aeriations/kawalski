import requests
from bs4 import BeautifulSoup

from ddgs import DDGS

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

def web_search(query: str, max_results: int = 5):
    try:
        results = []

        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=max_results
            )

            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "description": result.get("body", "")
                })

        return {
            "success": True,
            "query": query,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def fetch_webpage(url: str):
    try:
        resp = requests.get(
            url,
            timeout=10,
            headers=headers
        )
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.decompose()

        text = soup.get_text(separator=" ", strip=True)
        text = text[:20000]

        return {
            "success": True,
            "url": url,
            "title": soup.title.string if soup.title else "",
            "content": text
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

