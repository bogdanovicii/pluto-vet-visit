# Prompt: The Vet Visit 0.10 — make it play like a vanilla past

> **Historical: session prompt for 0.10.** Superseded by later releases (see `thunderstore/CHANGELOG.md`).

Paste everything below the line into a fresh Claude Code session opened in
`/Users/bogdanionescu/Claude Code Projects/Enter the gungeon pluto mod`.

---

You are working on **Pluto the Cat**, an Enter the Gungeon character mod (BepInEx + Alexandria, C#, Mono msbuild,
hand-drawn pixel art from ASCII row-strings in Python). Pluto's custom past, **The Vet Visit**, is the standalone
sub-project `PlutoVetVisit/` (its own git repo, remote `bogdanovicii/pluto-vet-visit`). The user tested 0.8.0 on the
Steam machine. Verdict: "works but could be improved; much better than before, but it does not look like the Gemini
design". Your job is milestone **0.10.0**: make the past play, look and read like a vanilla past. Another session has
already committed **0.9.0** on top of 0.8.0 (loadout re-check, explicit engage of every spawned enemy, Tech bursts,
greetings, white floor tiles). Start from 0.9.0, do not redo it; verify what it claims and finish what it started.

## Read first (paths relative to the repo root)

1. `PlutoVetVisit/docs/past-concepts.md` and the images in `PlutoVetVisit/reference/gemini/past_concepts/` — the
   Gemini concept set: level overview, three zone maps, cast sheets, prop sheets, tiles-and-walls study, story beats,
   plus a 30 x 52 ASCII zone draft. **This is the look the user wants.** The doc says per image what to copy.
2. `docs/superpowers/specs/2026-09-14-vet-visit-v2-design.md` — the three-act design (story, cast, room, APIs).
3. `PlutoVetVisit/thunderstore/CHANGELOG.md` (0.5.0 to 0.9.0), `PlutoVetVisit/docs/checklist.md` (milestones 5 to 9:
   what was supposed to happen in game), `tasks/vet-visit-todo.md`, `tasks/lessons.md` (read all of it; the last
   entries are about piped build status and the runtime outline).
4. `docs/research/04a-vanilla-pasts-structure.md` and `04b-alexandria-past-building-apis.md` — how vanilla pasts
   sequence their acts, and the exact APIs (AIActor.Spawn, HasBeenEngaged, PastCameraUtility, TextBoxManager,
   EnemyBuilder, ShootBehavior). `docs/research/05-*` for the boss builder.
5. The code: `PlutoVetVisit/src/VetVisitController.cs` (the three acts), `VetTech.cs` (Tech + Nurse), `VetBoss.cs`,
   `VetAttacks.cs`, `ClinicNpc.cs`, `ClinicDoor.cs`, `ClinicObjects.cs`, `PastConfig.cs`; the generators
   `PlutoVetVisit/tools/clinic_room.py`, `clinic_objects.py`, `tech_poses.py`, `nurse_poses.py`, `npc_poses.py`,
   `cast_layout.py`, `vetpixel.py` (palette), `validate.py`, `tests/`.
6. `.claude/skills/pluto-pixel-art/SKILL.md` and its `reference/` — the art rules of the main mod.

