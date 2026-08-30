import streamlit as st

from agent import answer_question
from analytics import get_available_sectors


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Business Intelligence Agent",
    page_icon="📊",
    layout="centered"
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 Business Intelligence Agent")

st.write(
    "Ask questions about pipeline, deals, billing, "
    "collections, work orders, and business performance."
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("Available Sectors")

    try:
        sectors = get_available_sectors()

        for sector in sectors:
            st.write(f"• {sector}")

    except Exception:
        st.write("Unable to load sectors.")


# ============================================================
# QUESTION INPUT
# ============================================================

st.subheader("Ask a Business Question")

question = st.text_input(
    "Enter your question",
    placeholder="e.g. How is the Renewables sector performing?"
)


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

st.caption("Example questions:")

st.write(
    """
    • What is our total pipeline value?

    • How much has been billed?

    • How much money is receivable?

    • How is the Renewables sector performing?

    • What are our biggest business risks?

    • Give me a short leadership update.
    """
)


# ============================================================
# ASK BUTTON
# ============================================================

if st.button("Ask", type="primary"):

    if not question.strip():

        st.warning("Please enter a business question.")

    else:

        with st.spinner("Analyzing Monday.com data..."):

            try:

                answer = answer_question(question)

                st.divider()

                st.subheader("Answer")

                st.markdown(answer)

            except Exception as e:

                st.error(
                    "Unable to process your question. "
                    "Please try again."
                )

                st.caption(
                    f"Error: {str(e)}"
                )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Data source: Monday.com • "
    "AI analysis powered by Gemini"
)