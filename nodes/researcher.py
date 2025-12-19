from langchain_community.tools import DuckDuckGoSearchResults
from state import ResearchState
from groq import Groq
import os

search_tool = DuckDuckGoSearchResults(num_results=3)

def researcher(state: ResearchState):
    """
    Researcher Agent: Searches the web and gathers sources.
    Uses Groq to refine search queries based on reviewer feedback.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    original_query = state["query"]
    feedback = state.get("review_feedback", {})

    # 1. Decide what to search
    if feedback and "missing_sections" in feedback:
        if "Invalid JSON" in str(feedback.get("missing_sections", [])):
            # Fallback to original query if previous iteration had errors
            search_query = original_query
        else:
            # Valid feedback: generate targeted search query
            missing = ", ".join(feedback["missing_sections"])
            prompt = f"""Task: Generate ONE search query to find missing info on: {missing}.
Context: The main topic is {original_query}.
Output: Return ONLY the query string. Do not use quotes. Do not add explanation."""
            
            response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0
            )
            search_query = response.choices[0].message.content.strip().replace('"', '')
            print(f"RE-RESEARCHING: {search_query}")
    else:
        # First iteration: use original query
        search_query = original_query
        print(f"RESEARCHING: {search_query}")

    # 2. Execute search
    try:
        results = search_tool.invoke(search_query)
        print(f"Found {len(str(results).split('snippet:'))} results")
    except Exception as e:
        results = f"Search Error: {str(e)}"
        print(f"Search failed: {str(e)}")

    # 3. Format and store result
    new_source = f"Query: {search_query}\nResults:\n{str(results)}"
    
    return {
        "sources": [new_source],
        "iteration": state["iteration"] + 1
    }
