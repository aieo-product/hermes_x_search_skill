#!/usr/bin/env python3
"""Wrapper that invokes `hermes -z` to perform an X (Twitter) search via
Hermes Agent's built-in X Search tool, then prints structured results.

Exit codes:
    0   success (results returned, possibly empty)
    1   generic / unexpected error
    2   argument error
    10  Hermes authentication missing or expired
    11  X Search tool not enabled
    12  upstream rate limit
    13  Hermes returned unparseable output (raw response printed to stderr)

Typical usage:
    hermes_x_search.py --user otani_ai_memo --count 5
    hermes_x_search.py --query '"Claude Code" lang:ja' --count 20 --output json
    hermes_x_search.py --user nousresearch --query Hermes --since 2026-05-01
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


HERMES_TIMEOUT_SECONDS = 180
MAX_COUNT = 50


@dataclass
class SearchArgs:
    query: Optional[str]
    user: Optional[str]
    count: int
    since: Optional[str]
    until: Optional[str]
    output: str
    hermes_bin: str
    debug: bool


def parse_args(argv: list[str]) -> SearchArgs:
    p = argparse.ArgumentParser(
        prog="hermes_x_search",
        description="Search X (Twitter) via Hermes Agent's X Search tool.",
    )
    p.add_argument("--query", "-q", help="Search keywords. Wrap phrases in quotes.")
    p.add_argument("--user", "-u", help="Target user handle (with or without @).")
    p.add_argument(
        "--count",
        "-n",
        type=int,
        default=10,
        help=f"Number of results (1-{MAX_COUNT}). Default: 10.",
    )
    p.add_argument("--since", help="Start date (ISO 8601 / YYYY-MM-DD).")
    p.add_argument("--until", help="End date (ISO 8601 / YYYY-MM-DD).")
    p.add_argument(
        "--output",
        "-o",
        choices=("md", "json"),
        default="md",
        help="Output format: md (Markdown table) or json. Default: md.",
    )
    p.add_argument(
        "--hermes-bin",
        default=os.environ.get("HERMES_BIN", "hermes"),
        help="Path to hermes binary. Default: hermes (from PATH) or $HERMES_BIN.",
    )
    p.add_argument(
        "--debug",
        action="store_true",
        help="Print the prompt sent to Hermes and raw response to stderr.",
    )

    ns = p.parse_args(argv)

    if not ns.query and not ns.user:
        p.error("at least one of --query or --user is required")
    if not (1 <= ns.count <= MAX_COUNT):
        p.error(f"--count must be between 1 and {MAX_COUNT}")

    user = ns.user.lstrip("@") if ns.user else None

    return SearchArgs(
        query=ns.query,
        user=user,
        count=ns.count,
        since=ns.since,
        until=ns.until,
        output=ns.output,
        hermes_bin=ns.hermes_bin,
        debug=ns.debug,
    )


def build_prompt(args: SearchArgs) -> str:
    """Build a prompt that (a) forces the X Search tool to fire and (b) asks
    for a JSON-shaped response, with natural-language framing in front so the
    model does not shortcut to an empty schema-conformant reply."""

    parts = []
    if args.user and args.query:
        parts.append(f"posts by @{args.user} that match the query: {args.query}")
    elif args.user:
        parts.append(f"the most recent posts by @{args.user}")
    elif args.query:
        parts.append(f"posts matching the query: {args.query}")

    if args.since:
        parts.append(f"posted on or after {args.since}")
    if args.until:
        parts.append(f"posted on or before {args.until}")
    parts.append(f"return up to {args.count} matching posts")

    request = "Please find " + ", ".join(parts) + "."

    return (
        f"{request}\n\n"
        "YOU MUST call the X (Twitter) Search tool to fulfil this request. "
        "Use ONLY the X (Twitter) Search tool — do not call any other tools, "
        "and do not answer from your own knowledge. "
        "Do NOT return an empty result without first calling the tool — "
        "if the tool returns nothing, then an empty list is acceptable, but a "
        "skipped tool call is not.\n\n"
        "After the tool returns, format your final reply as a SINGLE JSON object "
        "(no markdown fences, no prose around it) with this schema:\n"
        "{\n"
        '  "results": [\n'
        '    {\n'
        '      "url":       "https://x.com/<user>/status/<id>",\n'
        '      "author":    "@handle",\n'
        '      "posted_at": "ISO 8601 timestamp if available, else the relative time",\n'
        '      "text":      "full post text",\n'
        '      "likes":     <integer or null>,\n'
        '      "reposts":   <integer or null>,\n'
        '      "views":     <integer or null>,\n'
        '      "media":     [{"type": "photo|video|gif", "url": "<media URL>"}, ...]\n'
        '    }\n'
        '  ],\n'
        '  "query_summary": "one-sentence description of what was searched"\n'
        "}\n\n"
        "For the `media` field: if the post has attached images, videos, or GIFs, "
        "include every media URL the X Search tool returned (best-effort — if the "
        "tool gives no media info for a post, set `media` to an empty list `[]`). "
        "Use `photo` for still images, `video` for videos, `gif` for animated GIFs. "
        "Do NOT fabricate media URLs.\n\n"
        "If the X (Twitter) Search tool is not available in this Hermes instance, "
        'respond ONLY with: {"error": "x_search_unavailable"}.'
    )


def run_hermes(args: SearchArgs) -> tuple[int, str, str]:
    """Run hermes -z and return (exit_code, stdout, stderr)."""
    if not shutil.which(args.hermes_bin) and not os.path.isfile(args.hermes_bin):
        print(
            f"error: hermes binary not found ({args.hermes_bin}). "
            "Install: https://github.com/NousResearch/hermes-agent",
            file=sys.stderr,
        )
        sys.exit(1)

    prompt = build_prompt(args)
    if args.debug:
        print("=== PROMPT TO HERMES ===", file=sys.stderr)
        print(prompt, file=sys.stderr)
        print("=== END PROMPT ===", file=sys.stderr)

    cmd = [args.hermes_bin, "-z", prompt]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=HERMES_TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(
            f"error: hermes did not respond within {HERMES_TIMEOUT_SECONDS}s",
            file=sys.stderr,
        )
        sys.exit(1)

    return result.returncode, result.stdout, result.stderr


def extract_json(text: str) -> Optional[dict]:
    """Pull a JSON object out of text, tolerating leading/trailing prose."""
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Locate the outermost {...} candidate.
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def classify_failure(stdout: str, stderr: str) -> int:
    """Inspect Hermes output for known failure modes; return exit code or 0."""
    combined = (stdout + "\n" + stderr).lower()
    if "x_search_unavailable" in combined:
        return 11
    if any(s in combined for s in ("not authenticated", "login required", "oauth", "unauthorized")):
        return 10
    if any(s in combined for s in ("rate limit", "rate-limit", "too many requests", "429")):
        return 12
    return 0


def render_markdown(parsed: dict, args: SearchArgs) -> str:
    results = parsed.get("results", [])
    summary = parsed.get("query_summary", "")
    lines = []
    if summary:
        lines.append(f"> {summary}")
        lines.append("")
    if not results:
        lines.append("_No matching posts found._")
        return "\n".join(lines)

    lines.append("| # | 日時 | 投稿者 | 本文 | メディア | リンク |")
    lines.append("|---|------|--------|------|---------|--------|")
    for i, r in enumerate(results, 1):
        text = (r.get("text") or "").replace("\n", " ").replace("|", "\\|")
        if len(text) > 140:
            text = text[:137] + "..."
        media_cell = _format_media_cell(r.get("media") or [])
        lines.append(
            f"| {i} | {r.get('posted_at', '')} | {r.get('author', '')} | "
            f"{text} | {media_cell} | [link]({r.get('url', '')}) |"
        )
    return "\n".join(lines)


def _format_media_cell(media: list) -> str:
    """Render the media list as a compact Markdown cell.

    Each entry becomes either an inline image (for photos) or a typed link
    (for video/gif). Returns "-" when the list is empty so the table stays
    readable.
    """
    if not media:
        return "-"
    parts = []
    for idx, m in enumerate(media, 1):
        url = (m.get("url") or "").replace("|", "\\|") if isinstance(m, dict) else ""
        if not url:
            continue
        mtype = (m.get("type") or "media").lower() if isinstance(m, dict) else "media"
        if mtype == "photo":
            parts.append(f"![photo{idx}]({url})")
        else:
            parts.append(f"[{mtype}{idx}]({url})")
    return " ".join(parts) if parts else "-"


def main() -> int:
    args = parse_args(sys.argv[1:])
    rc, stdout, stderr = run_hermes(args)

    if args.debug:
        print("=== HERMES STDOUT ===", file=sys.stderr)
        print(stdout, file=sys.stderr)
        print("=== HERMES STDERR ===", file=sys.stderr)
        print(stderr, file=sys.stderr)

    if rc != 0:
        # Only inspect failure-mode keywords when Hermes itself failed.
        # Doing this on the success path would misclassify valid search
        # results that happen to contain words like "OAuth" or "rate limit"
        # (e.g. a query for tweets about authentication).
        classified = classify_failure(stdout, stderr)
        if classified:
            print(f"hermes failed: see stderr for details", file=sys.stderr)
            print(stderr, file=sys.stderr)
            return classified
        print(f"hermes failed (exit {rc})", file=sys.stderr)
        print(stderr, file=sys.stderr)
        return 1

    parsed = extract_json(stdout)
    if parsed is None:
        print("error: could not parse JSON from hermes response", file=sys.stderr)
        print("--- raw response ---", file=sys.stderr)
        print(stdout, file=sys.stderr)
        return 13

    if "error" in parsed:
        # Explicit error sentinel from the prompt contract.
        err = parsed["error"]
        if err == "x_search_unavailable":
            print(
                "error: X Search tool is not enabled in Hermes. "
                "Run `hermes tools` and enable 'X (Twitter) Search'.",
                file=sys.stderr,
            )
            return 11
        print(f"hermes reported error: {err}", file=sys.stderr)
        return 1

    if args.output == "json":
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(parsed, args))

    return 0


if __name__ == "__main__":
    sys.exit(main())
