# AI Resume Analyzer 🚀

An AI-powered resume analysis application built using **Python, Streamlit, and Large Language Models (LLMs)**. It analyzes a candidate's resume against a given job description, identifies skill matches and gaps, and generates actionable recommendations to improve the candidate's profile.

## ✨ Features

- **Resume Upload:** Upload resumes in PDF or DOCX format.
- **Resume Parsing:** Extract text from resumes, including paragraphs and tables.
- **Job Description Analysis:** Compare candidate qualifications and experience against job requirements.
- **Skill Matching:** Identify matching skills, missing skills, and preferred skills.
- **Gap Analysis:** Highlight areas where the candidate's profile does not align with the job description.
- **AI-Powered Recommendations:** Generate suggestions to improve the resume and strengthen the candidate's profile.
- **Downloadable Report:** Generate and download a professionally formatted DOCX analysis report.

## 🧠 How It Works

The application follows a two-stage LLM-based analysis pipeline:

**Stage 1: Structured Resume Analysis**

The first LLM call analyzes the resume and job description and extracts structured information, including:

- Candidate skills
- Candidate experience
- Qualifications
- Required and preferred skills
- Matching and missing skills
- Identified gaps

**Stage 2: Final Report Generation**

The second LLM call uses the structured analysis to generate:

- Strengths
- Gaps
- Missing or weak skills
- Improvement suggestions
- Overall summary

The final analysis is presented through the Streamlit interface and can be downloaded as a DOCX report.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Groq API | LLM inference |
| OpenAI Python SDK | API integration using Groq's compatible endpoint |
| PyPDF | PDF text extraction |
| python-docx | DOCX reading and report generation |
| python-dotenv | Environment variable management |
| JSON | Structured LLM responses |

## 📂 Project Structure

```text
AI-Resume-Analyzer/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
└── data/
    └── Sample resumes (optional)
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/manmeetmanchanda10016/AI-Resume-Analyzer.git
```

### 2. Navigate to the project directory

```bash
cd AI-Resume-Analyzer
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

Get your API key from [Groq Console](https://console.groq.com/).

**Important:** Never commit your `.env` file or expose your API key publicly.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

## 🚀 Future Improvements

- Resume scoring based on job requirements.
- Support for additional resume formats.
- More detailed experience and project analysis.
- Resume improvement and rewriting suggestions.
- Integration with additional LLM providers.

## 👨‍💻 Author

**Manmeet Singh Manchanda**

GitHub: [@manmeetmanchanda10016](https://github.com/manmeetmanchanda10016)

---

⭐ If you find this project interesting, consider giving the repository a star!