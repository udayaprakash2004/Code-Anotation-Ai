Code Annotation Ai
a web-compiler
Code Annotation Ai is an AI-powered code analysis and web-compiler application built with Streamlit. It lets users write or paste code, analyze it with AI, inspect detected issues, view corrected code, study time and space complexity, verify executable code, and download a final PDF analysis report.
Features
Dark syntax-highlighted Ace code editor
C, C++, Java, Python, JavaScript, HTML, and CSS support
Built-in code examples
Groq-powered AI code analysis
Syntax, structural, logic, and quality issue reporting
AI-generated corrected code
Explanation of detected issues and fixes
Time and space complexity analysis
Always-visible Matplotlib complexity growth graphs
Run and verify corrected C, C++, Java, Python, and JavaScript code through Judge0
Custom stdin input
HTML and CSS browser preview
Optimization recommendations
Security review
Learning notes
Downloadable corrected source code
Final Analysis Report as a PDF
Professional light interface with dark code editor and Code Annotation Ai branding
How It Works
Enter Code
    |
    v
Select Language
    |
    v
Local Checks + Groq AI Analysis
    |
    +--> Errors / Warnings / Info
    +--> Corrected Code
    +--> Explanation
    +--> Time & Space Complexity
    +--> Optimization
    +--> Security
    +--> Notes
    |
    +--> Complexity Growth Graphs
    |
    +--> Run / Verify Corrected Code
    |
    +--> Download Final PDF Report
Technology Stack
Area               Technology
Web framework      Streamlit AI analysis        Groq API Default AI model   openai/gpt-oss-120b Code editor        Streamlit Ace Code execution     Judge0 Graphs             Matplotlib + NumPy PDF reports        fpdf2 HTTP requests      Requests
Supported Languages
Analysis and editor
C
C++
Java
Python
JavaScript
HTML
CSS
Judge0 execution
C
C++
Java
Python
JavaScript
HTML and CSS use an in-app browser preview instead of Judge0 execution.
Project Structure
Code-Anotation-Ai/
├── app.py
├── requirements.txt
├── logo.png
├── README.md
└── .devcontainer/
The application currently loads the logo with:
LOGO_PATH = Path("logo.png")
Therefore, keep logo.png in the repository root beside app.py.
Installation
Clone
git clone https://github.com/udayaprakash2004/Code-Anotation-Ai.git
cd Code-Anotation-Ai
Install dependencies
pip install -r requirements.txt
Run
streamlit run app.py
API Configuration
The application reads these values from Streamlit secrets or environment variables:
GROQ_API_KEY --- required for AI analysis
JUDGE0_API_KEY --- optional depending on the Judge0 deployment
JUDGE0_URL --- optional; defaults to https://ce.judge0.com
GROQ_MODEL --- optional; defaults to openai/gpt-oss-120b
For Streamlit Cloud, configure the secrets in the application's Secrets settings.
Example:
GROQ_API_KEY = "your_groq_api_key"
JUDGE0_API_KEY = "your_judge0_api_key"
JUDGE0_URL = "https://ce.judge0.com"
Never commit API keys to GitHub.
Usage
Select a programming language.
Enter or paste code into the editor.
Optionally select and load an example.
Enter custom stdin if the program requires input.
Click Analyze.
Review the corrected code, explanation, optimization, security, notes, and complexity information.
For executable languages, click Run Corrected Code to verify the generated code.
Review program output and compiler/runtime messages.
Click Download Final Analysis Report (PDF) to generate the final project report.
Complexity Visualization
The application displays theoretical algorithmic growth curves for recognized Big-O forms such as:
O(1)
O(log n)
O(n)
O(n log n)
O(n²)
O(n³)
O(2^n)
O(n!)
The graph represents theoretical growth and is not a measured benchmark of one execution.
For HTML and CSS, algorithmic complexity is normally reported as N/A.
PDF Report
The PDF report is a central feature of Code Annotation Ai. It can contain:
Analysis summary
Errors
Warnings
Informational findings
Time complexity and explanation
Space complexity and explanation
Optimization recommendations
Security review
Notes
Verification status
Execution time
Program output
Compiler/runtime messages
Original code
Corrected code
Execution Notes
Supported executable code is submitted to Judge0. The application configures CPU, wall-clock, and memory limits and disables network access for the submission.
Do not submit passwords, API keys, private keys, tokens, or other confidential code unless you understand the privacy and security implications of the external AI and execution services.
Requirements
streamlit>=1.45,<2
groq>=0.30
requests>=2.31
fpdf2>=2.8
matplotlib>=3.8
numpy>=1.26
streamlit-ace>=0.1.1
Streamlit Deployment
Push app.py, requirements.txt, logo.png, and README.md to GitHub.
Create a Streamlit Community Cloud application.
Select the repository and main branch.
Set the main file to app.py.
Add the required API secrets.
Deploy.
Keep logo.png in the same directory as app.py.
Future Enhancements
More programming languages
Advanced compiler diagnostics
Test-case management
Project history
User authentication
More detailed performance benchmarking
Downloadable complexity charts
Improved HTML/CSS/JavaScript preview
Code formatting and linting
Project
Code Annotation Ai --- a web-compiler
Built with Streamlit, Groq, Judge0, Matplotlib, NumPy, Streamlit Ace, and fpdf2.
app:-
https://code-anotation-ai-3zdmrctb8uhfdqpqgukcyv.streamlit.app/
