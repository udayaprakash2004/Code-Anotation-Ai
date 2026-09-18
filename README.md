# Code Annotation Ai

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-Proprietary-red?style=flat-square)

**Code Annotation Ai** is a comprehensive web-compiler and AI-powered code analysis application built with Streamlit. It allows developers and students to write or paste code, analyze it using AI, inspect detected issues, view corrected code, study algorithmic complexity, and securely execute code to verify functionality. 

**Live Application:** [Code Annotation Ai Web-Compiler](https://code-anotation-ai-webcompiler.streamlit.app/)

---

## Features

* **Dark Syntax-Highlighted Editor:** Powered by Streamlit Ace with support for C, C++, Java, Python, JavaScript, HTML, and CSS.
* **AI Code Analysis:** Utilizes the Groq API to provide syntax, structural, logic, and quality issue reporting.
* **Intelligent Corrections:** Automatically generates corrected code alongside detailed explanations of fixes.
* **Complexity Analysis:** Calculates Time and Space complexity, accompanied by always-visible Matplotlib growth graphs.
* **Live Code Execution:** Run and verify C, C++, Java, Python, and JavaScript via a secure Judge0 integration (includes custom stdin support).
* **Web Preview:** Dedicated in-app browser preview for HTML and CSS.
* **Comprehensive Insights:** Receive optimization recommendations, security reviews, and detailed learning notes.
* **Downloadable PDF Reports:** Generate and download a final project report containing all analysis metrics, executed outputs, and original/corrected code using `fpdf2`.

---

## Architecture & Workflow

```text
Enter Code | Select Language
       |
       +--> Local Checks + Groq AI Analysis
              |
              +--> Errors / Warnings / Info
              +--> Corrected Code
              +--> Explanation
              +--> Time & Space Complexity
              +--> Optimization Recommendations
              +--> Security Review
              +--> Learning Notes
              |
              +--> Complexity Growth Graphs (Matplotlib)
              +--> Run / Verify Corrected Code (Judge0)
              +--> Download Final PDF Report
## Technology Stack

* **Web Framework:** Streamlit
* **AI Analysis:** Groq API (Default model: openai/gpt-oss-120b)
* **Code Editor:** Streamlit Ace
* **Code Execution:** Judge0
* **Data Visualization:** Matplotlib, NumPy
* **PDF Generation:** fpdf2
* **HTTP Requests:** Requests

---

## Project Structure

```text
Code-Anotation-Ai/
├── .devcontainer/
├── app.py
├── logo.png
├── requirements.txt
└── README.md

Installation
Clone the repository:

Bash
git clone [https://github.com/udayaprakash2004/Code-Anotation-Ai.git](https://github.com/udayaprakash2004/Code-Anotation-Ai.git)
cd Code-Anotation-Ai
Install dependencies:

Bash
pip install -r requirements.txt
Run the application:

Bash
streamlit run app.py
API Configuration
The application requires specific environment variables or Streamlit secrets to function. Create a .streamlit/secrets.toml file locally or configure these in your Streamlit Community Cloud settings:

Ini, TOML
GROQ_API_KEY = "your_groq_api_key"           # Required for AI analysis
JUDGE0_API_KEY = "your_judge0_api_key"       # Optional depending on Judge0 deployment
JUDGE0_URL = "[https://ce.judge0.com](https://ce.judge0.com)"         # Optional (defaults to this URL)
GROQ_MODEL = "openai/gpt-oss-120b"           # Optional (defaults to this model)
Security Warning: Never commit your API keys or secrets.toml file to GitHub.

Usage Guide
Select a programming language from the dropdown.

Enter or paste your code into the editor (or load a built-in example).

If your program requires input, provide it in the custom stdin field.

Click Analyze to trigger the Groq AI review.

Review the generated insights, including corrected code, optimization tips, and Big-O complexity graphs.

For supported executable languages, click Run Corrected Code to securely verify the output and review compiler/runtime messages.

Click Download Final Analysis Report (PDF) to export a professional document of your session.

Execution Constraints & Security
Executable code is submitted to a Judge0 environment.

The application automatically configures strict CPU, wall-clock, and memory limits, and disables network access for the submission.

Disclaimer: Do not submit passwords, active API keys, private keys, or highly confidential code, as they will be processed by external AI (Groq) and execution (Judge0) services.

Requirements
Ensure your environment meets the following specifications (requirements.txt):

streamlit>=1.45,<2

groq>=0.30

requests>=2.31

fpdf2>=2.8

matplotlib>=3.8

numpy>=1.26

streamlit-ace>=0.1.1

Streamlit Deployment
To deploy on Streamlit Community Cloud:

Push app.py, requirements.txt, logo.png, and README.md to your GitHub repository.

Create a new Streamlit Community Cloud application.

Select your repository and target branch.

Set the main file path to app.py.

Under Advanced Settings, add your required API secrets.

Click Deploy.

Future Enhancements
Support for additional programming languages.

Advanced compiler diagnostics.

Test-case management and assertion frameworks.

Project history and session persistence.

User authentication and role management.

Granular performance benchmarking.

Downloadable complexity charts.

Code formatting and local linting integration.

License & Copyright
Copyright (c) 2026 Udaya Prakash. All Rights Reserved.

This software and its source code are proprietary and confidential.

No permission is granted to any person or organization to use, copy, modify, distribute, reproduce, publish, sublicense, sell, or create derivative works from this software or any part of this repository without prior written permission from the copyright owner.

Unauthorized use, copying, modification, distribution, or reproduction of this software or its source code is prohibited.

For permission to use any part of this repository, please contact the copyright owner.
