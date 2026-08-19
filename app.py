import ast
import json
import re
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from groq import Groq
from fpdf import FPDF


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="CodeSense AI | Code Analyzer",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BLUE UI
# ============================================================
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(59,130,246,.25), transparent 30%),
            linear-gradient(135deg, #06152f 0%, #0b2a55 45%, #0f3b78 100%);
        color: #eef6ff;
    }

    [data-testid="stHeader"] {
        background: rgba(0,0,0,0);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #06152f, #082b59);
        border-right: 1px solid rgba(147,197,253,.20);
    }

    .hero {
        padding: 28px 32px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(37,99,235,.95), rgba(14,165,233,.82));
        box-shadow: 0 18px 50px rgba(0,0,0,.25);
        margin-bottom: 22px;
    }

    .hero h1 {
        margin: 0;
        font-size: 42px;
        color: white;
    }

    .hero p {
        margin: 8px 0 0 0;
        font-size: 17px;
        color: #e0f2fe;
    }

    .card {
        background: rgba(8, 30, 62, .72);
        border: 1px solid rgba(147,197,253,.18);
        border-radius: 18px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 10px 30px rgba(0,0,0,.16);
    }

    .metric-card {
        background: rgba(15, 55, 105, .75);
        border: 1px solid rgba(147,197,253,.20);
        border-radius: 16px;
        padding: 15px;
        text-align: center;
    }

    .metric-label {
        color: #bfdbfe;
        font-size: 13px;
    }

    .metric-value {
        color: white;
        font-size: 25px;
        font-weight: 700;
        margin-top: 4px;
    }

    .status-ok {
        color: #86efac;
        font-weight: 700;
    }

    .status-error {
        color: #fca5a5;
        font-weight: 700;
    }

    .small {
        color: #bfdbfe;
        font-size: 13px;
    }

    .stButton > button {
        border-radius: 12px;
        font-weight: 700;
        border: 0;
    }

    div[data-baseweb="tab-list"] {
        gap: 8px;
    }

    div[data-baseweb="tab"] {
        background: rgba(15,55,105,.55);
        border-radius: 10px;
        padding: 8px 14px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SECRETS
# ============================================================
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("GROQ_API_KEY is missing. Add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "analysis": None,
    "original_code": "",
    "language": "Python",
    "local_diagnostics": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# LOCAL STATIC CHECKS
# IMPORTANT: NO CODE IS EXECUTED.
# ============================================================
def check_python(code):
    diagnostics = []
    try:
        ast.parse(code)
        diagnostics.append({
            "type": "success",
            "message": "Python syntax is valid.",
            "line": None,
        })
    except SyntaxError as e:
        diagnostics.append({
            "type": "error",
            "message": e.msg,
            "line": e.lineno,
            "detail": e.text.strip() if e.text else "",
        })
    return diagnostics


def check_braces(code):
    pairs = {"(": ")", "[": "]", "{": "}"}
    closing = {")": "(", "]": "[", "}": "{"}
    stack = []

    for line_no, line in enumerate(code.splitlines(), start=1):
        in_string = False
        quote = None
        escaped = False

        for ch in line:
            if escaped:
                escaped = False
                continue

            if ch == "\\" and in_string:
                escaped = True
                continue

            if ch in ('"', "'"):
                if not in_string:
                    in_string = True
                    quote = ch
                elif quote == ch:
                    in_string = False
                continue

            if in_string:
                continue

            if ch in pairs:
                stack.append((ch, line_no))
            elif ch in closing:
                if not stack or stack[-1][0] != closing[ch]:
                    return [{
                        "type": "error",
                        "message": f"Unexpected '{ch}'. Check bracket/brace matching.",
                        "line": line_no,
                    }]
                stack.pop()

    if stack:
        ch, line_no = stack[-1]
        return [{
            "type": "error",
            "message": f"Missing closing '{pairs[ch]}'.",
            "line": line_no,
        }]

    return [{
        "type": "success",
        "message": "Brackets and braces appear balanced.",
        "line": None,
    }]


def check_cpp_java(code, language):
    diagnostics = check_braces(code)

    lines = code.splitlines()

    # Basic structural checks. These are intentionally conservative:
    # the LLM performs the deeper language-aware review.
    for i, raw in enumerate(lines, start=1):
        line = raw.strip()

        if not line or line.startswith("//") or line.startswith("#"):
            continue

        if language == "C++":
            control = re.match(r"^(if|for|while|switch)\s*\(.*\)\s*[^;{]*$", line)
            declaration_like = re.match(
                r"^(int|float|double|char|long|short|string|bool|auto)\s+.+$",
                line
            )

            if declaration_like and not line.endswith(("{", "}", ";", ":")):
                diagnostics.append({
                    "type": "warning",
                    "message": "Possible missing semicolon.",
                    "line": i,
                })

            if control and not line.endswith(("{", ";", ")")):
                diagnostics.append({
                    "type": "warning",
                    "message": "Check control-statement syntax.",
                    "line": i,
                })

        elif language == "Java":
            declaration_like = re.match(
                r"^(int|float|double|char|long|short|String|boolean|var)\s+.+$",
                line
            )

            if declaration_like and not line.endswith(("{", "}", ";", ":")):
                diagnostics.append({
                    "type": "warning",
                    "message": "Possible missing semicolon.",
                    "line": i,
                })

    return diagnostics


def static_check(code, language):
    if language == "Python":
        return check_python(code)
    return check_cpp_java(code, language)


# ============================================================
# GROQ ANALYSIS
# ============================================================
def get_ai_analysis(code, language):
    client = Groq(api_key=api_key)

    prompt = f"""
You are CodeSense AI, an expert compiler assistant, senior software engineer,
debugger, algorithm analyst, and code reviewer.

Analyze this {language} program WITHOUT executing it.

Your job is to make the analysis useful to a student and interviewer.

You MUST:
1. Identify syntax errors, including missing semicolons, brackets, braces,
   incorrect indentation, invalid declarations, malformed statements, etc.
2. Identify likely logical errors when they can be determined statically.
3. Explain every important error in simple language.
4. For each error, provide the line number when possible.
5. Explain WHY the error happens and HOW to fix it.
6. Give corrected code.
7. Add useful comments to the corrected code.
8. Explain the program briefly.
9. Analyze time complexity (TC).
10. Analyze space complexity (SC).
11. Explain the reasoning behind TC and SC.
12. Suggest practical optimization improvements.
13. Give a code quality score from 0 to 100.
14. Give a security score from 0 to 100.
15. Mention potential security concerns if any.
16. Do NOT execute the code.
17. Do not claim that code is runtime-correct if it was not executed.

Return ONLY valid JSON with EXACTLY these keys:

{{
  "status": "Valid / Errors Found / Warnings",
  "summary": "Brief explanation of what the program does",
  "errors": [
    {{
      "line": 1,
      "severity": "Error / Warning",
      "title": "Short error title",
      "explanation": "Why the problem occurs",
      "fix": "How to fix it"
    }}
  ],
  "corrected_code": "Complete corrected and commented code",
  "time_complexity": "O(...)",
  "time_explanation": "Reason for TC",
  "space_complexity": "O(...)",
  "space_explanation": "Reason for SC",
  "optimization_notes": "Practical improvements",
  "quality_score": 0,
  "security_score": 0,
  "security_notes": "Security observations"
}}

If there are no errors, return an empty errors array.
Do not return Markdown fences.

Language: {language}

Code:
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
    except Exception as e:
        return {"error": str(e)}


# ============================================================
# COMPLEXITY GRAPH
# ============================================================
def plot_complexity(tc):
    text = str(tc).lower().replace(" ", "")
    n = np.linspace(1, 10, 200)

    if "o(1)" in text:
        y = np.ones_like(n)
    elif "o(logn)" in text:
        y = np.log(n)
    elif "o(nlogn)" in text:
        y = n * np.log(n)
    elif "o(n^2)" in text or "o(n²)" in text:
        y = n ** 2
    elif "o(n^3)" in text or "o(n³)" in text:
        y = n ** 3
    elif "o(2^n)" in text:
        y = 2 ** n
    elif "o(n)" in text:
        y = n
    else:
        y = n

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(n, y, linewidth=2)
    ax.set_title(f"Time Complexity Growth — {tc}")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Relative Operations")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    return fig


# ============================================================
# PDF
# ============================================================
def generate_pdf(original, language, result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    def safe(value):
        return str(value).encode("latin-1", "replace").decode("latin-1")

    def title(text, size=13):
        pdf.set_font("Helvetica", "B", size)
        pdf.cell(0, 9, safe(text), ln=True)
        pdf.set_font("Helvetica", "", 10)

    def text(value):
        pdf.multi_cell(0, 6, safe(value))
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, safe(f"CodeSense AI Report — {language}"), ln=True, align="C")
    pdf.ln(6)

    title("1. Analysis Status")
    text(result.get("status", "N/A"))

    title("2. Program Summary")
    text(result.get("summary", "N/A"))

    title("3. Detected Errors / Warnings")
    errors = result.get("errors", [])
    if not errors:
        text("No significant static errors were identified.")
    else:
        for item in errors:
            text(
                f"Line {item.get('line', '?')} | {item.get('severity', '')} | "
                f"{item.get('title', '')}\n"
                f"Explanation: {item.get('explanation', '')}\n"
                f"Fix: {item.get('fix', '')}"
            )

    title("4. Time Complexity (TC)")
    text(result.get("time_complexity", "N/A"))
    text(result.get("time_explanation", "N/A"))

    title("5. Space Complexity (SC)")
    text(result.get("space_complexity", "N/A"))
    text(result.get("space_explanation", "N/A"))

    title("6. Quality & Security")
    text(
        f"Code Quality Score: {result.get('quality_score', 'N/A')}/100\n"
        f"Security Score: {result.get('security_score', 'N/A')}/100\n"
        f"Security Notes: {result.get('security_notes', 'N/A')}"
    )

    title("7. Optimization Notes")
    text(result.get("optimization_notes", "N/A"))

    title("8. Original Code")
    text(original)

    title("9. Corrected & Annotated Code")
    text(result.get("corrected_code", ""))

    return bytes(pdf.output())


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 💻 CodeSense AI")
    st.caption("AI Code Analyzer • Debugger • Complexity Assistant")
    st.success("Groq AI connected")

    st.markdown("---")
    st.markdown("### What this app does")
    st.markdown(
        """
        - 🔎 Detects syntax problems
        - 🧠 Explains errors
        - ✨ Generates corrected code
        - ⏱️ TC analysis
        - 💾 SC analysis
        - 🔐 Security review
        - 📊 Quality score
        - 📄 PDF report
        """
    )

    st.info(
        "Safety mode: code is analyzed but NOT executed in this application."
    )


# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <h1>💻 CodeSense AI</h1>
        <p>
            Intelligent code analysis, error explanation, correction,
            complexity analysis and professional reporting.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INPUT
# ============================================================
left, right = st.columns([1, 1.05], gap="large")

with left:
    st.markdown("### 🧑‍💻 Code Workspace")

    language = st.selectbox(
        "Programming Language",
        ["Python", "C++", "Java"],
        index=["Python", "C++", "Java"].index(st.session_state.language),
    )

    code = st.text_area(
        "Paste your code",
        value=st.session_state.original_code,
        height=520,
        placeholder=(
            "Example:\n\n"
            "int main() {\n"
            "    int a = 10\n"
            "    return 0;\n"
            "}"
        ),
    )

    analyze = st.button(
        "🔍 Analyze, Detect Errors & Correct Code",
        type="primary",
        use_container_width=True,
    )

    if analyze:
        if not code.strip():
            st.warning("Please enter code first.")
        else:
            st.session_state.language = language
            st.session_state.original_code = code

            with st.spinner("Running static checks and AI analysis..."):
                local = static_check(code, language)
                result = get_ai_analysis(code, language)

            st.session_state.local_diagnostics = local

            if "error" in result:
                st.error(f"Groq API error: {result['error']}")
                st.session_state.analysis = None
            else:
                st.session_state.analysis = result
                st.success("Analysis completed successfully.")


# ============================================================
# OUTPUT
# ============================================================
with right:
    st.markdown("### 📊 Analysis Dashboard")

    result = st.session_state.analysis

    if not result:
        st.info(
            "Enter code on the left and click Analyze. "
            "The app will inspect the code without running it."
        )
    else:
        status = result.get("status", "Unknown")

        if status == "Valid":
            st.success("✅ No major syntax problems detected.")
        elif status == "Warnings":
            st.warning("⚠️ Analysis completed with warnings.")
        else:
            st.error("❌ Errors were detected and explained below.")

        tabs = st.tabs(
            [
                "🚨 Errors",
                "✨ Corrected Code",
                "📈 Complexity",
                "🔐 Quality & Security",
                "📄 PDF Report",
            ]
        )

        with tabs[0]:
            st.markdown("#### Detected Problems")

            errors = result.get("errors", [])
            if not errors:
                st.success("No significant errors were identified.")
            else:
                for item in errors:
                    line = item.get("line", "?")
                    severity = item.get("severity", "Error")
                    title = item.get("title", "Issue")

                    with st.expander(
                        f"Line {line} • {severity} • {title}",
                        expanded=True,
                    ):
                        st.write("**Why:**", item.get("explanation", ""))
                        st.write("**Fix:**", item.get("fix", ""))

            st.markdown("#### Local Static Checks")
            for d in st.session_state.local_diagnostics:
                if d["type"] == "error":
                    st.error(
                        f"Line {d.get('line', '?')}: {d['message']}"
                    )
                elif d["type"] == "warning":
                    st.warning(
                        f"Line {d.get('line', '?')}: {d['message']}"
                    )
                else:
                    st.success(d["message"])

        with tabs[1]:
            st.markdown("#### AI Corrected & Annotated Code")
            st.code(
                result.get("corrected_code", ""),
                language=language.lower(),
            )

            st.caption(
                "The corrected code is generated for review. "
                "This app does not execute it."
            )

        with tabs[2]:
            st.markdown("#### Algorithm Complexity")

            m1, m2 = st.columns(2)

            with m1:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">TIME COMPLEXITY</div>
                        <div class="metric-value">{result.get('time_complexity', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with m2:
                st.markdown(
                    f"""
                    <div class="metric-card">
                        <div class="metric-label">SPACE COMPLEXITY</div>
                        <div class="metric-value">{result.get('space_complexity', 'N/A')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("#### Why?")
            st.info(result.get("time_explanation", "N/A"))
            st.info(result.get("space_explanation", "N/A"))

            st.markdown("#### Complexity Growth")
            fig = plot_complexity(result.get("time_complexity", "O(n)"))
            st.pyplot(fig)
            plt.close(fig)

        with tabs[3]:
            q1, q2 = st.columns(2)

            with q1:
                st.metric(
                    "Code Quality",
                    f"{result.get('quality_score', 0)}/100",
                )

            with q2:
                st.metric(
                    "Security",
                    f"{result.get('security_score', 0)}/100",
                )

            st.markdown("#### Security Review")
            st.info(result.get("security_notes", "No security notes."))

            st.markdown("#### Optimization Suggestions")
            st.success(result.get("optimization_notes", "No optimization notes."))

            st.markdown("#### Program Summary")
            st.write(result.get("summary", "N/A"))

        with tabs[4]:
            pdf = generate_pdf(
                st.session_state.original_code,
                st.session_state.language,
                result,
            )

            st.success("Professional PDF report is ready.")

            st.download_button(
                "📥 Download Complete PDF Report",
                data=pdf,
                file_name="CodeSense_AI_Code_Analysis_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "CodeSense AI • Static analysis only • No user code execution • "
    "AI-powered code understanding and correction"
)
