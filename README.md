# TVQA Dataset Utilities

This repository provides the original TVQA JSONL QA files alongside helper scripts
for converting them into a LongTVQA-style JSON schema.

## Data files

- `tvqa_train.jsonl` — training split (122,039 QAs)
- `tvqa_val.jsonl` — validation split (15,253 QAs)
- `tvqa_test_public.jsonl` — test-public split (7,623 QAs, no labels)
- `tvqa_subtitles.json` — clip-level subtitle text indexed by `vid_name`

Each JSONL line is a QA item with keys such as `qid`, `q`, `a0`-`a4`, `answer_idx` (train/val
only), `ts` (string range), `vid_name`, and `show_name`.

## Scripts

### `scripts/convert_tvqa_qa.py`

Converts a TVQA JSONL file into a LongTVQA-style QA JSON list.

- Converts `ts` from a string range to a `[start, end]` float list.
- Maps `answer_idx` into `answer` (`"a0"`-`"a4"`).
- Adds `episode_name` and `occur_clip` fields based on `vid_name`.
- Keeps `show_name` for reference.

Example:

```bash
python scripts/convert_tvqa_qa.py \
  --input tvqa_train.jsonl \
  --output outputs/LongTVQA_train.json
```

If you want to keep show prefixes inside `episode_name` (e.g. `friends_s01e01`),
add `--episode-with-show-prefix`.

### `scripts/build_tvqa_subtitles.py`

Generates clip-level and episode-level subtitle JSON files.

- Clip-level output is a normalized copy of the input JSON.
- Episode-level output concatenates clips in order and inserts clip markers
  like `<seg01_clip_00>`.

Example:

```bash
python scripts/build_tvqa_subtitles.py \
  --input tvqa_subtitles.json \
  --output-clip outputs/LongTVQA_subtitle_clip_level.json \
  --output-episode outputs/LongTVQA_subtitle_episode_level.json
```

Use `--episode-with-show-prefix` to include show prefixes in `episode_name` keys
when present.
