import io
import os
import re
import subprocess
import tempfile
from pathlib import Path

from pypdf import PdfReader

from job_api import (
    compose_live_summary,
    fetch_adzuna_jobs,
    extract_skill_signals,
)
from web_intel import search_web_intelligence

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_EXE = PROJECT_ROOT / ("backend_cli.exe" if os.name == "nt" else "backend_cli")
SKILLS_FILE = PROJECT_ROOT / "data" / "skills.txt"


def split_items(value: str, delimiter: str = ","):
    if not value:
        return []
    return [x.strip() for x in value.split(delimiter) if x.strip()]


def unique_keep_order(items):
    seen = set()
    result = []
    for item in items:
        item = item.strip()
        if not item:
            continue
        key = item.lower()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def signal_to_tip(signal: str) -> str:
    mapping = {
        "DSA": "Revise arrays, linked lists, trees, graphs, and DP.",
        "OOP": "Revise inheritance, polymorphism, abstraction, and encapsulation.",
        "STL": "Practice vector, map, set, queue, stack, and priority_queue.",
        "SQL": "Revise joins, indexes, normalization, and basic query writing.",
        "REST API": "Understand request-response flow and simple backend API design.",
        "System Design": "Revise basic scalability, services, and architecture thinking.",
        "Docker": "Understand containers and why they are used in deployment.",
        "AWS": "Revise the basics of cloud services and deployment concepts.",
        "Linux": "Practice basic terminal commands and file system navigation.",
        "Debugging": "Practice reading errors carefully and tracing issues step by step.",
        "Communication": "Prepare short, clear explanations of your projects and choices.",
        "Problem Solving": "Practice common interview patterns and timed problem solving.",
        "Algorithms": "Revise sorting, searching, recursion, and complexity analysis.",
        "Data Structures": "Revise arrays, stacks, queues, trees, graphs, and hash maps.",
        "Next.js": "Revise routing, server rendering, and component structure.",
        "React": "Revise components, props, state, hooks, and rendering flow.",
        "TypeScript": "Revise types, interfaces, unions, and function typing.",
        "Backend Development": "Focus on APIs, logic, databases, and clean modular design.",
        "Frontend Development": "Focus on UI structure, components, and browser behavior.",
        "Microservices": "Revise service boundaries, communication, and deployment basics.",
    }
    return mapping.get(signal, f"Review {signal}.")


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("c++", "cplusplus")
    text = text.replace("next.js", "nextjs")
    text = text.replace("node.js", "nodejs")
    text = text.replace("rest api", "restapi")
    text = text.replace("front-end", "frontend")
    text = text.replace("back-end", "backend")
    return text


def extract_extra_terms(text: str):
    text = normalize_text(text)

    patterns = {
        "Next.js": [r"\bnextjs\b", r"\bnext\s*js\b"],
        "React": [r"\breact\b"],
        "TypeScript": [r"\btypescript\b"],
        "Node.js": [r"\bnodejs\b", r"\bnode\s*js\b"],
        "Python": [r"\bpython\b"],
        "Java": [r"\bjava\b"],
        "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
        "C++": [r"cplusplus", r"\bcpp\b"],
        "SQL": [r"\bsql\b"],
        "AWS": [r"\baws\b", r"amazon web services"],
        "Docker": [r"\bdocker\b"],
        "Linux": [r"\blinux\b"],
        "Git": [r"\bgit\b"],
        "REST API": [r"restapi", r"\bapi\b"],
        "System Design": [r"system design"],
        "Microservices": [r"microservices?"],
        "Backend Development": [r"backend development", r"backend engineering", r"backend developer"],
        "Frontend Development": [r"frontend development", r"frontend engineering", r"frontend developer"],
        "Problem Solving": [r"problem solving", r"problem-solving"],
        "Communication": [r"communication", r"collaboration"],
        "Debugging": [r"debugging", r"troubleshoot"],
        "Testing": [r"testing", r"unit test", r"pytest", r"junit"],
    }

    hits = []
    for term, pats in patterns.items():
        for pat in pats:
            if re.search(pat, text):
                hits.append(term)
                break

    return hits


def extract_signals_from_text(text: str):
    base = extract_skill_signals(text)
    extra = extract_extra_terms(text)
    return unique_keep_order(base + extra)


