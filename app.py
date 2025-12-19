import streamlit as st
import os
from dotenv import load_dotenv
from graph import build_graph
from datetime import datetime

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Research Report Generator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5em;
    }
    .status-box {
        padding: 1em;
        border-radius: 0.5em;
        margin: 1em 0;
    }
    .status-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .status-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .status-warning {
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
        color: #856404;
    }
    .report-container {
        background-color: #f8f9fa;
        color: #333333; /* <--- ADD THIS LINE (Dark text for light background) */
        padding: 2em;
        border-radius: 1em;
        border-left: 5px solid #1f77b4;
        margin: 1em 0;
        font-size: 1.05em;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📚 Multi-Agent Research Report Generator</div>', unsafe_allow_html=True)
st.markdown("*Powered by LangGraph + Groq Llama 3.3 + DuckDuckGo*")
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.warning("⚠️ GROQ_API_KEY not set.")
        st.code("export GROQ_API_KEY='your-key-here'")
    else:
        st.success("✅ Groq API ready")

    st.markdown("### 📋 Workflow")
    st.markdown(
        "Researcher → Writer → Reviewer  \n"
        "*Loops until score ≥ 0.8 or 5 iterations*"
    )

# Query input
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔍 Enter Your Research Query")
    query = st.text_input(
        "query",
        placeholder="e.g. Lip reading using Deep Learning",
        label_visibility="collapsed",
    )

with col2:
    st.markdown("### 💡 Tips")
    st.markdown("- Be specific\n- Technical topics work best\n- 5–15 words")

# Button
if st.button("🚀 Generate Report", type="primary", use_container_width=True):
    if not query.strip():
        st.error("❌ Enter a query first")
        st.stop()
    if not os.getenv("GROQ_API_KEY"):
        st.error("❌ Set GROQ_API_KEY in your environment")
        st.stop()

    app = build_graph()

    initial_state = {
        "query": query,
        "sources": [],
        "draft": "",
        "review_feedback": {},
        "score": 0.0,
        "iteration": 0,
    }

    progress_col, status_col = st.columns([3, 1])
    with progress_col:
        progress_bar = st.progress(0)
    with status_col:
        status_text = st.empty()

    metrics_placeholder = st.empty()
    report_placeholder = st.empty()
    feedback_placeholder = st.empty()

    # --- FIX 1: Initialize final_result with initial_state ---
    final_result = initial_state.copy()
    iteration_count = 0

    try:
        # --- FIX 2: Added recursion_limit config ---
        for event in app.stream(initial_state, config={"recursion_limit": 50}):
            if not event:
                continue

            for node_name, state_data in event.items():
                # --- FIX 3: Update state instead of overwriting it ---
                # This ensures the 'draft' from the Writer node isn't erased
                # when the Reviewer node (which doesn't return a draft) runs next.
                final_result.update(state_data)
                
                iteration_count = state_data.get("iteration", iteration_count)
                current_score = state_data.get("score", 0.0)

                # UI progress
                progress = min(iteration_count / 5, 1.0)
                progress_bar.progress(progress)
                status_text.markdown(
                    f"**{node_name.upper()}** | Iter: {iteration_count} | Score: {current_score:.2f}"
                )

        # DEBUG: see exactly what we got (Uncomment if needed)
        # st.write("DEBUG FINAL STATE:", final_result)

        final_score = final_result.get("score", 0.0)
        final_feedback = final_result.get("review_feedback", {})
        final_draft = final_result.get("draft", "")

        # Metrics
        with metrics_placeholder.container():
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📊 Final Score", f"{final_score:.2f}")
            c2.metric("🔄 Iterations", iteration_count)
            c3.metric("❌ Missing", len(final_feedback.get("missing_sections", [])))
            c4.metric("⚠️ Claims", final_feedback.get("unsupported_claims", 0))

        # Status banner
        if final_score >= 0.8:
            st.markdown(
                '<div class="status-box status-success">✅ Excellent report (score ≥ 0.8)</div>',
                unsafe_allow_html=True,
            )
        elif final_score >= 0.6:
            st.markdown(
                '<div class="status-box status-info">ℹ️ Good report (some gaps)</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-box status-warning">⚠️ Fair report (max iterations reached)</div>',
                unsafe_allow_html=True,
            )

        # INLINE report
        with report_placeholder.container():
            st.markdown("### 📄 Generated Report")
            if final_draft.strip():
                st.markdown(
                    f'<div class="report-container">{final_draft}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("No report text generated. Check node logs / JSON errors.")

        # Feedback
        with feedback_placeholder.container():
            st.markdown("### 🔍 Detailed Feedback")
            f1, f2 = st.columns(2)

            with f1:
                st.markdown("**Missing Sections:**")
                missing = final_feedback.get("missing_sections", [])
                if missing:
                    for item in missing:
                        st.markdown(f"- {item}")
                else:
                    st.success("✅ None")

            with f2:
                st.markdown("**Summary:**")
                summary = final_feedback.get("feedback_summary", "No feedback")
                st.markdown(f"*{summary}*")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Check API key, model name, and terminal logs for stack trace.")

st.divider()
st.markdown("*Multi-agent LangGraph system | Resume-ready project*")