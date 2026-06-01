import json
import os
import re
import tempfile
from pathlib import Path
from typing import List

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADZUNA_BASE_URL = "https://api.adzuna.com/v1/api"
INTELLIGENCE_FILE = PROJECT_ROOT / "src" / "ui" / "company_role_intelligence.json"

TRACKED_SIGNAL_PATTERNS = {
    "C++": [r"c\+\+", r"cplusplus", r"\bcpp\b"],
    "Python": [r"\bpython\b"],
    "Java": [r"\bjava\b"],
    "JavaScript": [r"javascript", r"\bjs\b"],
    "HTML": [r"\bhtml\b"],
    "CSS": [r"\bcss\b"],
    "SQL": [r"\bsql\b"],
    "Git": [r"\bgit\b"],
    "STL": [r"\bstl\b"],
    "OOP": [r"\boop\b", r"object oriented", r"object-oriented"],
    "DSA": [r"\bdsa\b", r"data structures", r"algorithms?"],
    "REST API": [r"rest api", r"\bapi\b"],
    "Docker": [r"\bdocker\b"],
    "AWS": [r"\baws\b", r"amazon web services"],
    "Linux": [r"\blinux\b"],
    "System Design": [r"system design"],
    "Testing": [r"testing", r"unit test", r"pytest", r"junit"],
    "Debugging": [r"debugging", r"troubleshoot"],
    "Communication": [r"communication", r"collaboration"],
    "React": [r"\breact\b"],
    "Node.js": [r"node\.?js"],
}

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "your", "you", "are",
    "will", "our", "their", "they", "have", "has", "had", "job", "role", "jobs",
    "experience", "skills", "skill", "responsibilities", "responsibility",
    "requirements", "requirement", "company", "team", "teams", "work", "working",
    "strong", "able", "ability", "years", "year", "knowledge", "including",
    "preferred", "required", "good", "great", "must", "should", "use", "used",
    "using", "build", "builds", "built", "developer", "engineer", "eng",
    "senior", "junior", "intern", "internship", "software", "backend",
    "frontend", "fullstack", "full", "time", "remote", "location", "based",
    "design", "support", "product", "solutions", "technical", "technology"
}


def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("c++", "cplusplus")
    text = text.replace("node.js", "nodejs")
    text = text.replace("rest api", "restapi")
    return text


def get_adzuna_credentials() -> tuple[str, str]:
    app_id = os.getenv("ADZUNA_APP_ID", "").strip()
    app_key = os.getenv("ADZUNA_APP_KEY", "").strip()
    return app_id, app_key


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def _read_nonempty_lines(path: str) -> List[str]:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    return [line.rstrip("\n") for line in text.splitlines()]


def parse_role_file(path: str) -> tuple[str, List[str], List[str]]:
    lines = _read_nonempty_lines(path)

    title = ""
    required: List[str] = []
    preferred: List[str] = []
    current_section = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if not title:
            title = line
            continue

        if line == "Required:":
            current_section = "required"
            continue

        if line == "Preferred:":
            current_section = "preferred"
            continue

        if current_section == "required":
            required.append(line)
        elif current_section == "preferred":
            preferred.append(line)

    if not title:
        title = Path(path).stem.replace("_", " ").title()

    return title, _dedupe(required), _dedupe(preferred)


def parse_company_file(path: str) -> tuple[str, List[str], List[str], List[str]]:
    lines = _read_nonempty_lines(path)

    title = ""
    expected: List[str] = []
    focus: List[str] = []
    tips: List[str] = []
    current_section = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if not title:
            title = line
            continue

        if line == "Expected:":
            current_section = "expected"
            continue

        if line == "Focus:":
            current_section = "focus"
            continue

        if line == "Tips:":
            current_section = "tips"
            continue

        if current_section == "expected":
            expected.append(line)
        elif current_section == "focus":
            focus.append(line)
        elif current_section == "tips":
            tips.append(line)

    if not title:
        title = Path(path).stem.replace("_", " ").title()

    return title, _dedupe(expected), _dedupe(focus), _dedupe(tips)


def extract_skill_signals(text: str) -> List[str]:
    normalized = normalize_text(text)
    matched = []

    for skill, patterns in TRACKED_SIGNAL_PATTERNS.items():
        count = 0
        for pattern in patterns:
            count += len(re.findall(pattern, normalized))
        if count > 0:
            matched.append((skill, count))

    matched.sort(key=lambda x: (-x[1], x[0]))
    return [skill for skill, _ in matched]


