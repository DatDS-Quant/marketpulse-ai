"""Minimal Streamlit application for MarketPulse AI Module 0."""

from __future__ import annotations

import streamlit as st


def get_module_roadmap() -> list[str]:
    """Return the planned MVP modules shown in the dashboard.

    Input: none.
    Returns: a list of module names in planned build order.
    Why it exists: keeping the roadmap in one function makes the page easy to
    update as the project grows.
    """

    return [
        "Module 0 - Project Operating System",
        "Module 1 - Data Collection",
        "Module 2 - Processing and Schema Validation",
        "Module 3 - Trend Intelligence",
        "Module 4 - RAG with Citations",
        "Module 5 - Evaluation and Observability",
        "Module 6 - Human Review and Dashboard Polish",
    ]


def render_roadmap(roadmap_items: list[str]) -> None:
    """Render the MVP module roadmap in Streamlit.

    Input: a list of roadmap item labels.
    Returns: nothing; the function writes UI elements to the Streamlit page.
    Why it exists: separating rendering keeps the main function short and clear.
    """

    st.subheader("MVP Module Roadmap")
    for item in roadmap_items:
        st.write(f"- {item}")


def main() -> None:
    """Render the MarketPulse AI Streamlit skeleton.

    Input: none.
    Returns: nothing; Streamlit handles page rendering.
    Why it exists: this is the app entry point used by
    `streamlit run app/main.py`.
    """

    st.set_page_config(
        page_title="MarketPulse AI",
        page_icon="MP",
        layout="wide",
    )

    st.title("MarketPulse AI")
    st.write(
        "An AI-powered market intelligence automation platform for learning "
        "practical AI engineering through data pipelines, RAG, evaluation, "
        "observability, and dashboarding."
    )

    st.info("Current status: Module 0 initialized.")
    render_roadmap(get_module_roadmap())


if __name__ == "__main__":
    main()

