import streamlit as st
import os
import json
import subprocess
import tempfile
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO
import contextlib
from groq import Groq
from fpdf import FPDF


# ==========================================
# 1. PAGE SETUP & SECURITY
# ==========================================

st.set_page_config(
    page_title="AI Code Annotator & Compiler",
    layout="wide"
)


# ==========================================
# 2. GROQ API KEY
# ==========================================

try:
    api_key = st.secrets["GROQ_API_KEY"]

except KeyError:
    st.error(
        "API Key not found. Please configure GROQ_API_KEY "
        "in Streamlit Cloud Secrets."
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
# 4. GROQ AI CODE ANALYSIS
# ==========================================

def get_groq_analysis(api_key, code, language):
    """
    Uses Groq AI to analyze, correct, annotate,
    and optimize the submitted code.
    """

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
    "optimization_notes": "Explain possible optimization improvements"
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

        chat_completion = client.chat.completions.create(
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

        response_text = chat_completion.choices[0].message.content

        response_text = (
            response_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(response_text)

        return result

    except Exception as e:

        return {
            "error": str(e)
        }


# ==========================================
# 5. CODE EXECUTION
# ==========================================

def execute_code(code, language):
    """
    Executes Python code.

    Java and C++ execution are disabled on Streamlit Cloud
    because javac and g++ are not guaranteed to be installed.
    """

    # --------------------------------------
    # PYTHON
    # --------------------------------------

    if language == "Python":

        output = StringIO()

        try:

            with contextlib.redirect_stdout(output):

                exec(code, {})

            result = output.getvalue()

            if not result:
                return "Program executed successfully with no output."

            return result

        except Exception as e:

            return f"Python Execution Error:\n{e}"


    # --------------------------------------
    # C++
    # --------------------------------------

    elif language == "C++":

        return (
            "C++ execution is not available on Streamlit Cloud.\n\n"
            "The AI successfully corrected and annotated your C++ code.\n\n"
            "Copy the corrected code and run it using a C++ compiler "
            "such as Visual Studio, Code::Blocks, MinGW, or an online compiler."
        )


    # --------------------------------------
    # JAVA
    # --------------------------------------

    elif language == "Java":

        return (
            "Java execution is not available on Streamlit Cloud.\n\n"
            "The AI successfully corrected and annotated your Java code.\n\n"
            "Copy the corrected code and run it using a Java JDK "
            "or an online Java compiler."
        )


    return "Unsupported programming language."


# ==========================================
# 6. COMPLEXITY GRAPH
# ==========================================

def plot_complexity(time_complex):
    """
    Creates a visual graph for common time complexities.
    """

    fig, ax = plt.subplots(figsize=(5, 3))

    n = np.linspace(1, 10, 100)

    complexity = str(time_complex).lower()

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
# 7. PDF REPORT GENERATION
# ==========================================

def generate_pdf(original, language, analysis):
    """
    Generates a downloadable PDF analysis report.
    """

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )


    # --------------------------------------
    # Helper: Title
    # --------------------------------------

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


    # --------------------------------------
    # Helper: Text
    # --------------------------------------

    def add_text(text):

        safe_text = (
            str(text)
            .encode("latin-1", "replace")
            .decode("latin-1")
        )

        pdf.multi_cell(
            0,
            7,
            txt=safe_text
        )

        pdf.ln(5)


    # --------------------------------------
    # Main Title
    # --------------------------------------

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


    # --------------------------------------
    # Original Code
    # --------------------------------------

    add_title(
        "1. Original Code:"
    )

    add_text(
        original
    )


    # --------------------------------------
    # Corrections
    # --------------------------------------

    add_title(
        "2. Syntax & Indentation Corrections:"
    )

    add_text(
        analysis.get(
            "syntax_corrections",
            "None"
        )
    )


    # --------------------------------------
    # Complexity
    # --------------------------------------

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


    # --------------------------------------
    # Corrected Code
    # --------------------------------------

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
    "API Key successfully loaded from Secrets."
)


# ==========================================
# 9. MAIN LAYOUT
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


                # --------------------------------------
                # API ERROR
                # --------------------------------------

                if "error" in result:

                    st.error(
                        f"API Error: {result['error']}"
                    )


                # --------------------------------------
                # SUCCESS
                # --------------------------------------

                else:

                    st.session_state.analysis_result = result

                    st.session_state.original_code = user_code

                    st.session_state.selected_lang = language_choice

                    st.success(
                        "Analysis Complete!"
                    )


# ==========================================
# 11. AI OUTPUT
# ==========================================

with col_right:

    st.header(
        "2. AI Output & Compiler"
    )


    # --------------------------------------
    # No Result
    # --------------------------------------

    if not st.session_state.analysis_result:

        st.info(
            "Awaiting code input. "
            "Click 'Analyze & Annotate Code' "
            "on the left to see results here."
        )


    # --------------------------------------
    # Result Available
    # --------------------------------------

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
        # TAB 1: CORRECTED CODE
        # ==================================

        with tab1:

            st.write(
                "### Annotated Code"
            )

            language = (
                st.session_state.selected_lang
                .lower()
            )

            st.code(
                res.get(
                    "corrected_code",
                    ""
                ),
                language=language
            )


        # ==================================
        # TAB 2: ANALYSIS REPORT
        # ==================================

        with tab2:

            st.write(
                "### Corrections Made"
            )

            st.info(
                res.get(
                    "syntax_corrections",
                    "No corrections provided."
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
                    "No optimization notes provided."
                )
            )


            # --------------------------------------
            # Complexity Graph
            # --------------------------------------

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


                plt.close(
                    fig
                )


            # --------------------------------------
            # PDF
            # --------------------------------------

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
        # TAB 3: RUN OUTPUT
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
                    "Executing..."
                ):

                    exec_output = execute_code(
                        res.get(
                            "corrected_code",
                            ""
                        ),
                        st.session_state.selected_lang
                    )


                    st.text_area(
                        "Terminal / Stdout",
                        value=exec_output,
                        height=300
                    )
