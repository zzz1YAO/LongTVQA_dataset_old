#!/usr/bin/env python3
"""Convert TVQA JSONL QA files to LongTVQA-style JSON."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional


VID_PATTERN = re.compile(
    r"^(?:(?P<show>[a-z0-9]+)_)?s(?P<season>\d{2})e(?P<episode>\d{2})_seg(?P<seg>\d{2})_clip_(?P<clip>\d{2})$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class EpisodeInfo:
    show_prefix: Optional[str]
    season: str
    episode: str

    def episode_key(self, include_show_prefix: bool) -> str:
        if include_show_prefix and self.show_prefix:
            return f"{self.show_prefix}_s{self.season}e{self.episode}"
        return f"s{self.season}e{self.episode}"


def parse_episode(vid_name: str) -> EpisodeInfo:
    match = VID_PATTERN.match(vid_name)
    if not match:
        raise ValueError(f"Unexpected vid_name format: {vid_name}")
    return EpisodeInfo(
        show_prefix=match.group("show"),
        season=match.group("season"),
        episode=match.group("episode"),
    )


def parse_timestamp(ts_value: str) -> list[float]:
    start_str, end_str = ts_value.split("-", maxsplit=1)
    return [float(start_str), float(end_str)]


def convert_record(record: dict, include_show_prefix: bool) -> dict:
    episode_info = parse_episode(record["vid_name"])
    converted = {
        "qid": record["qid"],
        "q": record["q"],
        "a0": record["a0"],
        "a1": record["a1"],
        "a2": record["a2"],
        "a3": record["a3"],
        "a4": record["a4"],
        "ts": parse_timestamp(record["ts"]),
        "episode_name": episode_info.episode_key(include_show_prefix),
        "occur_clip": record["vid_name"],
        "show_name": record.get("show_name"),
    }
    answer_idx = record.get("answer_idx")
    if answer_idx is not None:
        converted["answer"] = f"a{answer_idx}"
    return converted


def load_jsonl(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Input JSONL file")
    parser.add_argument("--output", type=Path, required=True, help="Output JSON file")
    parser.add_argument(
        "--episode-with-show-prefix",
        action="store_true",
        help="Include show abbreviation in episode_name when present",
    )
    args = parser.parse_args()

    converted_records = [
        convert_record(record, include_show_prefix=args.episode_with_show_prefix)
        for record in load_jsonl(args.input)
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(converted_records, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
