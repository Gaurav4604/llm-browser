import requests
import trafilatura
from bs4 import BeautifulSoup


def fetch_search_results_bs4(query, num_results=10):
    """
    Fetch search results using Google or another search engine.
    """
    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        raise Exception("Failed to fetch search results")

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select(".tF2Cxc")[:num_results]:  # Google result block
        title = result.select_one("h3").text
        link = result.select_one(".yuRUbf a")["href"]
        snippet = (
            result.select_one(".VwiC3b").text if result.select_one(".VwiC3b") else ""
        )
        results.append({"title": title, "link": link, "snippet": snippet})

    return results


def scrape_webpage_content(url):
    """
    Scrape content from a URL using Trafilatura.
    """
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    return trafilatura.extract(downloaded)


def fetch_and_analyze_with_llama(llama, query):
    # Step 1: Fetch search results
    print("Fetching search results...")
    search_results = fetch_search_results_bs4(query)

    # Step 2: Scrape content from top results
    print("Scraping content from search results...")
    content_snippets = []
    for result in search_results:
        content = scrape_webpage_content(result["link"])
        if content:
            content_snippets.append(content)

    # Step 3: Analyze content using LLaMA
    print("Analyzing content with LLaMA...")
    combined_content = "\n\n".join(content_snippets)
    prompt = f"Using the following content, answer the question:\n{query}\n\n{combined_content}"
    best_answer = llama.ask(prompt).strip()

    return best_answer


# print(fetch_search_results_bs4("what is a cat?"))
