#!/usr/bin/env python3
"""Collect public TikTok metadata and transcripts through Scrape Creators.

This intentionally stores source URLs and API responses, not downloaded media.
Frame-level analysis belongs in a separately authorized media-analysis stage.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.scrapecreators.com"
DEFAULT_TERMS = (
    "app", "download", "link in bio", "use code", "sponsored", "ad", "partner",
    "affiliate", "available on ios", "available on android", "google play",
    "app store", "mobile app",
)


def request_json(path: str, params: dict[str, str], api_key: str, timeout: int = 45) -> dict:
    query = urlencode({key: value for key, value in params.items() if value != ""})
    request = Request(
        f"{BASE_URL}{path}?{query}",
        headers={"x-api-key": api_key, "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Scrape Creators returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Scrape Creators request failed: {exc.reason}") from exc


def first_video_id(video: dict) -> str:
    return str(video.get("aweme_id") or video.get("id") or "")


def video_url(video: dict) -> str:
    author = video.get("author") or {}
    handle = author.get("unique_id") or author.get("uniqueId") or ""
    identifier = first_video_id(video)
    return f"https://www.tiktok.com/@{handle}/video/{identifier}" if handle and identifier else ""


def text_for_filter(video: dict, detail: dict, transcript: dict) -> str:
    values = [video.get("desc"), detail.get("desc"), detail.get("caption")]
    values.append(transcript.get("transcript") or transcript.get("text"))
    values.append(json.dumps(video.get("anchors", []), ensure_ascii=False))
    return " ".join(str(value) for value in values if value).lower()


def looks_promotional(video: dict, detail: dict, transcript: dict, terms: tuple[str, ...]) -> tuple[bool, list[str]]:
    searchable = text_for_filter(video, detail, transcript)
    matched = sorted({term for term in terms if re.search(rf"\b{re.escape(term)}\b", searchable)})
    anchors = video.get("anchors") or detail.get("anchors") or []
    if anchors:
        matched.append("tiktok_anchor")
    return bool(matched), matched


def collect(args: argparse.Namespace) -> dict:
    api_key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not api_key:
        raise RuntimeError("SCRAPECREATORS_API_KEY is required and must not be committed")

    profile = request_json("/v1/tiktok/profile", {"user_id": args.user_id, "cache_max_age": "7d"}, api_key)
    videos: list[dict] = []
    cursor = ""
    while len(videos) < args.max_candidates:
        page = request_json(
            "/v3/tiktok/profile/videos",
            {"user_id": args.user_id, "sort_by": "popular", "region": args.region, "max_cursor": cursor},
            api_key,
        )
        batch = page.get("aweme_list") or page.get("videos") or []
        if not batch:
            break
        videos.extend(batch)
        next_cursor = str(page.get("max_cursor") or "")
        if not page.get("has_more") or not next_cursor or next_cursor == cursor:
            break
        cursor = next_cursor

    records = []
    for index, video in enumerate(videos[: args.max_candidates], start=1):
        url = video_url(video)
        if not url:
            continue
        detail = request_json("/v2/tiktok/video", {"url": url, "get_transcript": "false", "region": args.region}, api_key)
        transcript = {}
        if args.transcripts:
            transcript = request_json("/v1/tiktok/video/transcript", {"url": url}, api_key)
        promotional, matched_terms = looks_promotional(video, detail, transcript, tuple(args.term))
        records.append({
            "rank": index,
            "source_url": url,
            "creator_id": args.user_id,
            "region_proxy": args.region,
            "promotional_candidate": promotional,
            "promotion_signals": matched_terms,
            "metadata": video,
            "detail": detail,
            "transcript": transcript,
            "analysis_status": "needs_frame_analysis" if promotional else "filtered_out",
        })
        if args.delay:
            time.sleep(args.delay)

    return {
        "schema_version": "tiktok-recreation-research.v1",
        "creator_id": args.user_id,
        "region": args.region,
        "requested_candidates": args.max_candidates,
        "records": records,
        "notes": [
            "Promotion detection is heuristic and requires human review.",
            "This artifact contains metadata/transcripts and source URLs; it does not copy media.",
            "Frame-level analysis must be performed only where media-use rights permit it.",
        ],
        "profile": profile,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user-id", required=True, help="TikTok numeric user ID")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON path")
    parser.add_argument("--region", default="US", help="Proxy/collection region (default: US)")
    parser.add_argument("--max-candidates", type=int, default=1000)
    parser.add_argument("--delay", type=float, default=0.0, help="Delay between detail requests")
    parser.add_argument("--transcripts", action="store_true", help="Fetch transcript per video")
    parser.add_argument("--term", action="append", default=list(DEFAULT_TERMS), help="Extra promotion term")
    args = parser.parse_args()
    if args.max_candidates < 1:
        parser.error("--max-candidates must be positive")
    try:
        result = collect(args)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"Wrote {len(result['records'])} records to {args.output}")
        return 0
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
