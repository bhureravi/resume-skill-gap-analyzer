import re
from pathlib import Path
from typing import List, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from job_api import extract_skill_signals, get_curated_insights

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DDG_SEARCH_URL = "https://html.duckduckgo.com/html/"
BING_SEARCH_URL = "https://www.bing.com/search"
DEFAULT_TIMEOUT = 20
MAX_RESULTS_PER_QUERY = 4
MAX_PAGES_TO_CRAWL = 12
MAX_TEXT_CHARS = 12000

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def build_queries(company_label: str, role_label: str) -> List[str]:
    company_label = company_label.strip()
    role_label = role_label.strip()

    base = " ".join([company_label, role_label]).strip()
    if not base:
        base = company_label or role_label

    return [
        f"{base} interview questions",
        f"{base} skills",
        f"{base} preparation tips",
        f"{base} roadmap",
        f"{company_label} {role_label} hiring",
        f"{company_label} {role_label} experience",
        f"{role_label} interview questions",
        f"{role_label} skills",
    ]


def _dedupe_results(results: List[dict]) -> List[dict]:
    seen = set()
    final_results = []

    for item in results:
        key = item.get("link", "").strip().lower()
        if not key:
            key = (item.get("title", "") + "|" + item.get("snippet", "")).lower()

        if key in seen:
            continue

        seen.add(key)
        final_results.append(item)

    return final_results


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _is_valid_public_url(url: str) -> bool:
    if not url:
        return False

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False

    bad_domains = {
        "duckduckgo.com",
        "html.duckduckgo.com",
        "www.bing.com",
        "bing.com",
    }

    if parsed.netloc.lower() in bad_domains:
        return False

    return True


