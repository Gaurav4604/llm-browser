from duckduckgo_search import DDGS
import prompts

from ollama import Client
from pydantic import BaseModel


class QueryModel(BaseModel):
    queries: list[str]


def search_duckduckgo(query, max_results=5):
    # Use a context manager to properly instantiate DDGS.
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=max_results)
        return results


client = Client("http://localhost:11434")


def decompose_query(query: str):
    res = client.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": prompts.SYSTEM_QUERY_DECOMPOSE,
            },
            {"role": "user", "content": prompts.QUERY_DECOMPOSE_EXAMPLE},
            {"role": "user", "content": prompts.QUERY_PROMPT.format(query)},
        ],
        format=QueryModel.model_json_schema(),
        keep_alive=False,
        options={"temperature": 0.1, "num_ctx": 8192},
    )

    print(QueryModel.model_validate_json(res.message.content))


if __name__ == "__main__":
    decompose_query("Differentiate between AI and Functional Programming")
