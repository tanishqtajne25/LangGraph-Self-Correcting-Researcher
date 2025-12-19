> **An autonomous AI agent that conducts deep research, drafts technical reports, and iteratively improves its own work through a self-correction loop.**

##  Overview

Unlike standard chatbots that hallucinate or provide surface-level answers, this **Recursive Research Agent** employs a cyclic "Plan-and-Solve" architecture. It mimics a human researcher's workflow:
1.  **Drafting:** Generates an initial report based on web search.
2.  **Critiquing:** A specialized "Reviewer" agent scores the draft and identifies missing info.
3.  **Iterating:** If the score is low, the "Researcher" agent dynamically generates *new* search queries to fix specific gaps.
4.  **Refining:** The cycle repeats until the quality threshold (0.8/1.0) is met.

##  Architecture

The system is built on **LangGraph** (State Graph Architecture) with three specialized nodes:

```mermaid
graph LR
    A[Researcher] -->|Search Results| B[Writer]
    B -->|Draft| C[Reviewer]
    C -->|Critique & Score| D{Is Quality Good?}
    D -->|Yes| E[End]
    D -->|No| A
