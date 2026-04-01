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
st.set_page_config(page_title="AI Code Annotator & Compiler", layout="wide")

# Securely fetch the API key from Streamlit Secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
except KeyError:
    st.error("API Key not found. Please configure Streamlit Secrets before using the app.")
    st.stop()

# Initialize Session State
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "original_code" not in st.session_state:
    st.session_state.original_code = ""
if "selected_lang" not in st.session_state:
    st.session_state.selected_lang = ""

# ==========================================
# 2. CORE FUNCTIONS
# ==========================================

def get_groq_analysis(api_key, code, language):
    """Calls Groq API (Llama 3.3) to analyze, correct, and annotate the code."""
    client = Groq(api_key=api_key)
    
    prompt = f"""
    You are an expert compiler and code reviewer. Analyze the following {language} code.
    1. Fix syntax and indentation errors. (If it's Python with Matplotlib, fix plot structures).
    2. Add detailed annotations and comments explaining the logic.
    3. Optimize time and space complexity if possible.
    
    You MUST return ONLY a valid JSON object with EXACTLY these keys, no markdown blocks, no extra text:
    {{
        "corrected_code": "The fully corrected and commented code here",
        "syntax_corrections": "Explanation of syntax/indentation fixes made",
        "time_complexity": "e.g., O(n)",
        "space_complexity": "e.g., O(1)",
        "optimization_notes": "How you optimized the code"
    }}
    
    Code to analyze:
    {code}
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.1, 
        )
        response_text = chat_completion.choices[0].message.content
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        return json.loads(response_text)
    except Exception as e:
        return {"error": str(e)}

def execute_code(code, language):
    """Executes the corrected code safely in a temporary environment."""
    if language == "Python":
        output = StringIO()
        try:
            with contextlib.redirect_stdout(output):
                exec(code, {})
            return output.getvalue()
        except Exception as e:
            return str(e)
            
    elif language == "C++":
        with tempfile.TemporaryDirectory() as temp_dir:
            cpp_file = os.path.join(temp_dir, "main.cpp")
            exe_file = os.path.join(temp_dir, "main.exe" if os.name == 'nt' else "main")
            with open(cpp_file, "w") as f:
                f.write(code)
            
            compile_process = subprocess.run(["g++", cpp_file, "-o", exe_file], capture_output=True, text=True)
            if compile_process.returncode != 0:
                return f"Compilation Error:\n{compile_process.stderr}"
            
            run_process = subprocess.run([exe_file], capture_output=True, text=True)
            return run_process.stdout + run_process.stderr
            
    elif language == "Java":
        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = os.path.join(temp_dir, "Main.java")
            with open(java_file, "w") as f:
                f.write(code)
            
            compile_process = subprocess.run(["javac", java_file], capture_output=True, text=True)
            if compile_process.returncode != 0:
                return f"Compilation Error:\n{compile_process.stderr}"
            
            run_process = subprocess.run(["java", "-cp", temp_dir, "Main"], capture_output=True, text=True)
            return run_process.stdout + run_process.stderr

def plot_complexity(time_complex):
    """Uses Matplotlib to plot a visual representation of the complexity."""
    fig, ax = plt.subplots(figsize=(5, 3))
    n = np.linspace(1, 10, 100)
    
    if "O(1)" in time_complex: y = np.ones_like(n)
    elif "O(log n)" in time_complex: y = np.log(n)
    elif "O(n^2)" in time_complex: y = n**2
    else: y = n 
    
    ax.plot(n, y, color='blue', label=time_complex)
    ax.set_title("Time Complexity Growth")
    ax.set_xlabel("Input Size (n)")
    ax.set_ylabel("Operations")
    ax.legend()
    return fig

def generate_pdf(original, language, analysis):
    """Generates a downloadable PDF report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    def add_title(text):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt=text, ln=True, align='L')
        pdf.set_font("Arial", size=10)
    
    def add_text(text):
        safe_text = str(text).encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 7, txt=safe_text)
        pdf.ln(5)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"AI Code Analysis Report ({language})", ln=True, align='C')
    pdf.ln(10)

    add_title("1. Original Code:")
    add_text(original)
    
    add_title("2. Syntax & Indentation Corrections:")
    add_text(analysis.get('syntax_corrections', 'None'))
    
    add_title("3. Complexity Analysis:")
    add_text(f"Time: {analysis.get('time_complexity', 'N/A')}")
    add_text(f"Space: {analysis.get('space_complexity', 'N/A')}")
    add_text(f"Optimization Notes: {analysis.get('optimization_notes', 'None')}")
    
    add_title("4. Corrected & Annotated Code:")
    add_text(analysis.get('corrected_code', ''))

    # THE FIX IS RIGHT HERE:
    return bytes(pdf.output())

# ==========================================
# 3. FRONTEND LAYOUT
# ==========================================

st.sidebar.title("AI Code Annotator")
st.sidebar.markdown("*Powered by Groq Llama-3.3-70b*")
st.sidebar.success("API Key successfully loaded from Secrets.")

col_left, col_right = st.columns(2)

with col_left:
    st.header("1. Input Workspace")
    language_choice = st.selectbox("Select Language", ["Python", "C++", "Java"])
    user_code = st.text_area("Write or Paste your code here:", height=500, placeholder="// Enter your code...")
    
    if st.button("Analyze & Annotate Code", type="primary"):
        if not user_code.strip():
            st.warning("Please enter some code to analyze.")
        else:
            with st.spinner("Compiling and Analyzing via Groq API..."):
                result = get_groq_analysis(api_key, user_code, language_choice)
                if "error" in result:
                    st.error(f"API Error: {result['error']}")
                else:
                    st.session_state.analysis_result = result
                    st.session_state.original_code = user_code
                    st.session_state.selected_lang = language_choice
                    st.success("Analysis Complete!")

with col_right:
    st.header("2. AI Output & Compiler")
    
    if st.session_state.analysis_result:
        res = st.session_state.analysis_result
        
        tab1, tab2, tab3 = st.tabs(["Corrected Code", "Analysis Report", "Run Output"])
        
        with tab1:
            st.write("### Annotated Code")
            st.code(res.get('corrected_code', ''), language=st.session_state.selected_lang.lower())
        
        with tab2:
            st.write("### Corrections Made")
            st.info(res.get('syntax_corrections', ''))
            
            st.write("### Complexity Metrics")
            col_met1, col_met2 = st.columns(2)
            col_met1.metric("Time Complexity", res.get('time_complexity', 'N/A'))
            col_met2.metric("Space Complexity", res.get('space_complexity', 'N/A'))
            
            st.write("### Optimization Notes")
            st.success(res.get('optimization_notes', ''))
            
            if res.get('time_complexity'):
                st.write("### Complexity Graph")
                fig = plot_complexity(res.get('time_complexity'))
                st.pyplot(fig)
                
            st.write("---")
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
            
        with tab3:
            st.write(f"### Console Output ({st.session_state.selected_lang})")
            if st.button("▶ Run Corrected Code"):
                with st.spinner("Executing..."):
                    exec_output = execute_code(res.get('corrected_code', ''), st.session_state.selected_lang)
                    st.text_area("Terminal / Stdout", value=exec_output, height=300)
    else:
        st.info("Awaiting code input. Click 'Analyze & Annotate Code' on the left to see results here.")
