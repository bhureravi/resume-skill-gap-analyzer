# Resume Skill Gap Analyzer

A C++ based resume analysis system with a Streamlit dashboard.

## Features

- Resume vs Role comparison
- Resume vs Company expectation analysis
- Skill gap detection
- Personalized recommendations
- PDF support
- Live job signal integration
- Public-source web intelligence

## Tech Stack

Backend:
- C++
- OOP
- File Handling
- STL

Frontend:
- Streamlit

Integration:
- Python
- REST APIs

## Screenshots

![Home](screenshots/1.png)
![Results](screenshots/1.png)
![AI-Suggestions](screenshots/2.png)
![](screenshots/2.png)


## Running the Project

1. Clone the repository

```bash
git clone <repository-url>
cd resume-skill-gap-analyze
```

2. Create a virtual environment and activate it

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install the required packages

```bash
pip install -r requirements.txt
```

4. Install Ollama and download the model used for AI analysis

```bash
ollama pull qwen2.5:3b
```

Make sure Ollama is running before starting the application.

5. (Optional) Add your Adzuna API credentials in `.streamlit/secrets.toml` if you want live job market data.

6. Start the application

```bash
streamlit run src/ui/app.py
```

Once the app opens in your browser, upload a resume and a role description (company description is optional) and run the analysis. The platform will generate skill-gap insights, ATS-style scoring, interview preparation recommendations, and role-specific feedback.