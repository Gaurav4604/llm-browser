from ollama import chat
from search import fetch_search_results, scrape_webpage_content
from queries import generate_search_query


prompt_summarize_mono = """
You are a LLM that can summarize text.
You are given a piece of text and your task
is to summarize it, retain the most important
points present in the query and provide a concise summary.
Retain keywords present in the text
"""
prompt_compare_merge_summary = """
You are a LLM that can summarize text.
You are given two pieces of text and your task
is to compare them, retain the most important
points present in the both documents, merge them
and provide a concise summary.
Retain keywords present in the texts
"""


def summarize_with_llama(prev, data):
    print("Summarizing with Llama...")
    response = chat(
        messages=[
            {
                "role": "system",
                "content": prompt_summarize_mono,
            },
            {"role": "user", "content": data},
        ],
        model="llama3.2:1b",
        options={"num_ctx": 16384},
    )
    response = chat(
        messages=[
            {
                "role": "system",
                "content": prompt_compare_merge_summary,
            },
            {
                "role": "user",
                "content": """summary 1: {},\n\n summary 2: {}""".format(
                    prev, response["message"]["content"]
                ),
            },
        ],
        model="llama3.2:1b",
        options={"num_ctx": 16384},
    )
    return response["message"]["content"]


def fetch_and_analyze_with_ollama(query):
    # Step 1: Fetch search results
    print("Fetching search results...")
    search_results = fetch_search_results(generate_search_query(query))

    # Step 2: Scrape content from top results
    print("Scraping content from search results...")
    print(search_results)
    content_snippets = []
    for result in search_results:
        content = scrape_webpage_content(result["link"])
        if content:
            content_snippets.append(content)

    if not content_snippets:
        return "Unable to retrieve sufficient content from search results."

    # Step 3: Combine content
    print("Preparing data for analysis...")
    # combined_content = "\n\n".join(content_snippets)

    # # Step 4: Interact with LLaMA using ollama.chat
    # print("Analyzing content with LLaMA...")
    summary = ""
    for snippet in content_snippets:
        summary = summarize_with_llama(summary, snippet)

    # Send system message to set the task
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant. Given the following content from web search results, provide the best possible answer to the user's question. Ensure your response is concise and accurate.",
    }

    # Send user question and combined content
    user_message = {
        "role": "user",
        "content": f"Question: {query}\n\nContent:\n{summary}",
    }

    # Call the chat API
    response = chat(
        messages=[system_message, user_message],
        model="llama3.2",
        options={"num_ctx": 16384},
        stream=True,
    )
    for part in response:
        print(part["message"]["content"], end="", flush=True)


if __name__ == "__main__":
    fetch_and_analyze_with_ollama(
        "tell me some popular tourist spots in Darwin, Australia in 2024"
    )
