import ast
import base64
import html
import json
import os
import re
import time
from html.parser import HTMLParser
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import requests
import streamlit as st
import streamlit.components.v1 as components
from fpdf import FPDF
from groq import Groq
from streamlit_ace import st_ace


# ============================================================
# Code Annotation Ai — web-compiler / AI code reviewer
# ============================================================

st.set_page_config(
    page_title="Code Annotation Ai",
    page_icon="</>",
    layout="wide",
    initial_sidebar_state="collapsed",
)

APP_TITLE = "Code Annotation Ai"
APP_SUBTITLE = "a web-compiler"
LOGO_PATH = Path("logo.png")
MAX_CODE = 30000
JUDGE0_URL = st.secrets.get(
    "JUDGE0_URL",
    os.getenv("JUDGE0_URL", "https://ce.judge0.com"),
).rstrip("/")
JUDGE0_API_KEY = st.secrets.get(
    "JUDGE0_API_KEY",
    os.getenv("JUDGE0_API_KEY", ""),
)
GROQ_API_KEY = st.secrets.get(
    "GROQ_API_KEY",
    os.getenv("GROQ_API_KEY", ""),
)
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


# ============================================================
# Global styling — clean online-compiler look
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');


    :root {
        --bg: #f6f8fb;
        --surface: #ffffff;
        --surface-2: #f9fbfd;
        --ink: #15223a;
        --muted: #64748b;
        --border: #dce4ef;
        --brand: #2563eb;
        --brand-dark: #173a8f;
        --navy: #0f1f3d;
        --navy-2: #162a52;
        --success: #178a4d;
        --danger: #cc3340;
        --warning: #b96d00;
        --editor: #1e1e1e;
    }

    * { box-sizing: border-box; }

    html, body, [class*="css"] {
        font-family: "Inter", "Segoe UI", Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 100% 0%, rgba(37,99,235,.045), transparent 26%),
            linear-gradient(180deg, #f8fafc 0%, #f4f7fb 100%);
        color: var(--ink);
    }

    header[data-testid="stHeader"] {
        height: 0;
        background: transparent;
    }

    #MainMenu, footer {
        visibility: hidden;
    }

    .block-container {
        max-width: 1400px;
        padding: 0 22px 24px 22px;
    }

    /* Official product header */
    .brand-shell {
        margin: 0 -22px 12px -22px;
        min-height: 84px;
        padding: 8px 28px;
        background: #ffffff;
        border-bottom: 1px solid #dbe4ef;
        box-shadow: 0 3px 14px rgba(15,31,61,.06);
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
    }

    .brand-left {
        display: flex;
        align-items: center;
        gap: 15px;
        min-width: 0;
    }

    .brand-logo {
        display: block;
        width: 150px;
        height: 68px;
        object-fit: contain;
        object-position: center;
        background: #fff;
        flex: 0 0 auto;
    }

    .brand-copy {
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-width: 0;
    }

    .brand-title {
        font-size: 26px;
        line-height: 1.05;
        font-weight: 800;
        letter-spacing: -.45px;
        color: #0f1f3d;
        white-space: nowrap;
    }

    .brand-subtitle {
        margin-top: 4px;
        font-size: 12px;
        font-weight: 650;
        color: #4171b7;
    }

    .brand-nav {
        display: flex;
        align-items: center;
        gap: 24px;
        font-size: 12px;
        font-weight: 750;
        color: #24385b;
        white-space: nowrap;
        flex: 0 0 auto;
    }

    .brand-nav span {
        cursor: default;
    }

    .toolbar-label {
        font-size: 11px;
        font-weight: 750;
        color: #5f6d82;
        margin: 0 0 5px 1px;
    }

    .card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        box-shadow: 0 5px 18px rgba(20, 30, 50, .045);
    }

    .card-title {
        padding: 11px 14px;
        border-bottom: 1px solid #e8edf3;
        font-size: 13px;
        font-weight: 800;
        color: #22314d;
    }

    .section-card {
        background: #ffffff;
        border: 1px solid #dce4ef;
        border-radius: 10px;
        box-shadow: 0 5px 18px rgba(20,30,50,.045);
        overflow: hidden;
        margin-top: 14px;
    }

    .section-head {
        padding: 12px 15px;
        border-bottom: 1px solid #e8edf3;
        color: #173a8f;
        font-size: 14px;
        font-weight: 800;
        background: linear-gradient(90deg, #f7faff, #ffffff);
    }

    .section-body {
        padding: 14px;
        color: #344054;
        font-size: 12px;
        line-height: 1.6;
    }

    .feature-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 9px;
        border-radius: 999px;
        background: #eaf2ff;
        color: #1e4fa5;
        font-size: 10px;
        font-weight: 800;
        border: 1px solid #cfe0ff;
        margin-bottom: 9px;
    }

    .complexity-panel {
        background: #ffffff;
        border: 1px solid #cfdbeb;
        border-radius: 10px;
        box-shadow: 0 7px 20px rgba(22, 58, 100, .07);
        overflow: hidden;
    }

    .complexity-head {
        padding: 11px 13px;
        border-bottom: 1px solid #e6edf6;
        background: linear-gradient(90deg, #eef5ff, #ffffff);
        color: #173a8f;
        font-size: 13px;
        font-weight: 800;
    }

    .complexity-body {
        padding: 10px;
    }

    .always-visible-label {
        margin-top: 4px;
        margin-bottom: 8px;
        color: #173a8f;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .15px;
        text-transform: uppercase;
    }

    .summary-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 9px;
        padding: 11px;
    }

    .summary-item {
        background: #fff;
        border: 1px solid #e4e9f0;
        border-radius: 8px;
        padding: 10px 11px;
        min-height: 70px;
    }

    .summary-label {
        font-size: 10px;
        font-weight: 750;
        color: #718096;
    }

    .summary-value {
        margin-top: 5px;
        font-size: 22px;
        line-height: 1.1;
        font-weight: 800;
        color: #27354d;
    }

    .error { color: var(--danger); }
    .warning { color: var(--warning); }
    .info { color: #1d63c7; }
    .success { color: var(--success); }

    .issue-box, .note-box {
        margin: 0 11px 11px 11px;
        padding: 12px;
        background: #fff;
        border: 1px solid #e3e8ef;
        border-radius: 8px;
        color: #364153;
        font-size: 12px;
        line-height: 1.55;
    }

    .issue-box .line {
        color: var(--danger);
        font-weight: 800;
        margin-bottom: 5px;
    }

    /* Result tabs — always readable, including hover/focus */
    .stTabs {
        margin-top: 14px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0 !important;
        border-bottom: 1px solid #dbe3ed !important;
        background: #ffffff !important;
        box-shadow: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #334155 !important;
        font-size: 12px !important;
        font-weight: 750 !important;
        padding: 12px 15px !important;
        background: #ffffff !important;
        border: none !important;
        border-radius: 0 !important;
        opacity: 1 !important;
        box-shadow: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #173a8f !important;
        background: #f3f7fd !important;
    }

    .stTabs [data-baseweb="tab"]:focus,
    .stTabs [data-baseweb="tab"]:focus-visible {
        color: #173a8f !important;
        outline: none !important;
        box-shadow: inset 0 -2px 0 #2563eb !important;
    }

    .stTabs [aria-selected="true"] {
        color: #173a8f !important;
        background: #ffffff !important;
        border-bottom: 3px solid #2563eb !important;
    }

    /* Buttons: dark/official with white text for strong contrast */
    .stButton > button,
    .stDownloadButton > button {
        min-height: 38px !important;
        border-radius: 7px !important;
        font-weight: 750 !important;
        color: #ffffff !important;
        background: #101828 !important;
        border: 1px solid #101828 !important;
        box-shadow: 0 2px 5px rgba(15, 23, 42, .08) !important;
    }

    .stButton > button p,
    .stButton > button span,
    .stButton > button div,
    .stDownloadButton > button p,
    .stDownloadButton > button span,
    .stDownloadButton > button div {
        color: #ffffff !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        color: #ffffff !important;
        background: #162a52 !important;
        border-color: #162a52 !important;
    }

    .stButton > button[kind="primary"] {
        color: #ffffff !important;
        background: #2563eb !important;
        border-color: #2563eb !important;
    }

    .stButton > button[kind="primary"]:hover {
        color: #ffffff !important;
        background: #1d4ed8 !important;
        border-color: #1d4ed8 !important;
    }

    .stButton > button[kind="secondary"],
    .stDownloadButton > button[kind="secondary"] {
        color: #ffffff !important;
        background: #101828 !important;
        border-color: #101828 !important;
    }

    /* Streamlit's download links/buttons can inherit text colors; force them. */
    .stDownloadButton a,
    .stDownloadButton a:hover,
    .stDownloadButton button,
    .stDownloadButton button:hover {
        color: #ffffff !important;
    }

    .stDownloadButton svg,
    .stButton svg {
        fill: #ffffff !important;
        color: #ffffff !important;
    }

    div[data-baseweb="select"] > div {
        min-height: 38px !important;
        border-radius: 7px !important;
        border-color: #d7e0eb !important;
    }

    div[data-baseweb="select"] span {
        color: #22314d !important;
        font-weight: 650 !important;
    }

    .stTextArea textarea {
        background: white !important;
        color: #1e293b !important;
        border-radius: 7px !important;
        border: 1px solid #d9dfe8 !important;
        font-family: Consolas, "Courier New", monospace !important;
        font-size: 12px !important;
    }

    .output-panel {
        border: 1px solid #222;
        border-radius: 8px;
        overflow: hidden;
        background: #111;
    }

    .output-head {
        padding: 8px 11px;
        background: #191919;
        color: #d5d8de;
        border-bottom: 1px solid #292929;
        font-size: 11px;
        font-weight: 700;
    }

    .output-body {
        min-height: 132px;
        padding: 12px;
        white-space: pre-wrap;
        color: #76e58e;
        font: 12px/1.55 Consolas, "Courier New", monospace;
    }

    .output-error {
        color: #ff8181 !important;
    }

    .footer {
        padding: 14px 0 2px 0;
        text-align: center;
        color: #7c8798;
        font-size: 11px;
    }

    .small-caption {
        color: #748095;
        font-size: 11px;
        line-height: 1.45;
    }

    .section-card {
        background: #ffffff;
        border: 1px solid #d8e1ec;
        border-radius: 10px;
        margin: 14px 0;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(20, 35, 60, .045);
    }

    .section-head {
        padding: 14px 16px;
        background: linear-gradient(180deg, #f7faff 0%, #edf4fc 100%);
        border-bottom: 1px solid #dce5ef;
        color: #153a78 !important;
        font-size: 16px !important;
        font-weight: 850 !important;
    }

    .section-body {
        padding: 15px 16px 16px 16px;
        color: #27364e !important;
        font-size: 13px;
        line-height: 1.65;
    }

    .feature-badge {
        display: inline-block;
        margin-bottom: 10px;
        padding: 4px 8px;
        border-radius: 999px;
        background: #e7f0ff;
        border: 1px solid #c9dcff;
        color: #174ea6 !important;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: .55px;
    }

    .always-visible-label {
        margin: 18px 0 8px 0;
        color: #123b7a !important;
        font-size: 15px !important;
        font-weight: 850 !important;
        text-transform: uppercase;
        letter-spacing: .45px;
    }

    .complexity-panel {
        overflow: hidden;
        border: 1px solid #cbd9ea;
        border-radius: 10px;
        background: #ffffff;
        box-shadow: 0 6px 18px rgba(20, 35, 60, .05);
    }

    .complexity-head {
        padding: 13px 14px;
        background: linear-gradient(180deg, #f4f8ff 0%, #eaf2ff 100%);
        border-bottom: 1px solid #d8e4f2;
        color: #173f80 !important;
        font-size: 15px !important;
        font-weight: 850 !important;
    }

    .complexity-value-box {
        padding: 10px 14px 4px 14px;
    }

    .complexity-label {
        color: #596b84 !important;
        font-size: 12px !important;
        font-weight: 750 !important;
        margin-bottom: 3px;
    }

    .complexity-value {
        color: #143f94 !important;
        font-size: 32px !important;
        line-height: 1.05;
        font-weight: 900 !important;
        letter-spacing: -.5px;
    }

    .complexity-description {
        color: #526277 !important;
        font-size: 12px !important;
        padding: 0 14px 8px 14px;
    }

    .report-highlight {
        margin: 18px 0 10px 0;
        padding: 16px 18px;
        border: 2px solid #2f66c9;
        border-radius: 12px;
        background: linear-gradient(135deg, #eff6ff 0%, #ffffff 78%);
        box-shadow: 0 8px 24px rgba(37,99,235,.09);
    }

    .report-title {
        color: #153a78 !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        margin-bottom: 4px;
    }

    .report-subtitle {
        color: #52657f !important;
        font-size: 12px !important;
        margin-bottom: 10px;
    }

    .run-highlight {
        margin: 18px 0 10px 0;
        padding: 15px 17px;
        border: 1px solid #cfdbea;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 6px 18px rgba(20,35,60,.045);
    }

    .run-title {
        color: #153a78 !important;
        font-size: 18px !important;
        font-weight: 900 !important;
        margin-bottom: 4px;
    }

    .run-subtitle {
        color: #5b6c83 !important;
        font-size: 12px !important;
    }

    @media (max-width: 900px) {
        .brand-shell {
            align-items: flex-start;
            flex-direction: column;
            gap: 8px;
            padding: 10px 18px;
        }
        .brand-nav {
            gap: 14px;
            align-self: flex-start;
        }
        .brand-title {
            font-size: 22px;
        }
        .summary-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Branding
# ============================================================

def load_logo_data_uri(path):
    try:
        raw = Path(path).read_bytes()
        encoded = base64.b64encode(raw).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except OSError:
        return ""

logo_uri = load_logo_data_uri(LOGO_PATH)

brand_left, brand_right = st.columns([3.1, 1.35], gap="small")

with brand_left:
    if logo_uri:
        st.markdown(
            f"""
            <div class="brand-bar" style="gap:16px;">
                <img class="brand-logo" src="{logo_uri}" alt="Code Annotation Ai logo"
                     style="width:108px;height:64px;object-fit:contain;">
                <div>
                    <div style="font-size:27px;font-weight:900;line-height:1.05;color:#0f2347;">
                        Code Annotation Ai
                    </div>
                    <div style="margin-top:4px;font-size:13px;font-weight:700;color:#4b6ea8;">
                        a web-compiler
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="brand-bar">
                <div>
                    <div style="font-size:27px;font-weight:900;color:#0f2347;">
                        Code Annotation Ai
                    </div>
                    <div style="margin-top:4px;font-size:13px;font-weight:700;color:#4b6ea8;">
                        a web-compiler
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with brand_right:
    st.markdown(
        """
        <div class="brand-bar brand-nav">
            <span>Home</span>
            <span>Analyze</span>
            <span>Run</span>
            <span>Report</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Language definitions
# ============================================================

LANGUAGES = [
    "C",
    "C++",
    "Java",
    "Python",
    "JavaScript",
    "HTML",
    "CSS",
]

ACE_MODES = {
    "C": "c_cpp",
    "C++": "c_cpp",
    "Java": "java",
    "Python": "python",
    "JavaScript": "javascript",
    "HTML": "html",
    "CSS": "css",
}

EXTENSIONS = {
    "C": "c",
    "C++": "cpp",
    "Java": "java",
    "Python": "py",
    "JavaScript": "js",
    "HTML": "html",
    "CSS": "css",
}

JUDGE0_IDS = {
    "C": 50,
    "C++": 54,
    "Java": 62,
    "Python": 71,
    "JavaScript": 63,
}

EXAMPLES = {
    "C": {
        "Hello World": """#include <stdio.h>

int main(void) {
    printf("Hello World\\n");
    return 0;
}""",
        "Missing Semicolon": """#include <stdio.h>

int main(void) {
    int a = 10
    printf("%d\\n", a);
    return 0;
}""",
        "Logic Review": """#include <stdio.h>

int main(void) {
    for (int i = 0; i < 5; i++) {
        printf("%d ", i);
    }
    return 0;
}""",
    },
    "C++": {
        "Hello World": """#include <iostream>
using namespace std;

int main() {
    cout << "Hello World" << endl;
    return 0;
}""",
        "Missing Semicolon": """#include <iostream>
using namespace std;

int main() {
    int a = 10
    cout << a << endl;
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
    },
    "Java": {
        "Hello World": """public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}""",
        "Missing Semicolon": """public class Main {
    public static void main(String[] args) {
        int a = 10
        System.out.println(a);
    }
}""",
        "Logic Review": """public class Main {
    public static void main(String[] args) {
        for (int i = 0; i < 5; i++) {
            System.out.print(i + " ");
        }
    }
}""",
    },
    "Python": {
        "Hello World": """def main():
    print("Hello World")

main()""",
        "Syntax Error": """def main():
    value = 10
    print(value

main()""",
        "Logic Review": """def main():
    total = 0
    for i in range(5):
        total += i
    print(total)

main()""",
    },
    "JavaScript": {
        "Hello World": """function main() {
    console.log("Hello World");
}

main();""",
        "Syntax Error": """function main() {
    const value = 10
    console.log(value);
}

main();""",
        "Logic Review": """function main() {
    let total = 0;
    for (let i = 0; i < 5; i++) {
        total += i;
    }
    console.log(total);
}

main();""",
    },
    "HTML": {
        "Hello World": """<!DOCTYPE html>
<html>
<head>
    <title>Code Annotation Ai</title>
</head>
<body>
    <h1>Hello World</h1>
    <p>Welcome to the web-compiler.</p>
</body>
</html>""",
        "Landing Page": """<!DOCTYPE html>
<html>
<head>
    <title>Demo Page</title>
</head>
<body>
    <main>
        <h1>Code Annotation Ai</h1>
        <button onclick="document.body.style.background='#f5f7fa'">
            Click me
        </button>
    </main>
</body>
</html>""",
        "Form": """<!DOCTYPE html>
<html>
<body>
    <form>
        <label>Name</label>
        <input type="text" placeholder="Enter your name">
        <button type="submit">Submit</button>
    </form>
</body>
</html>""",
    },
    "CSS": {
        "Hello World": """body {
    font-family: Arial, sans-serif;
    background: #f4f4f4;
}

h1 {
    color: #4f46e5;
}""",
        "Card": """.card {
    width: 320px;
    margin: 40px auto;
    padding: 24px;
    border-radius: 14px;
    background: white;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.card h2 {
    margin-top: 0;
}""",
        "Responsive": """body {
    margin: 0;
    font-family: Arial, sans-serif;
}

.container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

@media (max-width: 800px) {
    .container {
        grid-template-columns: 1fr;
    }
}""",
    },
}


# ============================================================
# Session state
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = "Python"

if "source_code" not in st.session_state:
    st.session_state.source_code = EXAMPLES["Python"]["Hello World"]

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "execution" not in st.session_state:
    st.session_state.execution = None

if "stdin_text" not in st.session_state:
    st.session_state.stdin_text = ""


# ============================================================
# Utility helpers
# ============================================================

def normalize_text(value, fallback=""):
    return str(value if value is not None else fallback).strip()


def bracket_check(code):
    pairs = {"(": ")", "[": "]", "{": "}"}
    reverse = {")": "(", "]": "[", "}": "}"}
    stack = []
    in_single = False
    in_double = False
    in_backtick = False
    escape = False

    for line_no, line in enumerate(code.splitlines(), 1):
        for idx, ch in enumerate(line):
            if escape:
                escape = False
                continue

            if ch == "\\" and (in_single or in_double or in_backtick):
                escape = True
                continue

            if ch == "'" and not in_double and not in_backtick:
                in_single = not in_single
                continue
            if ch == '"' and not in_single and not in_backtick:
                in_double = not in_double
                continue
            if ch == "`" and not in_single and not in_double:
                in_backtick = not in_backtick
                continue

            if in_single or in_double or in_backtick:
                continue

            # Ignore common single-line comments.
            if ch == "#":
                break
            if ch == "/" and idx + 1 < len(line) and line[idx + 1] == "/":
                break

            if ch in pairs:
                stack.append((ch, line_no))
            elif ch in reverse:
                if not stack or stack[-1][0] != reverse[ch]:
                    return [{
                        "line": line_no,
                        "severity": "Error",
                        "title": "Mismatched bracket or brace",
                        "explanation": f"Unexpected '{ch}' on line {line_no}.",
                        "why": "The closing symbol does not match the most recent opening symbol.",
                        "fix": "Match each closing symbol with the correct opening symbol.",
                    }]
                stack.pop()

    if stack:
        ch, line_no = stack[-1]
        return [{
            "line": line_no,
            "severity": "Error",
            "title": "Missing closing bracket",
            "explanation": f"'{ch}' opened on line {line_no} has no matching closing symbol.",
            "why": "The parser expects the block or expression to be closed.",
            "fix": "Add the corresponding closing bracket, parenthesis, or brace.",
        }]

    return []


def python_check(code):
    try:
        ast.parse(code)
        return []
    except SyntaxError as exc:
        line = exc.lineno or "?"
        text = (exc.text or "").strip()
        return [{
            "line": line,
            "severity": "Error",
            "title": exc.msg or "Python syntax error",
            "explanation": text or "Python syntax is invalid.",
            "why": "Python could not parse the source into a valid syntax tree.",
            "fix": "Correct the syntax around the indicated line and analyze again.",
        }]


def semicolon_check(code, language):
    if language not in {"C", "C++", "Java"}:
        return []

    issues = []
    declaration = re.compile(
        r"^\s*(?:(?:const|static|final|public|private|protected)\s+)*"
        r"(?:int|float|double|char|bool|long|short|byte|String|boolean|size_t|auto)"
        r"\s+\w+.*"
    )

    for line_no, line in enumerate(code.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(("//", "#", "/*", "*")):
            continue
        if declaration.match(stripped) and not stripped.endswith((";", "{", "}", ",")):
            issues.append({
                "line": line_no,
                "severity": "Error",
                "title": "Possible missing semicolon",
                "explanation": "This declaration appears to require a semicolon.",
                "why": "C, C++, and Java statement declarations normally end with ';'.",
                "fix": "Add ';' at the end of the statement.",
            })

    return issues


def javascript_check(code):
    issues = []
    lines = code.splitlines()
    for line_no, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if re.match(r"^(const|let|var)\s+\w+\s*=", stripped):
            if not stripped.endswith((";", "{", "}")):
                issues.append({
                    "line": line_no,
                    "severity": "Warning",
                    "title": "Possible missing semicolon",
                    "explanation": "This JavaScript statement does not end with ';'.",
                    "why": "Although JavaScript can often use automatic semicolon insertion, explicit semicolons improve consistency.",
                    "fix": "Consider adding ';' at the end of the statement.",
                })
    return issues


class _HTMLValidationParser(HTMLParser):
    VOID_TAGS = {
        "area", "base", "br", "col", "embed", "hr", "img",
        "input", "link", "meta", "param", "source", "track", "wbr",
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag not in self.VOID_TAGS:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in self.VOID_TAGS:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append({
                "line": self.getpos()[0],
                "severity": "Error",
                "title": f"Unexpected closing tag </{tag}>",
                "explanation": "The closing HTML tag does not match the current open element.",
                "why": "HTML element nesting must remain structurally consistent.",
                "fix": f"Close the correct parent element before </{tag}>.",
            })
            return
        self.stack.pop()


def html_check(code):
    parser = _HTMLValidationParser()
    try:
        parser.feed(code)
        parser.close()
    except Exception as exc:
        parser.errors.append({
            "line": 1,
            "severity": "Error",
            "title": "HTML parsing error",
            "explanation": str(exc),
            "why": "The HTML parser could not complete the document.",
            "fix": "Check tag syntax and nesting.",
        })

    if parser.stack:
        parser.errors.append({
            "line": 1,
            "severity": "Warning",
            "title": "Unclosed HTML element",
            "explanation": f"Open element <{parser.stack[-1]}> was not closed.",
            "why": "Unclosed elements can produce unexpected browser layout behavior.",
            "fix": f"Add </{parser.stack[-1]}> where appropriate.",
        })

    return parser.errors


def local_checks(code, language):
    issues = []
    issues.extend(bracket_check(code))

    if language == "Python":
        issues.extend(python_check(code))
    elif language in {"C", "C++", "Java"}:
        issues.extend(semicolon_check(code, language))
    elif language == "JavaScript":
        issues.extend(javascript_check(code))
    elif language == "HTML":
        issues.extend(html_check(code))

    return issues


def normalize_analysis(ai, local_issues, code, language):
    result = {
        "errors": list(ai.get("errors", [])),
        "warnings": list(ai.get("warnings", [])),
        "info": list(ai.get("info", [])),
        "summary": normalize_text(ai.get("summary"), "No summary available."),
        "corrected_code": normalize_text(ai.get("corrected_code"), code),
        "time_complexity": normalize_text(ai.get("time_complexity"), "N/A"),
        "time_explanation": normalize_text(ai.get("time_explanation")),
        "space_complexity": normalize_text(ai.get("space_complexity"), "N/A"),
        "space_explanation": normalize_text(ai.get("space_explanation")),
        "optimization": normalize_text(ai.get("optimization")),
        "security": normalize_text(ai.get("security")),
        "notes": normalize_text(ai.get("notes")),
        "score": int(max(0, min(100, float(ai.get("score", 0))))),
    }

    existing = result["errors"] + result["warnings"] + result["info"]

    for issue in local_issues:
        duplicate = any(
            str(item.get("line")) == str(issue.get("line"))
            and item.get("title") == issue.get("title")
            for item in existing
        )
        if not duplicate:
            if issue.get("severity") == "Warning":
                result["warnings"].insert(0, issue)
            else:
                result["errors"].insert(0, issue)

    return result


# ============================================================
# Groq analysis
# ============================================================

def analyze_with_ai(code, language):
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY is missing.")

    client = Groq(api_key=GROQ_API_KEY)

    prompt = f"""
You are Code Annotation Ai, a professional code-analysis and web-compiler assistant.

Analyze the following {language} source code. Do not invent runtime output.

Return ONLY valid JSON in this exact shape:
{{
  "errors": [
    {{
      "line": 1,
      "severity": "Error",
      "title": "short title",
      "explanation": "what is wrong",
      "why": "why it matters",
      "fix": "specific correction"
    }}
  ],
  "warnings": [],
  "info": [],
  "summary": "what the program does",
  "corrected_code": "complete corrected source code",
  "time_complexity": "O(n) or N/A",
  "time_explanation": "brief explanation",
  "space_complexity": "O(1) or N/A",
  "space_explanation": "brief explanation",
  "optimization": "practical optimization suggestions",
  "security": "basic security review",
  "notes": "learning notes",
  "score": 0
}}

Rules:
- Preserve the intended behavior when correcting code.
- Detect syntax, structural, logic, and important quality issues.
- For C, C++, and Java, detect missing semicolons where applicable.
- For Python, detect syntax and indentation problems.
- For JavaScript, detect common syntax and logic issues.
- For HTML, check tag structure and document validity.
- For CSS, check selectors, braces, declarations, and obvious structural issues.
- For HTML and CSS, algorithmic complexity is normally "N/A".
- For simple linear code use O(n); nested loops may be O(n^2); logarithmic algorithms may be O(log n).
- The complexity should describe the algorithm, not a fabricated benchmark.
- Return the full corrected source.
- Keep comments concise and educational where useful.
- Score quality from 0 to 100.

SOURCE:
{code}
""".strip()

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        reasoning_effort="low",
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def analyze_code(code, language):
    local_issues = local_checks(code, language)

    try:
        ai = analyze_with_ai(code, language)
    except Exception as exc:
        return {
            "errors": local_issues,
            "warnings": [],
            "info": [],
            "summary": "AI analysis could not be completed.",
            "corrected_code": code,
            "time_complexity": "N/A",
            "time_explanation": str(exc),
            "space_complexity": "N/A",
            "space_explanation": "",
            "optimization": "",
            "security": "",
            "notes": "",
            "score": 0,
        }

    return normalize_analysis(ai, local_issues, code, language)


# ============================================================
# Complexity graphs
# ============================================================

def complexity_kind(expression):
    text = expression.lower().replace(" ", "")
    if "2^n" in text or "2ⁿ" in text or "exponential" in text:
        return "O(2^n)"
    if "n!" in text or "factorial" in text:
        return "O(n!)"
    if "nlogn" in text or "n*log" in text or "nlog(n)" in text:
        return "O(n log n)"
    if "logn" in text or "log(n)" in text:
        return "O(log n)"
    if "n^3" in text or "n³" in text:
        return "O(n^3)"
    if "n^2" in text or "n²" in text or "quadratic" in text:
        return "O(n^2)"
    if re.search(r"\bo\(n\)", text):
        return "O(n)"
    if text in {"o(1)", "constant", "constanttime", "constantspace"}:
        return "O(1)"
    return "N/A"


def complexity_values(kind):
    n = np.arange(1, 51)
    safe_n = n.astype(float)

    if kind == "O(1)":
        y = np.ones_like(safe_n)
    elif kind == "O(log n)":
        y = np.log2(safe_n)
    elif kind == "O(n)":
        y = safe_n
    elif kind == "O(n log n)":
        y = safe_n * np.log2(safe_n)
    elif kind == "O(n^2)":
        y = safe_n**2
    elif kind == "O(n^3)":
        y = safe_n**3
    elif kind == "O(2^n)":
        y = np.minimum(2.0**safe_n, 1e12)
    elif kind == "O(n!)":
        y = np.minimum(np.cumprod(safe_n), 1e12)
    else:
        y = None

    if y is None:
        return n, None

    max_y = max(float(np.max(y)), 1.0)
    return n, y / max_y


def show_complexity_plot(title, expression):
    kind = complexity_kind(expression)
    n, y = complexity_values(kind)

    if y is None:
        st.info(f"{title}: {expression or 'N/A'} — no standard growth curve available.")
        return

    fig, ax = plt.subplots(figsize=(5.7, 3.05))
    ax.plot(n, y, linewidth=2)
    ax.set_title(f"{title} — {kind}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Input size (normalized)")
    ax.set_ylabel("Relative growth")
    ax.grid(alpha=0.22)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    st.caption(
        "The curve visualizes theoretical growth. It is not a measured benchmark of this single execution."
    )


# ============================================================
# Judge0 execution
# ============================================================

def run_judge0(code, language, stdin_text):
    if language not in JUDGE0_IDS:
        return {
            "ok": False,
            "status": "Unsupported",
            "stdout": "",
            "stderr": "This language uses browser preview instead of Judge0 execution.",
            "compile_output": "",
            "time": None,
            "memory": None,
        }

    payload = {
        "source_code": code,
        "language_id": JUDGE0_IDS[language],
        "stdin": stdin_text or "",
        "cpu_time_limit": 2,
        "wall_time_limit": 5,
        "memory_limit": 128000,
        "enable_network": False,
    }

    headers = {"Content-Type": "application/json"}
    if JUDGE0_API_KEY:
        headers["X-Auth-Token"] = JUDGE0_API_KEY

    start = time.perf_counter()

    try:
        response = requests.post(
            f"{JUDGE0_URL}/submissions/?base64_encoded=false&wait=true",
            json=payload,
            headers=headers,
            timeout=30,
        )
    except requests.RequestException as exc:
        return {
            "ok": False,
            "status": "Connection Error",
            "stdout": "",
            "stderr": f"Judge0 connection error: {exc}",
            "compile_output": "",
            "time": None,
            "memory": None,
            "elapsed": time.perf_counter() - start,
        }

    if response.status_code not in (200, 201):
        return {
            "ok": False,
            "status": f"Judge0 HTTP {response.status_code}",
            "stdout": "",
            "stderr": response.text[:5000],
            "compile_output": "",
            "time": None,
            "memory": None,
            "elapsed": time.perf_counter() - start,
        }

    data = response.json()

    # Some Judge0 deployments return a token even when wait=true is ignored.
    if data.get("token") and not data.get("stdout") and not data.get("status"):
        token = data["token"]
        for _ in range(20):
            time.sleep(0.6)
            try:
                poll = requests.get(
                    f"{JUDGE0_URL}/submissions/{token}?base64_encoded=false",
                    headers=headers,
                    timeout=10,
                )
                if poll.status_code != 200:
                    continue
                data = poll.json()
                status_id = (data.get("status") or {}).get("id")
                if status_id not in (1, 2):
                    break
            except requests.RequestException:
                continue

    status = (data.get("status") or {}).get("description", "Unknown")
    return {
        "ok": status == "Accepted",
        "status": status,
        "stdout": data.get("stdout") or "",
        "stderr": data.get("stderr") or "",
        "compile_output": data.get("compile_output") or "",
        "message": data.get("message") or "",
        "time": data.get("time"),
        "memory": data.get("memory"),
        "elapsed": time.perf_counter() - start,
    }


# ============================================================
# Browser preview for HTML/CSS
# ============================================================

def html_preview(source, language):
    if language == "HTML":
        document = source
    elif language == "CSS":
        document = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{source}</style>
</head>
<body>
<div class="preview-shell">
    <h1>CSS Preview</h1>
    <p>This preview wraps your CSS with a small sample document.</p>
    <button>Sample Button</button>
</div>
</body>
</html>"""
    else:
        return

    components.html(
        document,
        height=430,
        scrolling=True,
    )


# ============================================================
# PDF report
# ============================================================

def make_pdf(language, original, result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, 15)

    def safe(value):
        return (
            str(value)
            .encode("latin-1", "replace")
            .decode("latin-1")
        )

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, safe("Code Annotation Ai Report"), ln=True, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, safe(f"Language: {language}"), ln=True)
    pdf.ln(3)

    sections = [
        ("Analysis Summary", result.get("summary", "")),
        ("Errors", json.dumps(result.get("errors", []), indent=2)),
        ("Warnings", json.dumps(result.get("warnings", []), indent=2)),
        ("Info", json.dumps(result.get("info", []), indent=2)),
        ("Time Complexity", result.get("time_complexity", "")),
        ("Time Explanation", result.get("time_explanation", "")),
        ("Space Complexity", result.get("space_complexity", "")),
        ("Space Explanation", result.get("space_explanation", "")),
        ("Optimization", result.get("optimization", "")),
        ("Security", result.get("security", "")),
        ("Notes", result.get("notes", "")),
        ("Verification Status", result.get("execution_status", "Not run")),
        ("Execution Time", result.get("execution_time", "")),
        ("Program Output", result.get("execution_stdout", "")),
        ("Compiler / Runtime Messages", result.get("execution_stderr", "") or result.get("execution_compile_output", "")),
        ("Original Code", original),
        ("Corrected Code", result.get("corrected_code", "")),
    ]

    for heading, body in sections:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 7, safe(heading), ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(0, 5, safe(body))
        pdf.ln(2)

    return bytes(pdf.output(dest="S"))


# ============================================================
# Controls
# ============================================================

c1, c2, c3, c4, c5 = st.columns([1.0, 1.45, 1.0, 0.9, 0.9], gap="small")

with c1:
    st.markdown('<div class="toolbar-label">Language</div>', unsafe_allow_html=True)
    selected_language = st.selectbox(
        "language",
        LANGUAGES,
        index=LANGUAGES.index(st.session_state.language),
        label_visibility="collapsed",
    )

with c2:
    st.markdown('<div class="toolbar-label">Example</div>', unsafe_allow_html=True)
    example_names = list(EXAMPLES[selected_language].keys())
    selected_example = st.selectbox(
        "example",
        example_names,
        label_visibility="collapsed",
    )

with c3:
    st.markdown('<div class="toolbar-label">&nbsp;</div>', unsafe_allow_html=True)
    load_example = st.button("Load Example", use_container_width=True)

with c4:
    st.markdown('<div class="toolbar-label">&nbsp;</div>', unsafe_allow_html=True)
    analyze_button = st.button("Analyze", type="primary", use_container_width=True)

with c5:
    st.markdown('<div class="toolbar-label">&nbsp;</div>', unsafe_allow_html=True)
    clear_button = st.button("Clear", use_container_width=True)

if selected_language != st.session_state.language:
    st.session_state.language = selected_language
    st.session_state.source_code = EXAMPLES[selected_language][list(EXAMPLES[selected_language].keys())[0]]
    st.session_state.analysis = None
    st.session_state.execution = None
    st.rerun()

if load_example:
    st.session_state.source_code = EXAMPLES[selected_language][selected_example]
    st.session_state.analysis = None
    st.session_state.execution = None
    st.rerun()

if clear_button:
    st.session_state.source_code = ""
    st.session_state.analysis = None
    st.session_state.execution = None
    st.rerun()


# ============================================================
# Editor + analysis summary + always-visible complexity graphs
# ============================================================

left, right = st.columns([1.08, 0.92], gap="medium")

with left:
    st.markdown('<div class="card-title">Code Editor</div>', unsafe_allow_html=True)

    source = st_ace(
        value=st.session_state.source_code,
        language=ACE_MODES[selected_language],
        theme="tomorrow_night",
        height=430,
        font_size=14,
        tab_size=4,
        wrap=False,
        show_gutter=True,
        show_print_margin=False,
        auto_update=True,
        key=f"code_editor_{selected_language}",
    )

    if source is None:
        source = st.session_state.source_code
    st.session_state.source_code = source

    st.markdown(
        '<div class="toolbar-label" style="margin-top:9px;">Custom Input (stdin)</div>',
        unsafe_allow_html=True,
    )
    stdin_text = st.text_area(
        "stdin",
        value=st.session_state.stdin_text,
        height=74,
        label_visibility="collapsed",
        placeholder="Enter program input here, one value per line if needed...",
    )
    st.session_state.stdin_text = stdin_text

with right:
    result = st.session_state.analysis
    errors = result.get("errors", []) if result else []
    warnings = result.get("warnings", []) if result else []
    infos = result.get("info", []) if result else []
    score = result.get("score", 0) if result else 0

    st.markdown('<div class="card-title">Analysis Summary</div>', unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="summary-grid">
            <div class="summary-item">
                <div class="summary-label error">Errors</div>
                <div class="summary-value error">{len(errors)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label warning">Warnings</div>
                <div class="summary-value">{len(warnings)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label info">Info</div>
                <div class="summary-value">{len(infos)}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label success">Score</div>
                <div class="summary-value success">{score}<small style="font-size:12px;">/100</small></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if result and errors:
        first = errors[0]
        st.markdown(
            f"""
            <div class="issue-box">
                <div class="line">Line {html.escape(str(first.get("line", "?")))}</div>
                <b>{html.escape(str(first.get("title", "Issue")))}</b><br>
                {html.escape(str(first.get("explanation", "")))}<br><br>
                <b>Why?</b><br>
                {html.escape(str(first.get("why", "")))}<br><br>
                <b>How to Fix?</b><br>
                {html.escape(str(first.get("fix", "")))}
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif result:
        st.markdown(
            '<div class="issue-box"><div class="line" style="color:#149447;">No blocking errors found.</div>'
            "Review the sections below for code quality, complexity, optimization, and security.</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="issue-box">Analyze the code to populate the dashboard and complexity graphs.</div>',
            unsafe_allow_html=True,
        )

    # Highlight feature: graphs are always visible beside the user's code.
    st.markdown(
        '<div class="always-visible-label">Complexity Visualizer — always visible</div>',
        unsafe_allow_html=True,
    )
    graph_left, graph_right = st.columns(2, gap="small")

    with graph_left:
        st.markdown(
            '<div class="complexity-panel"><div class="complexity-head">Time Complexity</div><div class="complexity-body">',
            unsafe_allow_html=True,
        )
        time_expression = result.get("time_complexity", "N/A") if result else "N/A"
        st.markdown(
            f"""
            <div class="complexity-value-box">
                <div class="complexity-label">Big-O Time</div>
                <div class="complexity-value">{html.escape(str(time_expression))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="complexity-description">{html.escape(result.get("time_explanation", "") if result else "")}</div>',
            unsafe_allow_html=True,
        )
        show_complexity_plot("Time Complexity Growth", time_expression)
        st.markdown("</div></div>", unsafe_allow_html=True)

    with graph_right:
        st.markdown(
            '<div class="complexity-panel"><div class="complexity-head">Space Complexity</div><div class="complexity-body">',
            unsafe_allow_html=True,
        )
        space_expression = result.get("space_complexity", "N/A") if result else "N/A"
        st.markdown(
            f"""
            <div class="complexity-value-box">
                <div class="complexity-label">Big-O Space</div>
                <div class="complexity-value">{html.escape(str(space_expression))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="complexity-description">{html.escape(result.get("space_explanation", "") if result else "")}</div>',
            unsafe_allow_html=True,
        )
        show_complexity_plot("Space Complexity Growth", space_expression)
        st.markdown("</div></div>", unsafe_allow_html=True)


# ============================================================
# Analyze action
# ============================================================

if analyze_button:
    if not source.strip():
        st.warning("Please enter code before analyzing.")
    elif len(source) > MAX_CODE:
        st.error(f"Code is too large. Maximum size is {MAX_CODE} characters.")
    else:
        with st.spinner("Analyzing code with Code Annotation Ai..."):
            st.session_state.analysis = analyze_code(source, selected_language)
            st.session_state.execution = None
        st.rerun()


# ============================================================
# Always-visible AI result sections
# ============================================================

result = st.session_state.analysis

if result:
    corrected = result.get("corrected_code", source)

    st.markdown(
        '<div class="section-card"><div class="section-head">1. Corrected Code</div><div class="section-body">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="feature-badge">MAIN OUTPUT</div>',
        unsafe_allow_html=True,
    )
    st.code(corrected, language=selected_language.lower())
    st.download_button(
        "Download Corrected Code",
        data=corrected,
        file_name=f"main.{EXTENSIONS[selected_language]}",
        mime="text/plain",
        use_container_width=True,
    )
    st.markdown(
        f'<div class="note-box" style="margin:12px 0 0 0;"><b>What does this code do?</b><br><br>{html.escape(result.get("summary", "No summary available."))}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Explanation — always visible
    st.markdown(
        '<div class="section-card"><div class="section-head">2. Explanation</div><div class="section-body">',
        unsafe_allow_html=True,
    )
    issues = result.get("errors", []) + result.get("warnings", []) + result.get("info", [])
    if issues:
        for issue in issues:
            color = (
                "error" if issue.get("severity") == "Error"
                else "warning" if issue.get("severity") == "Warning"
                else "info"
            )
            st.markdown(
                f"""
                <div class="note-box" style="margin:0 0 10px 0;">
                    <b class="{color}">Line {html.escape(str(issue.get("line", "?")))} — {html.escape(str(issue.get("title", "Issue")))}</b><br><br>
                    <b>Explanation:</b> {html.escape(str(issue.get("explanation", "")))}<br><br>
                    <b>Why:</b> {html.escape(str(issue.get("why", "")))}<br><br>
                    <b>How to Fix:</b> {html.escape(str(issue.get("fix", "")))}
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success("No significant issues were found.")
    st.markdown("</div></div>", unsafe_allow_html=True)

    # Optimization + Security + Notes — always visible
    opt_col, sec_col, notes_col = st.columns(3, gap="medium")

    with opt_col:
        st.markdown(
            f'<div class="section-card"><div class="section-head">3. Optimization</div><div class="section-body">{html.escape(result.get("optimization", "No optimization notes."))}</div></div>',
            unsafe_allow_html=True,
        )

    with sec_col:
        st.markdown(
            f'<div class="section-card"><div class="section-head">4. Security</div><div class="section-body">{html.escape(result.get("security", "No security notes."))}</div></div>',
            unsafe_allow_html=True,
        )

    with notes_col:
        st.markdown(
            f'<div class="section-card"><div class="section-head">5. Notes</div><div class="section-body">{html.escape(result.get("notes", "No notes."))}</div></div>',
            unsafe_allow_html=True,
        )

    # Dedicated complexity explanation is visible without switching tabs.
    tc_col, sc_col = st.columns(2, gap="medium")
    with tc_col:
        st.markdown(
            f'<div class="section-card"><div class="section-head">Time Complexity Explanation</div><div class="section-body"><b>{html.escape(result.get("time_complexity", "N/A"))}</b><br><br>{html.escape(result.get("time_explanation", ""))}</div></div>',
            unsafe_allow_html=True,
        )
    with sc_col:
        st.markdown(
            f'<div class="section-card"><div class="section-head">Space Complexity Explanation</div><div class="section-body"><b>{html.escape(result.get("space_complexity", "N/A"))}</b><br><br>{html.escape(result.get("space_explanation", ""))}</div></div>',
            unsafe_allow_html=True,
        )

else:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-head">AI Results</div>
            <div class="section-body">
                Analyze your code to display corrected code, explanation, optimization, security,
                notes, and detailed complexity information. The complexity visualizer remains visible
                beside the editor.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Run / Verify + Final Report
# ============================================================

if result:
    corrected = result.get("corrected_code", source)

    st.markdown(
        """
        <div class="run-highlight">
            <div class="run-title">▶ Run / Verify Corrected Code</div>
            <div class="run-subtitle">
                Execute the AI-corrected program and verify whether it compiles and runs successfully.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if selected_language in {"HTML", "CSS"}:
        st.markdown(
            '<div class="small-caption">Browser preview for markup and styles.</div>',
            unsafe_allow_html=True,
        )
        html_preview(corrected, selected_language)
    else:
        run_col, status_col = st.columns([1.45, 3.55], gap="small")

        with run_col:
            run_button = st.button(
                "▶  Run Corrected Code",
                type="primary",
                use_container_width=True,
                key="run_verified_code",
            )

        with status_col:
            if st.session_state.execution:
                execution_status = st.session_state.execution.get("status", "Unknown")
                elapsed = st.session_state.execution.get("elapsed")
                status_text = f"Status: {execution_status}"
                if elapsed is not None:
                    status_text += f" • {elapsed:.3f}s"
                st.markdown(
                    f'<div style="padding:9px 0;color:#52657f;font-size:12px;font-weight:700;">{html.escape(status_text)}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="padding:9px 0;color:#687a91;font-size:12px;">No verification run yet.</div>',
                    unsafe_allow_html=True,
                )

        if run_button:
            with st.spinner("Compiling and running the AI-corrected code..."):
                execution = run_judge0(
                    corrected,
                    selected_language,
                    st.session_state.stdin_text,
                )
                st.session_state.execution = execution
            st.rerun()

        execution = st.session_state.execution
        out_col, err_col = st.columns(2, gap="medium")

        with out_col:
            st.markdown(
                '<div class="output-panel"><div class="output-head">Program Output</div>',
                unsafe_allow_html=True,
            )
            output = (
                execution.get("stdout", "")
                if execution else
                "Press “Run Corrected Code” to verify the generated program."
            )
            st.markdown(
                f'<div class="output-body">{html.escape(output or "(no output)")}</div></div>',
                unsafe_allow_html=True,
            )

        with err_col:
            st.markdown(
                '<div class="output-panel"><div class="output-head">Compiler / Runtime Verification</div>',
                unsafe_allow_html=True,
            )

            if execution:
                message = execution.get("stderr", "") or execution.get("compile_output", "")
                if execution.get("message"):
                    message = f"{message}\n{execution['message']}".strip()

                if execution.get("ok"):
                    message = message or "Compilation and execution succeeded."
                    cls = "output-body"
                else:
                    message = message or execution.get("status", "Execution failed.")
                    cls = "output-body output-error"
            else:
                message = "No verification result yet."
                cls = "output-body"

            st.markdown(
                f'<div class="{cls}">{html.escape(message)}</div></div>',
                unsafe_allow_html=True,
            )

    # Prominent final report feature
    st.markdown(
        """
        <div class="report-highlight">
            <div class="report-title">▤  Final Analysis Report</div>
            <div class="report-subtitle">
                Download the complete project report: original code, corrected code,
                issues, explanations, complexity, optimization, security review,
                notes, and execution verification.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pdf_result = dict(result)
    if st.session_state.execution:
        pdf_result["execution_status"] = st.session_state.execution.get("status", "")
        pdf_result["execution_stdout"] = st.session_state.execution.get("stdout", "")
        pdf_result["execution_stderr"] = st.session_state.execution.get("stderr", "")
        pdf_result["execution_compile_output"] = st.session_state.execution.get("compile_output", "")
        pdf_result["execution_time"] = st.session_state.execution.get("elapsed", "")

    pdf_data = make_pdf(selected_language, source, pdf_result)

    st.download_button(
        "⬇  Download Final Analysis Report (PDF)",
        data=pdf_data,
        file_name="Code_Annotation_Ai_Final_Report.pdf",
        mime="application/pdf",
        use_container_width=True,
        key="download_final_report",
    )

else:
    st.markdown(
        """
        <div class="section-card">
            <div class="section-head">AI Results</div>
            <div class="section-body">
                Analyze your code to display corrected code, explanation, complexity,
                optimization, security, notes, and verification tools.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Footer
# ============================================================

st.markdown(
    """
    <div class="footer">
        Code Annotation Ai &nbsp;•&nbsp; a web-compiler &nbsp;•&nbsp; Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)
