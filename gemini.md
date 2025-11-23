# Study Notes Assistant Agent — Gemini CLI Project

## 1. Project Overview
You are building an AI agent that helps students efficiently study PDFs. The agent will:

- Summarize uploaded PDFs (using PyPDF)
- Generate quizzes (MCQs or mixed-style)
- Create flashcards for key terms and concepts
- UI: Streamlit (recommended) or HTML/CSS
- Backend: OpenAgents SDK
- Model: Gemini (via Gemini CLI)
- Tools: Context7 MCP server

The goal is to provide students with a full study workflow: summary → quiz → flashcards.

---

## 2. Libraries & Tools (Mandatory)
These libraries/tools are required for the project:

- **PyPDF** → For extracting text from PDFs  
- **Gemini CLI** → To interact with the AI model  
- **OpenAgents SDK** → For agent creation and tool binding  
- **Streamlit** (or HTML/CSS) → For UI display  
- **Context7 MCP** → Tool provider for AI integration  

---

## 3. Technical Rules
Follow these rules strictly:

1. **Zero-Bloat Rule**  
   - Write only what is needed. No extra code, decorators, or verbose error handling.

2. **API & Model Configuration**  
   - Gemini base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`  
   - Model: `gemini-2.0-flash`  
   - API key: via environment variable `GEMINI_API_KEY`  

3. **SDK Rule**  
   - Only use OpenAgents SDK, **do not use standard OpenAI library**.  
   - Every function must match tool documentation exactly.

4. **Error Recovery**  
   - If you encounter errors like `SyntaxError`, `ImportError`, `AttributeError` → stop immediately and check documentation.  
   - Re-run:  
     ```bash
     @get-library-docs openai-agents
     ```

5. **Dependencies**  
   - Install all required packages using your preferred package manager (`uv` or `pip`).

---

## 4. Project File Structure
Place all files inside the root folder for Gemini CLI:
study_notes_agent/
├── .gemnii/
│ └── settings.json # Contains API key
├── gemini.md # This instruction file
├── main.py # Agent + tool logic
├── pyproject.toml
├── README.md
├── .env # Optional env variables
└── uv.lock


Do **not** create extra subfolders outside this structure.

---

## 5. Implementation Flow
Follow this workflow:

### Step 1 — Load Docs & Verify Syntax
- Open Gemini CLI
- Run:
```bash
@get-library-docs openai-agents


Understand:

Tool decorators
Agent initialization
Model calling format
Tool registration
Re-read docs if unclear.
Step 2 — Tool Functions (main.py)
Define three tools:
extract_pdf_text(file_path)
Use PyPDF to read the PDF
Return raw text
generate_summary(text)
Pass text to Gemini AI
Generate concise, readable summary
Highlight key terms, formulas, definitions
generate_quiz(text)
Read the original PDF text
Generate MCQs or mixed quizzes
Provide answers for each question

generate_flashcards(summary_text)

Take summarized text
Create flashcards (Front: Term/Question, Back: Answer/Explanation)
Group by chapter/topic if possible

🔴 Important: Function definitions must strictly follow OpenAgents SDK documentation.

Step 3 — Agent Setup (main.py)

Set Gemini base URL
Use model gemini-2.0-flash
Bind all three tools to the agent
Add a static system prompt:

"You are a Study Notes Assistant. Summarize PDFs, then generate quizzes, then create flashcards."

Step 4 — UI Workflow (Streamlit or HTML/CSS)

User uploads PDF
Extract text using PyPDF
Display summary
Show Create Quiz button → display quiz
Show Generate Flashcards button → display flashcards
UI can use cards, blocks, containers, or other layouts

6. Testing Cases

Ensure all features work:
PDF upload → Summary displays correctly
Create Quiz → Quiz displays and answers are correct
Generate Flashcards → Flashcards display properly, grouped by topic
Large PDFs → Summary + quiz + flashcards are still accurate and readable

7. Final Submission Rules

Commit everything to GitHub:
Source code
README.md
Screenshot of Gemini CLI prompt
Paste this gemini.md inside your root folder

8. Notes

Agent must never invent content not present in the PDF
Keep outputs clear, concise, and student-friendly
Always follow library/tool documentation strictly