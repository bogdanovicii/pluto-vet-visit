# kennel_open_r_rattle verdict (2026-09-14): PASS (hand-copied)

- Motion design from the Gemini sheets kennel_cat_{idle,react,rattle} and kennel_dog_{idle,react} (the Gemini spending cap
  stopped the other ten sheets; the cone patient and the open kennels reuse the cat and dog moves).
- Direct conversion of a 40x48 kennel would repaint the cage; the motions were copied by hand onto the kennel's own
  occupants instead: tools/clinic_objects.py kennel_frames() (breathe, blink, jump, puff with an open mouth, paw at the door,
  latch jolt), written by write_kennel_art() to reference/art/kennel_open_r_rattle/.
- Review: the cage is pixel-identical across frames (only the animal and the latch change); the first idle frame equals the
  static kennel; motion reads at 1x behind the bars.
