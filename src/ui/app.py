import os

import streamlit as st

try:
    os.environ.setdefault("ADZUNA_APP_ID", st.secrets["ADZUNA_APP_ID"])
    os.environ.setdefault("ADZUNA_APP_KEY", st.secrets["ADZUNA_APP_KEY"])
except Exception:
    pass

from backend_bridge import run_backend_analysis

st.set_page_config(
    page_title="Resume Skill Gap Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": None,
        "Report a bug": None,
        "About": None,
    },
)

st.markdown(
    """
    <style>
        .stApp {
            background: #f7f4ee;
        }
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
            height: 0rem;
        }
        #MainMenu {
            visibility: hidden;
        }
        footer {
            visibility: hidden;
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        .hero {
            background: #fffdfa;
            border: 1px solid rgba(31, 41, 55, 0.08);
            border-radius: 24px 14px 20px 16px;
            padding: 1.1rem 1.2rem 1rem 1.2rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.05);
            margin-bottom: 1rem;
        }
        .soft-panel {
            background: #fffdf9;
            border: 1px solid rgba(31, 41, 55, 0.08);
            border-radius: 18px 12px 16px 22px;
            padding: 1rem 1rem;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.04);
        }
        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            color: #111827;
        }
        .section-note {
            color: #6b7280;
            font-size: 0.92rem;
            margin-bottom: 0.4rem;
        }
        .pill {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            background: #ece6da;
            color: #594d3e;
            font-size: 0.78rem;
            margin-bottom: 0.6rem;
        }
        div[data-testid="stFileUploader"] section {
            border-radius: 16px;
            background: #fffdf9;
            border: 1px solid rgba(31, 41, 55, 0.08);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="pill">Resume Skill Gap Analyzer</div>
        <h1 style="margin-bottom:0.35rem;">Simple resume-to-role prep dashboard</h1>
        <p style="margin:0;color:#6b7280;">
            Upload your resume, role file, and company file, then get clean recommendations,
            missing skills, and live job intelligence in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "last_result" not in st.session_state:
    st.session_state.last_result = None


def split_items(value: str, delimiter: str = ","):
    if not value:
        return []
    return [x.strip() for x in value.split(delimiter) if x.strip()]


with st.sidebar:
    st.header("Project Status")
    st.write("UI: Streamlit")
    st.write("Backend: C++ engine")
    st.write("Bridge: Python subprocess")
    st.write("Live job API: Adzuna")
    st.write("Web intelligence: Public-source crawler")
    st.divider()
    st.info("The app combines uploaded files, live signals, and public web intelligence into one clean output.")

left_col, right_col = st.columns([1.05, 0.95], gap="large")

with left_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Inputs</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-note">You can upload TXT or PDF files. PDFs are converted to text before analysis.</div>',
            unsafe_allow_html=True,
        )

        resume_file = st.file_uploader(
            "Upload Resume",
            type=["txt", "pdf"],
        )

        role_file = st.file_uploader(
            "Upload Role File",
            type=["txt", "pdf"],
        )

        company_file = st.file_uploader(
            "Upload Company File",
            type=["txt", "pdf"],
        )

        role_name = st.text_input(
            "Role Label",
            placeholder="Example: software developer",
        )

        company_name = st.text_input(
            "Company Label",
            placeholder="Example: amazon",
        )

        country_code = st.text_input(
            "Adzuna Country Code",
            value="gb",
        )

        location_filter = st.text_input(
            "Location Filter (optional)",
            placeholder="Example: London",
        )

        use_live_api = st.checkbox("Use live job API", value=True)
        use_web_intelligence = st.checkbox("Use web intelligence", value=True)

        run_clicked = st.button("Run Full Analysis", width="stretch")

with right_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">Result Summary</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-note">Scores appear here after the backend finishes.</div>',
            unsafe_allow_html=True,
        )

        if st.session_state.last_result and st.session_state.last_result.get("ok"):
            result = st.session_state.last_result

            c1, c2, c3 = st.columns(3)
            c1.metric("Role Score", f"{result.get('role_score', '0')}%", border=True)
            c2.metric("Company Score", f"{result.get('company_score', '0')}%", border=True)
            c3.metric("Overall Score", f"{result.get('overall_score', '0')}%", border=True)

            overall_val = 0
            try:
                overall_val = int(result.get("overall_score", "0"))
            except Exception:
                overall_val = 0

            st.progress(min(max(overall_val, 0), 100) / 100.0)

            if overall_val < 40:
                badge = "Beginner"
            elif overall_val < 70:
                badge = "Intermediate"
            else:
                badge = "Job Ready"

            st.success(f"Readiness: {badge}")

            st.markdown("### Extracted Skills")
            extracted = result.get("extracted_skills", "")
            if extracted:
                for skill in split_items(extracted):
                    st.write(f"- {skill}")
            else:
                st.write("No skills extracted yet.")

        elif st.session_state.last_result and not st.session_state.last_result.get("ok"):
            st.error(st.session_state.last_result.get("error", "Backend error"))
            if st.session_state.last_result.get("live_error"):
                st.warning(st.session_state.last_result.get("live_error"))
        else:
            st.info("Your analysis result will appear here after you run the backend.")

st.divider()

if st.session_state.last_result:
    result = st.session_state.last_result

    with st.container(border=True):
        st.markdown('<div class="section-title">Missing Skills</div>', unsafe_allow_html=True)
        missing_items = result.get("combined_missing", [])
        if missing_items:
            for item in missing_items:
                st.write(f"- {item}")
        else:
            st.write("No missing skill gaps found.")

    st.divider()

    with st.container(border=True):
        st.markdown('<div class="section-title">Recommendations</div>', unsafe_allow_html=True)
        recommendation_items = result.get("combined_recommendations", [])
        if recommendation_items:
            for item in recommendation_items:
                st.write(f"- {item}")
        else:
            st.write("No recommendations available yet.")

    st.divider()

    with st.container(border=True):
        st.markdown('<div class="section-title">Live Jobs</div>', unsafe_allow_html=True)
        live_jobs = result.get("live_jobs", [])
        if live_jobs:
            for job in live_jobs[:5]:
                st.markdown(f"**{job.get('title', 'Untitled')}**")
                st.write(f"{job.get('company', '')} — {job.get('location', '')}")
                snippet = job.get("snippet", "")
                if snippet:
                    st.write(snippet[:400] + ("..." if len(snippet) > 400 else ""))
                url = job.get("url", "")
                if url:
                    st.markdown(f"[Open listing]({url})")
                st.divider()
        else:
            st.write("No live jobs found. The app still uses web signals and public-source prep intelligence.")

    with st.expander("Debug output"):
        st.subheader("Web summary")
        st.code(result.get("web_summary", ""), language="text")

        st.subheader("Live summary")
        st.code(result.get("live_summary", ""), language="text")

        st.subheader("Raw backend output")
        st.code(result.get("raw", ""), language="text")

if run_clicked:
    if not resume_file or not role_file or not company_file:
        st.warning("Please upload all three files first: resume, role file, and company file.")
    else:
        with st.spinner("Running C++ analysis engine, live job API, and public web intelligence..."):
            result = run_backend_analysis(
                resume_file,
                role_file,
                company_file,
                role_label=role_name,
                company_label=company_name,
                use_live_job_api=use_live_api,
                use_web_intelligence=use_web_intelligence,
                country_code=country_code,
                location_filter=location_filter,
            )
            st.session_state.last_result = result
            st.rerun()