# GitHub Trending Skill

A Claude Code skill that fetches and summarizes GitHub Trending repositories.

## Features

- Fetch trending repos for **Today**, **This Week**, or **This Month**
- Filter by programming language (e.g., `python`, `rust`)
- Filter by spoken language (e.g., `zh` for Chinese)
- Outputs structured JSON with rank, stars, forks, descriptions

## Usage

### As a standalone script

```bash
# Daily trending (default)
python3 scripts/fetch_trending.py

# Weekly trending
python3 scripts/fetch_trending.py --since weekly

# Monthly trending, Python only
python3 scripts/fetch_trending.py --since monthly --language python

# Chinese repos
python3 scripts/fetch_trending.py --since daily --spoken-language zh
```

### As a Claude Code Skill

Copy or symlink the `github-trending/` directory into your `.claude/skills/` folder, then ask Claude things like:

- "What's trending on GitHub today?"
- "Show me this week's hot repos"
- "GitHub trending Python projects this month"
- "GitHub 热榜"
- "What are the most popular new repos?"

## Output Format

```json
{
  "since": "daily",
  "count": 13,
  "repos": [
    {
      "rank": 1,
      "owner": "warpdotdev",
      "repo": "warp",
      "url": "https://github.com/warpdotdev/warp",
      "description": "Warp is an agentic development environment...",
      "language": "Rust",
      "total_stars": "49,426",
      "period_stars": "+8,399",
      "forks": "3,229"
    }
  ]
}
```

## Structure

```
github-trending/
├── SKILL.md                  # Skill definition for Claude Code
├── scripts/
│   └── fetch_trending.py     # Python scraper
└── README.md
```
