## Global Langraph State
import operator
from typing import List, TypedDict, Dict, Any, Annotated

class ResearchState(TypedDict):
    query: str
    # "operator.add" tells LangGraph to APPEND new items, not overwrite
    sources: Annotated[List[str], operator.add] 
    draft: str
    review_feedback: Dict[str, Any]
    score: float
    iteration: int