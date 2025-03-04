import prompts

from ollama import Client
from pydantic import BaseModel
from search import search_duckduckgo, scrape_webpage_content


class QueryModel(BaseModel):
    queries: list[str]


class SitesSelected(BaseModel):
    sites: list[str]


class QuestionAnswer(BaseModel):
    question: str
    answer: str


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
        options={"temperature": 0, "num_ctx": 8192},
    )

    return QueryModel.model_validate_json(res.message.content).queries


def select_sites(websites: list[dict[str, str]], question: str):

    site_metadata = "\n".join(
        """
<site>
<link>
{}
<link>
<body>
{}
<body>
<site>
""".format(
            site["href"], site["body"]
        )
        for site in websites
    )

    res = client.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": prompts.WEB_GREEN_LIGHT_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompts.WEB_GREEN_LIGHT_PROMPT.format(
                    site_metadata,
                    question,
                ),
            },
        ],
        format=SitesSelected.model_json_schema(),
        options={"temperature": 0, "num_ctx": 16384},
    )

    return SitesSelected.model_validate_json(res.message.content).sites


def question_answer(page: str, question: str, main_question: str):
    res = client.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": prompts.WEB_ASSESS_PAGE_CONTENT_SYSTEM},
            {
                "role": "user",
                "content": prompts.WEB_ASSESS_PAGE_CONTENT_PROMPT.format(
                    page, question, main_question
                ),
            },
        ],
        format=QuestionAnswer.model_json_schema(),
        options={"temperature": 0, "num_ctx": 32768},
    )

    return QuestionAnswer.model_validate_json(res.message.content)


if __name__ == "__main__":
    main_question = "who are 21 pilots?"
    queries = decompose_query(main_question)
    question_answers = []
    for query in queries:
        links = select_sites(search_duckduckgo(query), query)
        for link in links:
            site_data = scrape_webpage_content(link)
            print(question_answer(site_data, query, main_question))
