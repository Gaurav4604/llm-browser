from ollama import chat
from search import fetch_search_results_bs4, scrape_webpage_content


def fetch_and_analyze_with_ollama(query):
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

    if not content_snippets:
        return "Unable to retrieve sufficient content from search results."

    # Step 3: Combine content
    print("Preparing data for analysis...")
    combined_content = "\n\n".join(content_snippets)

    # Step 4: Interact with LLaMA using ollama.chat
    print("Analyzing content with LLaMA...")

    # Send system message to set the task
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant. Given the following content from web search results, provide the best possible answer to the user's question. Ensure your response is concise and accurate.",
    }

    # Send user question and combined content
    user_message = {
        "role": "user",
        "content": f"Question: {query}\n\nContent:\n{combined_content}",
    }

    # Call the chat API
    response = chat(
        messages=[system_message, user_message],
        model="llama3.2:1b",
        stream=True,
    )
    for part in response:
        print(part["message"]["content"], end="", flush=True)


if __name__ == "__main__":
    fetch_and_analyze_with_ollama("good examples of semantic web design")
