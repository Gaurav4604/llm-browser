import argparse
from utils import QueryAgent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch and analyze search results with Ollama."
    )
    parser.add_argument(
        "-q", "--query", type=str, required=True, help="Query to search"
    )
    args = parser.parse_args()

    agent = QueryAgent()

    result = agent.execute(args.query)

    print("\nFinal Answer:")
    print(f"Question: {result.question}")
    print(f"Answer: {result.answer}")
