import streamlit as st
import pdfplumber
import re
from groq import Groq

# -------------------------------
# PAGE CONFIG
# -------------------------------

st.set_page_config(
    page_title="Resume Job Match Scorer",
    page_icon="📄",
    layout="wide"
)

# -------------------------------
# GROQ CLIENT
# -------------------------------

client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

# -------------------------------
# UI
# -------------------------------

st.title("📄 AI Resume Job Match Scorer")

st.write(
    "Upload a resume and paste a job description to get AI-powered feedback."
)

resume = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"]
)

job_description = st.text_area(
    "Paste Job Description",
    height=250
)

# -------------------------------
# BUTTONS
# -------------------------------

col1, col2 = st.columns(2)

analyze = col1.button("Analyze Resume")
rewrite = col2.button("Rewrite Resume")

# -------------------------------
# EXTRACT RESUME TEXT
# -------------------------------

resume_text = ""

if resume is not None:
    try:
        with pdfplumber.open(resume) as pdf:
            for page in pdf.pages:
                text = page.extract_text()

                if text:
                    resume_text += text + "\n"

    except Exception as e:
        st.error(f"Error reading PDF: {e}")

# -------------------------------
# ANALYZE RESUME
# -------------------------------

if analyze:

    if resume is None:
        st.error("Please upload a resume.")
        st.stop()

    if job_description.strip() == "":
        st.error("Please paste a job description.")
        st.stop()

    prompt = f"""
You are an ATS Resume Analyzer.

Return the response EXACTLY in this format:

Match Score: <number>

Matching Skills:
- skill1
- skill2

Missing Skills:
- skill1
- skill2

ATS Suggestions:
- suggestion1
- suggestion2

Resume Improvements:
- improvement1
- improvement2

Interview Tips:
- tip1
- tip2

Resume:
{resume_text}

Job Description:
{job_description}
"""

    try:

        with st.spinner("Analyzing Resume..."):

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )

        result = response.choices[0].message.content

        st.success("Analysis Completed")

        match = re.search(
            r"Match Score:\s*(\d+)",
            result,
            re.IGNORECASE
        )

        if match:
            score = int(match.group(1))

            st.subheader("Match Score")

            st.progress(score)

            st.metric(
                "Score",
                f"{score}%"
            )

        st.subheader("AI Analysis")

        st.write(result)

        st.download_button(
            label="Download Analysis",
            data=result,
            file_name="resume_analysis.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Error: {e}")

# -------------------------------
# REWRITE RESUME
# -------------------------------

if rewrite:

    if resume is None:
        st.error("Please upload a resume.")
        st.stop()

    if job_description.strip() == "":
        st.error("Please paste a job description.")
        st.stop()

    rewrite_prompt = f"""
Rewrite this resume so it better matches the job description.

Requirements:
- Improve ATS compatibility
- Add relevant keywords naturally
- Improve formatting
- Keep all information truthful
- Do not invent experience

Resume:
{resume_text}

Job Description:
{job_description}
"""

    try:

        with st.spinner("Rewriting Resume..."):

            rewrite_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": rewrite_prompt
                    }
                ],
                temperature=0.3
            )

        rewritten_resume = rewrite_response.choices[0].message.content

        st.success("Resume Rewritten")

        st.subheader("Optimized Resume")

        st.write(rewritten_resume)

        st.download_button(
            label="Download Rewritten Resume",
            data=rewritten_resume,
            file_name="optimized_resume.txt",
            mime="text/plain"
        )

    except Exception as e:
        st.error(f"Error: {e}")