def fetch_adzuna_jobs(
    role_label: str,
    company_label: str,
    country_code: str = "gb",
    location_filter: str = "",
    results_per_page: int = 5,
) -> dict:
    app_id, app_key = get_adzuna_credentials()

    if not app_id or not app_key:
        return {
            "ok": False,
            "error": "Missing Adzuna credentials. Add ADZUNA_APP_ID and ADZUNA_APP_KEY.",
            "jobs": [],
            "signals": [],
            "query": "",
        }

    query_parts = [part.strip() for part in [role_label, company_label] if part and part.strip()]
    query = " ".join(query_parts)

    if not query:
        return {
            "ok": False,
            "error": "Please provide a role name or a company name for the online search.",
            "jobs": [],
            "signals": [],
            "query": "",
        }

    url = f"{ADZUNA_BASE_URL}/jobs/{country_code}/search/1"
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": query,
        "results_per_page": results_per_page,
        "content-type": "application/json",
    }

    if location_filter.strip():
        params["where"] = location_filter.strip()

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()

    jobs = []
    corpus = []

    for item in data.get("results", [])[:results_per_page]:
        title = item.get("title", "").strip()
        company = item.get("company", {}).get("display_name", "").strip()
        location = item.get("location", {}).get("display_name", "").strip()
        snippet = item.get("description", "").strip()
        url = item.get("redirect_url", "").strip()

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "snippet": snippet,
                "url": url,
            }
        )

        corpus.append(" ".join([title, company, location, snippet]))

    signals = extract_skill_signals(" ".join(corpus))

    return {
        "ok": True,
        "error": "",
        "jobs": jobs,
        "signals": signals,
        "query": query,
        "country_code": country_code,
        "location_filter": location_filter.strip(),
    }


def load_intelligence_db() -> dict:
    if not INTELLIGENCE_FILE.exists():
        return {}
    try:
        return json.loads(INTELLIGENCE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def make_intelligence_key(company_label: str, role_label: str) -> str:
    return f"{company_label.strip().lower()}|{role_label.strip().lower()}"


def get_curated_insights(company_label: str, role_label: str, live_signals: List[str] | None = None) -> dict:
    db = load_intelligence_db()
    key = make_intelligence_key(company_label, role_label)

    entry = db.get(key) or db.get("default", {})
    live_signals = live_signals or []

    focus = _dedupe(entry.get("focus", []) + [f"Live signal: {s}" for s in live_signals[:5]])
    tips = _dedupe(entry.get("tips", []))
    keywords = _dedupe(entry.get("keywords", []) + live_signals)

    return {
        "title": entry.get("title", "General Prep"),
        "focus": focus,
        "tips": tips,
        "keywords": keywords,
    }


def build_enriched_role_file(original_path: str, extra_signals: List[str]) -> str:
    title, required, preferred = parse_role_file(original_path)
    preferred = _dedupe(preferred + extra_signals)

    lines = [title, "", "Required:"]
    lines.extend(required)
    lines.append("")
    lines.append("Preferred:")
    lines.extend(preferred)

    return _write_temp_text("role_enriched_", "\n".join(lines) + "\n")


def build_enriched_company_file(
    original_path: str,
    jobs: List[dict],
    extra_signals: List[str],
) -> str:
    title, expected, focus, tips = parse_company_file(original_path)

    expected = _dedupe(expected + extra_signals[:8])
    focus = _dedupe(focus + [f"Live market trend: {signal}" for signal in extra_signals[:5]])

    live_tips = []
    for signal in extra_signals[:5]:
        live_tips.append(f"Review recent postings for repeated mentions of {signal}.")

    for job in jobs[:3]:
        title_text = job.get("title", "").strip()
        company_text = job.get("company", "").strip()
        if title_text:
            live_tips.append(f"Recent role example: {title_text} at {company_text}.")

    tips = _dedupe(tips + live_tips)

    lines = [title, "", "Expected:"]
    lines.extend(expected)
    lines.append("")
    lines.append("Focus:")
    lines.extend(focus)
    lines.append("")
    lines.append("Tips:")
    lines.extend(tips)

    return _write_temp_text("company_enriched_", "\n".join(lines) + "\n")


def compose_live_summary(fetch_result: dict) -> str:
    if not fetch_result.get("ok"):
        return fetch_result.get("error", "Live search unavailable.")

    jobs = fetch_result.get("jobs", [])
    signals = fetch_result.get("signals", [])
    query = fetch_result.get("query", "")

    lines = []
    lines.append(f"Fetched {len(jobs)} live job posts for: {query}")

    if signals:
        lines.append("Common online signals: " + ", ".join(signals[:8]))

    for index, job in enumerate(jobs[:3], start=1):
        title = job.get("title", "")
        company = job.get("company", "")
        location = job.get("location", "")
        lines.append(f"{index}. {title} @ {company} ({location})")

    return "\n".join(lines)


def _write_temp_text(prefix: str, text: str) -> str:
    with tempfile.NamedTemporaryFile(
        delete=False,
        prefix=prefix,
        suffix=".txt",
        mode="w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(text)
        return temp_file.name