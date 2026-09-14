# Prompt: Gemini concept art for The Vet Visit (Pluto's past)

Paste everything below the line into a fresh Claude Code session opened in
`/Users/bogdanionescu/Claude Code Projects/Enter the gungeon pluto mod`.

---

You are working on **Pluto the Cat**, an Enter the Gungeon character mod (BepInEx + Alexandria CharacterAPI, C#, Mono
msbuild, hand-drawn pixel art generated from ASCII row-strings in Python). Pluto's custom past, **The Vet Visit**, lives
in the standalone sub-project `PlutoVetVisit/` (own git repo). Your job in this session is **concept art only**: use the
most capable Gemini image model available through the `image-generation` skill to produce a set of painted reference
images that show how the finished past level should look, so that a later session can hand-draw the real pixel art and
build the room from them. You will not write game code and you will not produce sprites.

## Read first (all paths relative to the repo root)

1. `PlutoVetVisit/docs/prompts/gemini-past-concept-prompt.md` (this brief, if present)
2. `docs/superpowers/specs/2026-09-14-vet-visit-v2-design.md` - the three-act level design (story, cast, room, props)
3. `docs/superpowers/specs/2026-09-13-vet-visit-past-design.md` - v1 spec: the clinic look, the Vet boss, the win picture
4. `docs/research/04a-vanilla-pasts-structure.md` - how the six vanilla pasts are built (one big hand-made room, zones)
5. `docs/research/03b-etg-vanilla-sprite-conventions.md` and `docs/research/03a-pixel-art-craft-rules.md` - the vanilla art rules
6. `.claude/skills/pluto-pixel-art/SKILL.md` plus `reference/palette.md` and `reference/specs.md` - Pluto's palette and canvases
7. `PlutoVetVisit/tools/gemini_art.py` - the existing Gemini wrapper (prompt list, output dir, how the CLI is called)
8. `PlutoVetVisit/tools/clinic_room.py` and `PlutoVetVisit/tools/clinic_objects.py` - the current 26x18 room and its props
9. `PlutoVetVisit/tools/vetpixel.py` - the clinic palette (exact hex values for scrubs teal, steel, tile white, carrier blue, etc.)

Hard project rules (from the user, do not break them):
- Never edit anything under `PlutoTheCat/`, `tools/`, `thunderstore/`, `build.sh` or `tasks/todo.md`. Work only inside
  `PlutoVetVisit/` and its `docs/`.
- Generated images are **references only**. The user compared Gemini sprites with hand-drawn ones and chose hand-drawn.
  Do not pixelize generations into sprites, do not put any generated PNG into `Resources/`, do not touch the row-string art.
- The Gemini key is `GEMINI_API_KEY` in the environment (also in `PlutoVetVisit/.env`). Never print it.
- Existing outputs in `PlutoVetVisit/reference/gemini/` are skipped unless `--force`; put the new set in
  `PlutoVetVisit/reference/gemini/past_concepts/` and do not overwrite the boss card / win pic / icon already there.

## What to build

Extend `PlutoVetVisit/tools/gemini_art.py` (or add `PlutoVetVisit/tools/gemini_past_concepts.py` reusing its `Prompt`
class and CLI call) with the prompt set below, run it, then write `PlutoVetVisit/docs/past-concepts.md`: a contact sheet
page that embeds every image with its intended use and a short list of what the pixel-art session should copy from it
and what it should ignore. Use the best Gemini image model the skill exposes (the newest "pro" image model, not the
flash tier); if the skill has a model flag, set it explicitly and log which model produced each file. Generate at the
largest size the model allows and keep the raw PNGs. Do at least two candidates for the three full-level images and
keep the better one, noting why in the doc.

## The level (what every image must agree on)