def search_duckduckgo(query: str, max_results: int = MAX_RESULTS_PER_QUERY) -> List[dict]:
    try:
        response = requests.get(
            DDG_SEARCH_URL,
            params={"q": query},
            headers=HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result_card in soup.select(".result"):
        anchor = result_card.select_one("a.result__a")
        snippet_el = result_card.select_one(".result__snippet")

        if not anchor:
            continue

        href = anchor.get("href", "").strip()
        title = _clean_text(anchor.get_text(" ", strip=True))
        snippet = _clean_text(snippet_el.get_text(" ", strip=True)) if snippet_el else ""

        if not href or not title:
            continue

        results.append(
            {
                "title": title,
                "snippet": snippet,
                "link": href,
                "query": query,
                "source": "duckduckgo",
            }
        )

        if len(results) >= max_results:
            break

    return results


def search_bing(query: str, max_results: int = MAX_RESULTS_PER_QUERY) -> List[dict]:
    try:
        response = requests.get(
            BING_SEARCH_URL,
            params={"q": query},
            headers=HEADERS,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for card in soup.select("li.b_algo"):
        anchor = card.select_one("h2 a")
        if not anchor:
            continue

        href = anchor.get("href", "").strip()
        title = _clean_text(anchor.get_text(" ", strip=True))
        snippet_el = card.select_one(".b_caption p")
        snippet = _clean_text(snippet_el.get_text(" ", strip=True)) if snippet_el else ""

        if not href or not title:
            continue

        if href.startswith("/"):
            href = urljoin("https://www.bing.com", href)

        results.append(
            {
                "title": title,
                "snippet": snippet,
                "link": href,
                "query": query,
                "source": "bing",
            }
        )

        if len(results) >= max_results:
            break

    return results


def fetch_page_text(url: str) -> str:
    if not _is_valid_public_url(url):
        return ""

    try:
        response = requests.get(url, headers=HEADERS, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except Exception:
        return ""

    content_type = response.headers.get("content-type", "").lower()
    if "text/html" not in content_type and "application/xhtml+xml" not in content_type:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "img", "header", "footer", "nav"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)
    text = _clean_text(text)

    if len(text) > MAX_TEXT_CHARS:
        text = text[:MAX_TEXT_CHARS]

    return text


def _role_source_urls(role_label: str) -> List[str]:
    role = role_label.lower().strip()
    urls = []

    if any(k in role for k in ["backend", "software", "sde", "developer", "engineer"]):
        urls.extend([
            "https://roadmap.sh/backend",
            "https://roadmap.sh/software-design-architecture",
            "https://www.geeksforgeeks.org/system-design-tutorial/",
            "https://www.freecodecamp.org/news/tag/interview-preparation/",
        ])

    if any(k in role for k in ["frontend", "ui", "ux"]):
        urls.extend([
            "https://roadmap.sh/frontend",
            "https://roadmap.sh/javascript",
            "https://www.geeksforgeeks.org/web-development/",
            "https://www.freecodecamp.org/news/tag/interview-preparation/",
        ])

    if any(k in role for k in ["data analyst", "data analysis", "analytics"]):
        urls.extend([
            "https://roadmap.sh/data-analyst",
            "https://www.geeksforgeeks.org/data-analysis/",
            "https://www.freecodecamp.org/news/tag/data-science/",
        ])

    if any(k in role for k in ["data engineer", "ml engineer", "machine learning", "ml", "ai", "scientist"]):
        urls.extend([
            "https://roadmap.sh/ai-engineer",
            "https://roadmap.sh/data-engineer",
            "https://www.geeksforgeeks.org/machine-learning/",
            "https://www.freecodecamp.org/news/tag/machine-learning/",
        ])

    if any(k in role for k in ["product manager", "pm"]):
        urls.extend([
            "https://roadmap.sh/product-manager",
            "https://www.interviewbit.com/blog/product-manager-interview-questions/",
            "https://www.freecodecamp.org/news/tag/interview-preparation/",
        ])

    if any(k in role for k in ["devops", "cloud", "sre", "platform"]):
        urls.extend([
            "https://roadmap.sh/devops",
            "https://roadmap.sh/system-design",
            "https://www.geeksforgeeks.org/devops/",
            "https://www.freecodecamp.org/news/tag/devops/",
        ])

    if not urls:
        urls.extend([
            "https://roadmap.sh/",
            "https://www.freecodecamp.org/news/tag/interview-preparation/",
            "https://www.geeksforgeeks.org/",
        ])

    return urls


def _company_source_urls(company_label: str) -> List[str]:
    company = company_label.lower().strip()
    urls = []

    if "amazon" in company:
        urls.extend([
            "https://www.aboutamazon.com/news/innovation-at-amazon",
            "https://www.amazon.jobs/content/en/teams",
            "https://www.amazon.jobs/content/en/teams/engineering",
        ])

    if "google" in company:
        urls.extend([
            "https://blog.google/inside-google/",
            "https://blog.google/technology/",
            "https://careers.google.com/",
        ])

    if "microsoft" in company:
        urls.extend([
            "https://blogs.microsoft.com/ai/",
            "https://blogs.microsoft.com/opensource/",
            "https://careers.microsoft.com/",
        ])

    if "meta" in company or "facebook" in company:
        urls.extend([
            "https://engineering.fb.com/",
            "https://about.fb.com/",
            "https://www.metacareers.com/",
        ])

    if "apple" in company:
        urls.extend([
            "https://www.apple.com/newsroom/",
            "https://jobs.apple.com/",
        ])

    if "netflix" in company:
        urls.extend([
            "https://netflixtechblog.com/",
            "https://jobs.netflix.com/",
        ])

    if "uber" in company:
        urls.extend([
            "https://www.uber.com/blog/engineering/",
            "https://www.uber.com/global/en/careers/",
        ])

    if "nvidia" in company:
        urls.extend([
            "https://blogs.nvidia.com/",
            "https://www.nvidia.com/en-us/about-nvidia/careers/",
        ])

    if "adobe" in company:
        urls.extend([
            "https://blog.adobe.com/en/topics/engineering",
            "https://careers.adobe.com/",
        ])

    if not urls:
        urls.extend([
            "https://news.ycombinator.com/",
            "https://www.freecodecamp.org/news/tag/interview-preparation/",
        ])

    return urls


def _fallback_source_urls(company_label: str, role_label: str) -> List[str]:
    urls = []
    urls.extend(_role_source_urls(role_label))
    urls.extend(_company_source_urls(company_label))

    seen = set()
    final = []
    for url in urls:
        key = url.lower().strip()
        if key and key not in seen:
            seen.add(key)
            final.append(url)
    return final


def _crawl_sources(urls: List[str]) -> List[dict]:
    crawled = []
    for url in urls:
        page_text = fetch_page_text(url)
        if not page_text:
            continue

        crawled.append(
            {
                "title": url,
                "snippet": page_text[:500],
                "link": url,
                "page_text": page_text,
                "source": "public_page",
            }
        )

    return crawled


def search_web_intelligence(company_label: str, role_label: str, num_results: int = 5) -> dict:
    fallback_curated = get_curated_insights(company_label, role_label, [])

    queries = build_queries(company_label, role_label)
    all_results: List[dict] = []
    corpus_parts: List[str] = []

    for query in queries:
        ddg_results = search_duckduckgo(query, max_results=num_results)
        bing_results = search_bing(query, max_results=num_results)
        all_results.extend(ddg_results)
        all_results.extend(bing_results)

    all_results = _dedupe_results(all_results)

    if len(all_results) < 3:
        fallback_urls = _fallback_source_urls(company_label, role_label)
        fallback_pages = _crawl_sources(fallback_urls)
        all_results.extend(fallback_pages)
        all_results = _dedupe_results(all_results)

    crawled_count = 0
    for item in all_results[:MAX_PAGES_TO_CRAWL]:
        if item.get("page_text"):
            page_text = item["page_text"]
        else:
            page_text = fetch_page_text(item.get("link", ""))
            item["page_text"] = page_text

        if page_text:
            corpus_parts.append(" ".join([item.get("title", ""), item.get("snippet", ""), page_text]))
            crawled_count += 1

    signals = extract_skill_signals(" ".join(corpus_parts))
    curated = get_curated_insights(company_label, role_label, signals)

    summary_lines = []

    if all_results:
        summary_lines.append(
            f"Collected {len(all_results)} public web results for: {company_label} / {role_label}"
        )
    else:
        summary_lines.append("No public web results were found.")
        summary_lines.append("Using curated fallback intelligence.")

    if crawled_count > 0:
        summary_lines.append(f"Crawled {crawled_count} public pages successfully.")

    if signals:
        summary_lines.append("Detected signals: " + ", ".join(signals[:8]))

    for index, item in enumerate(all_results[:3], start=1):
        title = item.get("title", "")
        link = item.get("link", "")
        summary_lines.append(f"{index}. {title}")
        if link:
            summary_lines.append(f"   {link}")

    return {
        "ok": True,
        "error": "",
        "queries": queries,
        "results": all_results,
        "signals": signals,
        "summary": "\n".join(summary_lines),
        "curated": curated,
        "fallback_used": len(all_results) == 0,
    }