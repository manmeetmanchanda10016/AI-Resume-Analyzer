
import json
import os
from io import BytesIO

import streamlit as st
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from pypdf import PdfReader
from openai import OpenAI
from dotenv import load_dotenv


# -------------------- CONFIGURATION --------------------

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

REPORT_SECTIONS = [
    ("strengths", "Strengths"),
    ("gaps", "Gaps"),
    ("missing_or_weak_skills", "Missing or Weak Skills"),
    ("improvement_suggestions", "Improvement Suggestions"),
    ("overall_summary", "Overall Summary"),
]


# -------------------- GROQ CLIENT --------------------

def get_client():

    if not API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Check your .env file."
        )

    return OpenAI(
        api_key=API_KEY,
        base_url="https://api.groq.com/openai/v1"
    )


# -------------------- RESUME EXTRACTION --------------------

def extract_resume(uploaded_file):

    file_name = uploaded_file.name.lower()

    if file_name.endswith(".pdf"):

        reader = PdfReader(uploaded_file)
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages).strip()

    elif file_name.endswith(".docx"):

        reader = Document(uploaded_file)
        paragraphs = []

        for paragraph in reader.paragraphs:
            paragraphs.append(paragraph.text)

        for table in reader.tables:
            for row in table.rows:
                for cell in row.cells:
                    paragraphs.append(cell.text)

        return "\n".join(paragraphs).strip()

    else:
        raise ValueError(
            "Unsupported file format. Upload a PDF or DOCX."
        )


# -------------------- LLM CALL 1 --------------------

def analyze_resume(resume_text, job_description):

    """Compare resume and job description using structured JSON."""

    client = get_client()

    instructions = """
    You compare resumes against job descriptions.

    Reply with JSON only, using exactly these keys.
    Every value must be a list of short strings.

    {
        "candidate_skills": [],
        "candidate_experience": [],
        "candidate_qualification": [],
        "required_skills": [],
        "preferred_skills": [],
        "matching_skills": [],
        "missing_skills": [],
        "gaps": []
    }

    Rules:
    - Use only information appearing in the resume or job description.
    - Never invent skills, employers, job titles, dates, or qualifications.
    - Missing skills are skills requested in the job description
      that are not identified in the resume.
    - Distinguish required skills from preferred skills.
    - Gaps should focus on experience, qualifications,
      responsibilities, and role requirements.
    - Do not assume that an unmentioned skill is unknown.
    - Leave a list empty when there is nothing to report.
    """

    user_message = f"""
    Compare this resume against this job description.

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    return json.loads(
        response.choices[0].message.content
    )


# -------------------- LLM CALL 2 --------------------

def generate_final_report(structured_analysis):

    """Convert structured analysis into readable resume feedback."""

    client = get_client()

    instructions = """
    You write short, honest resume feedback for a candidate.

    Reply with JSON only, using exactly these keys.
    Every value must be a string.

    {
        "strengths": "",
        "gaps": "",
        "missing_or_weak_skills": "",
        "improvement_suggestions": "",
        "overall_summary": ""
    }

    Rules:
    - The first four values must be Markdown bullet lists.
    - Write overall_summary as one short paragraph.
    - Never leave a value empty.
    - If a section has nothing to report, state that in one bullet.
    - Put specific tools and technologies in missing_or_weak_skills.
    - Put experience, qualifications, and responsibilities in gaps.
    - Base everything only on the supplied structured analysis.
    - Never invent anything new.
    - Never use the words "lacks", "lacking", "no experience",
      "no exposure", "does not know", or "does not have".
    - Refer to what is or is not identified in the resume,
      rather than making claims about the candidate's actual abilities.
    - Do not give a numeric score or percentage.
    - Make suggestions specific and actionable.
    """

    user_message = f"""
    Turn this structured data into resume feedback.

    {json.dumps(structured_analysis, indent=2)}
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": instructions
            },
            {
                "role": "user",
                "content": user_message
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )

    report = json.loads(
        response.choices[0].message.content
    )

    # Process every report section
    for key, _ in REPORT_SECTIONS:

        value = report.get(key, "")

        if isinstance(value, list):
            value = "\n".join(
                "- " + str(point) for point in value
            )

        report[key] = value or (
            "- Nothing further was identified from the provided resume."
        )

    return report


