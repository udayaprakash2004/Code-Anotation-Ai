import streamlit as st
import os
import json
import requests
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
import contextlib
from groq import Groq
from fpdf import FPDF


# ==========================================
# 1. PAGE SETUP
# ==========================================

st.set_page_config(
    page_title="AI Code Annotator & Compiler",
    layout="wide"
)


# ==========================================
# 2. API KEYS
# ==========================================

try:
    api_key = st.secrets["GROQ_API_KEY"]

except KeyError:
    st.error(
        "GROQ_API_KEY not found. "
        "Please add it in Streamlit Cloud → Settings → Secrets."
    )
    st.stop()


# ==========================================
# 3. SESSION STATE
# ==========================================

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "original_code" not in st.session_state:
    st.session_state.original_code = ""

if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = ""


# ==========================================
# 4. GROQ AI ANALYSIS
# ==========================================

def get_groq_analysis(api_key, code, language):

    client = Groq(api_key=api_key)

    prompt = f"""
You are an expert software engineer, compiler,
code reviewer, and algorithm analyst.

Analyze the following {language} code.

Perform these tasks:

1. Find and fix syntax errors.
2. Find and fix indentation errors.
3. Fix obvious logical errors.
4. Add useful comments explaining important parts.
5. Preserve the original purpose of the program.
6. Analyze time complexity.
7. Analyze space complexity.
8. Suggest optimization improvements.
9. Return the complete corrected code.

IMPORTANT:

Return ONLY a valid JSON object.

The JSON must contain EXACTLY these five keys:

{{
    "corrected_code": "Complete corrected and commented code",
    "syntax_corrections": "Explain syntax, indentation, and logical corrections",
    "time_complexity": "Example: O(n)",
    "space_complexity": "Example: O(1)",
    "optimization_notes": "Explain optimization improvements"
}}

Do NOT return Markdown.
Do NOT use ```json.
Do NOT add text before or after the JSON.

Programming language:
{language}

Code:

{code}
"""

    try:

        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.1,

            response_format={
                "type": "json_object"
            }
        )

        response_text = response.choices[0].message.content

        response_text = (
            response_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(response_text)

    except Exception as e:

        return {
            "error": str(e)
        }


# ==========================================
# 5. PISTON CODE EXECUTION
# ==========================================

PISTON_URL = "https://emkc.org/api/v2/piston"


def get_piston_runtime(language):

    """
    Gets an available Piston runtime for the selected language.
    """

    language_map = {
        "Python": ["python", "py", "python3"],
        "C++": ["c++", "cpp"],
        "Java": ["java"]
    }

    requested_names = language_map.get(language, [])

    try:

        response = requests.get(
            f"{PISTON_URL}/runtimes",
            timeout=10
        )

        response.raise_for_status()

        runtimes = response.json()

        for runtime in runtimes:

            runtime_language = runtime.get(
                "language",
                ""
            ).lower()

            aliases = [
                str(alias).lower()
                for alias in runtime.get(
                    "aliases",
                    []
                )
            ]

            if (
                runtime_language in requested_names
                or any(
                    name in aliases
                    for name in requested_names
                )
            ):

                return {
                    "language": runtime["language"],
                    "version": runtime["version"]
                }

        return None

    except Exception as e:

        return {
            "error": str(e)
        }


def execute_code(code, language, stdin=""):

    """
    Executes Python, C++, and Java code using
    the Piston code execution API.
    """

    # --------------------------------------
    # Get runtime
    # --------------------------------------

    runtime = get_piston_runtime(language)

    if runtime is None:

        return (
            "Execution Error:\n"
            f"No Piston runtime found for {language}."
        )

    if "error" in runtime:

        return (
            "Execution Service Error:\n"
            + runtime["error"]
        )


    # --------------------------------------
    # File names
    # --------------------------------------

    if language == "Python":

        filename = "main.py"

    elif language == "C++":

        filename = "main.cpp"

    elif language == "Java":

        filename = "Main.java"

    else:

        return "Unsupported programming language."


    # --------------------------------------
    # Request payload
    # --------------------------------------

    payload = {
        "language": runtime["language"],
        "version": runtime["version"],

        "files": [
            {
                "name": filename,
                "content": code
            }
        ],

        "stdin": stdin,

        "args": [],

        "compile_timeout": 10000,

        "run_timeout": 5000,

        "compile_cpu_time": 10000,

        "run_cpu_time": 5000
    }


    # --------------------------------------
    # Execute
    # --------------------------------------

    try:

        response = requests.post(
            f"{PISTON_URL}/execute",
            json=payload,
            timeout=20
        )

        if response.status_code != 200:

            return (
                "Execution API Error:\n"
                f"HTTP {response.status_code}\n\n"
                f"{response.text}"
            )

        result = response.json()


        # --------------------------------------
        # Compilation result
        # --------------------------------------

        compile_result = result.get(
            "compile"
        )

        if compile_result:

            compile_stderr = compile_result.get(
                "stderr",
                ""
            )

            compile_stdout = compile_result.get(
                "stdout",
                ""
            )

            compile_code = compile_result.get(
                "code"
            )

            if (
                compile_code not in [0, None]
                or compile_stderr.strip()
            ):

                output = "Compilation Error:\n\n"

                if compile_stderr:

                    output += compile_stderr

                if compile_stdout:

                    output += "\n" + compile_stdout

                return output


        # --------------------------------------
        # Run result
        # --------------------------------------

        run_result = result.get(
            "run"
        )

        if not run_result:

            return "No execution result was returned."


        stdout = run_result.get(
            "stdout",
            ""
        )

        stderr = run_result.get(
            "stderr",
            ""
        )

        exit_code = run_result.get(
            "code"
        )


        # --------------------------------------
        # Runtime error
        # --------------------------------------

        if (
            exit_code not in [0, None]
            or stderr.strip()
        ):

            output = ""

            if stdout:

                output += stdout

            if stderr:

                output += "\n\nRuntime Error:\n"
                output += stderr

            if not output:

                output = "Program terminated with an error."

            return output


        # --------------------------------------
        # Successful output
        # --------------------------------------

        if stdout:

            return stdout

        return "Program executed successfully with no output."


    except requests.exceptions.Timeout:

        return (
            "Execution timed out.\n"
            "The program took too long to compile or run."
        )

    except requests.exceptions.RequestException as e:

        return (
            "Connection error while contacting "
            "the code execution service:\n"
            f"{e}"
        )

    except Exception as e:

        return (
            "Unexpected execution error:\n"
            f"{e}"
        )


# ==========================================
# 6. COMPLEXITY GRAPH
# ==========================================

def plot_complexity(time_complex):

    fig, ax = plt.subplots(
        figsize=(5, 3)
    )

    n = np.linspace(
        1,
        10,
        100
    )

    complexity = str(
        time_complex
    ).lower()

    complexity = (
        complexity
        .replace(" ", "")
        .replace("²", "^2")
        .replace("³", "^3")
    )


    if "o(1)" in complexity:

        y = np.ones_like(n)

    elif "o(logn)" in complexity:

        y = np.log(n)

    elif "o(nlogn)" in complexity:

        y = n * np.log(n)

    elif "o(n^2)" in complexity:

        y = n ** 2

    elif "o(n^3)" in complexity:

        y = n ** 3

    elif "o(2^n)" in complexity:

        y = 2 ** n

    elif "o(n)" in complexity:

        y = n

    else:

        y = n


    ax.plot(
        n,
        y,
        label=time_complex
    )

    ax.set_title(
        "Time Complexity Growth"
    )

    ax.set_xlabel(
        "Input Size (n)"
    )

    ax.set_ylabel(
        "Operations"
    )

    ax.legend()

    return fig


# ==========================================
# 7. PDF GENERATION
# ==========================================

def generate_pdf(
    original,
    language,
    analysis
):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )


    def add_title(text):

        pdf.set_font(
            "Arial",
            "B",
            14
        )

        pdf.cell(
            200,
            10,
            txt=text,
            ln=True,
            align="L"
        )

        pdf.set_font(
            "Arial",
            size=10
        )


    def add_text(text):

        safe_text = (
            str(text)
            .encode(
                "latin-1",
                "replace"
            )
            .decode("latin-1")
        )

        pdf.multi_cell(
            0,
            7,
            txt=safe_text
        )

        pdf.ln(5)


    pdf.set_font(
        "Arial",
        "B",
        16
    )

    pdf.cell(
        200,
        10,
        txt=f"AI Code Analysis Report ({language})",
        ln=True,
        align="C"
    )

    pdf.ln(10)


    add_title(
        "1. Original Code:"
    )

    add_text(
        original
    )


    add_title(
        "2. Syntax & Indentation Corrections:"
    )

    add_text(
        analysis.get(
            "syntax_corrections",
            "None"
        )
    )


    add_title(
        "3. Complexity Analysis:"
    )

    add_text(
        f"Time: {analysis.get('time_complexity', 'N/A')}"
    )

    add_text(
        f"Space: {analysis.get('space_complexity', 'N/A')}"
    )

    add_text(
        "Optimization Notes: "
        + analysis.get(
            "optimization_notes",
            "None"
        )
    )


    add_title(
        "4. Corrected & Annotated Code:"
    )

    add_text(
        analysis.get(
            "corrected_code",
            ""
        )
    )


    return bytes(
        pdf.output()
    )