Hard rules (from the user):
- Never edit anything under `PlutoTheCat/`, `tools/` (the main mod's), `thunderstore/` at the root, `build.sh` at the
  root, or `tasks/todo.md`. Work only inside `PlutoVetVisit/` and the repo's `docs/` and `tasks/vet-visit-todo.md`.
- Art stays hand-drawn row-strings. Gemini images are references only: never pixelize a generation into a sprite,
  never put a generated PNG into `Resources/`. You MAY generate new reference images for ideas with
  `python3 PlutoVetVisit/tools/gemini_past_concepts.py` (add prompts to its PROMPTS list; model `gemini-3-pro-image`,
  key `GEMINI_API_KEY` in the environment, never print it; outputs under `PlutoVetVisit/reference/gemini/`).
- The game does not run on this Mac. Build with `PlutoVetVisit/build.sh` (check its exit status, never behind a pipe),
  run `python3 -m unittest discover -s PlutoVetVisit/tools/tests -t PlutoVetVisit`, and treat the Steam machine as the
  only real test. Hand-off: copy the zip to `PlutoVetVisit/releases/`, tag + `gh release create`, republish the drop
  page (artifact `https://claude.ai/code/artifact/88955979-ec59-45b0-a1af-8e482aa1dedb`, files `pluto_vet_visit_zip.json`
  = {name, bytes, sha256, encoding:"base64", data}), then message the Steam session (`ListAgents`, name starts with
  `plutosm-`) with the links, sha256 and what to test. Read the artifact before republishing (another session may
  have changed it). Commit inside `PlutoVetVisit/` per milestone; do not push the parent repo.

## What the user saw in 0.8.0 (fix in this order)

1. **Pluto has no gun and cannot shoot.** In the past he arrives unarmed. 0.9.0 added a loadout re-check for a
   minute and a `vet_loadout` console command; verify it against the decompiled source, do not trust the log line.
   Read `PlayerController.ReinitializeGuns`, `GunInventory`, `startingGunIds`, `PastCameraUtility.LockConversation` /
   `SetInputOverride("past")` (the overrides must be cleared: an uncleared "past" or "npcConversation" override leaves
   the player unable to shoot even with a gun), `ToggleGunRenderers` / `ToggleHandRenderers` reasons, and how the
   Convict/Marine past controllers hand back the loadout (`docs/research/04a`). Check that Pluto's gun `pluto:kibble_sack`
   exists at that point (`Game.Items.ContainsID`), that `inventory.ChangeGun` selects it, that no input override remains
   after the intro (log `player.CurrentInputState`, `AcceptingNonMotionInput`, `IsInputOverridden` at the end of every
   act), and that the intro's `finally` runs even when a line throws. Add a watchdog: if 3 s after the intro the player
   has no current gun or input is still overridden, fix it and log why.
2. **The ward staff do nothing: they do not move or shoot.** The Techs are `EnemyBuilder.BuildPrefab` enemies spawned
   with `AIActor.Spawn(..., autoEngage: true)` plus `HasBeenEngaged = true` and `IgnoreForRoomClear = true`. 0.9.0 added
   "explicit engage with a target fallback". Find the real cause in the decompiled game: candidates are the
   `BehaviorSpeculator` never ticking (it needs `aiActor.enabled`, a `TargetBehavior` with a valid `PlayerController`
   in range, `bs.enabled`, and `AIActor.State == Normal`), the actor still in `AwakenAnimationType.Spawn` waiting for a
   clip named `spawn`/`awaken` that does not exist (use `AwakenAnimationType.Default`, or add the clip), `IsGone`,
   `PreventAllDamage`, the `ShootBehavior` requiring an `AIShooter`/`aiAnimator` state it does not have, the shoot point
   parented wrong, or `aiActor.ParentRoom` being null because the actor was spawned before the room was ready.
   Compare with how `VetBoss` (which does fight) is set up and with the research's Bullet-Kin brain listing. Make the
   Tech visibly do the vanilla things: walk toward Pluto, stop at range, play `tell`, fire, play `die` and leave a
   corpse; the Nurse the same with her fan and her net. Log one line per spawned actor with state, speculator enabled,
   engaged, target found (0.9.0 started this: keep it). Test each with `spawn pluto:vet_tech` in a normal room too.
3. **Character interactions and story flow.** The user wants: act 1 as now (intro at the desk, bystanders to talk to);
   in act 2 a Vet Tech **greets Pluto and tells him to go to the third room** (a line, then the staff attack: the greeting
   is the tell, like the Convict past's soldiers), the ward waves fight properly, the door opens; in act 3 the **dialogue
   with the Vet** (the three existing lines) and then the boss fight starts with the boss card, health bar and music
   (`GenericIntroDoer.TriggerSequence`; the 14 s watchdog stays). Every human in the clinic must be able to attack and
   shoot: Techs (pistol syringes), the Nurse (droplet fans, net), the Vet (his existing attacks). Make every line
   skippable with interact, and make the letterbox / camera lock / input override symmetric (lock, unlock) per act.
   Keep the lines in the config. 0.9.0 added greetings and mid-fight lines; keep what works, fix what does not.
4. **Bullet patterns should match a vanilla boss fight and its helpers.** Study the Gungeon bosses' scripts the
   research names (Beholster, Gorgun, Bullet King helpers) and shape the Vet's phases and the helpers' patterns like
   them: readable tells, fans and rings with gaps, aimed bursts that lead the player, phase changes at health
   thresholds. **Balance: not easy, not hard.** Target for a mid-run Pluto with the kibble sack: Techs die in a few
   hits, the Nurse in ~10 s of focused fire, the Vet in 60 to 90 s, the whole past in 4 to 6 minutes; Pluto should lose
   about one to two hearts in a clean run. Expose health, speeds and cooldowns in `PastConfig` so the tester can tune
   without a rebuild, and document the knobs in `docs/checklist.md`.
5. **Level look: the Gemini mock-ups.** The user wants the room to look like the concept images: white tile floor
   with pale grout, the clinic's steel-and-teal north walls, cabinets and glass, the theatre lamp and table under it,
   the ward's kennel rows, the waiting room's chairs, desk and window. 0.9.0 added a `FloorTiles` config; check what it
   does and whether the lab tileset can be re-tinted or whether the floor must be a big walkable floor prop drawn from
   `tiles_and_walls.png` (plain / drain / paw-print / cracked variants) and placed under the actors (HeightOffGround
   below every other decor). Redraw or add props where the mock-ups have something the room lacks; use the prop sheets
   for silhouettes. Keep the Primerdyne pink-red ambient light subtle. Compare the in-game screenshot the user sends
   with `level_overview.png` side by side and iterate. Use Gemini for **new** reference ideas when you need them
   (a wall-face study, a floor-tile set at 2K, a cutscene beat), never for sprites.
6. **Story well driven.** Read the vanilla pasts' beat lists in `04a` and make every act have a clear beginning
   (camera, line), middle (the fight or the walk) and end (door, sound, line). Add the intercom and the epilogue where
   0.7.0 put them, make Rex and Grandma react (a bubble) when the ward door opens, and give the Vet a line when the
   Nurse comes in.

## Deliverables

1. Fixes and features above, each verified as far as static checks allow: the decompiled source consulted for every
   runtime claim (write what you checked in `PlutoVetVisit/docs/checklist.md` milestone 10), tests updated
   (`tools/tests`), `validate.py` extended for anything new the build must catch.
2. `PlutoVetVisit/docs/checklist.md` milestone 10: numbered in-game steps with the exact log lines to look for, and
   the config knobs for balance.
3. Version 0.10.0 in `src/PastPlugin.cs` and `thunderstore/manifest.json`, changelog, `releases/Pluto_Vet_Visit-0.10.0.zip`,
   GitHub release v0.10.0, drop page republished, Steam session messaged. Commit message per milestone.
4. `tasks/vet-visit-todo.md` updated with what was done and what the tester must report; `tasks/lessons.md` if the
   user corrects you.

Do not merge into `PlutoTheCat/` (milestone 1.0 is a separate approval). When done, give the user a short summary
with the paths, the sha256 of the zip, and the three things you most want checked in game.
