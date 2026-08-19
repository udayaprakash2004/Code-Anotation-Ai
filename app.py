import ast
import json
import re
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from fpdf import FPDF
from groq import Groq


# ============================================================
# CODE SENSE AI
# AI CODE ERROR DETECTOR + ANNOTATOR + COMPLEXITY ANALYZER
# No user-code execution. No Piston API.
# ============================================================

st.set_page_config(
    page_title="CodeSense AI",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PROFESSIONAL BLUE UI
# ============================================================
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 15% 5%, rgba(59,130,246,.28), transparent 28%),
        radial-gradient(circle at 90% 15%, rgba(14,165,233,.18), transparent 25%),
        linear-gradient(135deg, #041329 0%, #082c5c 48%, #0b4d8f 100%);
    color: #f8fbff;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #031126, #062a55);
    border-right: 1px solid rgba(147,197,253,.22);
}
.block-container { padding-top: 1.4rem; max-width: 1500px; }

.hero {
    padding: 30px 34px;
    border-radius: 24px;
    background: linear-gradient(135deg, #0756c9, #0ea5e9);
    box-shadow: 0 18px 55px rgba(0,0,0,.28);
    margin-bottom: 22px;
}
.hero h1 { margin: 0; color: white; font-size: 43px; }
.hero p { margin: 8px 0 0; color: #e0f2fe; font-size: 17px; }

.card {
    background: rgba(4,25,53,.68);
    border: 1px solid rgba(147,197,253,.18);
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 15px;
}

.metric {
    background: rgba(12,61,117,.70);
    border: 1px solid rgba(147,197,253,.20);
    border-radius: 16px;
    padding: 15px;
    text-align: center;
}
.metric-label { color: #bfdbfe; font-size: 12px; }
.metric-value { color: white; font-size: 27px; font-weight: 800; }

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 44px;
}
div[data-baseweb="tab"] {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# GROQ SECRET
# ============================================================
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error(
        "GROQ_API_KEY is missing. Add a NEW key in "
        "Streamlit Cloud → Settings → Secrets."
    )
    st.stop()


# ============================================================
# SESSION STATE
# ============================================================
if "result" not in st.session_state:
    st.session_state.result = None
if "code" not in st.session_state:
    st.session_state.code = ""
if "language" not in st.session_state:
    st.session_state.language = "Python"
if "local_checks" not in st.session_state:
    st.session_state.local_checks = []


# ============================================================
# LANGUAGE HELPERS
# ============================================================
EXTENSIONS = {
    "Python": ".py",
    "C++": ".cpp",
    "Java": ".java",
}


# ============================================================
# LOCAL STATIC ANALYSIS
# This never executes user code.
# ============================================================
def python_static_check(code):
    checks = []

    try:
        ast.parse(code)
        checks.append({
            "severity": "success",
            "line": None,
            "title": "Python syntax is valid",
            "message": "The Python parser accepted the submitted syntax."
        })
    except SyntaxError as e:
        line = e.lineno or "?"
        msg = e.msg or "Syntax error"
        checks.append({
            "severity": "error",
            "line": line,
            "title": msg,
            "message": (
                f"Python detected a syntax problem on line {line}. "
                f"{e.text.strip() if e.text else ''}"
            )
        })

    return checks


def bracket_check(code):
    checks = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    reverse = {")": "(", "]": "[", "}": "{"}
    stack = []

    in_string = False
    quote = None
    escaped = False

    for line_no, line in enumerate(code.splitlines(), 1):
        i = 0
        while i < len(line):
            ch = line[i]

            if escaped:
                escaped = False
                i += 1
                continue

            if in_string:
                if ch == "\\":
                    escaped = True
                elif ch == quote:
                    in_string = False
                    quote = None
                i += 1
                continue

            if ch in ("'", '"'):
                in_string = True
                quote = ch
                i += 1
                continue

            if ch in pairs:
                stack.append((ch, line_no))
            elif ch in reverse:
                if not stack or stack[-1][0] != reverse[ch]:
                    checks.append({
                        "severity": "error",
                        "line": line_no,
                        "title": "Mismatched bracket or brace",
                        "message": f"Unexpected '{ch}' on line {line_no}."
                    })
                    return checks
                stack.pop()

            i += 1

    if stack:
        opening, line_no = stack[-1]
        checks.append({
            "severity": "error",
            "line": line_no,
            "title": "Missing closing bracket",
            "message": f"'{opening}' opened on line {line_no} has no matching closing symbol."
        })
    else:
        checks.append({
            "severity": "success",
            "line": None,
            "title": "Brackets and braces balanced",
            "message": "No unmatched brackets/braces were found."
        })

    return checks


def semicolon_check(code, language):
    checks = []
    lines = code.splitlines()

    if language not in ("C++", "Java"):
        return checks

    keywords_without_semicolon = (
        "if", "else", "for", "while", "switch", "try", "catch", "finally",
        "class", "public", "private", "protected"
    )

    declaration = re.compile(
        r"^(?:const\s+)?(?:unsigned\s+|signed\s+)?"
        r"(?:int|long|short|float|double|char|bool|string|String|boolean|"
        r"auto|size_t|byte)\s+.+"
    )

    for line_no, raw in enumerate(lines, 1):
        line = raw.strip()

        if not line or line.startswith("//") or line.startswith("#"):
            continue

        if declaration.match(line):
            if not line.endswith((";", "{", "}", ",")):
                checks.append({
                    "severity": "warning",
                    "line": line_no,
                    "title": "Possible missing semicolon",
                    "message": "This statement appears to require ';' at the end."
                })

        # Common assignment / output / return statements.
        if (
            ("=" in line or line.startswith(("return ", "cout ", "System.out.", "printf(")))
            and not line.endswith((";", "{", "}", ",", ":"))
            and not line.startswith(keywords_without_semicolon)
        ):
            checks.append({
                "severity": "warning",
                "line": line_no,
                "title": "Possible missing semicolon",
                "message": "This statement may need a terminating ';'."
            })

    return checks


def basic_language_check(code, language):
    checks = []
    checks.extend(bracket_check(code))
    checks.extend(semicolon_check(code, language))

    if language == "Java":
        if "class " not in code:
            checks.append({
                "severity": "warning",
                "line": None,
                "title": "No Java class detected",
                "message": "A Java source file normally contains a class declaration."
            })

    if language == "C++":
        if "#include" not in code and "using namespace" not in code:
            checks.append({
                "severity": "warning",
                "line": None,
                "title": "No include directive detected",
                "message": "Check whether required C++ headers are missing."
            })

    return checks


def local_static_analysis(code, language):
    if language == "Python":
        return python_static_check(code)
    return basic_language_check(code, language)


# ============================================================
# AI ANALYSIS
# ============================================================
def analyze_with_groq(code, language, local_checks):
    client = Groq(api_key=GROQ_API_KEY)

    local_summary = json.dumps(local_checks, ensure_ascii=False)

    prompt = f"""
You are CodeSense AI, an expert compiler assistant, senior software engineer,
debugger, code reviewer, algorithm analyst and security reviewer.

Analyze the submitted {language} source code WITHOUT executing it.

The application is a static analysis tool. Never claim that code was compiled
or executed.

LOCAL STATIC CHECKS:
{local_summary}

Perform a detailed but student-friendly analysis.

Requirements:
1. Detect syntax errors.
2. Detect likely missing semicolons.
3. Detect missing/mismatched (), [], {{}}.
4. Detect indentation problems for Python.
5. Detect malformed declarations/statements where reasonably clear.
6. Detect likely logical issues that can be identified without execution.
7. Give line numbers whenever possible.
8. Explain each problem in simple language.
9. Explain why it occurs.
10. Give an exact practical fix.
11. Produce complete corrected and commented code.
12. Briefly explain what the program does.
13. Calculate/estimate Time Complexity (TC).
14. Calculate/estimate Space Complexity (SC).
15. Explain why the TC and SC are what you report.
16. Suggest optimizations.
17. Review common security problems.
18. Give Code Quality Score 0-100.
19. Give Security Score 0-100.
20. Do not execute the code.
21. Do not invent runtime output.
22. If an issue cannot be confirmed statically, label it as a warning/possible issue.

Return ONLY valid JSON. No Markdown fences.

Exact JSON structure:
{{
  "status": "Valid|Errors Found|Warnings",
  "program_summary": "Short explanation",
  "errors": [
    {{
      "line": 1,
      "severity": "Error|Warning",
      "title": "Short title",
      "explanation": "Why it occurs",
      "fix": "Exact fix"
    }}
  ],
  "corrected_code": "Complete corrected and commented source code",
  "time_complexity": "O(...)",
  "time_explanation": "Detailed reason",
  "space_complexity": "O(...)",
  "space_explanation": "Detailed reason",
  "optimization_notes": "Useful improvements",
  "quality_score": 0,
  "quality_reason": "Why this score was given",
  "security_score": 0,
  "security_notes": "Security observations",
  "learning_notes": "Short student learning takeaway"
}}

Language: {language}

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

        raw = response.choices[0].message.content
        return json.loads(raw)

    except Exception as exc:
        return {"error": str(exc)}


# ============================================================
# MERGE LOCAL + AI ERRORS
# ============================================================
def merge_errors(ai_result, local_checks):
    errors = ai_result.get("errors", [])

    for item in local_checks:
        if item["severity"] == "success":
            continue

        duplicate = any(
            str(x.get("line")) == str(item.get("line"))
            and item["title"].lower() in str(x.get("title", "")).lower()
            for x in errors
        )

        if not duplicate:
            errors.insert(
                0,
                {
                    "line": item.get("line"),
                    "severity": "Error" if item["severity"] == "error" else "Warning",
                    "title": item["title"],
                    "explanation": item["message"],
                    "fix": "Review the indicated line and apply the suggested correction."
                }
            )

    ai_result["errors"] = errors

    if any(e.get("severity") == "Error" for e in errors):
        ai_result["status"] = "Errors Found"
    elif errors:
        ai_result["status"] = "Warnings"
    else:
        ai_result["status"] = "Valid"

    return ai_result


# ============================================================
# COMPLEXITY GRAPH
# ============================================================
def complexity_graph(tc):
    normalized = str(tc).lower().replace(" ", "")
    n = np.linspace(1, 10, 200)

    if "o(1)" in normalized:
        y = np.ones_like(n)
    elif "o(logn)" in normalized:
        y = np.log(n)
    elif "o(nlogn)" in normalized:
        y = n * np.log(n)
    elif "o(n^2)" in normalized or "o(n²)" in normalized:
        y = n ** 2
    elif "o(n^3)" in normalized or "o(n³)" in normalized:
        y = n ** 3
    elif "o(2^n)" in normalized:
        y = 2 ** n
    elif "o(n)" in normalized:
        y = n
    else:
        y = n

    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.plot(n, y, linewidth=2)
    ax.set_title(f"Time Complexity Growth — {tc}")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Relative Operations")
    ax.grid(alpha=0.20)
    fig.tight_layout()
    return fig


# ============================================================
# PDF REPORT
# ============================================================
def generate_pdf(code, language, result):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    def safe(value):
        return str(value).encode("latin-1", "replace").decode("latin-1")

    def heading(value, size=13):
        pdf.set_font("Helvetica", "B", size)
        pdf.cell(0, 9, safe(value), ln=True)
        pdf.set_font("Helvetica", "", 10)

    def paragraph(value):
        pdf.multi_cell(0, 6, safe(value))
        pdf.ln(2)

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, safe(f"CodeSense AI — {language} Code Analysis Report"),
             ln=True, align="C")
    pdf.ln(6)

    heading("1. Analysis Status")
    paragraph(result.get("status", "N/A"))

    heading("2. Program Summary")
    paragraph(result.get("program_summary", "N/A"))

    heading("3. Errors and Warnings")
    errors = result.get("errors", [])

    if not errors:
        paragraph("No significant static errors or warnings were identified.")
    else:
        for error in errors:
            paragraph(
                f"Line: {error.get('line', '?')}\n"
                f"Severity: {error.get('severity', 'N/A')}\n"
                f"Problem: {error.get('title', 'N/A')}\n"
                f"Why: {error.get('explanation', 'N/A')}\n"
                f"Fix: {error.get('fix', 'N/A')}"
            )

    heading("4. Time Complexity")
    paragraph(result.get("time_complexity", "N/A"))
    paragraph(result.get("time_explanation", "N/A"))

    heading("5. Space Complexity")
    paragraph(result.get("space_complexity", "N/A"))
    paragraph(result.get("space_explanation", "N/A"))

    heading("6. Code Quality")
    paragraph(
        f"Score: {result.get('quality_score', 'N/A')}/100\n"
        f"Reason: {result.get('quality_reason', 'N/A')}"
    )

    heading("7. Security")
    paragraph(
        f"Score: {result.get('security_score', 'N/A')}/100\n"
        f"Notes: {result.get('security_notes', 'N/A')}"
    )

    heading("8. Optimization")
    paragraph(result.get("optimization_notes", "N/A"))

    heading("9. Learning Takeaway")
    paragraph(result.get("learning_notes", "N/A"))

    heading("10. Original Code")
    paragraph(code)

    heading("11. Corrected and Annotated Code")
    paragraph(result.get("corrected_code", ""))

    output = pdf.output()
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 💻 CodeSense AI")
    st.caption("AI Code Analyzer & Annotator")

    st.success("Groq AI connected")

    st.markdown("---")
    st.markdown("### Supported Languages")
    st.markdown("🐍 Python\n\n⚙️ C++\n\n☕ Java")

    st.markdown("---")
    st.markdown("### Analysis")
    st.markdown(
        """
        🔎 Syntax detection  
        📍 Line-level explanation  
        🔧 Automatic correction  
        ⏱️ Time Complexity  
        💾 Space Complexity  
        🔐 Security review  
        ⭐ Quality score  
        📄 PDF report
        """
    )

    st.info(
        "Safety mode enabled: this version does NOT execute submitted code "
        "and does NOT use the public Piston API."
    )


# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero">
    <h1>💻 CodeSense AI</h1>
    <p>
        Intelligent source-code analysis, error explanation,
        correction, annotation, TC/SC analysis and professional reporting.
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# MAIN WORKSPACE
# ============================================================
left, right = st.columns([1, 1.08], gap="large")


with left:
    st.markdown("### 🧑‍💻 Code Workspace")

    language = st.selectbox(
        "Programming Language",
        ["Python", "C++", "Java"],
        index=["Python", "C++", "Java"].index(st.session_state.language),
    )

    code = st.text_area(
        "Write or paste your code",
        value=st.session_state.code,
        height=550,
        placeholder=(
            "Example C++:\n\n"
            "#include <iostream>\n"
            "using namespace std;\n\n"
            "int main() {\n"
            "    int a = 10\n"
            "    cout << a;\n"
            "    return 0;\n"
            "}"
        ),
    )

    st.caption(
        "The application analyzes your source code. It does not compile "
        "or execute it."
    )

    if st.button(
        "🔍 Analyze & Annotate Code",
        type="primary",
        use_container_width=True,
    ):
        if not code.strip():
            st.warning("Please enter some code.")
        else:
            st.session_state.code = code
            st.session_state.language = language

            with st.spinner("Checking syntax and asking AI to analyze the code..."):
                local_checks = local_static_analysis(code, language)
                result = analyze_with_groq(code, language, local_checks)

            if "error" in result:
                st.error(f"Groq API error: {result['error']}")
                st.session_state.result = None
            else:
                result = merge_errors(result, local_checks)
                st.session_state.local_checks = local_checks
                st.session_state.result = result
                st.success("Analysis completed.")


with right:
    st.markdown("### 📊 Analysis Dashboard")

    result = st.session_state.result

    if result is None:
        st.info(
            "Enter code and click Analyze & Annotate Code. "
            "Your results will appear here."
        )
    else:
        status = result.get("status", "Warnings")

        if status == "Valid":
            st.success("✅ Code analysis completed — no major problems detected.")
        elif status == "Errors Found":
            st.error("❌ Errors found. Review the explanations below.")
        else:
            st.warning("⚠️ Analysis completed with warnings.")

        # Top metrics
        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.markdown(
                f'<div class="metric"><div class="metric-label">TC</div>'
                f'<div class="metric-value">{result.get("time_complexity", "N/A")}</div></div>',
                unsafe_allow_html=True,
            )

        with m2:
            st.markdown(
                f'<div class="metric"><div class="metric-label">SC</div>'
                f'<div class="metric-value">{result.get("space_complexity", "N/A")}</div></div>',
                unsafe_allow_html=True,
            )

        with m3:
            st.markdown(
                f'<div class="metric"><div class="metric-label">QUALITY</div>'
                f'<div class="metric-value">{result.get("quality_score", "N/A")}</div></div>',
                unsafe_allow_html=True,
            )

        with m4:
            st.markdown(
                f'<div class="metric"><div class="metric-label">SECURITY</div>'
                f'<div class="metric-value">{result.get("security_score", "N/A")}</div></div>',
                unsafe_allow_html=True,
            )

        tabs = st.tabs([
            "🚨 Errors",
            "✨ Corrected Code",
            "📚 Explanation",
            "📈 TC / SC",
            "🔐 Quality",
            "📄 PDF",
        ])

        # ----------------------------------------------------
        # ERRORS
        # ----------------------------------------------------
        with tabs[0]:
            st.markdown("#### Detected Errors & Warnings")

            errors = result.get("errors", [])

            if not errors:
                st.success("No significant problems were identified.")
            else:
                for item in errors:
                    line = item.get("line", "?")
                    severity = item.get("severity", "Warning")
                    title = item.get("title", "Issue")

                    icon = "🚨" if severity == "Error" else "⚠️"

                    with st.expander(
                        f"{icon} Line {line} — {severity}: {title}",
                        expanded=True,
                    ):
                        st.markdown("**Why does this happen?**")
                        st.write(item.get("explanation", "N/A"))

                        st.markdown("**How do I fix it?**")
                        st.success(item.get("fix", "N/A"))

            st.markdown("#### Local Static Checks")

            for item in st.session_state.local_checks:
                if item["severity"] == "error":
                    st.error(
                        f"Line {item.get('line', '?')}: "
                        f"{item['title']} — {item['message']}"
                    )
                elif item["severity"] == "warning":
                    st.warning(
                        f"Line {item.get('line', '?')}: "
                        f"{item['title']} — {item['message']}"
                    )
                else:
                    st.success(item["message"])

        # ----------------------------------------------------
        # CORRECTED CODE
        # ----------------------------------------------------
        with tabs[1]:
            st.markdown("#### ✨ Corrected & Annotated Code")

            corrected = result.get("corrected_code", "")

            st.code(
                corrected,
                language=language.lower(),
            )

            st.info(
                "The corrected version is generated for review. "
                "This application intentionally does not execute it."
            )

        # ----------------------------------------------------
        # EXPLANATION
        # ----------------------------------------------------
        with tabs[2]:
            st.markdown("#### 📝 What Does This Code Do?")
            st.write(result.get("program_summary", "N/A"))

            st.markdown("#### 🎓 Learning Takeaway")
            st.info(result.get("learning_notes", "N/A"))

        # ----------------------------------------------------
        # COMPLEXITY
        # ----------------------------------------------------
        with tabs[3]:
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("### ⏱️ Time Complexity")
                st.metric("TC", result.get("time_complexity", "N/A"))
                st.write(result.get("time_explanation", "N/A"))

            with c2:
                st.markdown("### 💾 Space Complexity")
                st.metric("SC", result.get("space_complexity", "N/A"))
                st.write(result.get("space_explanation", "N/A"))

            st.markdown("### 📈 Complexity Visualization")
            fig = complexity_graph(result.get("time_complexity", "O(n)"))
            st.pyplot(fig)
            plt.close(fig)

        # ----------------------------------------------------
        # QUALITY
        # ----------------------------------------------------
        with tabs[4]:
            q1, q2 = st.columns(2)

            with q1:
                st.metric(
                    "Code Quality",
                    f'{result.get("quality_score", 0)}/100'
                )
                st.write(result.get("quality_reason", "N/A"))

            with q2:
                st.metric(
                    "Security",
                    f'{result.get("security_score", 0)}/100'
                )
                st.write(result.get("security_notes", "N/A"))

            st.markdown("### 🚀 Optimization Suggestions")
            st.success(result.get("optimization_notes", "N/A"))

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------
        with tabs[5]:
            st.markdown("### 📄 Professional Analysis Report")

            pdf_bytes = generate_pdf(
                st.session_state.code,
                st.session_state.language,
                result,
            )

            st.success("Your complete report is ready.")

            st.download_button(
                "📥 Download Full PDF Report",
                data=pdf_bytes,
                file_name="CodeSense_AI_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption(
    "CodeSense AI • AI-powered static code analysis • "
    "Python • C++ • Java • No arbitrary code execution"
)