# ==========================================
# 8. SIDEBAR
# ==========================================

st.sidebar.title(
    "AI Code Annotator"
)

st.sidebar.markdown(
    "*Powered by Groq GPT-OSS 120B*"
)

st.sidebar.success(
    "AI API successfully loaded."
)


# ==========================================
# 9. MAIN COLUMNS
# ==========================================

col_left, col_right = st.columns(
    2
)


# ==========================================
# 10. INPUT WORKSPACE
# ==========================================

with col_left:

    st.header(
        "1. Input Workspace"
    )


    language_choice = st.selectbox(
        "Select Language",
        [
            "Python",
            "C++",
            "Java"
        ]
    )


    user_code = st.text_area(
        "Write or Paste your code here:",
        height=500,
        placeholder="Enter your code here..."
    )


    # Program input

    program_input = st.text_area(
        "Program Input (optional):",
        height=100,
        placeholder="Enter input for your program here..."
    )


    if st.button(
        "Analyze & Annotate Code",
        type="primary"
    ):

        if not user_code.strip():

            st.warning(
                "Please enter some code to analyze."
            )

        else:

            with st.spinner(
                "Analyzing code using Groq AI..."
            ):

                result = get_groq_analysis(
                    api_key,
                    user_code,
                    language_choice
                )


                if "error" in result:

                    st.error(
                        f"API Error: {result['error']}"
                    )

                else:

                    st.session_state.analysis_result = result

                    st.session_state.original_code = user_code

                    st.session_state.selected_lang = language_choice

                    st.success(
                        "Analysis Complete!"
                    )


