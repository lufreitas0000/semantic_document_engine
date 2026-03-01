"""
Streamlit Web Interface.
This application knows NOTHING about PostgreSQL, pgvector, or our Domain.
It only knows how to send HTTP requests to our FastAPI server and render the JSON responses.
"""
import streamlit as st
import httpx

# The coordinates of our backend engine
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Semantic Engine", page_icon="🧠", layout="centered")

st.title("Semantic Document Engine")
st.markdown("Search academic papers using Dense Vector Mathematics.")

# --- UI Layout: Two Tabs ---
tab1, tab2 = st.tabs(["Search Knowledge Base", "Ingest New Papers"])

with tab2:
    st.header("Ingest Papers into Database")
    ingest_query = st.text_input("arXiv/Scholar Query", value="Quantum Gravity")
    ingest_limit = st.slider("Number of papers to ingest", 1, 10, 5)

    if st.button("Ingest"):
        with st.spinner("Downloading and calculating mathematical embeddings..."):
            try:
                # Trigger the FastAPI POST endpoint
                response = httpx.post(
                    f"{API_URL}/ingest/",
                    params={"query": ingest_query, "limit": ingest_limit},
                    timeout=30.0 # Neural networks take time!
                )
                response.raise_for_status()
                data = response.json()
                st.success(f"Successfully ingested {data['papers_ingested']} papers!")
            except Exception as e:
                st.error(f"Failed to ingest: {e}")

with tab1:
    st.header("Semantic Vector Search")
    search_query = st.text_input("Ask a conceptual question:")

    if st.button("Search"):
        if not search_query:
            st.warning("Please enter a query.")
        else:
            with st.spinner("Calculating cosine distances..."):
                try:
                    # Trigger the FastAPI GET endpoint
                    response = httpx.get(
                        f"{API_URL}/search/",
                        params={"query": search_query, "limit": 5}
                    )
                    response.raise_for_status()
                    data = response.json()

                    st.subheader("Nearest Mathematical Neighbors:")
                    for paper in data["results"]:
                        with st.expander(f"📄 {paper['title']}"):
                            st.write(paper['abstract'])
                            st.caption(f"Internal UUID: {paper['id']}")

                except Exception as e:
                    st.error(f"Search failed. Is the API running? Error: {e}")
