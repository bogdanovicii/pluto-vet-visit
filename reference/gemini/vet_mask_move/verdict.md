# vet_mask_move verdict (2026-09-14): PASS (hand-copied)

- Gemini sheets (vet_mask_*.png) set the design: white surgical gloves and a pale blue surgical mask under the glasses.
- The direct pixelize conversion failed review (noisy silhouettes, holes, changing proportions, chroma green at the feet;
  see scratchpad review_clips.png). Following pluto-artist ("copy it by hand into rows ... whichever reviews better"),
  the design was copied by hand into the Vet's own row-string frames: tools/vet_poses.py masked_head() / gloved(),
  MASK_CLIPS, written by write_mask_art() to reference/art/vet_mask_move/.
- Review: same 48x40 canvas, hitbox columns and feet row as the in-game clip; outline-free like every AIActor frame (the
  game outlines at runtime); mask reads at 1x; frames match the in-game timing one to one.
