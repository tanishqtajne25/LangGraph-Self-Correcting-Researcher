import json
from state import ResearchState
from groq import Groq
import os

def reviewer(state: ResearchState):
    """
    Reviewer Agent: Evaluates draft quality and identifies missing sections.
    Returns JSON with score, missing sections, and feedback summary.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    prompt = f"""You are a strict technical reviewer. Evaluate this draft against the user's query.

USER QUERY: {state['query']}

DRAFT TO REVIEW:
{state['draft']}

Return a JSON object with EXACTLY these keys:
{{
    "missing_sections": ["list", "of", "missing", "topics"],
    "unsupported_claims": <number>,
    "score": <float 0.0 to 1.0>,
    "feedback_summary": "One sentence summary of overall quality"
}}

Guidelines for scoring:
- 0.0–0.3: Missing most key concepts, inaccurate
- 0.3–0.6: Covers basics but missing important details
- 0.6–0.8: Good coverage but some gaps remain
- 0.8–1.0: Comprehensive and well-structured

Return ONLY valid JSON. No additional text."""
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0,
        response_format={"type": "json_object"}
    )
    
    response_text = response.choices[0].message.content
    
    try:
        review = json.loads(response_text)
        print(f"Score: {review.get('score', 0.0):.2f} | Missing: {review.get('missing_sections', [])}")
    except json.JSONDecodeError as e:
        print(f"JSON parsing error, using fallback")
        review = {
            "missing_sections": ["Could not parse review"],
            "unsupported_claims": 0,
            "score": 0.5,
            "feedback_summary": "Review parsing error - retrying recommended"
        }

    return {
        "review_feedback": review,
        "score": review.get("score", 0.0)
    }
