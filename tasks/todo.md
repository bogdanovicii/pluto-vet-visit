# Task 6: Clinic prop art (ASCII) and placements

## Plan
- [x] Step 1: Write failing tests `tools/tests/test_objects.py` (verbatim from brief)
- [x] Step 2: Run tests, confirm RED (OBJECTS empty)
- [x] Step 3: Replace `tools/clinic_objects.py` with brief's art module (verbatim; extracted via sed from the brief to guarantee byte-exact ASCII/backslash content — no row-width bugs found, R() passed clean on first run)
- [x] Step 4: Wire `tools/make_art.py` and `tools/validate.py`
- [x] Step 5: Run tests GREEN (18/18); run make_art.py; inspected both previews (wide + heavy zoom crops) with Read tool — all 13 props read clearly with dark outlines; no ASCII changes needed
- [x] Step 6: `./build.sh` -> 13 object sprites / room 26x18, 19 placeables / all checks passed / 0 errors; committed
- [x] Self-review + write task-6-report.md

## Review
All steps completed with no deviations from the brief. TDD loop: RED (test_registry + test_furniture_blocks_and_decor_does_not
failing on empty OBJECTS) -> GREEN (18/18 after pasting the brief's clinic_objects.py verbatim, no art bugs found) -> wired
make_art.py/validate.py -> regenerated art/room/previews -> visually verified -> build.sh clean -> committed.
No ASCII art needed adjustment; the brief's hand-drawn maps were all rectangular and used only palette keys already
defined (either in vetpixel's clinic additions or the main mod's base PALETTE, e.g. 'o'/'K'/'B'/'W'/'Z'/'H'/'e').
See task-6-report.md for full detail.
