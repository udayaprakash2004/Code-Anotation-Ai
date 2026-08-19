import ast
import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from fpdf import FPDF
from groq import Groq


# ============================================================
# Code=Annotation-AI
# Professional code analysis, correction and local execution
# ============================================================

st.set_page_config(
    page_title="Code=Annotation-AI",
    page_icon="</>",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PROJECT_URL = "https://github.com/udayaprakash2004/Code-Anotation-Ai"
MAX_CODE_CHARS = 30000
RUN_TIMEOUT = 8
RUNNER_ENABLED = os.getenv("CODESENSE_LOCAL_RUNNER", "true").lower() == "true"


# ============================================================
# BACKGROUND IMAGE
# ============================================================
def get_background_css():
    bg_path = Path(__file__).parent / "background.png"

    if not bg_path.exists():
        return """
        .stApp {
            background: #f4f6f8;
        }
        """

    encoded = base64.b64encode(bg_path.read_bytes()).decode("utf-8")

    return f"""
    .stApp {{
        background-image:
            linear-gradient(rgba(19, 27, 43, 0.38), rgba(19, 27, 43, 0.38)),
            url("data:image/png;base64,{encoded}");
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
    }}
    """


# ============================================================
# PROFESSIONAL UI
# ============================================================
st.markdown(
    f"""
<style>

{get_background_css()}

html, body, [class*="css"] {{
    font-family: "Segoe UI", Arial, sans-serif;
}}

[data-testid="stHeader"] {{
    background: rgba(255,255,255,0.94);
    border-bottom: 1px solid #d8dee7;
}}

.block-container {{
    max-width: 1450px;
    padding-top: 0.8rem;
    padding-bottom: 2rem;
}}

header[data-testid="stHeader"] {{
    height: 2.8rem;
}}

.app-shell {{
    background: rgba(255,255,255,0.97);
    border: 1px solid #d9e0e8;
    border-radius: 12px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.14);
    overflow: hidden;
}}

.topbar {{
    height: 66px;
    background: #ffffff;
    border-bottom: 1px solid #dce2e9;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
}}

.brand {{
    font-size: 22px;
    font-weight: 750;
    color: #182230;
    letter-spacing: -0.3px;
}}

.brand-mark {{
    color: #315f89;
}}

.top-right {{
    color: #667384;
    font-size: 13px;
}}

.workspace {{
    padding: 18px;
    background: #f7f9fb;
}}

.panel {{
    background: #ffffff;
    border: 1px solid #d8e0e8;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(16,24,40,0.05);
}}

.panel-title {{
    height: 48px;
    display: flex;
    align-items: center;
    padding: 0 16px;
    background: #ffffff;
    border-bottom: 1px solid #e1e6ec;
    color: #283544;
    font-size: 14px;
    font-weight: 700;
}}

.status-dot {{
    width: 8px;
    height: 8px;
    background: #4d8b62;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
}}

.editor-note {{
    color: #6a7685;
    font-size: 12px;
    padding: 8px 2px 4px;
}}

.note {{
    background: #ffffff;
    color: #263241;
    border: 1px solid #d9e0e8;
    border-radius: 8px;
    padding: 12px 14px;
    line-height: 1.55;
}}

.metric-card {{
    background: #ffffff;
    border: 1px solid #d9e0e8;
    border-radius: 8px;
    padding: 12px;
    text-align: center;
}}

.metric-label {{
    color: #718096;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: .5px;
}}

.metric-value {{
    color: #24384d;
    font-size: 22px;
    font-weight: 750;
    margin-top: 2px;
}}

.footer {{
    text-align: center;
    color: #e9eef5;
    font-size: 12px;
    padding: 18px;
}}

.footer a {{
    color: #ffffff;
    text-decoration: none;
    font-weight: 650;
}}

/* Make Streamlit's language selector / select bars WHITE */
div[data-baseweb="select"] > div {{
    background: #ffffff !important;
    color: #1f2937 !important;
    border: 1px solid #cfd7e1 !important;
    box-shadow: none !important;
}}

div[data-baseweb="select"] span {{
    color: #1f2937 !important;
}}

div[data-baseweb="popover"] {{
    background: #ffffff !important;
}}

/* White code-writing area */
.stTextArea textarea {{
    background: #ffffff !important;
    color: #17202b !important;
    border: 1px solid #cbd5df !important;
    border-radius: 7px !important;
    font-family: Consolas, "Courier New", monospace !important;
    font-size: 14px !important;
    line-height: 1.55 !important;
    box-shadow: inset 0 1px 3px rgba(0,0,0,.04) !important;
}}

.stTextArea textarea:focus {{
    border-color: #6d8eac !important;
    box-shadow: 0 0 0 1px #6d8eac !important;
}}

/* White input boxes */
.stTextInput input {{
    background: #ffffff !important;
    color: #17202b !important;
    border: 1px solid #cbd5df !important;
}}

/* Professional buttons */
.stButton > button,
.stDownloadButton > button {{
    background: #ffffff;
    color: #2b4056;
    border: 1px solid #bdc9d5;
    border-radius: 7px;
    font-weight: 650;
    min-height: 40px;
}}

.stButton > button:hover,
.stDownloadButton > button:hover {{
    border-color: #597b9b;
    color: #1d486d;
    background: #f7fafc;
}}

button[kind="primary"] {{
    background: #315f89 !important;
    color: #ffffff !important;
    border-color: #315f89 !important;
}}

button[kind="primary"]:hover {{
    background: #274e73 !important;
}}

.stTabs [data-baseweb="tab-list"] {{
    gap: 0;
    background: #ffffff;
    border-bottom: 1px solid #dce2e8;
}}

.stTabs [data-baseweb="tab"] {{
    background: #ffffff !important;
    color: #637184 !important;
    border-radius: 0 !important;
    padding: 10px 16px;
    font-weight: 600;
}}

.stTabs [aria-selected="true"] {{
    color: #284e70 !important;
    border-bottom: 2px solid #315f89 !important;
}}

div[data-testid="stExpander"] {{
    background: #ffffff;
    border: 1px solid #dce2e8;
}}

</style>

<div class="app-shell">
    <div class="topbar">
        <div class="brand"><span class="brand-mark">Code=</span>Annotation-AI</div>
        <div class="top-right">Code analysis · correction · complexity · testing</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# GROQ KEY
# ============================================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error(
        "GROQ_API_KEY is not configured. Add it in Streamlit Secrets "
        "or as an environment variable."
    )
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "code": "",
    "language": "Python",
    "result": None,
    "local_checks": [],
    "run_output": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# STATIC ANALYSIS
# ============================================================
def bracket_check(code):
    pairs = {"(": ")", "[": "]", "{": "}"}
    reverse = {")": "(", "]": "[", "}": "{"}
    stack = []
    checks = []

    in_string = False
    quote = None
    escaped = False

    for line_no, line in enumerate(code.splitlines(), 1):
        for ch in line:
            if escaped:
                escaped = False
                continue

            if in_string:
                if ch == "\\":
                    escaped = True
                elif ch == quote:
                    in_string = False
                    quote = None
                continue

            if ch in ("'", '"'):
                in_string = True
                quote = ch
            elif ch in pairs:
                stack.append((ch, line_no))
            elif ch in reverse:
                if not stack or stack[-1][0] != reverse[ch]:
                    return [{
                        "severity": "error",
                        "line": line_no,
                        "title": "Mismatched bracket or brace",
                        "message": f"Unexpected '{ch}' on line {line_no}."
                    }]
                stack.pop()

    if stack:
        opening, line_no = stack[-1]
        checks.append({
            "severity": "error",
            "line": line_no,
            "title": "Missing closing bracket",
            "message": (
                f"'{opening}' opened on line {line_no} "
                "does not have a matching closing symbol."
            ),
        })
    else:
        checks.append({
            "severity": "success",
            "line": None,
            "title": "Balanced delimiters",
            "message": "No unmatched (), [], or {} were detected.",
        })

    return checks


def python_check(code):
    try:
        ast.parse(code)
        return [{
            "severity": "success",
            "line": None,
            "title": "Python syntax is valid",
            "message": "The Python parser accepted the source code.",
        }]
    except SyntaxError as e:
        return [{
            "severity": "error",
            "line": e.lineno,
            "title": e.msg or "Python syntax error",
            "message": (
                f"Line {e.lineno or '?'}: "
                f"{e.text.strip() if e.text else 'Check this statement.'}"
            ),
        }]


def semicolon_check(code, language):
    if language not in ("C++", "Java"):
        return []

    checks = []
    declaration = re.compile(
        r"^(?:const\s+)?(?:unsigned\s+|signed\s+)?"
        r"(?:int|long|short|float|double|char|bool|string|String|"
        r"boolean|auto|size_t)\s+.+"
    )

    for line_no, raw in enumerate(code.splitlines(), 1):
        line = raw.strip()

        if not line or line.startswith("//") or line.startswith("#"):
            continue

        if declaration.match(line) and not line.endswith((";", "{", "}", ",")):
            checks.append({
                "severity": "warning",
                "line": line_no,
                "title": "Possible missing semicolon",
                "message": "This declaration appears to require ';'.",
            })

    return checks


def local_analysis(code, language):
    checks = bracket_check(code)

    if language == "Python":
        checks.extend(python_check(code))
    else:
        checks.extend(semicolon_check(code, language))

    return checks


# ============================================================
# AI ANALYSIS
# ============================================================
def ai_analyze(code, language, checks):
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are Code=Annotation-AI, a professional programming assistant.

Analyze the following {language} code. Do not execute it.

Local checks:
{json.dumps(checks, ensure_ascii=False)}

Return ONLY JSON with this exact structure:

{{
  "status": "Valid|Errors Found|Warnings",
  "program_summary": "...",
  "errors": [
    {{
      "line": 1,
      "severity": "Error|Warning",
      "title": "...",
      "explanation": "...",
      "fix": "..."
    }}
  ],
  "corrected_code": "...",
  "time_complexity": "O(...)",
  "time_explanation": "...",
  "space_complexity": "O(...)",
  "space_explanation": "...",
  "optimization_notes": "...",
  "quality_score": 0,
  "quality_reason": "...",
  "security_score": 0,
  "security_notes": "...",
  "learning_notes": "..."
}}

Requirements:
- Find syntax errors.
- Find missing semicolons.
- Find missing/mismatched brackets.
- Find Python indentation problems.
- Give line numbers whenever possible.
- Explain why each problem occurs.
- Explain how to fix it.
- Return complete corrected code.
- Add useful comments to the corrected code.
- Explain what the program does.
- Calculate TC and SC.
- Give optimization advice.
- Give a basic security review.
- Never claim the code was executed.
- Never invent console output.
- Do not change correct logic unnecessarily.

SOURCE CODE:
{code}
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as exc:
        return {"error": str(exc)}


def merge_results(result, checks):
    errors = result.get("errors", [])

    for item in checks:
        if item["severity"] == "success":
            continue

        duplicate = any(
            str(e.get("line")) == str(item.get("line"))
            and item["title"].lower() in str(e.get("title", "")).lower()
            for e in errors
        )

        if not duplicate:
            errors.insert(0, {
                "line": item.get("line"),
                "severity": (
                    "Error" if item["severity"] == "error"
                    else "Warning"
                ),
                "title": item["title"],
                "explanation": item["message"],
                "fix": "Review the indicated line and apply the correction.",
            })

    result["errors"] = errors

    if any(e.get("severity") == "Error" for e in errors):
        result["status"] = "Errors Found"
    elif errors:
        result["status"] = "Warnings"
    else:
        result["status"] = "Valid"

    return result


# ============================================================
# LOCAL RUNNER
# ============================================================
def run_process(command, cwd, stdin_text):
    try:
        p = subprocess.run(
            command,
            cwd=cwd,
            input=stdin_text,
            text=True,
            capture_output=True,
            timeout=RUN_TIMEOUT,
            shell=False,
        )
        return {
            "success": p.returncode == 0,
            "return_code": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Execution timed out.",
            "timed_out": True,
        }
    except Exception as e:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": str(e),
            "timed_out": False,
        }


def run_python(code, stdin_text):
    python = shutil.which("python") or shutil.which("python3")

    if not python:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Python interpreter was not found.",
            "timed_out": False,
        }

    with tempfile.TemporaryDirectory() as folder:
        file = Path(folder) / "main.py"
        file.write_text(code, encoding="utf-8")
        return run_process([python, str(file)], folder, stdin_text)


def run_cpp(code, stdin_text):
    compiler = shutil.which("g++") or shutil.which("clang++")

    if not compiler:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "g++/clang++ was not found. Install a C++ compiler.",
            "timed_out": False,
        }

    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "main.cpp"
        exe = Path(folder) / ("main.exe" if os.name == "nt" else "main")
        source.write_text(code, encoding="utf-8")

        compile_result = run_process(
            [compiler, str(source), "-O2", "-o", str(exe)],
            folder,
            "",
        )

        if not compile_result["success"]:
            compile_result["stage"] = "Compilation"
            return compile_result

        result = run_process([str(exe)], folder, stdin_text)
        result["stage"] = "Execution"
        return result


def run_java(code, stdin_text):
    javac = shutil.which("javac")
    java = shutil.which("java")

    if not javac or not java:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Java JDK was not found. Install a JDK.",
            "timed_out": False,
        }

    with tempfile.TemporaryDirectory() as folder:
        source = Path(folder) / "Main.java"
        source.write_text(code, encoding="utf-8")

        compile_result = run_process(
            [javac, str(source)],
            folder,
            "",
        )

        if not compile_result["success"]:
            compile_result["stage"] = "Compilation"
            return compile_result

        result = run_process(
            [java, "-cp", folder, "Main"],
            folder,
            stdin_text,
        )
        result["stage"] = "Execution"
        return result


def run_code(code, language, stdin_text):
    if not RUNNER_ENABLED:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": (
                "Runner is disabled. Enable CODESENSE_LOCAL_RUNNER=true "
                "on a trusted local machine."
            ),
            "timed_out": False,
        }

    if len(code) > MAX_CODE_CHARS:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Code exceeds the execution size limit.",
            "timed_out": False,
        }

    if language == "Python":
        return run_python(code, stdin_text)
    if language == "C++":
        return run_cpp(code, stdin_text)
    if language == "Java":
        return run_java(code, stdin_text)

    return {
        "success": False,
        "return_code": -1,
        "stdout": "",
        "stderr": "Unsupported language.",
        "timed_out": False,
    }


# ============================================================
# PDF
# ============================================================
def create_pdf(original, language, result):
    pdf = FPDF()
    pdf.set_auto_page_break(True, 15)
    pdf.add_page()

    def safe(x):
        return str(x).encode("latin-1", "replace").decode("latin-1")

    def title(x):
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, safe(x), ln=True)
        pdf.set_font("Helvetica", "", 10)

    def text(x):
        pdf.multi_cell(0, 5.5, safe(x))
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(
        0, 12,
        safe(f"Code=Annotation-AI Report — {language}"),
        ln=True,
        align="C",
    )

    title("Status")
    text(result.get("status", "N/A"))

    title("Program Summary")
    text(result.get("program_summary", "N/A"))

    title("Errors and Warnings")
    errors = result.get("errors", [])
    if errors:
        for e in errors:
            text(
                f"Line: {e.get('line', '?')}\n"
                f"Severity: {e.get('severity', 'N/A')}\n"
                f"Problem: {e.get('title', 'N/A')}\n"
                f"Why: {e.get('explanation', 'N/A')}\n"
                f"Fix: {e.get('fix', 'N/A')}"
            )
    else:
        text("No significant errors detected.")

    title("Time Complexity")
    text(result.get("time_complexity", "N/A"))
    text(result.get("time_explanation", "N/A"))

    title("Space Complexity")
    text(result.get("space_complexity", "N/A"))
    text(result.get("space_explanation", "N/A"))

    title("Quality and Security")
    text(
        f"Quality: {result.get('quality_score', 'N/A')}/100\n"
        f"{result.get('quality_reason', '')}\n\n"
        f"Security: {result.get('security_score', 'N/A')}/100\n"
        f"{result.get('security_notes', '')}"
    )

    title("Optimization")
    text(result.get("optimization_notes", "N/A"))

    title("Learning Notes")
    text(result.get("learning_notes", "N/A"))

    title("Original Code")
    text(original)

    title("Corrected Code")
    text(result.get("corrected_code", ""))

    raw = pdf.output()
    return raw.encode("latin-1") if isinstance(raw, str) else bytes(raw)


# ============================================================
# MAIN WORKSPACE
# ============================================================
st.markdown('<div class="workspace">', unsafe_allow_html=True)

left, right = st.columns([1, 1.12], gap="medium")

with left:
    st.markdown(
        '<div class="panel-title"><span class="status-dot"></span>'
        'Source Code</div>',
        unsafe_allow_html=True,
    )

    language = st.selectbox(
        "Language",
        ["Python", "C++", "Java"],
        index=["Python", "C++", "Java"].index(st.session_state.language),
        label_visibility="collapsed",
    )

    # The select bar above is deliberately white.
    code = st.text_area(
        "Code",
        value=st.session_state.code,
        height=535,
        placeholder=(
            "Write or paste your code here...\n\n"
            "Example:\n"
            "int main() {\n"
            "    int a = 10\n"
            "    cout << a;\n"
            "    return 0;\n"
            "}"
        ),
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="editor-note">'
        'Editor • Syntax analysis is performed before AI review.'
        '</div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "Analyze & Annotate",
        type="primary",
        use_container_width=True,
    ):
        if not code.strip():
            st.warning("Enter some code first.")
        elif len(code) > MAX_CODE_CHARS:
            st.error(f"Maximum supported code size: {MAX_CODE_CHARS} characters.")
        else:
            st.session_state.code = code
            st.session_state.language = language
            st.session_state.run_output = None

            with st.spinner("Analyzing source code..."):
                checks = local_analysis(code, language)
                result = ai_analyze(code, language, checks)

            if "error" in result:
                st.error(result["error"])
            else:
                st.session_state.local_checks = checks
                st.session_state.result = merge_results(result, checks)
                st.success("Analysis completed.")

with right:
    st.markdown(
        '<div class="panel-title"><span class="status-dot"></span>'
        'Analysis</div>',
        unsafe_allow_html=True,
    )

    result = st.session_state.result

    if result is None:
        st.markdown(
            '<div class="note" style="margin-top:16px;">'
            '<b>Ready.</b><br><br>'
            'Enter source code on the left and select '
            '<b>Analyze & Annotate</b> to inspect errors, '
            'generate corrected code, calculate complexity and review quality.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        errors = result.get("errors", [])
        status = result.get("status", "Warnings")

        if status == "Valid":
            st.success("No significant errors detected.")
        elif status == "Errors Found":
            st.error("Errors were detected and explained.")
        else:
            st.warning("Warnings were detected.")

        a, b, c, d = st.columns(4)

        metrics = [
            ("TC", result.get("time_complexity", "N/A")),
            ("SC", result.get("space_complexity", "N/A")),
            ("QUALITY", result.get("quality_score", "N/A")),
            ("SECURITY", result.get("security_score", "N/A")),
        ]

        for col, (label, value) in zip([a, b, c, d], metrics):
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">{label}</div>'
                    f'<div class="metric-value">{value}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        tabs = st.tabs([
            "Issues",
            "Corrected Code",
            "Notes",
            "TC / SC",
            "Run",
            "Review",
            "PDF",
        ])

        with tabs[0]:
            if not errors:
                st.success("No significant issues found.")
            else:
                for e in errors:
                    with st.expander(
                        f"Line {e.get('line', '?')} · "
                        f"{e.get('severity', 'Warning')} · "
                        f"{e.get('title', 'Issue')}",
                        expanded=True,
                    ):
                        st.markdown("**Why**")
                        st.write(e.get("explanation", "N/A"))
                        st.markdown("**Fix**")
                        st.write(e.get("fix", "N/A"))

        with tabs[1]:
            st.markdown("#### Corrected Source")
            st.code(
                result.get("corrected_code", ""),
                language=language.lower(),
            )
            st.info(
                "Review the corrected source before running it."
            )

        with tabs[2]:
            st.markdown("#### What the program does")
            st.markdown(
                f'<div class="note">{result.get("program_summary", "N/A")}</div>',
                unsafe_allow_html=True,
            )

            st.markdown("#### Learning notes")
            st.markdown(
                f'<div class="note">{result.get("learning_notes", "N/A")}</div>',
                unsafe_allow_html=True,
            )

        with tabs[3]:
            x, y = st.columns(2)

            with x:
                st.markdown("#### Time Complexity")
                st.metric("TC", result.get("time_complexity", "N/A"))
                st.markdown(
                    f'<div class="note">{result.get("time_explanation", "N/A")}</div>',
                    unsafe_allow_html=True,
                )

            with y:
                st.markdown("#### Space Complexity")
                st.metric("SC", result.get("space_complexity", "N/A"))
                st.markdown(
                    f'<div class="note">{result.get("space_explanation", "N/A")}</div>',
                    unsafe_allow_html=True,
                )

            tc = str(result.get("time_complexity", "O(n)")).lower()
            n = np.linspace(1, 10, 150)

            if "o(1)" in tc:
                values = np.ones_like(n)
            elif "log" in tc:
                values = np.log(n)
            elif "nlogn" in tc:
                values = n * np.log(n)
            elif "n^2" in tc or "n²" in tc:
                values = n ** 2
            elif "2^n" in tc:
                values = 2 ** n
            else:
                values = n

            fig, ax = plt.subplots(figsize=(7, 3))
            ax.plot(n, values)
            ax.set_title(f"Complexity Growth — {result.get('time_complexity', 'N/A')}")
            ax.set_xlabel("Input size")
            ax.set_ylabel("Relative operations")
            ax.grid(alpha=.2)
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with tabs[4]:
            st.markdown("#### Run Corrected Code")

            st.markdown(
                '<div class="note">'
                '<b>Same website, same page.</b><br>'
                'The corrected source is compiled/executed and the console '
                'result is displayed here. No Piston public API is used.'
                '</div>',
                unsafe_allow_html=True,
            )

            stdin_text = st.text_area(
                "Program input",
                height=120,
                placeholder="Optional stdin...",
            )

            if st.button(
                "Run Corrected Code",
                type="primary",
                use_container_width=True,
            ):
                corrected = result.get("corrected_code", "").strip()

                if not corrected:
                    st.error("No corrected code is available.")
                else:
                    with st.spinner("Compiling and running..."):
                        st.session_state.run_output = run_code(
                            corrected,
                            language,
                            stdin_text,
                        )

            execution = st.session_state.run_output

            if execution:
                if execution.get("success"):
                    st.success(
                        f"Completed successfully · "
                        f"Exit code {execution.get('return_code', 0)}"
                    )

                    output = execution.get("stdout", "")
                    st.markdown("#### Console Output")
                    st.code(output if output else "(no console output)")
                else:
                    st.error(
                        f"{execution.get('stage', 'Execution')} failed"
                    )

                    if execution.get("stderr"):
                        st.markdown("#### Compiler / Runtime Error")
                        st.code(execution["stderr"])

                    if execution.get("stdout"):
                        st.markdown("#### Partial Output")
                        st.code(execution["stdout"])

                    if execution.get("timed_out"):
                        st.warning("Execution exceeded the timeout.")

        with tabs[5]:
            p, q = st.columns(2)

            with p:
                st.markdown("#### Code Quality")
                st.metric(
                    "Score",
                    f'{result.get("quality_score", 0)}/100',
                )
                st.markdown(
                    f'<div class="note">{result.get("quality_reason", "N/A")}</div>',
                    unsafe_allow_html=True,
                )

            with q:
                st.markdown("#### Security Review")
                st.metric(
                    "Score",
                    f'{result.get("security_score", 0)}/100',
                )
                st.markdown(
                    f'<div class="note">{result.get("security_notes", "N/A")}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("#### Optimization")
            st.markdown(
                f'<div class="note">{result.get("optimization_notes", "N/A")}</div>',
                unsafe_allow_html=True,
            )

        with tabs[6]:
            pdf = create_pdf(
                st.session_state.code,
                language,
                result,
            )

            st.download_button(
                "Download PDF Report",
                data=pdf,
                file_name="Code_Annotation_AI_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    f"""
    <div class="footer">
        Code=Annotation-AI · Developer Code Analysis Platform ·
        <a href="{PROJECT_URL}" target="_blank">Official Project Repository</a>
    </div>
    """,
    unsafe_allow_html=True,
)
