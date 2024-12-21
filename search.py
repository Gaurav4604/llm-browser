from googlesearch import search
import trafilatura
import requests


def fetch_search_results(query):
    res = search(query, num_results=10, lang="en", ssl_verify=False, advanced=True)
    results = []
    # Extract search results
    for result in res:
        title = result.title
        link = result.url
        results.append({"title": title, "link": link, "snippet": result.description})

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
        downloaded = trafilatura.extract(response.text)
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
    search_links = [
        "https://www.accuweather.com/en/au/hahndorf/25247/hourly-weather-forecast/25247",
        "https://www.eldersweather.com.au/local-forecast/sa/hahndorf",
        "https://www.weatherbug.com/weather-forecast/now/hahndorf-south-australia-as",
    ]
    for link in search_links:
        scraped_data = scrape_webpage_content(link)
        if scraped_data:
            print(scraped_data)
