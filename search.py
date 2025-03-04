from duckduckgo_search import DDGS
import trafilatura
import requests


def search_duckduckgo(query, max_results=5):
    # Use a context manager to properly instantiate DDGS.
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        return results


def scrape_webpage_content(url):
    """
    Scrape content from a URL using Trafilatura with a 10-second timeout.
    """
    try:
        # Use requests to fetch the URL with a timeout
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"link \t{url}\t failed with status code {response.status_code}")
            return None

        # Feed the response content to Trafilatura
        downloaded = trafilatura.extract(
            response.text,
            favor_precision=True,
            include_links=False,
            include_tables=False,
            deduplicate=True,
        )
        if not downloaded:
            return None
        print("link \t" + url + "\t scraped")
        return downloaded
    except requests.exceptions.Timeout:
        print("link \t" + url + "\t timeout occurred")
        return None
    except requests.exceptions.RequestException as e:
        print(f"link \t{url}\t error: {e}")
        return None


if __name__ == "__main__":
    sites = search_duckduckgo("who are 21 pilots?")
    print(sites)
    for site in sites:
        print(scrape_webpage_content(site["href"]))
