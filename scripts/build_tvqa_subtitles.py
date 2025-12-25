#!/usr/bin/env python3
"""Build clip-level and episode-level subtitle JSON files from TVQA subtitles."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


VID_PATTERN = re.compile(
    r"^(?:(?P<show>[a-z0-9]+)_)?s(?P<season>\d{2})e(?P<episode>\d{2})_seg(?P<seg>\d{2})_clip_(?P<clip>\d{2})$",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ClipInfo:
    show_prefix: Optional[str]
    season: str
    episode: str
    segment: int
    clip: int

    def episode_key(self, include_show_prefix: bool) -> str:
        if include_show_prefix and self.show_prefix:
            return f"{self.show_prefix}_s{self.season}e{self.episode}"
        return f"s{self.season}e{self.episode}"

    def marker(self) -> str:
        return f"<seg{self.segment:02d}_clip_{self.clip:02d}>"


def parse_clip_key(vid_name: str) -> ClipInfo:
    match = VID_PATTERN.match(vid_name)
    if not match:
        raise ValueError(f"Unexpected clip key: {vid_name}")
    return ClipInfo(
        show_prefix=match.group("show"),
        season=match.group("season"),
        episode=match.group("episode"),
        segment=int(match.group("seg")),
        clip=int(match.group("clip")),
    )


def build_episode_subtitles(
    clip_subtitles: dict[str, str], include_show_prefix: bool
) -> dict[str, str]:
    episode_map: dict[str, list[tuple[ClipInfo, str]]] = defaultdict(list)
    for clip_key, subtitle in clip_subtitles.items():
        clip_info = parse_clip_key(clip_key)
        episode_key = clip_info.episode_key(include_show_prefix)
        episode_map[episode_key].append((clip_info, subtitle))

    episode_subtitles: dict[str, str] = {}
    for episode_key, entries in episode_map.items():
        entries.sort(key=lambda item: (item[0].segment, item[0].clip))
        parts = [f"{clip_info.marker()} {subtitle}" for clip_info, subtitle in entries]
        episode_subtitles[episode_key] = " ".join(parts)
    return episode_subtitles


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Input clip-level JSON")
    parser.add_argument(
        "--output-clip",
        type=Path,
        required=True,
        help="Output clip-level JSON path",
    )
    parser.add_argument(
        "--output-episode",
        type=Path,
        required=True,
        help="Output episode-level JSON path",
    )
    parser.add_argument(
        "--episode-with-show-prefix",
        action="store_true",
        help="Include show abbreviation in episode_name when present",
    )
    args = parser.parse_args()

    with args.input.open("r", encoding="utf-8") as handle:
        clip_subtitles = json.load(handle)

    args.output_clip.parent.mkdir(parents=True, exist_ok=True)
    args.output_episode.parent.mkdir(parents=True, exist_ok=True)

    with args.output_clip.open("w", encoding="utf-8") as handle:
        json.dump(clip_subtitles, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    episode_subtitles = build_episode_subtitles(
        clip_subtitles, include_show_prefix=args.episode_with_show_prefix
    )
    with args.output_episode.open("w", encoding="utf-8") as handle:
        json.dump(episode_subtitles, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
