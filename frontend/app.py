import streamlit as st
import requests
from pypdf import PdfReader

def extract_text(file):
    pdf_reader = PdfReader(file)
    return "\n".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

# Page configuration
st.set_page_config(page_title="Tathya Misinformation Detector", layout="wide")

# Display the logo at the top
st.markdown(
    "<div style='text-align: center;'><img src='https://i.imgur.com/HRY0JFl.png' width='150'></div>",
    unsafe_allow_html=True
)

# Title and description with enhanced UI
st.markdown("<h1 style='text-align: center; color: #1f77b4;'>🔍 Tathya Misinformation Detector</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 18px;'>Analyze news articles or social media posts for credibility and bias.</p>", unsafe_allow_html=True)

# Rest of the code remains unchanged...

# Input section
st.subheader("📝 Input Content", divider="blue")
col1, col2 = st.columns([2, 1])  # Two-column layout

with col1:
    option = st.radio("Choose Input Type", ("Text", "PDF Upload"), horizontal=True)
    content = ""
    if option == "Text":
        content = st.text_area("Enter news or social media post:", height=150, placeholder="Type or paste content here...")
    else:
        uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], help="Select a PDF to analyze")
        if uploaded_file:
            content = extract_text(uploaded_file)
            st.write("*📄 Extracted Text Preview*:")
            st.text_area("", value=content[:500] + "..." if len(content) > 500 else content, height=100, disabled=True)

with col2:
    st.write("")  # Spacer
    analyze_button = st.button("🔍 Analyze", type="primary")
    report_button = st.button("🚨 Report Suspicious Content")

    if analyze_button:
        if content:
            try:
                response = requests.post("http://127.0.0.1:8000/analyze", json={"content": content})
                result = response.json()
                st.session_state["result"] = result  # Store result in session state
            except requests.ConnectionError:
                st.session_state["result"] = {
                    "credibility_score": 50,  # Default fallback value
                    "sentiment": "NEUTRAL",
                    "needs_fact_check": "N/A",
                    "analysis": "Processing... (Backend not available)"
                }
        else:
            st.error("⚠️ Please provide content to analyze!")

    if report_button:
        if content:
            st.success("✅ Content reported for review!")
        else:
            st.error("⚠️ No content to report!")

# Results section
if "result" in st.session_state:
    st.subheader("📊 Analysis Results", divider="blue")
    result = st.session_state["result"]

    # Fixing credibility score issue
    credibility_score = result["credibility_score"]
    credibility_percentage = credibility_score if credibility_score > 1 else credibility_score * 100  # Handle both cases

    col3, col4 = st.columns(2)

    with col3:
        st.metric("🔎 Credibility Score", f"{credibility_percentage:.0f}%", help="Score from 0% to 100%")
        st.write(f"*🗣 Sentiment:* {result['sentiment']}")

    with col4:
        st.write(f"*📌 Needs Fact-Check:* {result.get('needs_fact_check', 'N/A')}")
        st.write("*📑 Analysis Details:*")
        st.info(result["analysis"])

# Footer
st.markdown("---")
st.caption("🚀 Built by *Team Tathya* for Hackathon 2025")