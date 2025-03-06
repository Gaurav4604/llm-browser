SYSTEM_QUERY_DECOMPOSE = f"""
You are a statement decomposer,
Your role is to decompose complex questions into simpler sub-questions,
If you feel that the question is basic enough, you can let it remain the same

This query will be used for a google search,
so ensure that the query is very concise

NOTE: TRY TO BREAK THE CONCEPT DOWN, AS LITTLE AS POSSIBLE
"""

QUERY_DECOMPOSE_EXAMPLE = """
I will provide you with some example questions and its simpler sub-questions, later I will
also provide you with the question, I want you to de-compose into simpler sub-questions

Types:
    1. Comparison:
        Examples:
        - Question: What are the differences between A and B?
        - Sub-Questions generated:
                1. What is the definition of A?
                2. What is the definition of B?
        - Question: In what distinct ways do A and B vary?
        - Sub-Questions generated:
                1. How is A fundamentally described?
                2. How is B fundamentally described?
    
    2. Contrast:
        - Question: In what ways do A and B differ in their inherent characteristics?
        - Sub-Questions generated:
            1. What are the essential features of A?
            2. What are the essential features of B?
        - Question: How can the intrinsic qualities of A be distinguished from those of B?
        - Sub-Questions generated:
            1. What intrinsic qualities define A?
            2. Which qualities clearly separate A from B?

    3. Synthesis:
        - Question: How can elements from A, B, and C be combined to create a new integrated model?
        - Sub-Questions generated:
            1. What are the key components or principles of A?
            2. What are the key components or principles of B?
            3. What are the key components or principles of C?
        - Question: What approach can merge the components of A, B, and C into a unified framework?
        - Sub-Questions generated:
            1. What fundamental aspects constitute A?
            2. What fundamental aspects constitute B?
            3. What fundamental aspects constitute C?
    
    4. Analysis:
        - Question: How can A be broken down into its constituent parts, and what is the role of each part?
        - Sub-Questions generated:
            1. What are the individual components that make up A?
            2. What function does each component serve within A?
            3. How do these components interact to form the overall structure of A?
        - Question: In what manner can A be dissected into its individual segments, and what function does each segment perform?
        - Sub-Questions generated:
            1. What segments comprise A?
            2. What is the role of each segment?
            3. How do these segments combine to establish A's complete structure?

    5. Evaluation:
        - Question: How effective is A in achieving its intended purpose, and what are its strengths and limitations?
        - Sub-Questions generated:
            1. What criteria can be used to assess the performance of A?
            2. How does A perform according to these criteria?
            3. What strengths does A exhibit?
            4. What limitations or weaknesses are evident in A?
        - Question: To what extent does A fulfill its goals, and what are its notable advantages and drawbacks?
        - Sub-Questions generated:
            1. What benchmarks determine A's success?
            2. How well does A meet these benchmarks?
            3. What are the major advantages of A?
            4. What are the key drawbacks of A?

    6. Application:
        - Question: How can the concepts of A be applied to solve challenges presented by B?
        - Sub-Questions generated:
            1. What are the fundamental principles or techniques underlying A?
            2. What specific challenges or requirements does B present?
            3. How can the principles of A be mapped to address the challenges of B?
            4. What potential issues might arise when applying A to the context of B?
        - Question: In what ways can the principles of A be utilized to tackle the problems encountered in B?
        - Sub-Questions generated:
            1. What are the core principles of A?
            2. What problems or challenges does B pose?
            3. How can these principles be effectively adapted to resolve the challenges of B?
            4. What obstacles could emerge during this adaptation?

    7. Definition:
        - Question: What is the definition of A?
        - Sub-Questions generated:
                1. What are the essential characteristics that define A?
                2. How is A fundamentally described within its context?
        - Question: How can A be defined in relation to B?
        - Sub-Questions generated:
                1. What is the core meaning of A?
                2. How does the relationship with B shape the definition of A?

    8. Explanation:
        - Question: How can the workings of A be explained?
        - Sub-Questions generated:
                1. What processes underlie the operation of A?
                2. What are the key mechanisms that drive A?
        - Question: Can you explain how A functions within the framework of B?
        - Sub-Questions generated:
                1. What role does A play in the functioning of B?
                2. How do the interactions between A and B facilitate overall performance?

    9. Justification:
        - Question: Why is A considered essential for B?
        - Sub-Questions generated:
                1. What evidence supports the critical role of A in B?
                2. How does A contribute to the overall success or efficiency of B?
        - Question: What are the reasons for implementing A in the context of B?
        - Sub-Questions generated:
                1. What benefits does A offer in this scenario?
                2. How do these benefits outweigh any potential drawbacks?
"""


QUERY_PROMPT = """
The following is a question that needs to be decomposed into simpler question,
if required:

<question>
{}
</questions>
"""


"""
#######################################
PROMPTS TO CONSUME AND UNDERSTAND WEB CONTENT
#######################################
"""


