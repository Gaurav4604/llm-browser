from googlesearch import search
import trafilatura


def fetch_search_results(query):
    print(query)
    res = search(query, num_results=10, lang="en", ssl_verify=False, advanced=True)
    results = []
    # Extract search results
    for result in res:
        print(result)
        title = result.title
        link = result.url
        results.append({"title": title, "link": link, "snippet": result.description})

    return results


def scrape_webpage_content(url):
    """
    Scrape content from a URL using Trafilatura.
    """
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    return trafilatura.extract(downloaded)
