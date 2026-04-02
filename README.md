Project Title: AI Code Annotator & Web Compiler
​Overview
​The AI Code Annotator & Web Compiler is a high-speed, single-file web application designed to act as an intelligent, interactive IDE. Powered by the Groq API (Llama-3.3-70b), this tool allows developers to input raw or buggy code and instantly receive a fully annotated, optimized, and syntactically corrected version. Built with a side-by-side UI reminiscent of popular online compilers, the application not only explains the code but also executes it in real-time and visualizes its computational efficiency.
​Core Features
​Instant AI Code Review: Utilizes Groq's low-latency LPUs to rapidly analyze user code, automatically fixing syntax mistakes, indentation errors, and structural bugs.
​Automated Annotation: Generates detailed, inline comments and docstrings to explain complex logic and make raw code instantly readable.
​Multi-Language Execution: Features a secure, container-like temporary execution environment capable of compiling and running Python, C++, and Java code directly in the browser.
​Algorithmic Complexity Visualization: Automatically determines the Big-O Time and Space complexity of the submitted code and plots the execution growth curve using Matplotlib.
​Downloadable PDF Reports: Compiles the original code, the AI's syntax corrections, the optimization notes, and the fully annotated final code into a cleanly formatted, downloadable PDF document using fpdf2.
​Technical Stack
​Frontend & Web Framework: Streamlit (Python)
​AI Engine: Groq API (Llama-3.3-70b-versatile model)
​Data Visualization: Matplotlib, NumPy
​Report Generation: fpdf2
​Backend Execution: Subprocess & Tempfile (Python built-ins for safe file I/O and process execution)
​System Architecture & Workflow
​Input Phase: The user pastes their code into the left-hand workspace and selects their target language.
​Analysis Phase: A strictly prompted API call is sent to Groq, commanding the LLM to return a formatted JSON object containing the corrected code, a list of syntax fixes, and complexity metrics.
​Execution Phase: The app writes the AI-corrected code to a temporary system directory, uses native system compilers (g++, javac, or Python's exec) to run the file, and captures the standard output/errors.
​Output Phase: The right-hand dashboard populates with three interactive tabs: the newly annotated code, the analytical report (including the plotted complexity graph), and the terminal execution output.
