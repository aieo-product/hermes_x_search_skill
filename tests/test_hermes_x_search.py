"""Smoke tests for hermes_x_search wrapper (no Hermes invocation required)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Make the script importable
SCRIPT_DIR = Path(__file__).resolve().parent.parent / "skills" / "hermes-x-search" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import hermes_x_search as hxs  # noqa: E402


class TestParseArgs:
    def test_requires_query_or_user(self):
        with pytest.raises(SystemExit):
            hxs.parse_args([])

    def test_user_strips_at_sign(self):
        a = hxs.parse_args(["--user", "@example"])
        assert a.user == "example"
        a2 = hxs.parse_args(["--user", "example"])
        assert a2.user == "example"

    def test_count_range(self):
        with pytest.raises(SystemExit):
            hxs.parse_args(["--user", "x", "--count", "0"])
        with pytest.raises(SystemExit):
            hxs.parse_args(["--user", "x", "--count", "100"])
        a = hxs.parse_args(["--user", "x", "--count", "5"])
        assert a.count == 5

    def test_default_output_is_md(self):
        a = hxs.parse_args(["--user", "x"])
        assert a.output == "md"

    def test_invalid_output_rejected(self):
        with pytest.raises(SystemExit):
            hxs.parse_args(["--user", "x", "--output", "csv"])


class TestBuildPrompt:
    def test_includes_user(self):
        a = hxs.parse_args(["--user", "example"])
        p = hxs.build_prompt(a)
        assert "@example" in p
        assert "X (Twitter) Search tool" in p

    def test_includes_query(self):
        a = hxs.parse_args(["--query", "hello world"])
        p = hxs.build_prompt(a)
        assert "hello world" in p

    def test_includes_date_range(self):
        a = hxs.parse_args([
            "--user", "x",
            "--since", "2026-05-01",
            "--until", "2026-05-10",
        ])
        p = hxs.build_prompt(a)
        assert "2026-05-01" in p
        assert "2026-05-10" in p

    def test_forces_json_schema(self):
        a = hxs.parse_args(["--user", "x"])
        p = hxs.build_prompt(a)
        assert '"results"' in p
        assert '"query_summary"' in p
        assert "x_search_unavailable" in p


class TestExtractJson:
    def test_clean_json(self):
        out = hxs.extract_json('{"results": [], "query_summary": "ok"}')
        assert out == {"results": [], "query_summary": "ok"}

    def test_json_with_preamble(self):
        text = 'Some preamble text...\n{"results": [{"a": 1}], "query_summary": "x"}\nThanks!'
        out = hxs.extract_json(text)
        assert out is not None
        assert out["results"] == [{"a": 1}]

    def test_unparseable(self):
        assert hxs.extract_json("just a sentence") is None
        assert hxs.extract_json("") is None

    def test_nested_objects(self):
        text = '{"results": [{"meta": {"k": 1}}], "query_summary": "x"}'
        out = hxs.extract_json(text)
        assert out["results"][0]["meta"]["k"] == 1


class TestClassifyFailure:
    def test_auth_keywords(self):
        for kw in ("not authenticated", "OAuth", "Unauthorized", "login required"):
            assert hxs.classify_failure("", kw) == 10

    def test_rate_limit(self):
        for kw in ("rate limit exceeded", "Too Many Requests", "HTTP 429"):
            assert hxs.classify_failure("", kw) == 12

    def test_x_search_unavailable(self):
        assert hxs.classify_failure('{"error": "x_search_unavailable"}', "") == 11

    def test_clean_output(self):
        assert hxs.classify_failure('{"results": [{}]}', "") == 0


class TestRenderMarkdown:
    def test_empty_results(self):
        md = hxs.render_markdown(
            {"results": [], "query_summary": "no hits"},
            hxs.parse_args(["--user", "x"]),
        )
        assert "No matching" in md
        assert "no hits" in md

    def test_table_render(self):
        md = hxs.render_markdown(
            {
                "results": [
                    {
                        "url": "https://x.com/u/status/1",
                        "author": "@u",
                        "posted_at": "2026-05-18T01:00:00Z",
                        "text": "hello",
                    }
                ],
                "query_summary": "found 1",
            },
            hxs.parse_args(["--user", "u"]),
        )
        assert "| # |" in md
        assert "@u" in md
        assert "https://x.com/u/status/1" in md

    def test_pipe_in_text_is_escaped(self):
        md = hxs.render_markdown(
            {
                "results": [
                    {"url": "u", "author": "a", "posted_at": "t", "text": "has|pipe"}
                ],
                "query_summary": "",
            },
            hxs.parse_args(["--user", "u"]),
        )
        assert "has\\|pipe" in md
