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


class QueryAgent:
    def __init__(self, ollama_url="http://localhost:11434"):
        self.client = Client(ollama_url)

    def check_decompose_needed(self, query: str) -> bool:
        """Determine if a query needs to be decomposed into sub-queries"""
        res = self.client.chat(
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

    def decompose_query(self, query: str) -> list[str]:
        """Break down a complex query into simpler sub-queries"""
        res = self.client.chat(
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

    def select_sites(self, websites: list[dict[str, str]], question: str) -> list[str]:
        """Select relevant websites from search results for a given question"""
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

        res = self.client.chat(
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

    def question_answer(
        self, page: str, question: str, main_question: str
    ) -> QuestionAnswer:
        """Answer a specific question based on webpage content"""
        res = self.client.chat(
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

    def build_context_and_answer(
        self, context: list[QuestionAnswer], question: str
    ) -> QuestionAnswer:
        """Synthesize answers from multiple sources into a final answer"""
        res = self.client.chat(
            model="llama3.2",
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

    def execute(self, main_question: str) -> QuestionAnswer:
        """Main execution flow to process a query and return an answer"""
        print(f"Processing question: {main_question}")

        # Check if query needs decomposition
        decompose_needed = self.check_decompose_needed(main_question)
        print(f"Decomposition needed: {decompose_needed}")

        if decompose_needed:
            # Handle complex queries through decomposition
            queries = self.decompose_query(main_question)
            print(f"Decomposed into: {queries}")

            question_answers = []
            for query in queries:
                print(f"Processing sub-query: {query}")
                search_results = search_duckduckgo(query)
                links = self.select_sites(search_results, query)

                for link in links:
                    print(f"Extracting data from: {link}")
                    site_data = scrape_webpage_content(link)
                    answer = self.question_answer(site_data, query, main_question)
                    print(f"Sub-answer: {answer.answer[:100]}...")
                    question_answers.append(answer)

            final_answer = self.build_context_and_answer(
                question_answers, main_question
            )
            return final_answer
        else:
            # Handle simple queries directly
            query = main_question
            search_results = search_duckduckgo(query)
            links = self.select_sites(search_results, query)

            question_answers = []
            for link in links:
                print(f"Extracting data from: {link}")
                site_data = scrape_webpage_content(link)
                answer = self.question_answer(site_data, query, main_question)
                question_answers.append(answer)

            final_answer = self.build_context_and_answer(
                question_answers, main_question
            )
            return final_answer


if __name__ == "__main__":
    # Example usage
    agent = QueryAgent()
    question = "what is the difference between instagram and tiktok?"
    result = agent.execute(question)
    print("\nFinal Answer:")
    print(f"Question: {result.question}")
    print(f"Answer: {result.answer}")
