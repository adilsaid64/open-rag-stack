import re
from collections import Counter
from typing import Any, Optional

import requests
import streamlit as st

st.set_page_config(
    page_title="RAG Demo",
    page_icon="🧠",
    layout="centered",
)

RAG_ORCHESTRATOR_URL: str = "http://rag-orchestrator:8000"


def extract_keywords(text: str, top_n: int = 3) -> list[str]:
    words = re.findall(r"\b\w{4,}\b", text.lower())
    common = Counter(words).most_common(top_n)
    return [word for word, _ in common]


def post_json(
    endpoint: str, payload: dict[str, Any]
) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    try:
        resp = requests.post(f"{RAG_ORCHESTRATOR_URL}{endpoint}", json=payload)
        resp.raise_for_status()
        return resp.json(), None
    except requests.RequestException as e:
        return None, str(e)


def ingest_section() -> None:
    st.subheader("📄 Ingest Document")

    with st.form("ingest_form"):
        text: str = st.text_area("Document Text", height=200)

        with st.expander("🛠 Optional Metadata"):
            col1, col2 = st.columns(2)
            title: str = col1.text_input("Title")
            author: str = col2.text_input("Author")

        submitted: bool = st.form_submit_button("🚀 Ingest Document")

        if submitted:
            if not text.strip():
                st.warning("Please enter some text to ingest.")
                return

            metadata: dict[str, Any] = {
                "title": title,
                "author": author,
            }

            payload: dict[str, Any] = {
                "text": text,
                "metadata": metadata,
            }

            response, error = post_json("/ingest/", payload)

            if error:
                st.error(f"❌ Ingestion failed: {error}")
            else:
                st.success("✅ Document ingested successfully!")
                st.json(response)


def query_section() -> None:
    st.subheader("❓ Ask a Question")

    with st.form("query_form"):
        question: str = st.text_input("Your question")
        top_k: int = st.slider("Number of contexts to retrieve", 1, 5, 3)
        submitted: bool = st.form_submit_button("🔍 Query")

        if submitted:
            if not question.strip():
                st.warning("Please enter a question.")
                return

            payload: dict[str, Any] = {"question": question, "top_k": top_k}
            response, error = post_json("/query/", payload)

            if error:
                st.error(f"❌ Query failed: {error}")
            else:
                st.markdown("### ✅ Answer")
                st.success(
                    response.get("answer", "No answer returned")
                    if response is not None
                    else "Response is None"
                )


def main() -> None:
    st.title("🧠 Retrieval-Augmented Generation Demo")

    tab1, tab2 = st.tabs(["📄 Ingest", "❓ Query"])

    with tab1:
        ingest_section()
    with tab2:
        query_section()


if __name__ == "__main__":
    main()
