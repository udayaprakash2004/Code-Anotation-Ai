import ast
import json
import os
import requests
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import streamlit as st
from groq import Groq
from fpdf import FPDF


# ==========================================================
# Code=Annotation-AI
# ==========================================================

st.set_page_config(
    page_title="Code=Annotation-AI",
    page_icon="</>",
    layout="wide",
    initial_sidebar_state="collapsed",
)

GITHUB_URL = "https://github.com/udayaprakash2004/Code-Anotation-Ai"
MAX_CODE = 30000
TIMEOUT = 8


# ==========================================================
# PROFESSIONAL PURPLE UI
# ==========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --purple: #5b21b6;
    --purple2: #6d28d9;
    --purple3: #7c3aed;
    --dark: #24105f;
    --text: #202534;
    --muted: #687386;
    --border: #dfe3eb;
    --green: #159447;
    --red: #dc3038;
    --orange: #e58a00;
}

* {
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: "Inter", "Segoe UI", Arial, sans-serif;
}

.stApp {
    min-height: 100vh;
    background:
        radial-gradient(circle at 12% 20%, rgba(255,255,255,.10), transparent 20%),
        radial-gradient(circle at 86% 10%, rgba(255,255,255,.08), transparent 22%),
        linear-gradient(135deg, #351080 0%, #4b1499 48%, #6417a7 100%);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1460px;
    padding: 0 24px 20px 24px;
}

header[data-testid="stHeader"] {
    height: 0;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


/* ---------- Header ---------- */

.app-header {
    height: 82px;
    margin: 0 -24px 22px -24px;
    padding: 0 34px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background:
        linear-gradient(90deg, rgba(34,10,95,.96), rgba(83,22,158,.94));
    border-bottom: 1px solid rgba(255,255,255,.16);
    box-shadow: 0 5px 20px rgba(24, 6, 75, .25);
}

.logo {
    font-size: 28px;
    line-height: 1.1;
    font-weight: 800;
    letter-spacing: -1px;
}

.tagline {
    margin-top: 6px;
    font-size: 12px;
    font-weight: 500;
    opacity: .9;
}

.nav {
    display: flex;
    gap: 34px;
    align-items: center;
    font-size: 13px;
    font-weight: 650;
}

.nav-item {
    display: flex;
    gap: 8px;
    align-items: center;
    opacity: .96;
}


/* ---------- Main white workspace ---------- */

.main-card {
    background: #f9fafc;
    border: 1px solid rgba(255,255,255,.55);
    border-radius: 9px;
    box-shadow: 0 15px 40px rgba(28, 5, 75, .24);
    padding: 18px;
}


/* ---------- Top controls ---------- */

.control-label {
    color: #697486;
    font-size: 12px;
    font-weight: 650;
    margin: 0 0 7px 1px;
}

div[data-baseweb="select"] > div {
    background: #ffffff !important;
    border: 1px solid #d9dee7 !important;
    border-radius: 6px !important;
    min-height: 40px !important;
    color: #273142 !important;
    box-shadow: none !important;
}

div[data-baseweb="select"] span {
    color: #273142 !important;
}

div[data-baseweb="select"] svg {
    color: #455266 !important;
}

.stButton > button,
.stDownloadButton > button {
    min-height: 40px;
    border-radius: 6px;
    border: 1px solid #d9dee7;
    background: white;
    color: #303a4a;
    font-size: 12px;
    font-weight: 650;
    box-shadow: none;
}

.stButton > button:hover,
.stDownloadButton > button:hover {
    border-color: #6d28d9;
    color: #5b21b6;
    background: #fff;
}

button[kind="primary"] {
    background: #6023bf !important;
    border-color: #6023bf !important;
    color: white !important;
}

button[kind="primary"]:hover {
    background: #4f1da1 !important;
}


/* ---------- Panels ---------- */

.panel {
    background: white;
    border: 1px solid #e1e5ec;
    border-radius: 8px;
    box-shadow: 0 2px 9px rgba(30,40,60,.045);
    overflow: hidden;
}

.panel-heading {
    height: 52px;
    display: flex;
    align-items: center;
    padding: 0 17px;
    border-bottom: 1px solid #e7e9ee;
    color: #273142;
    font-size: 14px;
    font-weight: 700;
}

.heading-icon {
    color: #6b28c8;
    margin-right: 9px;
    font-weight: 800;
}


/* ---------- Editor ---------- */

.stTextArea textarea {
    background: #ffffff !important;
    color: #17202b !important;
    border: 1px solid #d8dee7 !important;
    border-radius: 6px !important;
    font-family: Consolas, "Courier New", monospace !important;
    font-size: 13px !important;
    line-height: 1.55 !important;
    padding: 13px !important;
    box-shadow: none !important;
}

.stTextArea textarea:focus {
    border-color: #7950c8 !important;
    box-shadow: 0 0 0 1px #7950c8 !important;
}

.stTextInput input {
    background: white !important;
    color: #17202b !important;
    border: 1px solid #d8dee7 !important;
}


/* ---------- Summary cards ---------- */

.summary-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 11px;
    padding: 14px 14px 16px;
}

.summary-card {
    min-height: 82px;
    background: #fff;
    border: 1px solid #e5e8ee;
    border-radius: 7px;
    padding: 12px;
}

.summary-label {
    font-size: 11px;
    font-weight: 600;
    color: #707b8d;
}

.summary-value {
    margin-top: 8px;
    font-size: 23px;
    font-weight: 750;
    color: #242b39;
}

.red { color: #d83239 !important; }
.orange { color: #dc8700 !important; }
.blue { color: #2b6dd0 !important; }
.green { color: #149044 !important; }


/* ---------- Error card ---------- */

.error-section {
    border-top: 1px solid #eceef2;
    padding: 13px 14px 16px;
}

.error-title {
    font-size: 13px;
    font-weight: 750;
    color: #3b4351;
    margin-bottom: 12px;
}

.error-card {
    border: 1px solid #e1e4e9;
    border-radius: 7px;
    padding: 14px;
    background: #fff;
}

.error-line {
    color: #df3038;
    font-size: 12px;
    font-weight: 750;
    margin-bottom: 7px;
}

.error-text {
    color: #3c4655;
    font-size: 12px;
    line-height: 1.55;
}

.why {
    color: #6c2abb;
    font-size: 12px;
    font-weight: 750;
    margin-top: 13px;
}

.fix {
    color: #159447;
    font-size: 12px;
    font-weight: 750;
    margin-top: 13px;
}


/* ---------- Lower result section ---------- */

.result-card {
    margin-top: 16px;
    background: white;
    border: 1px solid #e1e5ec;
    border-radius: 8px;
    box-shadow: 0 2px 9px rgba(30,40,60,.045);
    overflow: hidden;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #e1e4ea;
    background: white;
}

.stTabs [data-baseweb="tab"] {
    color: #566173 !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    padding: 11px 17px !important;
    background: white !important;
    border-radius: 0 !important;
}

.stTabs [aria-selected="true"] {
    color: #5b21b6 !important;
    border-bottom: 2px solid #5b21b6 !important;
}

.code-box {
    background: #fbfcfe;
    border: 1px solid #e1e5eb;
    border-radius: 6px;
    padding: 2px;
}

.note-box {
    background: #ffffff;
    border: 1px solid #e1e5eb;
    border-radius: 7px;
    padding: 14px;
    color: #364152;
    font-size: 12px;
    line-height: 1.6;
}


/* ---------- Runner ---------- */

.runner {
    border-top: 1px solid #e4e7ed;
    padding: 16px;
}

.runner-title {
    font-size: 14px;
    font-weight: 750;
    color: #2d3543;
    margin-bottom: 13px;
}

.console {
    background: #101010;
    color: #52e66b;
    min-height: 105px;
    padding: 12px;
    border-radius: 5px;
    font-family: Consolas, monospace;
    font-size: 12px;
    white-space: pre-wrap;
    border: 1px solid #252525;
}

.console-error {
    color: #ff7474;
}

.runner-time {
    text-align: right;
    color: #677184;
    font-size: 11px;
    margin-top: 4px;
}

.footer-text {
    color: rgba(255,255,255,.88);
    text-align: center;
    font-size: 11px;
    padding: 17px 0 2px;
}

.footer-text a {
    color: white;
    font-weight: 700;
    text-decoration: none;
}

@media (max-width: 900px) {
    .summary-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .nav {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)


# ==========================================================
# HEADER
# ==========================================================

st.markdown("""
<div class="app-header">
    <div>
        <div class="logo">Code=Annotation-AI</div>
        <div class="tagline">AI Code Analyzer, Annotator &amp; Optimizer</div>
    </div>
    <div class="nav">
        <div class="nav-item">⌂ &nbsp;Home</div>
        <div class="nav-item">▣ &nbsp;Report</div>
        <div class="nav-item">ⓘ &nbsp;About</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-card">', unsafe_allow_html=True)


# ==========================================================
# API KEY
# ==========================================================

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY is missing. Add it in Streamlit Secrets.")
    st.stop()


# ==========================================================
# STATE
# ==========================================================

if "source_code" not in st.session_state:
    st.session_state.source_code = """# Write your code here

def main():
    a = 10
    print(a)

main()
"""

if "language" not in st.session_state:
    st.session_state.language = "Python"

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "run_result" not in st.session_state:
    st.session_state.run_result = None


# ==========================================================
# EXAMPLES
# ==========================================================

examples = {
    "Missing Semicolon": """#include <iostream>
using namespace std;

int main() {
    int a = 10
    cout << a;
    return 0;
}""",
    "Hello World": """#include <iostream>
using namespace std;

int main() {
    cout << "Hello World";
    return 0;
}""",
    "Logic Review": """#include <iostream>
using namespace std;

int main() {
    for (int i = 0; i < 5; i++) {
        cout << i << " ";
    }
    return 0;
}""",
}


# ==========================================================
# LOCAL CHECKS
# ==========================================================

def bracket_check(code):
    pairs = {"(": ")", "[": "]", "{": "}"}
    rev = {")": "(", "]": "[", "}": "{"}
    stack = []

    for line_no, line in enumerate(code.splitlines(), 1):
        for ch in line:
            if ch in pairs:
                stack.append((ch, line_no))
            elif ch in rev:
                if not stack or stack[-1][0] != rev[ch]:
                    return [{
                        "line": line_no,
                        "severity": "Error",
                        "title": "Mismatched bracket or brace",
                        "explanation": f"Unexpected '{ch}' on line {line_no}.",
                        "fix": "Match every closing bracket with its opening bracket."
                    }]
                stack.pop()

    if stack:
        ch, line_no = stack[-1]
        return [{
            "line": line_no,
            "severity": "Error",
            "title": "Missing closing bracket",
            "explanation": f"'{ch}' opened on line {line_no} has no matching closing bracket.",
            "fix": "Add the corresponding closing bracket."
        }]

    return []


def python_check(code):
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [{
            "line": e.lineno or "?",
            "severity": "Error",
            "title": e.msg or "Python syntax error",
            "explanation": e.text.strip() if e.text else "Python syntax is invalid.",
            "fix": "Correct the syntax shown on the indicated line."
        }]


def cpp_java_semicolon_check(code, language):
    if language not in ["C++", "Java"]:
        return []

    issues = []
    pattern = re.compile(
        r"^\s*(?:int|float|double|char|bool|long|short|"
        r"String|boolean|auto|size_t)\s+\w+.*"
    )

    for n, line in enumerate(code.splitlines(), 1):
        s = line.strip()
        if pattern.match(s) and not s.endswith((";", "{", "}")):
            issues.append({
                "line": n,
                "severity": "Error",
                "title": "Missing semicolon",
                "explanation": f"Missing semicolon at the end of the statement.",
                "fix": "Add a semicolon ';' at the end of the statement."
            })

    return issues


def local_checks(code, language):
    result = []
    result.extend(bracket_check(code))

    if language == "Python":
        result.extend(python_check(code))
    else:
        result.extend(cpp_java_semicolon_check(code, language))

    return result


# ==========================================================
# GROQ ANALYSIS
# ==========================================================

def analyze_with_ai(code, language):
    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are Code=Annotation-AI, a professional source-code analysis tool.

Analyze this {language} program. Do not execute it.

Return ONLY valid JSON:

{{
  "errors": [
    {{
      "line": 1,
      "severity": "Error|Warning",
      "title": "short title",
      "explanation": "brief explanation",
      "why": "why the compiler/interpreter complains",
      "fix": "exact correction"
    }}
  ],
  "summary": "brief description of what the code does",
  "corrected_code": "complete corrected source code",
  "time_complexity": "O(...)",
  "time_explanation": "brief reason",
  "space_complexity": "O(...)",
  "space_explanation": "brief reason",
  "optimization": "useful optimization suggestions",
  "security": "basic security review",
  "notes": "useful learning notes",
  "score": 0
}}

Rules:
- Detect syntax errors.
- Detect missing semicolons for C++/Java.
- Detect missing/mismatched brackets.
- Detect Python indentation/syntax issues.
- Explain every important error.
- Return the complete corrected code.
- Preserve the intended logic.
- Add concise comments to corrected code where useful.
- Never invent execution output.
- Score from 0 to 100.

CODE:
{code}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def analyze_code(code, language):
    local = local_checks(code, language)

    try:
        ai = analyze_with_ai(code, language)
    except Exception as e:
        return {
            "errors": local,
            "summary": "AI analysis could not be completed.",
            "corrected_code": code,
            "time_complexity": "N/A",
            "time_explanation": str(e),
            "space_complexity": "N/A",
            "space_explanation": "",
            "optimization": "",
            "security": "",
            "notes": "",
            "score": 0,
        }

    existing = ai.get("errors", [])

    for item in local:
        if not any(
            str(x.get("line")) == str(item.get("line"))
            and x.get("title") == item.get("title")
            for x in existing
        ):
            existing.insert(0, item)

    ai["errors"] = existing
    return ai


# ==========================================================
# ==========================================================
# CLOUD CODE RUNNER — JUDGE0
# ==========================================================

LANGUAGE_IDS = {
    "Python": 71,  # Python 3.8.1
    "C++": 54,      # GNU++17
    "Java": 62,     # Java 13
}

JUDGE0_URL = st.secrets.get(
    "JUDGE0_URL",
    os.getenv("JUDGE0_URL", "https://ce.judge0.com"),
).rstrip("/")


def run_corrected(code, language, stdin_text):
    """Run code through Judge0 so Streamlit Cloud never executes
    arbitrary user code inside the Streamlit container."""

    payload = {
        "source_code": code,
        "language_id": LANGUAGE_IDS[language],
        "stdin": stdin_text or "",
        "cpu_time_limit": 2,
        "wall_time_limit": 5,
        "memory_limit": 128000,
        "enable_network": False,
    }

    try:
        response = requests.post(
            f"{JUDGE0_URL}/submissions/?base64_encoded=false&wait=true",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=25,
        )
    except requests.RequestException as exc:
        return {
            "ok": False,
            "stdout": "",
            "stderr": f"Judge0 connection error: {exc}",
            "compile_output": "",
            "status": "Connection Error",
            "time": None,
            "memory": None,
            "exit_code": -1,
        }

    # Some Judge0 hosts disable wait=true. Fall back to token polling.
    if response.status_code not in (200, 201):
        return {
            "ok": False,
            "stdout": "",
            "stderr": response.text[:4000],
            "compile_output": "",
            "status": f"Judge0 HTTP {response.status_code}",
            "time": None,
            "memory": None,
            "exit_code": -1,
        }

    data = response.json()

    if "token" in data and "status" not in data:
        token = data["token"]

        for _ in range(18):
            time.sleep(0.6)
            try:
                r = requests.get(
                    f"{JUDGE0_URL}/submissions/{token}?base64_encoded=false",
                    timeout=10,
                )
                if r.status_code != 200:
                    continue

                data = r.json()
                status_id = (data.get("status") or {}).get("id")

                if status_id not in (1, 2):
                    break
            except requests.RequestException:
                continue

    status = (data.get("status") or {}).get("description", "Unknown")
    ok = status == "Accepted"

    return {
        "ok": ok,
        "stdout": data.get("stdout") or "",
        "stderr": data.get("stderr") or "",
        "compile_output": data.get("compile_output") or "",
        "status": status,
        "message": data.get("message") or "",
        "time": data.get("time"),
        "memory": data.get("memory"),
        "exit_code": data.get("exit_code", 0),
    }


# PDF
# ==========================================================

def make_pdf(language, original, result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, 15)

    def safe(s):
        return str(s).encode("latin-1", "replace").decode("latin-1")

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 11, safe("Code=Annotation-AI Report"), ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, safe(f"Language: {language}"), ln=True)
    pdf.ln(4)

    sections = [
        ("Analysis Summary", result.get("summary", "")),
        ("Errors", json.dumps(result.get("errors", []), indent=2)),
        ("Time Complexity", result.get("time_complexity", "")),
        ("Time Explanation", result.get("time_explanation", "")),
        ("Space Complexity", result.get("space_complexity", "")),
        ("Space Explanation", result.get("space_explanation", "")),
        ("Optimization", result.get("optimization", "")),
        ("Security", result.get("security", "")),
        ("Notes", result.get("notes", "")),
        ("Original Code", original),
        ("Corrected Code", result.get("corrected_code", "")),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, safe(heading), ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, safe(body))
        pdf.ln(3)

    output = pdf.output()
    return output.encode("latin-1") if isinstance(output, str) else bytes(output)


# ==========================================================
# TOP CONTROLS
# ==========================================================

c1, c2, c3, c4, c5 = st.columns([1.0, 1.45, .9, .9, .9], gap="small")

with c1:
    st.markdown('<div class="control-label">Select Language</div>', unsafe_allow_html=True)
    language = st.selectbox(
        "language",
        ["C++", "Python", "Java"],
        index=["C++", "Python", "Java"].index(st.session_state.language),
        label_visibility="collapsed",
    )

with c2:
    st.markdown('<div class="control-label">Example</div>', unsafe_allow_html=True)
    example = st.selectbox(
        "example",
        ["Missing Semicolon", "Hello World", "Logic Review"],
        label_visibility="collapsed",
    )

with c3:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    analyze = st.button("⌁  Analyze Code", type="primary", use_container_width=True)

with c4:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    clear = st.button("▢  Clear Code", use_container_width=True)

with c5:
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    copy = st.button("▣  Copy Code", use_container_width=True)


if language != st.session_state.language:
    st.session_state.language = language
    if language == "C++":
        st.session_state.source_code = examples["Missing Semicolon"]
    elif language == "Java":
        st.session_state.source_code = """public class Main {
    public static void main(String[] args) {
        int a = 10
        System.out.println(a);
    }
}"""
    else:
        st.session_state.source_code = """def main():
    a = 10
    print(a)

main()"""
    st.session_state.analysis = None
    st.session_state.run_result = None
    st.rerun()

if clear:
    st.session_state.source_code = ""
    st.session_state.analysis = None
    st.session_state.run_result = None
    st.rerun()

if example:
    # Only load an example when Analyze is not being pressed.
    pass


# ==========================================================
# MAIN TWO-COLUMN PANELS
# ==========================================================

left, right = st.columns([1, 1], gap="small")

with left:
    st.markdown("""
    <div class="panel">
        <div class="panel-heading">
            <span class="heading-icon">&lt;/&gt;</span>
            Your Code
        </div>
    </div>
    """, unsafe_allow_html=True)

    source = st.text_area(
        "source",
        value=st.session_state.source_code,
        height=330,
        label_visibility="collapsed",
        placeholder="Write or paste your source code here...",
    )

    st.session_state.source_code = source

    st.markdown('<div class="control-label">Input / Custom Input (stdin)</div>', unsafe_allow_html=True)

    stdin_text = st.text_area(
        "stdin",
        height=78,
        label_visibility="collapsed",
        placeholder="Enter input for the program (if any)",
    )

with right:
    result = st.session_state.analysis

    if result is None:
        errors = []
    else:
        errors = result.get("errors", [])

    error_count = len([e for e in errors if e.get("severity", "Error") == "Error"])
    warning_count = len([e for e in errors if e.get("severity") == "Warning"])
    score = result.get("score", 0) if result else 0

    st.markdown("""
    <div class="panel">
        <div class="panel-heading">Analysis Summary</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="summary-grid">
        <div class="summary-card">
            <div class="summary-label red">Errors</div>
            <div class="summary-value red">{error_count}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label orange">Warnings</div>
            <div class="summary-value">{warning_count}</div>
        </div>
        <div class="summary-card">
            <div class="summary-label blue">Info</div>
            <div class="summary-value">0</div>
        </div>
        <div class="summary-card">
            <div class="summary-label green">Score</div>
            <div class="summary-value green">{score}<small style="font-size:13px">/100</small></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if errors:
        first = errors[0]
        st.markdown(f"""
        <div class="error-section">
            <div class="error-title">⊕ &nbsp; Errors Found</div>
            <div class="error-card">
                <div class="error-line">Line {first.get("line", "?")}</div>
                <div class="error-text">{first.get("title", "Issue")}<br>
                {first.get("explanation", "")}</div>
                <div class="why">Why?</div>
                <div class="error-text">{first.get("why", first.get("explanation", ""))}</div>
                <div class="fix">How to Fix?</div>
                <div class="error-text">{first.get("fix", "")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-section">
            <div class="error-title">✓ &nbsp; No Errors Found</div>
            <div class="error-card">
                <div class="error-text">
                    Analyze the code to receive syntax, logic, complexity and
                    optimization feedback.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# ANALYZE
# ==========================================================

if analyze:
    if not source.strip():
        st.warning("Please enter code before analyzing.")
    elif len(source) > MAX_CODE:
        st.error(f"Code is too large. Maximum size is {MAX_CODE} characters.")
    else:
        with st.spinner("Analyzing code..."):
            st.session_state.analysis = analyze_code(source, language)
            st.session_state.run_result = None
        st.rerun()


# ==========================================================
# RESULT AREA
# ==========================================================

result = st.session_state.analysis

st.markdown('<div class="result-card">', unsafe_allow_html=True)

tabs = st.tabs([
    "Corrected Code",
    "Explanation",
    "Time & Space Complexity",
    "Optimization",
    "Security",
    "Notes",
])

if result:
    with tabs[0]:
        corrected = result.get("corrected_code", source)

        a, b = st.columns([5, 1])
        with a:
            st.markdown("### Corrected Code")
        with b:
            if st.button("▣  Copy", key="copy_corrected", use_container_width=True):
                st.toast("Corrected code is ready to copy from the code block.")

        st.code(corrected, language=language.lower())

        x, y = st.columns(2)
        with x:
            st.markdown(f"""
            <div class="note-box">
                <b>What Does This Code Do?</b><br><br>
                {result.get("summary", "No summary available.")}
            </div>
            """, unsafe_allow_html=True)

        with y:
            st.markdown(f"""
            <div class="note-box">
                <b>Language</b><br><br>
                {language}<br><br>
                <b>Lines</b><br>
                {len(corrected.splitlines())}
            </div>
            """, unsafe_allow_html=True)

    with tabs[1]:
        if result.get("errors"):
            for e in result["errors"]:
                st.markdown(f"""
                <div class="note-box" style="margin-bottom:10px">
                    <b>Line {e.get("line", "?")} — {e.get("title", "Issue")}</b><br><br>
                    <b>Explanation:</b> {e.get("explanation", "")}<br><br>
                    <b>Why:</b> {e.get("why", "")}<br><br>
                    <b>How to Fix:</b> {e.get("fix", "")}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("No significant issues were found.")

    with tabs[2]:
        x, y = st.columns(2)

        with x:
            st.markdown(f"""
            <div class="note-box">
                <b>Time Complexity</b><br><br>
                <strong style="font-size:20px">{result.get("time_complexity", "N/A")}</strong>
                <br><br>{result.get("time_explanation", "")}
            </div>
            """, unsafe_allow_html=True)

        with y:
            st.markdown(f"""
            <div class="note-box">
                <b>Space Complexity</b><br><br>
                <strong style="font-size:20px">{result.get("space_complexity", "N/A")}</strong>
                <br><br>{result.get("space_explanation", "")}
            </div>
            """, unsafe_allow_html=True)

    with tabs[3]:
        st.markdown(
            f'<div class="note-box">{result.get("optimization", "No optimization notes.")}</div>',
            unsafe_allow_html=True,
        )

    with tabs[4]:
        st.markdown(
            f'<div class="note-box">{result.get("security", "No security notes.")}</div>',
            unsafe_allow_html=True,
        )

    with tabs[5]:
        st.markdown(
            f'<div class="note-box">{result.get("notes", "No notes.")}</div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown("""
    <div style="padding:38px;text-align:center;color:#778194">
        Analyze your code to display corrected code, explanation,
        complexity, optimization and security review.
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# RUN CORRECTED CODE
# ==========================================================

if result:
    st.markdown('<div class="result-card runner">', unsafe_allow_html=True)

    st.markdown(
        '<div class="runner-title">▣ &nbsp; Run Corrected Code</div>',
        unsafe_allow_html=True,
    )

    r1, r2, r3 = st.columns([1, 1, 4])

    with r1:
        run_button = st.button(
            "▶  Run Code",
            type="primary",
            use_container_width=True,
            key="run_corrected",
        )

    with r2:
        st.button(
            "■  Stop",
            use_container_width=True,
            disabled=True,
            key="stop_disabled",
        )

    with r3:
        if st.session_state.run_result:
            elapsed = st.session_state.run_result.get("elapsed", 0)
            st.markdown(
                f'<div class="runner-time">Execution Time: '
                f'<b style="color:#159447">{elapsed:.3f} sec</b></div>',
                unsafe_allow_html=True,
            )

    if run_button:
        corrected = result.get("corrected_code", source)

        start = time.perf_counter()

        with st.spinner("Compiling and running corrected code..."):
            execution = run_corrected(corrected, language, stdin_text)

        execution["elapsed"] = time.perf_counter() - start
        st.session_state.run_result = execution
        st.rerun()

    execution = st.session_state.run_result

    o1, o2 = st.columns(2)

    with o1:
        st.markdown('<div class="control-label">Program Output</div>', unsafe_allow_html=True)

        if execution and execution.get("ok"):
            output = execution.get("stdout", "")
            st.markdown(
                f'<div class="console">{output if output else "(no output)"}</div>',
                unsafe_allow_html=True,
            )
        elif execution:
            st.markdown(
                '<div class="console console-error">Execution failed.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="console">Run the corrected code to see output.</div>',
                unsafe_allow_html=True,
            )

    with o2:
        st.markdown('<div class="control-label">Compiler Messages</div>', unsafe_allow_html=True)

        if execution:
            if execution.get("ok"):
                msg = "Compilation successful.\nExit code: 0"
                cls = "console"
            else:
                msg = execution.get("stderr", "Unknown error.")
                cls = "console console-error"

            st.markdown(
                f'<div class="{cls}">{msg}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="console">No execution yet.</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    d1, d2 = st.columns([1, 1])

    with d1:
        pdf_data = make_pdf(language, source, result)

        st.download_button(
            "▤  Download Report (PDF)",
            data=pdf_data,
            file_name="Code_Annotation_AI_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with d2:
        st.download_button(
            "⇩  Download Corrected Code",
            data=result.get("corrected_code", ""),
            file_name=(
                "main.py" if language == "Python"
                else "main.cpp" if language == "C++"
                else "Main.java"
            ),
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ==========================================================
# FOOTER
# ==========================================================

st.markdown(
    f"""
    <div class="footer-text">
        Code=Annotation-AI © 2025 &nbsp;|&nbsp; Built with Streamlit
        &nbsp;|&nbsp;
        <a href="{GITHUB_URL}" target="_blank">Project Repository</a>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
