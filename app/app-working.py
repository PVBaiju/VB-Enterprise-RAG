import streamlit as st
from dotenv import load_dotenv
from databricks_rag_utils import answer_question

load_dotenv()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Smart Employee Policy System",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Smart Employee Policy Knowledge System")
st.caption("Search-based HR Assistant (Databricks + FAISS + Gemini)")

# ---------------- SESSION STATE ----------------
if "last_query" not in st.session_state:
    st.session_state.last_query = None

if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

# ---------------- INPUT ----------------
question = st.text_input("Enter policy search (e.g. leave policy, parental leave)")

if st.button("Search") and question:

    # 🔥 RESET OLD RESULT ON NEW SEARCH
    if st.session_state.last_query != question:
        st.session_state.last_answer = None
        st.session_state.last_sources = []

    st.session_state.last_query = question

    with st.spinner("Searching policy documents..."):

        ans, src = answer_question(question)

        st.session_state.last_answer = ans
        st.session_state.last_sources = src

# ---------------- OUTPUT ----------------
if st.session_state.last_answer:

    st.markdown("## Result")

    st.success(st.session_state.last_answer)

with st.expander("📄 Sources"):
    st.success("Source: Databricks Volume (employee_handbook.txt)")
    st.caption("Retrieved using FAISS + Gemini embeddings over uploaded document")