# -------------------- DOWNLOAD REPORT --------------------

def create_download_report(report, resume_name, job_title):

    """Create a formatted Word report and return its bytes."""

    document = Document()

    # Page margins
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)

    # Default font
    styles = document.styles
    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(10)

    # Title
    title = document.add_heading("Resume Analysis Report", 0)
    title.runs[0].font.color.rgb = RGBColor(31, 78, 121)

    document.add_paragraph(f"Resume: {resume_name}")
    document.add_paragraph(f"Job Role: {job_title}")

    document.add_paragraph(
        "This report compares the information identified in the "
        "provided resume against the supplied job description."
    )

    document.add_paragraph()

    # Add report sections
    for key, heading in REPORT_SECTIONS:

        document.add_heading(heading, level=1)

        content = report.get(key, "")

        if key == "overall_summary":
            document.add_paragraph(content)
            continue

        # Convert Markdown-style bullets into Word bullets
        for line in content.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("- "):

                paragraph = document.add_paragraph(
                    style="List Bullet"
                )

                paragraph.add_run(line[2:])

            else:
                document.add_paragraph(line)

    # Footer
    footer = section.footer.paragraphs[0]
    footer.text = "Generated by AI Resume Analyzer"

    # Save to memory
    buffer = BytesIO()
    document.save(buffer)
    buffer.seek(0)

    return buffer.getvalue()


# -------------------- STREAMLIT UI --------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")

st.caption(
    "Compare your resume against a job description "
    "and receive actionable feedback."
)

# Sidebar
with st.sidebar:

    st.header("About")

    st.write(
        "Upload your resume and paste a job description "
        "to identify matching skills, gaps, and improvements."
    )

    st.info("Supported formats: PDF and DOCX")


# Main inputs
col1, col2 = st.columns([1, 1])

with col1:

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx"]
    )

with col2:

    job_title = st.text_input(
        "Job title",
        placeholder="e.g. Machine Learning Intern"
    )

job_description = st.text_area(
    "Paste the job description",
    height=250,
    placeholder="Paste the complete job description here..."
)

analyze_button = st.button(
    "Analyze Resume",
    type="primary",
    use_container_width=True
)


# -------------------- ANALYSIS WORKFLOW --------------------

if analyze_button:

    if not API_KEY:

        st.error(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    elif not uploaded_file:

        st.warning("Please upload your resume.")

    elif not job_description.strip():

        st.warning("Please enter a job description.")

    else:

        try:

            with st.spinner("Extracting resume text..."):

                resume_text = extract_resume(uploaded_file)

            if not resume_text:

                st.error(
                    "No readable text was found in the resume. "
                    "If this is a scanned PDF, use OCR first."
                )

                st.stop()

            with st.spinner(
                "Analyzing resume against the job description..."
            ):

                structured_analysis = analyze_resume(
                    resume_text,
                    job_description
                )

            with st.spinner("Generating your final report..."):

                report = generate_final_report(
                    structured_analysis
                )

            # Store results in session state
            st.session_state["report"] = report

            st.session_state["structured_analysis"] = (
                structured_analysis
            )

            st.session_state["resume_name"] = uploaded_file.name

            st.session_state["job_title"] = (
                job_title.strip() or "Not specified"
            )

            st.success("Resume analysis completed!")

        except Exception as e:

            st.error(f"An error occurred: {e}")


# -------------------- DISPLAY RESULTS --------------------

if "report" in st.session_state:

    report = st.session_state["report"]

    st.divider()

    st.header("Resume Analysis Results")

    # Display report sections
    for key, heading in REPORT_SECTIONS:

        st.subheader(heading)

        content = report.get(key, "")

        if key == "overall_summary":

            st.write(content)

        else:

            st.markdown(content)

    # Download report
    st.divider()

    st.subheader("Download Your Report")

    docx_bytes = create_download_report(
        report,
        st.session_state["resume_name"],
        st.session_state["job_title"]
    )

    st.download_button(
        label="📥 Download Report (.docx)",
        data=docx_bytes,
        file_name="resume_analysis_report.docx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        use_container_width=True
    )

    # Optional: show structured analysis
    with st.expander("View detailed structured analysis"):

        st.json(st.session_state["structured_analysis"])
