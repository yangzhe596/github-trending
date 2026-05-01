---
name: github-trending
description: >
  Fetch and summarize GitHub Trending repositories. Use this skill whenever the user
  asks about GitHub trending, popular repos, what's hot on GitHub, trending projects,
  or wants to discover new/open-source projects. Supports today, this week, and this
  month views. Trigger on keywords like "trending", "hot repos", "popular projects",
  "github热榜", "github趋势", "github trending", even if not explicitly requesting
  a specific time range.
---

# GitHub Trending Fetcher

Fetch, parse, and present GitHub Trending repositories in a clean, organized format.

## How it works

This skill uses a bundled Python script that scrapes GitHub's trending page and extracts
structured data about trending repositories. It supports three time ranges:

- **Today** (`daily`) — repos gaining stars right now
- **This Week** (`weekly`) — repos with strong weekly momentum
- **This Month** (`monthly`) — repos with sustained popularity

## Usage

Run the bundled script to fetch trending data:

```bash
python3 <skill-dir>/scripts/fetch_trending.py [--since daily|weekly|monthly] [--language <lang>] [--spoken-language <code>]
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `--since` | Time range: `daily`, `weekly`, or `monthly` | `daily` |
| `--language` | Filter by programming language (e.g., `python`, `rust`, `typescript`) | all |
| `--spoken-language` | Filter by spoken language code (e.g., `zh` for Chinese, `en` for English) | all |

### Fetching all three ranges

When the user doesn't specify a time range, fetch all three and present them separately:

```bash
python3 <skill-dir>/scripts/fetch_trending.py --since daily
python3 <skill-dir>/scripts/fetch_trending.py --since weekly
python3 <skill-dir>/scripts/fetch_trending.py --since monthly
```

## Output format

The script outputs JSON with the following structure:

```json
{
  "since": "daily",
  "language": "all",
  "fetched_at": "2026-05-01T12:00:00",
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
      "forks": "1,234"
    }
  ]
}
```

## Presenting results to the user

After fetching, present the results as a **markdown table** with these columns:

| # | Project | Description | Language | Stars | Trend |

- **#** — rank number
- **Project** — clickable link `[owner/repo](url)`
- **Description** — truncate to ~60 chars
- **Language** — programming language
- **Stars** — total star count
- **Trend** — period stars with a fire emoji prefix, e.g. `🔥 +8,399`

### When showing all three ranges

Structure the output like this:

```
## GitHub Trending — Today (2026-05-01)

| # | Project | Description | Language | Stars | Trend |
|---|---------|-------------|----------|-------|-------|
...

## GitHub Trending — This Week

...

## GitHub Trending — This Month

...
```

### Highlighting patterns

After the tables, add a brief **"Highlights"** section (2-4 bullet points) noting:
- The hottest project (highest period stars)
- Any dominant themes (e.g., "AI Agent tools dominate this week")
- Notable language trends (e.g., "Rust projects on the rise")
- Any interesting patterns (e.g., "Multiple Chinese projects trending")

Keep highlights concise — one line each.

## Error handling

- If GitHub returns a non-200 status, inform the user and suggest trying again later
- If the page has fewer results than expected, note this but still present what was found
- If a specific language filter returns no results, suggest broadening the search

## Tips

- The user may ask in Chinese or English — respond in the same language they use
- For casual queries like "what's hot on GitHub?", default to fetching all three ranges
- For specific requests like "show me trending Python repos this week", fetch only that combination
- If the user asks to compare time ranges, show all three side by side
