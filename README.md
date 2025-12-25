# LongTVQA Dataset Files

This repository contains the LongTVQA dataset exports as JSON-formatted files.
Despite the `.jsonl` suffix, the QA splits are stored as a JSON array, and the
subtitle files are JSON objects.

## Data files

- `LongTVQA_train.jsonl` — training split QA list.
- `LongTVQA_val.jsonl` — validation split QA list.
- `LongTVQA_subtitles_clip_level.jsonl` — clip-level subtitle text indexed by
  `occur_clip` (e.g. `castle_s01e01_seg02_clip_00`).
- `LongTVQA_subtitles_episode_level.jsonl` — episode-level subtitle text indexed by
  `episode_name` (e.g. `castle_s01e01`).

## Subtitle file examples

Clip-level subtitles map clip ids to a single subtitle string:

```json
"castle_s01e01_seg02_clip_00": "(Kath...)"
```

Episode-level subtitles map episode ids to a string that concatenates clips with
segment markers:

```json
"castle_s01e01": "<seg02_clip_00>xxx</seg02_clip_00>xxx"
```

## QA item schema

Each entry in the train/val arrays is a QA item with keys such as:

- `qid`: integer question id.
- `q`: question text.
- `a0`-`a4`: answer options.
- `answer`: correct option key (`"a0"`-`"a4"`).
- `ts`: `[start, end]` float list of the temporal span.
- `episode_name`: episode identifier (e.g. `grey_s03e20`).
- `occur_clip`: clip identifier (e.g. `grey_s03e20_seg02_clip_14`).
- `show_name`: show title.
