import argparse
from llama_analyze import fetch_and_analyze_with_ollama

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fetch and analyze search results with Ollama."
    )
    parser.add_argument(
        "-q", "--query", type=str, required=True, help="Query to search"
    )
    args = parser.parse_args()

    fetch_and_analyze_with_ollama(args.query)
