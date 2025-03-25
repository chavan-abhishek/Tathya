# frontend/app.py
import streamlit as st
import requests
import os
from pypdf import PdfReader

# Page configuration
st.set_page_config(page_title="Tathya Misinformation Detector", layout="wide")

# Display the logo at the top
st.markdown(
    "<div style='text-align: center;'><img src='https://i.imgur.com/HRY0JFl.png' width='150'></div>",
    unsafe_allow_html=True
)

# Title and description
st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🔍 Tathya Misinformation Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Analyze news articles or social media posts for credibility and bias.</p>", unsafe_allow_html=True)

# Backend API URL
API_BASE_URL = "http://127.0.0.1:8000"

# Input section
st.subheader("📝 Input Content", divider="blue")
col1, col2 = st.columns([2, 1])

extracted_text = ""

with col1:
    option = st.radio("Choose Input Type", ("Text", "PDF Upload"), horizontal=True)

    if option == "Text":
        content = st.text_area("Enter news or social media post:", height=150, placeholder="Type or paste content here...")
    else:
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf", "txt", "docx"], help="Select a file to analyze")
        if uploaded_file:
            # Upload file to backend
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            try:
                response = requests.post(f"{API_BASE_URL}/upload/", files=files)
                if response.status_code == 200:
                    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
                    # Extract text for display (optional)
                    if uploaded_file.type == "application/pdf":
                        pdf_reader = PdfReader(uploaded_file)
                        extracted_text = "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
                    elif uploaded_file.type == "text/plain":
                        extracted_text = uploaded_file.read().decode("utf-8")
                    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        from docx import Document
                        doc = Document(uploaded_file)
                        extracted_text = "\n".join([para.text for para in doc.paragraphs])
                    if extracted_text:
                        st.write("📜 Extracted Text:", extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text)
                    else:
                        st.warning("⚠️ No readable text found in file.")
                else:
                    st.error(f"⚠️ Upload failed: {response.text}")
            except requests.ConnectionError:
                st.error("⚠️ Backend not available. Please ensure the server is running.")

with col2:
    st.write("")  # Spacer
    query_button = st.button("🔍 Query Document", type="primary")
    report_button = st.button("🚨 Report Suspicious Content")

    if query_button:
        if option == "Text" and not content:
            st.error("⚠️ Please provide text content to query!")
        elif option == "PDF Upload" and not uploaded_file:
            st.error("⚠️ Please upload a file to query!")
        else:
            query = st.text_input("Enter your query about the content:", placeholder="e.g., Is this claim true?")
            if query:
                st.write(f"🔍 Querying: *{query}*")
                with st.spinner("Processing query..."):
                    try:
                        # Use POST for /query/ (updated backend will expect this)
                        response = requests.post(f"{API_BASE_URL}/query/", json={"query": query})
                        if response.status_code == 200:
                            result = response.json().get("response", {})
                            st.session_state["query_result"] = result
                        else:
                            st.error(f"⚠️ Query failed: {response.text}")
                    except requests.ConnectionError:
                        st.error("⚠️ Backend not available. Please ensure the server is running.")

    if report_button:
        if content or uploaded_file:
            st.success("✅ Content reported for review!")
        else:
            st.error("⚠️ No content to report!")

# Results section
if "query_result" in st.session_state:
    st.subheader("📊 Query Results", divider="blue")
    result = st.session_state["query_result"]
    col3, col4 = st.columns(2)
    with col3:
        status = "True" if result.get("credibility_score", 0) > 0.7 else "False" if result.get("credibility_score", 0) < 0.3 else "Uncertain"
        st.metric("🔎 Query Outcome", status,
                  delta="Credible" if status == "True" else "Check Details" if status == "Uncertain" else "Suspicious",
                  delta_color="green" if status == "True" else "red" if status == "False" else "gray")
        st.metric("Credibility Score", f"{result.get('credibility_score', 0):.2f}")
        st.metric("Mistakes Found", result.get("num_mistakes", 0))
    with col4:
        st.write("*📑 Analysis:*")
        st.info(result.get("analysis", "No analysis available"))
        st.write("*🔍 Sentiment:*", result.get("sentiment", "N/A"))
        st.write("*📚 Cross-Reference:*", result.get("cross_reference", "N/A"))
        st.write("*✅ Corrected Data:*", result.get("corrected_data", "N/A"))

# Footer
st.markdown("---")
st.caption("🚀 Built by *Team Tathya* for IEEE Hackathon 2025")