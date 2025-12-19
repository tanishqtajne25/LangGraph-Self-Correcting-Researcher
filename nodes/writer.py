from state import ResearchState
from groq import Groq
import os

def writer(state: ResearchState):
    """
    Writer Agent: Creates comprehensive technical reports from gathered sources.
    Uses Groq to write based on sources and reviewer feedback.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    all_sources = "\n\n".join(state['sources'])
    
    prompt = f"""You are a technical writer.
Task: Write a comprehensive, well-structured report on: {state['query']}

Directives:
1. Use ONLY the provided sources below.
2. Organize the report with clear sections (e.g., Overview, Architecture, Key Concepts, Applications, Challenges).
3. If sources mention errors or invalid data, ignore them and focus on valid technical content.
4. Write in a professional, academic tone.

Reviewer Feedback from Previous Draft (address these issues):
{state.get('review_feedback', {}).get('missing_sections', 'None')}

Sources:
{all_sources}

Generate a comprehensive report:"""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2500,
        temperature=0
    )
    
    draft = response.choices[0].message.content
    print(f" Generated report ({len(draft.split())} words)")
    
    return {"draft": draft}