def uploaded_file_to_text(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    suffix = Path(uploaded_file.name).suffix.lower()
    raw_bytes = uploaded_file.getvalue()

    if suffix == ".pdf":
        pages = []
        try:
            reader = PdfReader(io.BytesIO(raw_bytes))
            for page in reader.pages:
                try:
                    page_text = page.extract_text() or ""
                except Exception:
                    page_text = ""
                if page_text.strip():
                    pages.append(page_text)
        except Exception as e:
            raise RuntimeError(f"Could not read PDF '{uploaded_file.name}': {e}")

        content = "\n".join(pages).strip()
        if not content:
            raise RuntimeError(
                f"Could not extract text from PDF '{uploaded_file.name}'. "
                "Use a text-based PDF or convert it to .txt."
            )
        return content

    return raw_bytes.decode("utf-8", errors="ignore")


def write_temp_text(prefix: str, text: str) -> str:
    with tempfile.NamedTemporaryFile(
        delete=False,
        prefix=prefix,
        suffix=".txt",
        mode="w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(text)
        return temp_file.name


def build_standard_role_file(role_name: str, raw_text: str, signals: list[str]) -> str:
    title = role_name.strip() or "Selected Role"
    combined = unique_keep_order(extract_signals_from_text(raw_text) + signals)

    required = combined[:10]
    preferred = combined[10:20]

    lines = [title, "", "Required:"]
    if required:
        lines.extend(required)
    else:
        lines.append("Problem Solving")
        lines.append("Communication")

    lines.append("")
    lines.append("Preferred:")
    if preferred:
        lines.extend(preferred)
    else:
        lines.append("Debugging")
        lines.append("Testing")

    return write_temp_text("role_std_", "\n".join(lines) + "\n")


def build_standard_company_file(company_name: str, raw_text: str, role_name: str, signals: list[str]) -> str:
    title = company_name.strip() or role_name.strip() or "Selected Company"
    combined = unique_keep_order(extract_signals_from_text(raw_text) + signals)

    expected = combined[:10]
    focus = combined[10:16]
    tips = []

    if expected:
        for sig in expected[:5]:
            tips.append(signal_to_tip(sig))
    else:
        tips.append("Study the company’s engineering/blog pages and job descriptions.")
        tips.append("Prepare a short explanation of why you fit the role.")

    if not focus:
        focus = [
            "Problem solving",
            "Clean code",
            "Role-specific preparation",
        ]

    lines = [title, "", "Expected:"]
    lines.extend(expected if expected else ["Problem Solving", "Communication"])

    lines.append("")
    lines.append("Focus:")
    lines.extend(focus)

    lines.append("")
    lines.append("Tips:")
    lines.extend(unique_keep_order(tips))

    return write_temp_text("company_std_", "\n".join(lines) + "\n")


def parse_backend_output(stdout: str) -> dict:
    data = {}
    inside_block = False

    for raw_line in stdout.splitlines():
        line = raw_line.strip()

        if line == "===RESULT_START===":
            inside_block = True
            continue

        if line == "===RESULT_END===":
            break

        if inside_block and "=" in line:
            key, value = line.split("=", 1)
            data[key.strip().lower()] = value.strip()

    return data


def cleanup_files(*file_paths):
    for path in file_paths:
        if path and Path(path).exists():
            try:
                Path(path).unlink()
            except OSError:
                pass


def run_backend_analysis(
    resume_upload,
    role_upload,
    company_upload=None,
    role_label: str = "",
    company_label: str = "",
    use_live_job_api: bool = True,
    use_web_intelligence: bool = True,
    country_code: str = "gb",
    location_filter: str = "",
):
    temp_files = []

    try:
        resume_text = uploaded_file_to_text(resume_upload)
        role_text = uploaded_file_to_text(role_upload)
        company_text = uploaded_file_to_text(company_upload) if company_upload else ""

        if not resume_text.strip() or not role_text.strip():
            return {
                "ok": False,
                "error": "Resume and role file are required.",
                "raw": "",
                "live_used": False,
                "web_used": False,
                "web_summary": "",
                "live_jobs": [],
                "live_signals": [],
                "web_results": [],
                "web_signals": [],
                "curated": {},
                "combined_missing": [],
                "combined_recommendations": [],
            }

        resume_path = write_temp_text("resume_", resume_text)
        temp_files.append(resume_path)

        live_result = {
            "ok": False,
            "error": "",
            "jobs": [],
            "signals": [],
            "query": "",
        }

        web_result = {
            "ok": False,
            "error": "",
            "results": [],
            "signals": [],
            "summary": "",
            "queries": [],
            "curated": {},
            "fallback_used": False,
        }

        live_used = False
        web_used = False
        live_summary = ""
        web_summary = ""

        live_signals = []
        web_signals = []
        curated = {}

        if use_live_job_api:
            live_result = fetch_adzuna_jobs(
                role_label=role_label,
                company_label=company_label,
                country_code=country_code,
                location_filter=location_filter,
                results_per_page=5,
            )
            live_signals = live_result.get("signals", [])
            if live_result.get("ok"):
                live_used = True
                live_summary = compose_live_summary(live_result)
            else:
                live_summary = live_result.get("error", "")

        if use_web_intelligence:
            web_result = search_web_intelligence(
                company_label=company_label,
                role_label=role_label,
                num_results=5,
            )
            web_signals = web_result.get("signals", [])
            web_used = bool(web_result.get("results"))
            web_summary = web_result.get("summary", "")
            curated = web_result.get("curated", {})
        else:
            curated = {}

        raw_role_signals = extract_signals_from_text(role_text)
        raw_company_signals = extract_signals_from_text(company_text if company_text.strip() else role_text)

        combined_signals = unique_keep_order(
            raw_role_signals
            + raw_company_signals
            + live_signals
            + web_signals
            + curated.get("keywords", [])
        )

        role_path_to_send = build_standard_role_file(
            role_label or "Selected Role",
            role_text,
            combined_signals,
        )
        company_path_to_send = build_standard_company_file(
            company_label or role_label or "Selected Company",
            company_text if company_text.strip() else role_text,
            role_label or "Selected Role",
            combined_signals,
        )

        temp_files.extend([role_path_to_send, company_path_to_send])

        if not BACKEND_EXE.exists():
            return {
                "ok": False,
                "error": f"Backend executable not found: {BACKEND_EXE}",
                "raw": "",
                "live_used": live_used,
                "web_used": web_used,
                "live_summary": live_summary,
                "web_summary": web_summary,
                "live_jobs": live_result.get("jobs", []),
                "live_signals": live_signals,
                "web_results": web_result.get("results", []),
                "web_signals": web_signals,
                "curated": curated,
                "combined_missing": [],
                "combined_recommendations": [],
            }

        cmd = [
            str(BACKEND_EXE),
            resume_path,
            role_path_to_send,
            company_path_to_send,
            str(SKILLS_FILE),
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )

        parsed = parse_backend_output(result.stdout)
        parsed["raw"] = result.stdout
        parsed["stderr"] = result.stderr.strip()
        parsed["live_used"] = live_used
        parsed["web_used"] = web_used
        parsed["live_summary"] = live_summary
        parsed["web_summary"] = web_summary
        parsed["live_jobs"] = live_result.get("jobs", [])
        parsed["live_signals"] = live_signals
        parsed["web_results"] = web_result.get("results", [])
        parsed["web_signals"] = web_signals
        parsed["curated"] = curated

        backend_recommendations = split_items(parsed.get("recommendations", ""), "||")
        web_tips = [signal_to_tip(sig) for sig in web_signals]
        live_tips = [signal_to_tip(sig) for sig in live_signals]
        curated_tips = curated.get("tips", [])
        curated_focus = curated.get("focus", [])

        combined_recommendations = unique_keep_order(
            backend_recommendations + curated_tips + web_tips + live_tips
        )

        combined_missing = unique_keep_order(
            split_items(parsed.get("missing_role", ""))
            + split_items(parsed.get("missing_company", ""))
            + curated_focus
        )

        parsed["combined_recommendations"] = combined_recommendations
        parsed["combined_missing"] = combined_missing

        if result.returncode != 0:
            parsed["ok"] = False
            parsed["error"] = parsed["stderr"] or "Backend process failed."
        else:
            parsed["ok"] = True

        return parsed

    finally:
        cleanup_files(*temp_files)