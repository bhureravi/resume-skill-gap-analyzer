import json
import re
from typing import Any, Dict, List

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:3b"

EMPTY_AI_RESULT = {
    "summary": "",
    "ats_score": None,
    "ats_improvements": [],
    "top_gaps": [],
    "priority_actions": [],
    "interview_focus": [],
}


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()
    return text


def _extract_json_object(text: str) -> str:
    text = text.strip()
    first = text.find("{")
    last = text.rfind("}")
    if first != -1 and last != -1 and last > first:
        return text[first : last + 1]
    return text


def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        value = str(item).strip()
        if not value:
            continue
        key = value.lower()
        if key not in seen:
            seen.add(key)
            result.append(value)
    return result


def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        parts = re.split(r"[,\n|]+", value)
        return [x.strip() for x in parts if x.strip()]
    return []


def _safe_int(value: Any) -> int | None:
    try:
        return int(str(value).strip())
    except Exception:
        return None


def _collect_grounded_skills(backend_data: Dict[str, Any]) -> List[str]:
    skills = []
    skills.extend(_as_list(backend_data.get("ground_truth_skills", [])))
    skills.extend(_as_list(backend_data.get("extracted_skills", "")))
    return _dedupe(skills)


def _resume_quality_cap(resume_text: str, backend_data: Dict[str, Any]) -> int:
    word_count = len(re.findall(r"\b\w+\b", resume_text))
    grounded_skills = _collect_grounded_skills(backend_data)

    lower = resume_text.lower()
    evidence_hits = 0
    for kw in [
        "project",
        "projects",
        "built",
        "developed",
        "implemented",
        "experience",
        "intern",
        "worked on",
    ]:
        if kw in lower:
            evidence_hits += 1

    bullet_hits = sum(
        1
        for line in resume_text.splitlines()
        if line.strip().startswith(("-", "*", "•", "1.", "2.", "3."))
    )

    if word_count < 40:
        cap = 8
    elif word_count < 80:
        cap = 18
    elif word_count < 150:
        cap = 28
    elif word_count < 250:
        cap = 40
    elif word_count < 400:
        cap = 55
    else:
        cap = 68

    cap += min(10, len(grounded_skills) // 3)
    cap += min(8, evidence_hits * 2)
    cap += min(5, bullet_hits)

    return max(5, min(cap, 85))


def _pad_items(items: List[str], fallback_items: List[str], target: int = 4) -> List[str]:
    out = _dedupe(items)
    for item in fallback_items:
        if len(out) >= target:
            break
        if item and item.lower() not in [x.lower() for x in out]:
            out.append(item)
    return out[:target]


def _fallback_summary(resume_text: str, backend_data: Dict[str, Any]) -> str:
    score = _safe_int(backend_data.get("overall_score"))
    grounded = _collect_grounded_skills(backend_data)

    if score is None:
        score_part = "The resume shows partial alignment with the target role."
    else:
        score_part = f"The resume has an estimated fit score of {score}/100 based on the current analysis."

    if grounded:
        skill_part = f"Key signals detected include {', '.join(grounded[:5])}."
    else:
        skill_part = "The analysis could not extract enough stable skill evidence."

    return f"{score_part} {skill_part}"


def _normalize_result(data: Dict[str, Any], backend_data: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
    result = dict(EMPTY_AI_RESULT)

    if not isinstance(data, dict):
        result["summary"] = _fallback_summary(resume_text, backend_data)
        result["ats_score"] = _resume_quality_cap(resume_text, backend_data)
        return result

    raw_summary = str(data.get("summary", "")).strip()
    result["summary"] = raw_summary if len(raw_summary) >= 50 else _fallback_summary(resume_text, backend_data)

    model_score = _safe_int(data.get("ats_score"))
    backend_score = _safe_int(backend_data.get("overall_score"))
    quality_cap = _resume_quality_cap(resume_text, backend_data)

    if backend_score is not None:
        score = min(backend_score, quality_cap)
    elif model_score is not None:
        score = min(model_score, quality_cap)
    else:
        score = quality_cap

    result["ats_score"] = max(0, min(score, 100))

    base_missing = _as_list(backend_data.get("combined_missing", []))
    if not base_missing:
        base_missing = _as_list(backend_data.get("missing_role", "")) + _as_list(backend_data.get("missing_company", ""))

    base_recommendations = _as_list(backend_data.get("combined_recommendations", []))
    grounded = _collect_grounded_skills(backend_data)

    result["ats_improvements"] = _pad_items(
        _as_list(data.get("ats_improvements", [])),
        [
            f"Add clearer proof for {base_missing[0]}" if base_missing else "Add stronger proof of role-relevant work in the resume.",
            "Rewrite project bullets with impact, tools, and outcomes.",
            "Make skills visible in project descriptions, not only in a skills section.",
            "Use concise action-oriented bullets throughout the resume.",
        ],
    )

    result["top_gaps"] = _pad_items(
        _as_list(data.get("top_gaps", [])),
        [
            base_missing[0] if len(base_missing) > 0 else "Backend development",
            base_missing[1] if len(base_missing) > 1 else "SQL",
            base_missing[2] if len(base_missing) > 2 else "REST API",
            base_missing[3] if len(base_missing) > 3 else "System design",
        ],
    )

    result["priority_actions"] = _pad_items(
        _as_list(data.get("priority_actions", [])),
        [
            base_recommendations[0] if len(base_recommendations) > 0 else "Strengthen one backend project and explain it clearly.",
            base_recommendations[1] if len(base_recommendations) > 1 else "Revise the missing role skills first.",
            base_recommendations[2] if len(base_recommendations) > 2 else "Prepare 2–3 project stories for interviews.",
            "Add measurable results to resume bullets.",
        ],
    )

    result["interview_focus"] = _pad_items(
        _as_list(data.get("interview_focus", [])),
        [
            grounded[0] if len(grounded) > 0 else "Explain your strongest project end-to-end.",
            grounded[1] if len(grounded) > 1 else "Be ready for questions on backend basics.",
            grounded[2] if len(grounded) > 2 else "Revise your chosen tech stack deeply.",
            "Practice short, confident explanations of your work.",
        ],
    )

    return result


def build_ai_prompt(
    resume_text: str,
    role_text: str,
    company_text: str,
    backend_data: Dict[str, Any],
) -> str:
    grounded_skills = _collect_grounded_skills(backend_data)
    grounded_skills_text = ", ".join(grounded_skills[:40]) if grounded_skills else "None"

    return f"""
You are an ATS resume reviewer.

Rules:
- Return ONLY valid JSON.
- Do not add markdown.
- Do not add explanations outside JSON.
- Use only facts from the resume text, role text, company text, and grounded skills.
- Do NOT invent technologies that are not present.
- Keep wording short, natural, and direct.
- Each list must contain up to 4 items.
- Summary must be 3 to 4 sentences.
- Make the answer useful for internship preparation.

Return exactly this JSON shape:
{{
  "summary": "3-4 sentences",
  "ats_score": 0,
  "ats_improvements": ["..."],
  "top_gaps": ["..."],
  "priority_actions": ["..."],
  "interview_focus": ["..."]
}}

Resume text:
{resume_text}

Role text:
{role_text}

Company text:
{company_text}

Grounded skills:
{grounded_skills_text}

Backend summary:
Overall Score: {backend_data.get("overall_score", "")}
Missing Role Skills: {backend_data.get("missing_role", "")}
Missing Company Skills: {backend_data.get("missing_company", "")}
Extracted Skills: {backend_data.get("extracted_skills", "")}
""".strip()


def generate_ai_insights(
    resume_text: str,
    role_text: str,
    company_text: str = "",
    backend_data: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    backend_data = backend_data or {}

    resume_text = resume_text[:4000]
    role_text = role_text[:2000]
    company_text = company_text[:1500]

    prompt = build_ai_prompt(
        resume_text=resume_text,
        role_text=role_text,
        company_text=company_text,
        backend_data=backend_data,
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.0,
            "num_predict": 1000,
        },
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=180)
        response.raise_for_status()
        raw_text = response.json().get("response", "").strip()
    except Exception as e:
        fallback = dict(EMPTY_AI_RESULT)
        fallback["summary"] = f"Ollama request failed: {e}"
        fallback["ats_score"] = _resume_quality_cap(resume_text, backend_data)
        fallback["ats_improvements"] = _pad_items(
            [],
            [
                "Add stronger project evidence in the resume.",
                "Mention tools and outcomes clearly.",
                "Make skills visible in project bullets.",
                "Use concise ATS-friendly wording.",
            ],
        )
        fallback["top_gaps"] = _pad_items(
            [],
            [
                "Role-specific backend experience",
                "SQL",
                "REST API",
                "System design",
            ],
        )
        fallback["priority_actions"] = _pad_items(
            [],
            [
                "Revise the top missing skills first.",
                "Add one strong backend project bullet.",
                "Rewrite resume bullets with impact.",
                "Prepare a short project explanation.",
            ],
        )
        fallback["interview_focus"] = _pad_items(
            [],
            [
                "Explain your best project clearly.",
                "Revise backend fundamentals.",
                "Be ready for questions on your tech stack.",
                "Practice short interview answers.",
            ],
        )
        return fallback

    raw_text = _strip_code_fences(raw_text)
    raw_text = _extract_json_object(raw_text)

    try:
        parsed = json.loads(raw_text)
        return _normalize_result(parsed, backend_data, resume_text)
    except Exception as e:
        fallback = dict(EMPTY_AI_RESULT)
        fallback["summary"] = f"JSON parse failed: {e}"
        fallback["ats_score"] = _resume_quality_cap(resume_text, backend_data)
        fallback["ats_improvements"] = _pad_items(
            [],
            [
                "Add stronger project evidence in the resume.",
                "Mention tools and outcomes clearly.",
                "Make skills visible in project bullets.",
                "Use concise ATS-friendly wording.",
            ],
        )
        fallback["top_gaps"] = _pad_items(
            [],
            [
                "Role-specific backend experience",
                "SQL",
                "REST API",
                "System design",
            ],
        )
        fallback["priority_actions"] = _pad_items(
            [],
            [
                "Revise the top missing skills first.",
                "Add one strong backend project bullet.",
                "Rewrite resume bullets with impact.",
                "Prepare a short project explanation.",
            ],
        )
        fallback["interview_focus"] = _pad_items(
            [],
            [
                "Explain your best project clearly.",
                "Revise backend fundamentals.",
                "Be ready for questions on your tech stack.",
                "Practice short interview answers.",
            ],
        )
        return fallback