# ==========================================
# 11. OUTPUT WORKSPACE
# ==========================================

with col_right:

    st.header(
        "2. AI Output & Compiler"
    )


    if not st.session_state.analysis_result:

        st.info(
            "Awaiting code input. "
            "Click 'Analyze & Annotate Code' "
            "on the left to see results here."
        )


    else:

        res = st.session_state.analysis_result


        tab1, tab2, tab3 = st.tabs(
            [
                "Corrected Code",
                "Analysis Report",
                "Run Output"
            ]
        )


        # ==================================
        # CORRECTED CODE
        # ==================================

        with tab1:

            st.write(
                "### Annotated Code"
            )

            st.code(
                res.get(
                    "corrected_code",
                    ""
                ),
                language=(
                    st.session_state.selected_lang.lower()
                )
            )


        # ==================================
        # ANALYSIS REPORT
        # ==================================

        with tab2:

            st.write(
                "### Corrections Made"
            )

            st.info(
                res.get(
                    "syntax_corrections",
                    ""
                )
            )


            st.write(
                "### Complexity Metrics"
            )


            col_met1, col_met2 = st.columns(
                2
            )


            col_met1.metric(
                "Time Complexity",
                res.get(
                    "time_complexity",
                    "N/A"
                )
            )


            col_met2.metric(
                "Space Complexity",
                res.get(
                    "space_complexity",
                    "N/A"
                )
            )


            st.write(
                "### Optimization Notes"
            )

            st.success(
                res.get(
                    "optimization_notes",
                    ""
                )
            )


            if res.get(
                "time_complexity"
            ):

                st.write(
                    "### Complexity Graph"
                )

                fig = plot_complexity(
                    res.get(
                        "time_complexity"
                    )
                )

                st.pyplot(
                    fig
                )

                plt.close(fig)


            st.write(
                "---"
            )


            pdf_bytes = generate_pdf(
                st.session_state.original_code,
                st.session_state.selected_lang,
                res
            )


            st.download_button(
                label="📥 Download Full PDF Report",
                data=pdf_bytes,
                file_name="Code_Analysis_Report.pdf",
                mime="application/pdf"
            )


        # ==================================
        # RUN OUTPUT
        # ==================================

        with tab3:

            st.write(
                f"### Console Output "
                f"({st.session_state.selected_lang})"
            )


            if st.button(
                "▶ Run Corrected Code"
            ):

                with st.spinner(
                    "Compiling and executing..."
                ):

                    exec_output = execute_code(
                        res.get(
                            "corrected_code",
                            ""
                        ),
                        st.session_state.selected_lang,
                        program_input
                    )


                    st.text_area(
                        "Terminal / Stdout",
                        value=exec_output,
                        height=300
                    )
