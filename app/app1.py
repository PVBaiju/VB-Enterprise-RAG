"""
Enterprise Document Q&A Assistant - Streamlit Web App
Powered by Groq AI + Local Embeddings (No Databricks for now)
"""

# Suppress PyTorch/Streamlit compatibility warning
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import os
from dotenv import load_dotenv
from rag_utils import (
    answer_question,
    extract_text_from_file,
    chunk_text,
    validate_credentials,
    add_documents_to_store,
)

# Load environment variables from .env file
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Enterprise Document Q&A Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
    }
    .success-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        margin: 10px 0;
    }
    .error-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        margin: 10px 0;
    }
    .info-box {
        padding: 15px;
        border-radius: 5px;
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        margin: 10px 0;
    }
    .source-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #f5f5f5;
        border-left: 4px solid #ff9800;
        margin: 5px 0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Check credentials on startup
credentials_valid, missing_vars = validate_credentials()

# Main content - Display BEFORE checking credentials
st.title("📚 Enterprise Document Q&A Assistant")
st.caption("Powered by Groq AI + Local Embeddings | Ask questions about your documents")

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    if not credentials_valid:
        st.error("❌ Configuration Required")
        st.error(f"**Missing variables:** {', '.join(missing_vars)}")
        with st.expander("📋 How to Configure", expanded=True):
            st.markdown("""
            ### Step 1: Create `.env` file
            ```bash
            cp .env.sample .env
            ```
            
            ### Step 2: Add your Google Gemini API key
            ```
            GOOGLE_API_KEY=your_google_api_key_here
            ```
            
            ### Step 3: Install dependencies
            ```bash
            pip install -r requirements.txt
            ```
            
            ### Step 4: Run the app
            ```bash
            streamlit run app.py
            ```
            
            ### Get Google API Key
            1. Visit https://aistudio.google.com/app/apikey
            2. Click "Create API Key" → "Create API key in new project"
            3. Copy the API key
            4. Paste in `.env` as GOOGLE_API_KEY
            
            **Note:** Google Gemini free tier includes 15 RPM quota (sufficient for testing)
            """)
    else:
        st.success("✓ Configuration valid - Ready to use!")
    
    st.divider()
    
    st.markdown("""
    ### About
    Enterprise Document Q&A Assistant powered by:
    - **Google Gemini** - Free AI model
    - **SentenceTransformers** - Free embeddings
    - **Streamlit** - Web interface
    """)

# Show warning but let user see the UI
if not credentials_valid:
    st.warning(f"⚠️ **Configuration Required**\n\nPlease configure the missing environment variables to use the Q&A features.\n\nMissing: {', '.join(missing_vars)}\n\nSee sidebar for setup instructions.")

# Create tabs for different features
tab1, tab2, tab3 = st.tabs(["💬 Q&A", "📤 Document Upload", "ℹ️ Help"])

# ============= TAB 1: Q&A =============
with tab1:
    st.header("Ask Questions About Your Documents")
    
    if not credentials_valid:
        st.error("🔴 **Configuration Required**")
        st.markdown(f"""
        The Q&A feature requires Groq API configuration. 
        
        **Missing variables:**
        - {chr(10).join(['- ' + var for var in missing_vars])}
        
        Please see the **Configuration** section in the sidebar to set these up.
        """)
    else:
        col1, col2 = st.columns([4, 1])
        with col1:
            question = st.text_input(
                "Enter your question",
                placeholder="e.g., What is the leave policy?",
                label_visibility="collapsed"
            )
        
        with col2:
            ask_button = st.button("🔍 Ask", use_container_width=True)
        
        if ask_button and question:
            try:
                with st.spinner("🔄 Searching documents and generating answer..."):
                    answer, sources = answer_question(question)
                
                # Display answer
                st.subheader("📋 Answer")
                st.markdown(f"""
                <div class="success-box">
                {answer}
                </div>
                """, unsafe_allow_html=True)
                
                # Display sources
                st.subheader("📄 Sources")
                if sources:
                    for src in sources:
                        st.markdown(f"""
                        <div class="source-box">
                        <strong>📄 {src['file_name']}</strong><br>
                        <em>{src['chunk_preview']}</em>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No sources found for this query.")
                
                # Store in session for history
                if "queries" not in st.session_state:
                    st.session_state.queries = []
                st.session_state.queries.append({"question": question, "answer": answer})
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
        
        # Show recent queries
        if "queries" in st.session_state and st.session_state.queries:
            st.divider()
            st.subheader("📝 Recent Queries")
            for i, q in enumerate(reversed(st.session_state.queries[-5:]), 1):
                with st.expander(f"{i}. {q['question'][:50]}..."):
                    st.write(q['answer'])

# ============= TAB 2: Document Upload =============
with tab2:
    st.header("📤 Upload Documents")
    
    st.info("""
    **Upload documents** - They will be processed and stored locally in memory for Q&A.
    
    Supported formats: PDF, DOCX, TXT
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Select documents to upload",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_files:
        st.subheader("📋 File Preview & Processing")
        
        for uploaded_file in uploaded_files:
            with st.expander(f"📄 {uploaded_file.name}"):
                try:
                    # Read file
                    file_bytes = uploaded_file.read()
                    text = extract_text_from_file(file_bytes, uploaded_file.name)
                    
                    # Show file info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("File Size", f"{len(file_bytes) / 1024:.2f} KB")
                    with col2:
                        st.metric("Text Length", f"{len(text)} chars")
                    with col3:
                        chunks = chunk_text(text)
                        st.metric("Chunks", len(chunks))
                    
                    # Show preview
                    st.write("**Preview:**")
                    st.text_area(
                        "Content preview (first 500 chars)",
                        value=text[:500] + "..." if len(text) > 500 else text,
                        height=200,
                        disabled=True
                    )
                    
                    # ADD DOCUMENTS TO STORE
                    chunks = chunk_text(text)
                    add_documents_to_store(chunks, uploaded_file.name)
                    
                    st.success(f"✓ Successfully processed and added {uploaded_file.name} ({len(chunks)} chunks)")
                
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")

# ============= TAB 3: Help =============
with tab3:
    st.header("ℹ️ Help & Documentation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚀 Getting Started")
        st.markdown("""
        ### Step 1: Setup Groq API
        1. Visit https://console.groq.com
        2. Create account
        3. Generate API key
        4. Add to `.env` file
        
        ### Step 2: Prepare Documents
        1. Upload PDFs, DOCX, or TXT files
        2. Ask questions about them
        """)
    
    with col2:
        st.subheader("❓ Example Questions")
        example_questions = [
            "What is the leave policy?",
            "What are the reimbursement rules?",
            "What is the onboarding process?",
        ]
        
        for q in example_questions:
            st.markdown(f"- {q}")
    
    st.divider()
    
    st.subheader("🔧 Environment Variables Required")
    st.code("""
GROQ_API_KEY=gsk_your_groq_api_key_here
    """)
    
    st.subheader("🎯 Key Features")
    features = [
        "🔍 Document search using embeddings",
        "🤖 LLM-powered answers using Groq AI",
        "📄 Support for PDF, DOCX, and TXT files",
        "⚡ Fast local processing",
        "� Free embeddings (no API needed)",
        "📊 Document chunking",
    ]
    for feature in features:
        st.markdown(f"- {feature}")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
<p>Enterprise Document Q&A Assistant | Built with Groq AI + Streamlit</p>
<p>© 2026 Enterprise Solutions</p>
</div>
""", unsafe_allow_html=True)
