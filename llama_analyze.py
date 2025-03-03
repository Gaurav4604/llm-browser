from ollama import chat
from search import fetch_search_results, scrape_webpage_content
from queries import generate_search_query
from web_search_required import llama_check_if_web_search_required


prompt_summarize_mono = """
You can summarize text.
You are given a piece of text and your task
is to summarize it, retain the most important
points present in the query and provide a concise summary.
Retain keywords present in the text
"""
prompt_compare_merge_summary = """
You can summarize text.
You are given two pieces of text and your task
is to compare them, retain the most important
points present in the both documents, merge them
and provide a concise summary.
Retain keywords present in the texts
"""

prompt_ground_data_to_query = """
You can extract valid content from a given text.
You are given a large text summary, your role is to
extract the most relevant information from the text that is directly related to the grounding query.
"""

prompt_content_template = "{} this is the summary, {} this is my grounding query"


def extract_valid_content(content, grounding_query):
    print("Extracting valid content")
    response = chat(
        messages=[
            {
                "role": "system",
                "content": prompt_ground_data_to_query,
            },
            {
                "role": "user",
                "content": prompt_content_template.format(content, grounding_query),
            },
        ],
        model="llama3.2:1b",
        options={"num_ctx": 16384},
    )
    return response["message"]["content"]


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


def check_if_context_is_valid(question, context):
    system_message = {
        "role": "system",
        "content": "You are a helpful assistant. Given the following content from web search results, Tell me, as a Yes/No, if the provided context can answer my question or not",
    }

    # Send user question and combined content
    user_message = {
        "role": "user",
        "content": f"Question: {question}\n\nContent:\n{context}",
    }

    # Call the chat API
    response = chat(
        messages=[system_message, user_message],
        model="llama3.2",
        options={"num_ctx": 16384},
    )
    print(response["message"]["content"])
    return not "No" in response["message"]["content"]


def answer_user_question(question, context=None):
    if context is not None:
        system_message = {
            "role": "system",
            "content": "You are a helpful assistant. Given the following content from web search results, provide the best possible answer to the user's question. Ensure your response is concise and accurate.",
        }

        # Send user question and combined content
        user_message = {
            "role": "user",
            "content": f"Question: {question}\n\nContent:\n{context}",
        }

        # Call the chat API
        response = chat(
            messages=[system_message, user_message],
            model="llama3.2",
            options={"num_ctx": 16384},
        )
        return response["message"]["content"]
    else:
        response = chat(
            messages=[
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="llama3.2",
        )
        return response["message"]["content"]


def fetch_and_analyze_with_ollama(query):
    # Check if web search is needed
    if llama_check_if_web_search_required(query):
        # Step 1: Fetch search results
        search_query = generate_search_query(query)
        print("Search query: {}".format(search_query))

        print("Fetching search results...")
        search_results = fetch_search_results(search_query)

        # Step 2: Scrape content from top results
        print("Scraping content from search results...")
        aggregate_summary = ""
        response = None
        for result in search_results:
            print(result)
            # Scrape content from the webpage
            content = scrape_webpage_content(result["link"])
            if content:
                # Extract content in relation to search query, from webpage
                summary = extract_valid_content(content, search_query)

                # Check content validity
                if check_if_context_is_valid(query, summary):
                    print("Content Validated, Answering User Query...")
                    response = answer_user_question(query, summary)
                    break
                # Content not enough, add to summary and search more
                else:
                    aggregate_summary = summarize_with_llama(aggregate_summary, summary)

        # response defined, since we found a valid context in summary
        if response is not None:
            print(response)
        # response not yet defined, use aggregated summary
        else:
            response = answer_user_question(query, aggregate_summary)
            print(response)
    else:
        print("No web search required. Answering user query directly...")
        response = answer_user_question(query)
        print(response)


if __name__ == "__main__":
    fetch_and_analyze_with_ollama(
        "tell me some popular tourist spots in Darwin, Australia in 2024"
    )