WEB_GREEN_LIGHT_SYSTEM_PROMPT = """
You are responsible for reading structured information,
which contains:
1. A link to the website
2. A short description about the content of the website

Using the following, your role is to select a subset of the websites,
which can be scraped

Your assessment criteria should be based on the following:

1. do they provide any explanation to the question, the user has asked?
2. do they display examples that could be useful in answering the user's question

"""


WEB_GREEN_LIGHT_PROMPT = """
The following are the websites, which contain link, and a short description about the website

<sites>
{}
<sites>

The following is the question they're intended to answer

<question>
{}
<question>

select a subset of the following sites

BE EXTREMELY STRICT IN YOUR LINK ASSESSMENT, TRY TO SELECT AS LOW A NUMBER OF LINKS AS POSSIBLE
"""


WEB_ASSESS_PAGE_CONTENT_SYSTEM = """
You are responsible for assessing the content of a webpage,
Your role check if a given page answers user's question,
if so, you should return the answer to the user's question
"""

WEB_ASSESS_PAGE_CONTENT_PROMPT = """
The following is the content of a webpage

<web-page>
{}
<web-page>

using the above, answer this question
<question>
{}
<question>

and also this question
<question>
{}
<question>
"""


QUERY_DECOMPOSE_NEEDED_SYSTEM = f"""
Your role is to assess whether a query should be decomposed into multiple sub-queries before processing.

A query requires decomposition if it meets one or more of these criteria:

1. MULTIPLE DISTINCT TOPICS: The query contains separate questions that could be answered independently.
   Example: "What is the capital of France and how do I install Python on Windows?"

2. COMPLEX REASONING REQUIREMENTS: 
   a. The query requires breaking down a complex topic into simpler components
      Example: "Explain how transformer models work in NLP"
   
   b. The query requests comprehensive characteristics of a complex subject
      Example: "What are all the considerations for implementing a production RAG system?"
   
   c. The query involves multi-step reasoning or calculations
      Example: "If I invest $1000 with 5% compound interest, how much will I have after 10 years, and what percentage of that is profit?"

3. DOMAIN EXPERTISE SPANNING: The query spans multiple domains of knowledge
   Example: "How do economic policies affect climate change mitigation efforts?"

4. TEMPORAL REASONING: The query requires reasoning across different time periods
   Example: "Compare machine learning approaches from the 1990s to current methods"

5. COMPARATIVE ANALYSIS: The query asks for comparison between multiple entities
   Example: "Compare and contrast PyTorch, TensorFlow, and JAX for LLM deployment"

6. REQUEST FOR EXHAUSTIVE INFORMATION: The query asks for "all" or "comprehensive" information
   Example: "List all the parameters in the LLaMA 3 model"

DOES NOT need decomposition:
- Simple, focused questions about a single concept
- Clear, direct requests for specific information
- Basic how-to questions with a single objective
- Yes/no questions or simple classification tasks

Your task is to return a JSON object with a single boolean field "decompose_needed".
"""

QUERY_DECOMPOSE_NEEDED_PROMPT = """
Analyze the following query and determine if it requires decomposition into sub-queries:

Query: {}

Provide your reasoning step by step before making your final decision.
"""

# Example exchanges to add
QUERY_DECOMPOSE_EXAMPLES = [
    {
        "role": "user",
        "content": "Analyze the following query and determine if it requires decomposition into sub-queries:\n\nQuery: How do I fine-tune BERT for text classification?\n\nProvide your reasoning step by step before making your final decision.",
    },
    {
        "role": "assistant",
        "content": """
Step-by-step reasoning:
1. This query is about a single topic: fine-tuning BERT for text classification.
2. While fine-tuning BERT involves multiple steps, it's a standard process with a clear singular objective.
3. The query doesn't combine multiple unrelated topics.
4. It doesn't require extensive comparative analysis.
5. It requests a specific process rather than comprehensive details about multiple subjects.

Final decision: This query does not need decomposition. It's a focused how-to question about a specific ML task.

{"decompose_needed": false}
""",
    },
    {
        "role": "user",
        "content": "Analyze the following query and determine if it requires decomposition into sub-queries:\n\nQuery: What are the differences between various embedding models, and how do I implement a vector database with FAISS for RAG?\n\nProvide your reasoning step by step before making your final decision.",
    },
    {
        "role": "assistant",
        "content": """
Step-by-step reasoning:
1. This query contains two distinct parts:
   - Comparing different embedding models (analytical/comparative)
   - Implementing a vector database with FAISS (implementation/how-to)
2. The first part requires comparative analysis across multiple embedding models.
3. The second part involves a separate implementation task.
4. These could be addressed independently and require different types of responses.
5. The first part alone could be complex enough for its own query, as there are many embedding models.

Final decision: This query needs decomposition into at least two sub-queries.

{"decompose_needed": true}
""",
    },
]


CONDENSE_AND_ANSWER = """
Your role is to answer the user's question, using the context provided to you.

<context>
{}
<context>

<question>
{}
<question>
"""
