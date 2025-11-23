import os
import streamlit as st
from PyPDF2 import PdfReader
from openai import OpenAI
from agents import Agent, FunctionTool, RunContextWrapper
from agents.strict_schema import ensure_strict_json_schema
from pydantic import BaseModel, Field
from typing import Any
from pathlib import Path

# --- Configuration from gemini.md ---
GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/openai/"
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Initialize OpenAI client for Gemini ---
client = OpenAI(
    api_key=GEMINI_API_KEY,
    base_url=GEMINI_API_BASE,
)

# --- Core Logic Functions (plain Python functions) ---

def _extract_pdf_text(file_path: str) -> str:
    r"""
    Extracts text from a PDF file.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return ""

def _generate_summary(text: str) -> str:
    r"""
    Generates a concise, readable summary from the provided text using Gemini AI.
    Highlights key terms, formulas, and definitions.
    """
    if not text:
        return "No text provided for summarization."
    
    prompt = f"""Summarize the following text concisely and clearly.
Highlight key terms, formulas, and definitions:

{text}"""
    try:
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return "Failed to generate summary."

def _generate_quiz(text: str) -> str:
    r"""
    Generates multiple-choice or mixed-style quiz questions from the original PDF text.
    Provides answers for each question.
    """
    if not text:
        return "No text provided for quiz generation."

    prompt = f"""Generate a quiz (mix of multiple-choice and short answer questions)
from the following text. Provide the answers immediately after each question:

{text}"""
    try:
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating quiz: {e}")
        return "Failed to generate quiz."

def _generate_flashcards(summary_text: str) -> str:
    r"""
    Creates flashcards (Front: Term/Question, Back: Answer/Explanation) from summarized text.
    Attempts to group by chapter/topic if possible.
    """
    if not summary_text:
        return "No summarized text provided for flashcard generation."

    prompt = f"""Create flashcards from the following summarized text.
Format each flashcard as 'Front: [Term/Question] | Back: [Answer/Explanation]'.
Group flashcards by topic or concept if natural:\n\n{summary_text}"""
    try:
        response = client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error generating flashcards: {e}")
        return "Failed to generate flashcards."


class ExtractPdfTextParams(BaseModel):
    """Parameters for extracting text from a PDF file."""
    file_path: str = Field(description="The path to the PDF file.")

async def on_invoke_extract_pdf_text(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed_params = ExtractPdfTextParams.model_validate_json(args)
    return _extract_pdf_text(parsed_params.file_path)


class GenerateSummaryParams(BaseModel):
    """Parameters for generating a summary from text."""
    text: str = Field(description="The text to summarize.")

async def on_invoke_generate_summary(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed_params = GenerateSummaryParams.model_validate_json(args)
    return _generate_summary(parsed_params.text)


class GenerateQuizParams(BaseModel):
    """Parameters for generating a quiz from text."""
    text: str = Field(description="The text to generate a quiz from.")

async def on_invoke_generate_quiz(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed_params = GenerateQuizParams.model_validate_json(args)
    return _generate_quiz(parsed_params.text)


class GenerateFlashcardsParams(BaseModel):
    """Parameters for generating flashcards from summarized text."""
    summary_text: str = Field(description="The summarized text for flashcard generation.")

async def on_invoke_generate_flashcards(ctx: RunContextWrapper[Any], args: str) -> str:
    parsed_params = GenerateFlashcardsParams.model_validate_json(args)
    return _generate_flashcards(parsed_params.summary_text)


# --- Agent Setup ---
# Wrap the core logic functions as FunctionTool objects for the Agent
tool_extract_pdf_text = FunctionTool(
    _extract_pdf_text,
    description="Extracts text from a PDF file.",
    params_json_schema=ensure_strict_json_schema(ExtractPdfTextParams.model_json_schema()),
    on_invoke_tool=on_invoke_extract_pdf_text,
    strict_json_schema=True
)
tool_generate_summary = FunctionTool(
    _generate_summary,
    description="Generates a concise, readable summary from the provided text using Gemini AI.",
    params_json_schema=ensure_strict_json_schema(GenerateSummaryParams.model_json_schema()),
    on_invoke_tool=on_invoke_generate_summary,
    strict_json_schema=True
)
tool_generate_quiz = FunctionTool(
    _generate_quiz,
    description="Generates multiple-choice or mixed-style quiz questions from the original PDF text.",
    params_json_schema=ensure_strict_json_schema(GenerateQuizParams.model_json_schema()),
    on_invoke_tool=on_invoke_generate_quiz,
    strict_json_schema=True
)
tool_generate_flashcards = FunctionTool(
    _generate_flashcards,
    description="Creates flashcards (Front: Term/Question, Back: Answer/Explanation) from summarized text.",
    params_json_schema=ensure_strict_json_schema(GenerateFlashcardsParams.model_json_schema()),
    on_invoke_tool=on_invoke_generate_flashcards,
    strict_json_schema=True
)

assistant_agent = Agent(
    name="StudyNotesAssistant",
    instructions=(
        "You are a Study Notes Assistant. Your primary goal is to help students efficiently study PDFs. "
        "Summarize uploaded PDFs, then generate quizzes, then create flashcards. "
        "Use the provided tools to achieve these tasks."
    ),
    model=GEMINI_MODEL,
    tools=[tool_extract_pdf_text, tool_generate_summary, tool_generate_quiz, tool_generate_flashcards],
)
# --- Streamlit UI Workflow ---
st.title("📚 Study Notes Assistant")

uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    # Save uploaded file temporarily using pathlib for robust path handling
    temp_dir = Path(r"C:\Users\Hydra Sanwal\.gemini\tmp\8c08de96a4d8eea83896343b3c8771c78c053a1b43e83d0d18d28f123efeceaa")
    temp_dir.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    file_path = temp_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Extract text using the core logic function
    with st.spinner("Extracting text from PDF..."):
        pdf_text = _extract_pdf_text(str(file_path)) # Pass string path to PyPDF2
    
    if pdf_text:
        st.subheader("Extracted Text (partial view)")
        st.text_area("PDF Content", pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text, height=300)

        # Generate Summary
        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                summary = _generate_summary(pdf_text)
            st.subheader("Summary")
            st.write(summary)
            st.session_state['summary'] = summary # Store summary for flashcards

        # Generate Quiz
        if st.button("Generate Quiz"):
            with st.spinner("Generating quiz..."):
                quiz = _generate_quiz(pdf_text)
            st.subheader("Quiz")
            st.write(quiz)

        # Generate Flashcards (requires summary)
        if 'summary' in st.session_state and st.session_state['summary']:
            if st.button("Generate Flashcards"):
                with st.spinner("Generating flashcards..."):
                    flashcards = _generate_flashcards(st.session_state['summary'])
                st.subheader("Flashcards")
                st.write(flashcards)
        elif st.button("Generate Flashcards (Summary not yet generated)", disabled=True):
             st.info("Please generate a summary first to create flashcards.")
    else:
        st.error("Could not extract text from the PDF. Please try another file.")

# Ensure GEMINI_API_KEY is set
if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY environment variable is not set. Please set it to interact with the Gemini API.")