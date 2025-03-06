import prompts

from ollama import Client
from pydantic import BaseModel
from search import search_duckduckgo, scrape_webpage_content


class QueryModel(BaseModel):
    queries: list[str]


class QuestionRequiresDecompose(BaseModel):
    decompose_needed: bool


class SitesSelected(BaseModel):
    sites: list[str]


class QuestionAnswer(BaseModel):
    question: str
    answer: str


client = Client("http://localhost:11434")


def check_decompose_needed(query: str):
    res = client.chat(
        model="llama3.2",
        messages=[
            {
                "role": "system",
                "content": prompts.QUERY_DECOMPOSE_NEEDED_SYSTEM,
            },
            # Include examples for few-shot learning
            prompts.QUERY_DECOMPOSE_EXAMPLES[0],
            prompts.QUERY_DECOMPOSE_EXAMPLES[1],
            prompts.QUERY_DECOMPOSE_EXAMPLES[2],
            prompts.QUERY_DECOMPOSE_EXAMPLES[3],
            {
                "role": "user",
                "content": prompts.QUERY_DECOMPOSE_NEEDED_PROMPT.format(query),
            },
        ],
        format=QuestionRequiresDecompose.model_json_schema(),
        keep_alive=False,
        options={"temperature": 0},
    )

    return QuestionRequiresDecompose.model_validate_json(
        res.message.content
    ).decompose_needed


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
        options={"temperature": 0.2, "num_ctx": 16384},
    )

    return QuestionAnswer.model_validate_json(res.message.content)


def build_context_and_anwer(context: list[QuestionAnswer], question: str):
    res = client.chat(
        model="huihui_ai/deepseek-r1-abliterated",
        messages=[
            {
                "role": "user",
                "content": prompts.CONDENSE_AND_ANSWER.format(
                    "\n".join(
                        list(
                            map(
                                lambda c: f"""
<question>
{c.question}
<question>
                                                              
<answer>
{c.answer}
<answer>
""",
                                context,
                            )
                        )
                    ),
                    question,
                ),
            }
        ],
        format=QuestionAnswer.model_json_schema(),
        options={"temperature": 0.5, "num_ctx": 8192},
    )

    return QuestionAnswer.model_validate_json(res.message.content)


if __name__ == "__main__":
    main_question = "what are some interesting things that make malaysian chinese?"
    decompose_needed = check_decompose_needed(main_question)

    print(decompose_needed)

    if decompose_needed:
        queries = decompose_query(main_question)
        print(queries)
        question_answers = []
        for query in queries:
            links = select_sites(search_duckduckgo(query), query)
            for link in links:
                site_data = scrape_webpage_content(link)
                print(question_answer(site_data, query, main_question))
                question_answers.append(
                    question_answer(site_data, query, main_question)
                )
        final_answer = build_context_and_anwer(question_answers, main_question)
        print(final_answer)
    else:
        query = main_question
        links = select_sites(search_duckduckgo(query), query)
        for link in links:
            site_data = scrape_webpage_content(link)
            print(question_answer(site_data, query, main_question))
