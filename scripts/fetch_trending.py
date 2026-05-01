#!/usr/bin/env python3
"""
Fetch GitHub Trending repositories and output structured JSON.

Usage:
    python3 fetch_trending.py [--since daily|weekly|monthly] [--language <lang>] [--spoken-language <code>]
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from html import unescape
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

GITHUB_TRENDING_URL = "https://github.com/trending"

LANG_MAP = {
    "python": "python", "javascript": "javascript", "typescript": "typescript",
    "rust": "rust", "go": "go", "java": "java", "c++": "c++", "c#": "c%23",
    "c": "c", "ruby": "ruby", "php": "php", "swift": "swift", "kotlin": "kotlin",
    "scala": "scala", "shell": "shell", "html": "html", "css": "css",
    "jupyter-notebook": "jupyter-notebook", "vue": "vue", "svelte": "svelte",
    "zig": "zig", "lua": "lua", "haskell": "haskell", "elixir": "elixir",
    "clojure": "clojure", "dart": "dart", "r": "r", "objective-c": "objective-c",
}

SPOKEN_LANG_MAP = {
    "zh": "zh-hans", "en": "en", "ja": "ja", "ko": "ko",
    "es": "es", "fr": "fr", "de": "de", "pt": "pt",
    "ru": "ru", "ar": "ar", "it": "it", "vi": "vi",
}


def build_url(since: str, language: str | None = None, spoken_language: str | None = None) -> str:
    url = f"{GITHUB_TRENDING_URL}?since={since}"
    if language:
        lang_slug = LANG_MAP.get(language.lower(), language.lower())
        url = f"{GITHUB_TRENDING_URL}/{lang_slug}?since={since}"
    if spoken_language:
        sl = SPOKEN_LANG_MAP.get(spoken_language.lower(), spoken_language.lower())
        url += f"&spoken_language_code={sl}"
    return url


def fetch_page(url: str) -> str:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    })
    try:
        with urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except HTTPError as e:
        print(json.dumps({"error": f"HTTP {e.code}: {e.reason}", "url": url}), file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(json.dumps({"error": f"Connection error: {e.reason}", "url": url}), file=sys.stderr)
        sys.exit(1)


def clean_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_trending(html: str, since: str) -> list[dict]:
    repos = []
    articles = re.findall(
        r'<article class="Box-row">(.*?)</article>',
        html, re.DOTALL
    )

    for idx, article in enumerate(articles, 1):
        # Extract owner/repo from the h2 link
        repo_match = re.search(
            r'<h2[^>]*>\s*<a[^>]*href="/([^"]+)"',
            article, re.DOTALL
        )
        if not repo_match:
            continue

        repo_path = repo_match.group(1).strip().rstrip("/")
        parts = repo_path.split("/")
        if len(parts) < 2:
            continue

        owner = parts[0]
        repo_name = parts[1]

        # Description
        desc_match = re.search(
            r'<p class="col-9[^"]*">(.*?)</p>',
            article, re.DOTALL
        )
        description = clean_html(desc_match.group(1)) if desc_match else ""

        # Programming language
        lang_match = re.search(
            r'itemprop="programmingLanguage">(.*?)<',
            article
        )
        language = lang_match.group(1).strip() if lang_match else ""

        # Total stars — find the stargazers link; the number appears after SVG content, before </a>
        stars_match = re.search(
            r'href="/' + re.escape(repo_path) + r'/stargazers".*?</svg>\s*([\d,]+)\s*</a>',
            article, re.DOTALL
        )
        total_stars = stars_match.group(1).strip() if stars_match else ""

        # Period stars (today/this week/this month)
        period_match = re.search(r'([\d,]+)\s+stars?\s+(today|this week|this month)', article)
        period_stars = f"+{period_match.group(1)}" if period_match else ""

        # Forks — same pattern: SVG then number
        forks_match = re.search(
            r'href="/' + re.escape(repo_path) + r'/forks".*?</svg>\s*([\d,]+)\s*</a>',
            article, re.DOTALL
        )
        forks = forks_match.group(1).strip() if forks_match else ""

        repos.append({
            "rank": idx,
            "owner": owner,
            "repo": repo_name,
            "url": f"https://github.com/{repo_path}",
            "description": description,
            "language": language,
            "total_stars": total_stars,
            "period_stars": period_stars,
            "forks": forks,
        })

    return repos


def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub Trending repositories")
    parser.add_argument(
        "--since", choices=["daily", "weekly", "monthly"], default="daily",
        help="Time range (default: daily)"
    )
    parser.add_argument(
        "--language", type=str, default=None,
        help="Filter by programming language (e.g., python, rust)"
    )
    parser.add_argument(
        "--spoken-language", type=str, default=None,
        help="Filter by spoken language code (e.g., zh, en)"
    )
    args = parser.parse_args()

    url = build_url(args.since, args.language, args.spoken_language)
    html = fetch_page(url)
    repos = parse_trending(html, args.since)

    result = {
        "since": args.since,
        "language": args.language or "all",
        "spoken_language": args.spoken_language or "all",
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(repos),
        "repos": repos,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
