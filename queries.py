import ollama
import re
from search import fetch_search_results, scrape_webpage_content


def extract_string_between_quotes(text):
    """
    Extracts the string between two consecutive double quotes from the input text.

    Args:
        text (str): The input text containing the quoted string.

    Returns:
        str: The extracted string, or None if no quotes are found.
    """
    pattern = r"'([^']*)'"
    match = re.search(pattern, text)

    if match:
        return match.group(1)
    else:
        return None


prompt = """
You're NOT an AI assistant. You're NOT a search engine.
you're an assistant who's task is to generate a search query based on the given question.
You're to provide the search query to input in the seach box for the internet, which will result in a web search for the question.
"""

example_search_1 = """
the following is an example format for answer you should provide, to the question
Question: I want to know about Troye Sivan. Can you help me with that? - Answer: who is troye sivan?
"""

example_search_2 = """
the following is an example format for answer you should provide, to the question
Question: I want to learn about the Eiffel Tower. Can you provide details?
Answer: what is the eiffel tower?
"""

example_search_3 = """
the following is an example format for answer you should provide, to the question
Question: Could you explain what quantum computing is?
Answer: what is quantum computing?
"""


def generate_search_query(question):
    """generates search query from the given question"""
    res = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": example_search_1},
            {"role": "user", "content": example_search_2},
            {"role": "user", "content": example_search_3},
            {"role": "user", "content": question},
        ],
        stream=False,
    )
    return res["message"]["content"]


# print(generate_search_query("explain me what machine learning is"))