**Story.** Pluto, a chunky tabby-and-white cat, was taken to the vet to be neutered. That is his regret. The past
replays that day and lets him fight his way out. Three acts in ONE big room, 30 x 52 cells, zones stacked south to
north, sealed by a sliding clinic door that opens when the zone is cleared (like the Marine's Primerdyne lab past).

1. **Waiting room (south, no combat).** Pluto's blue plastic carrier by a row of plastic chairs. A reception desk with
   the Receptionist behind it, a computer, a bell, a jar of treats. Patients waiting: Rex, the neighbour's dog, trembling
   on a chair; Grandma Cat, ancient and unimpressed, in a loaf; a chick, a rabbit and a squirrel loose on the floor.
   A wall TV, a potted plant, a fish tank, a clock, a "wet floor" sign, posters, a floor mat with paw prints, a window
   with daylight. The Owner (hoodie, jeans) sets the carrier down and leaves.
2. **The ward (middle, two enemy waves).** Kennel cages along both long walls (open and closed variants, some with
   patients in cones), a nurse station in the middle with a treat jar and two cat-food bowls, a "PREP" sign, an
   X-ray light box, a medicine shelf, an IV stand, a sharps bin, side doors the Vet Techs come out of. Vet Techs:
   humans in teal scrubs with a syringe pistol. The Nurse: twice a Tech's size, cap, shotgun-sized syringe.
3. **Operating theatre (north, boss).** A big overhead surgical lamp, a steel exam table with straps, monitor cart,
   vaccine fridge, glass cabinets with jars and syringe boxes, sink counter, pet scale, anatomy poster, a cone of
   shame, syringe tray on a cart, scattered cat toys (toy mouse, ball, feather wand, small scratching post). The Vet
   waits behind the table: tall, slightly sinister, white coat over teal scrubs, round glasses catching the light,
   dark hair, one gloved hand holding an enormous syringe of glowing blue liquid.

**Mood.** Bright, clinical, clean white and pale grey tiles, teal and steel accents, a single pink-red tint in the
ambient light like the Primerdyne lab (the lab's ambient light is (0.91, 0.64, 0.64)); friendly on the surface,
faintly menacing (syringes everywhere, straps on the table, cones). Grim humour, not gore. No blood.

**Pluto's look (for any image he appears in).** Chunky tabby-and-white cat: grey-brown taupe tabby (#8B7A66 base,
#B4A180 light, #66524A shadow), near-black mackerel bars, forehead "M", tabby mask around the eyes, white blaze between
the eyes down to a white muzzle, a small white oval on the crown surrounded by tabby, big pink ears, hazel-green eyes
with slit pupils, ringed tail. Clinic palette to reuse in every image: scrubs teal #3F9E8F / dark #2C7367, steel
#3A3F4A / #8C94A2 / #C9CFD8, tile white #F4F6F8 / shade #DCE0E6, carrier blue #6F8FBF / #4A6390, syringe liquid
#4FA8E8, medical red #D83A3A, plastic orange #F08A24, plastic yellow #F5D547, wood #A97B4F / #7A5A3A.

## How Enter the Gungeon looks (put this style block, adapted, in every prompt)

- **Camera:** fixed top-down three-quarter view. Floors are seen from above; walls are seen as a thin dark top strip
  plus a vertical face about 2 tiles tall on the north wall; the south wall shows only its top edge. Characters and
  props stand upright on the floor as if drawn from the front, casting a small soft ellipse shadow at their feet. No
  vanishing-point perspective, no camera tilt, no isometric angle.
- **Scale:** 16 pixels = one game unit = one floor tile. A Gungeoneer is about 15 px wide and 22 px tall (about 1.4
  tiles), a boss 2 to 4 tiles tall, a chair or cabinet 1 to 2 tiles. Every image must respect these proportions so the
  layout can be read straight into a 30 x 52 cell map.
- **Pixel-art rendering:** crisp hard-edged pixels, no anti-aliasing, no gradients, no dithering, no blur, no
  photographic texture. Flat cel shading: each material has two or three tones (base, cooler-greyer shadow, warmer
  highlight), one shadow shape per mass from a top-left light. 8 to 15 colours per character, a small controlled
  palette per scene. Characters and enemies have a crisp 1-px black outline; floor tiles and wall faces do not.
- **Character design language:** big heads (head about half the body height), 1-px stick legs, tiny 1-px dot eyes or
  simple black eyes, small hands, chunky readable silhouettes, exaggerated props (oversized syringes and guns).
  Enemies read at a glance from their silhouette and one accent colour.
- **Room language:** rooms are rectangles of tiles with chunky wall borders, sometimes diagonal corners. Decor sits
  on the floor as separate props (tables, cabinets, chairs, plants, crates) that block movement; small decor
  (toys, papers, mats) is flat and walkable. Pits are dark holes with a rim. Doors are gaps in the wall with a door
  frame. Boss rooms are big open floors with props around the edge, never in the middle of the arena.
- **Reference the real thing:** the look of the Marine's past (Primerdyne R&D lab: white tile floor, glass,
  steel, computers, lab benches, scientists) is the closest vanilla room, and Bullet Kin / Hegemony soldier are the
  closest vanilla enemy shapes. Say "in the style of Enter the Gungeon (Dodge Roll Games, 2016), Primerdyne lab past"
  in every prompt.
- **Always:** no text, no letters, no logos, no watermark, no UI, no borders, subject fills the frame.

## The image set (name, aspect, what it must show)

Level maps (top-down, whole room, one tile grid consistent throughout, walls drawn as in the game):
1. `level_overview` 9:16 - the full 30 x 52 room as one image, three zones south to north with the two sliding doors
   between them, Pluto's carrier at the bottom, the Vet behind the table at the top. Pluto standing beside the carrier
   for scale.
2. `zone1_waiting_room` 4:3 - the south zone alone, every prop above visible, all NPCs and critters in place.
3. `zone2_ward` 4:3 - the middle zone alone, kennels both sides, nurse station, side doors, three Vet Techs mid-attack.
4. `zone3_theatre` 4:3 - the north zone alone as a boss arena: open floor, lamp overhead, props along the walls,
   the Vet behind the table, the Nurse and two Techs entering from a side door.

Cast sheets (character on a plain mid-grey background, front / side / back standing in one row, a second row with a
walk pose, an attack or "tell" pose and a hit pose; drawn at game proportions as if 32 to 64 px tall then shown big):
5. `cast_vet_tech` 16:9 - teal scrubs, cap, syringe pistol, Bullet-Kin body plan.
6. `cast_nurse` 16:9 - the Tech's design at twice the size, nurse cap, shotgun-sized syringe, a net.
7. `cast_vet_boss` 16:9 - The Vet (existing design, see boss card in `reference/gemini/`), plus his three attack
   tells: aimed booster shot, spray bottle fan, pill-time volley, and the cone-of-shame throw.
8. `cast_owner_receptionist` 16:9 - the Owner (hoodie, jeans, carrying the carrier) and the Receptionist (office
   worker at the desk) side by side.
9. `cast_patients` 16:9 - Rex (trembling dog on a chair), Grandma Cat (grey loaf), a chick, a rabbit and a squirrel;
   two mutant patients wearing cones.

Prop sheets (flat lay, plain mid-grey background, each prop drawn upright as it sits in the top-down room, 1-px outline,
grouped by zone, generous spacing so each can be cropped):
10. `props_waiting_room` 1:1 - carrier (open and closed), row of plastic chairs, reception desk with computer and bell,
    treat jar, wall TV, plant, fish tank, clock, wet-floor sign, floor mat with paw prints, window, posters.
11. `props_ward` 1:1 - kennel cage closed / open / with a cone patient inside, nurse station, PREP sign, X-ray box,
    medicine shelf, IV stand, sharps bin, food bowls, litter box, sliding clinic door closed and open, intercom speaker.
12. `props_theatre` 1:1 - surgical lamp, exam table with straps, monitor cart, vaccine fridge, glass cabinet with
    jars, sink counter, pet scale, anatomy poster, cone of shame, syringe tray cart, toy mouse, ball, feather wand,
    scratching post.
13. `tiles_and_walls` 1:1 - a tileset study: the white tile floor (plain, drain, paw-print, cracked variants), the
    north wall face with skirting, the wall top strip, a corner, the door gap with frame, a floor-to-wall shadow line.

Story beats (16:9 painted in-game screenshots, camera letterboxed like a cutscene, still in the top-down game view):
14. `beat_intro` - the Owner setting the carrier down by the chairs, Receptionist looking up, Rex shaking.
15. `beat_ward_fight` - Pluto with his kibble gun dodge-rolling past a kennel while Techs fire syringes.
16. `beat_boss_intro` - the Vet behind the table under the lamp, syringe raised, Pluto hissing in the doorway.
17. `beat_victory` - Pluto smug on the table, the Vet flat on the floor, the cone kicked into a corner (matches the
    existing win picture, keep it consistent).

## Prompt writing rules for you

- Every prompt starts with the style block, then the scene, then the negative list. Spell out the palette hexes for
  the key materials. State the tile grid and the character height in tiles. Say "no text" twice.
- For maps, tell the model the room is a tall rectangle of white tiles with a dark chunky wall border and that the
  two zone doors are on the centre line.
- For sheets, ask for a neutral flat grey (#6C6C7A) background, equal spacing, nothing overlapping.
- Keep the Vet's look identical to `reference/gemini/vet_bosscard_raw.png`: if the skill supports a reference image,
  attach it for every image that shows him.
- After generation, view each image, reject anything with perspective tilt, gradients, text, or wrong proportions,
  and regenerate with a tightened prompt (log the change). Two rounds maximum per image.

## Deliverables

1. New prompt script under `PlutoVetVisit/tools/`, runnable with `--dry-run`, `--only NAME` and `--force`.
2. All PNGs in `PlutoVetVisit/reference/gemini/past_concepts/`, plus a downscaled contact sheet
   `PlutoVetVisit/docs/past-concepts-sheet.png`.
3. `PlutoVetVisit/docs/past-concepts.md`: every image embedded, the model used, the final prompt text, what the pixel
   session should take from it (layout, prop positions, silhouettes, palette) and what to ignore (rendering noise,
   any perspective, any text).
4. A proposed 30 x 52 ASCII zone layout draft in that doc, derived from the level_overview image (walls `#`, floor `.`,
   door gaps `D`, prop initials), as a starting point for `tools/clinic_room.py` in the next session.
5. Commit inside `PlutoVetVisit/` only, message "docs: Gemini concept set for the three-zone past". Do not push.

Do not start building the level, sprites or code in this session. When done, give the user a short summary with the
paths and the two or three images you think are strongest.
