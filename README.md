# The Vet Visit — Pluto's custom past (standalone project)

Developed separately from `../PlutoTheCat`; merged into it only when finished (see
`../docs/superpowers/specs/2026-09-13-vet-visit-past-design.md`). Build with `./build.sh`; tests with
`python3 -m unittest discover -s tools/tests -v`. Gemini art: put `GEMINI_API_KEY=...` in `.env` here
or export it in `~/.zshenv`, then `python3 tools/gemini_art.py`.

Gemini outputs land in `reference/gemini/` and are checked in; existing files are skipped unless you
pass `--force`. `python3 tools/gemini_art.py --dry-run` prints the generation plan without calling the
CLI. To redo a single piece after tweaking its prompt in `tools/gemini_art.py`, run
`python3 tools/gemini_art.py --force --only <name>` (e.g. `--only vet_bosscard_raw.png`), then
`python3 tools/make_art.py` to rebuild the boss card, win picture and icon from the new reference.
