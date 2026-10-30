# AI Avatar Presenter Video Series

Turns plain-text scripts into a series of avatar-presenter videos using the HeyGen API.

## Setup
```bash
pip install -r requirements.txt
cp .env.example .env        # add HEYGEN_API_KEY
python cli.py list-avatars  # pick avatar_id
python cli.py list-voices   # pick voice_id
# put both in series.yaml
```

## Usage
```bash
python cli.py generate --dry-run   # validate scripts, write payload JSON
python cli.py generate             # render all episodes
python cli.py generate ep01        # one episode
python cli.py generate --force     # re-render
```

## Adding episodes
1. Write `scripts/ep03.txt` — one paragraph per scene (blank line between).
2. Add an entry under `episodes:` in `series.yaml`.

Videos land in `output/`. `output/manifest.json` records video IDs, so an interrupted run resumes without paying twice.

## Notes
- Scene text limit: 5000 chars. Free/trial plans may restrict resolution and duration.
- To use another provider (D-ID, Synthesia), add a client beside `heygen.py` exposing the same methods.
