import io
import os
import subprocess
import tempfile
from pathlib import Path

from pypdf import PdfReader

from job_api import (
    build_enriched_company_file,
    build_enriched_role_file,
    compose_live_summary,
    fetch_adzuna_jobs,
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
    }
    return mapping.get(signal, f"Review {signal}.")


def uploaded_file_to_temp_text(uploaded_file, prefix: str) -> str | None:
    if uploaded_file is None:
        return None

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

        with tempfile.NamedTemporaryFile(
            delete=False,
            prefix=prefix,
            suffix=".txt",
            mode="w",
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(content)
            return temp_file.name

    with tempfile.NamedTemporaryFile(
        delete=False,
        prefix=prefix,
        suffix=".txt",
        mode="wb",
    ) as temp_file:
        temp_file.write(raw_bytes)
        return temp_file.name


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
    company_upload,
    role_label: str = "",
    company_label: str = "",
    use_live_job_api: bool = True,
    use_web_intelligence: bool = True,
    country_code: str = "gb",
    location_filter: str = "",
):
    temp_files = []

    try:
        resume_path = uploaded_file_to_temp_text(resume_upload, "resume_")
        role_path = uploaded_file_to_temp_text(role_upload, "role_")
        company_path = uploaded_file_to_temp_text(company_upload, "company_")

        temp_files.extend([resume_path, role_path, company_path])

        if not resume_path or not role_path or not company_path:
            return {
                "ok": False,
                "error": "Missing one or more uploaded files.",
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

        role_path_to_send = role_path
        company_path_to_send = company_path

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

        combined_signals = []
        for item in live_signals + web_signals:
            if item not in combined_signals:
                combined_signals.append(item)

        for item in curated.get("keywords", []):
            if item not in combined_signals:
                combined_signals.append(item)

        if combined_signals:
            role_path_to_send = build_enriched_role_file(role_path, combined_signals)
            company_path_to_send = build_enriched_company_file(
                company_path,
                live_result.get("jobs", []),
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