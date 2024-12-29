import ollama


# Define the Llama-based classifier with keyword enhancement
def llama_based_check_with_keywords(question):
    keywords = [
        "current",
        "latest",
        "today",
        "now",
        "near me",
        "local",
        "recent",
        "new",
        "weather",
        "score",
        "time",
        "price",
        "cost",
        "event",
        "person",
        "location",
    ]
    # Add synonyms or related terms (can expand this list as needed)
    synonyms = {
        "current": ["present", "ongoing", "happening"],
        "latest": ["newest", "fresh", "most recent"],
        "weather": ["forecast", "climate", "temperature"],
        "price": ["cost", "expense", "rate"],
        "person": ["individual", "human", "personnel"],
    }
    # Flatten keywords and synonyms into a single list
    expanded_keywords = keywords + [
        synonym for key in synonyms.values() for synonym in key
    ]
    # Create a comma-separated string of keywords for the prompt
    keyword_list = ", ".join(expanded_keywords)

    # Enhanced prompt with keywords guidance
    prompt = f"""
    Analyze the following question and determine if it requires a web search. 
    Consider if it mentions keywords like {keyword_list}, their synonyms, or topics requiring up-to-date or local information (e.g., news, events, prices, or weather). 
    Respond with 'Web Search' or 'No Web Search'.

    Question: {question}
    """
    # Call the Llama model
    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )
    print(response["message"]["content"])
    return not (response["message"]["content"].find("No Web Search") != -1)


# questions = [
#     "What is the weather forecast for tomorrow?",
#     "Explain the process of photosynthesis.",
#     "When is Troye Sivan's next tour?",
#     "Should I wear a hat tomorrow?",
# ]


# for question in questions:
#     print(f"Question: {question}")
#     print(f"Classification: {llama_based_check_with_keywords(question)}\n")


# step 1: get search query
# step 2: get search results from web search engine
# step 3: for each search result, get summary of webpage using LLM,
#         check if summary answers question, if yes, return answer
#         else, continue to next search result, aggregate for a common summary
# step 4: build out a common summary
# step 5: re-ask the question with the common summary as context
