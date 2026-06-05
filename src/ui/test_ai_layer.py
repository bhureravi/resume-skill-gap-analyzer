import json

from ai_insights import generate_ai_insights

sample_resume = """
I am a computer science student with project experience in backend development.
Built a resume analyzer using C++, Python, file handling, and Streamlit.
Worked on an internal project that compared role requirements with resume content.
Also used Next.js in a college project and learned API integration.
"""

sample_role = """
Software Developer Intern role requiring backend development, problem solving,
OOP, SQL, REST APIs, debugging, and good communication.
"""

sample_company = """
Company prefers students who can work on backend systems, APIs, and scalable products.
"""

backend_data = {
    "overall_score": "72",
    "combined_missing": ["SQL", "System Design", "Communication"],
    "combined_recommendations": [
        "Focus on SQL and REST APIs.",
        "Practice explaining your projects clearly.",
    ],
    "live_summary": "Fetched some live job signals.",
    "web_summary": "Collected public web research results.",
}

result = generate_ai_insights(
    resume_text=sample_resume,
    role_text=sample_role,
    company_text=sample_company,
    backend_data=backend_data,
)

print(json.dumps(result, indent=2))