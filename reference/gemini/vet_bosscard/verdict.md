# vet_bosscard verdict (2026-09-14): PASS

- Source: vet_bosscard_c2.png (Gemini, 3 candidates), converted with tools/build_art.py (crop 0.36-1.0, grid 232x229 at (193,6), 38 colours, 1E1614 outline, chroma fringe removed: 206 px).
- review_art.py: 37 colours, 22.8 % opaque, 0 stray. Its one FAIL, "opaque pixels right of x=192", is the PLAYER card rule; this is boss art, which belongs there (targets.md: boss art lives in the right half).
- Style: bold near-black outline, 3-4 cel tones per material (coat, scrubs, skin, syringe), light from the top-left; sits next to vanilla Beholster-style art.
- Composition: full figure in the right half, closed silhouette, x < 190 transparent (art_sources check), lunging toward Pluto's card with the syringe pistol and scalpel.
- Pixel craft: alpha 0/255, no chroma fringe after cleanup, eyes/glasses/teeth read at 1x.
