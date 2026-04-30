import streamlit as st
from dotenv import load_dotenv
from databricks_rag_utils import answer_question

load_dotenv()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="VisionBoard HR Portal",
    page_icon="🏢",
        layout="wide"
)

# ---------------- CUSTOM HEADER ----------------
#st.markdown(
   # """
   # <style>
    #    .main-header {
        #    font-size: 38px;
       #     font-weight: 700;
       #     color: #1f4e79;
      #  }
     #   .sub-header {
      #      font-size: 16px;
     #       color: gray;
      #  }
     #   .card {
      #      padding: 15px;
     #       border-radius: 12px;
     #       background-color: #f5f7fb;
     #       border: 1px solid #e0e0e0;
     #   }
   # </style>
   # """,
  #  unsafe_allow_html=True
#)
# ---------------- LOGO ----------------
#st.image("visionboard-edit.jpg", width=120)

# ---------------- HEADER ----------------
st.markdown("""
<div style="text-align:center;">
    <h1> VisionBoard HR Portal</h1>
    <p style="color:gray;">Smart Employee Policy Assistant</p>
</div>
""", unsafe_allow_html=True)

#st.markdown("<div class='main-header'>🏢 VisionBoard HR Assistant</div>", unsafe_allow_html=True)
#st.markdown("<div class='sub-header'>Smart Employee Policy Knowledge System</div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([2, 1])

with col1:

    st.markdown("### 💬 Ask HR Questions")

    question = st.text_input(
        "Search policies",
        placeholder="e.g. leave policy, parental leave, benefits"
    )

    search_btn = st.button("🔍 Search")

    if search_btn and question:

        with st.spinner("Searching company handbook..."):

            answer, sources = answer_question(question)

        st.markdown("## 🧠 Answer")

        st.success(answer)

        st.markdown("### 📄 Source")
        st.info("Data retrieved from employee_handbook.txt (Databricks Volume)")

with col2:

    st.markdown("### 💡 Quick Access")

    if st.button("📌 Leave Policy"):
        answer, _ = answer_question("leave policy")
        st.success(answer)

    if st.button("💰 Benefits"):
        answer, _ = answer_question("benefits")
        st.success(answer)

    if st.button("🧭 Onboarding"):
        answer, _ = answer_question("onboarding process")
        st.success(answer)

    if st.button("⏰ Working Hours"):
        answer, _ = answer_question("working hours")
        st.success(answer)

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("Powered by Databricks + FAISS + Gemini + Groq")