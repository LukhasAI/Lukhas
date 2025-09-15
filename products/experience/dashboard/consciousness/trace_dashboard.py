from ...streamlit_safe import get_streamlit

try:
    from reasoning.reasoning_metrics import logic_drift_index, recall_efficiency_score
except ImportError:  # pragma: no cover - exercised via fallback in tests
    # ΛTAG: reasoning_metrics_fallback
    def logic_drift_index(previous_trace: dict, current_trace: dict) -> float:
        prev = previous_trace.get("overall_confidence", 0.0)
        curr = current_trace.get("overall_confidence", 0.0)
        return round(prev - curr, 4)

    def recall_efficiency_score(invoked, optimal) -> float:
        optimal_count = len(optimal) or 1
        overlap = len({item.get("key") for item in invoked} & {item.get("key") for item in optimal})
        return round(overlap / optimal_count, 4)

# ΛTAG: streamlit_dashboard
st = get_streamlit()


def render_dashboard():
    """
    Renders a Streamlit dashboard to expose recall/logic metrics.
    """
    st.title("Reasoning and Memory Metrics Dashboard")

    # --- Logic Drift Index ---
    st.header("Logic Drift Index")
    # This is a placeholder for a real data source
    previous_trace = {"overall_confidence": 0.8}
    current_trace = {"overall_confidence": 0.7}
    drift = logic_drift_index(previous_trace, current_trace)
    st.metric("Logic Drift", drift)

    # --- Recall Efficiency Score ---
    st.header("Recall Efficiency Score")
    # This is a placeholder for a real data source
    invoked_memories = [{"key": "a"}, {"key": "b"}]
    optimal_memories = [{"key": "a"}, {"key": "b"}, {"key": "c"}]
    score = recall_efficiency_score(invoked_memories, optimal_memories)
    st.metric("Recall Efficiency", score)


if __name__ == "__main__":
    render_dashboard()
