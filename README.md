# The Vet Visit — Pluto's custom past (standalone project)

Developed separately from `../PlutoTheCat`; merged into it only when finished (see
`../docs/superpowers/specs/2026-09-13-vet-visit-past-design.md`). Build with `./build.sh`; tests with
`python3 -m unittest discover -s tools/tests -v`. Gemini art: put `GEMINI_API_KEY=...` in `.env` here
(gitignored — never commit it) or export it in `~/.zshenv`, then `python3 tools/gemini_art.py`.

Gemini outputs land in `reference/gemini/` and are checked in; existing files are skipped unless you
pass `--force`. `python3 tools/gemini_art.py --dry-run` prints the generation plan without calling the
CLI. To redo a single piece after tweaking its prompt in `tools/gemini_art.py`, run
`python3 tools/gemini_art.py --force --only <name>` (e.g. `--only vet_bosscard_raw.png`), then
`python3 tools/make_art.py` to rebuild the boss card, win picture and icon from the new reference.

## Layout

```
PlutoVetVisit/
  PlutoVetVisit.csproj, packages.config, nuget.config   net35 project, same package set as PlutoTheCat
  build.sh                   art -> nuget restore -> msbuild -> validate -> dist/Pluto_Vet_Visit-<version>.zip
  vet_check.sh                greps a BepInEx log for [VetVisit] lines, prints PASS/FAIL
  src/
    PastPlugin.cs             BepInEx entry point (GUID bogdan.etg.plutovetvisit)
    PastConfig.cs             config bindings (BepInEx/config/bogdan.etg.plutovetvisit.cfg)
    PastLevel.cs              GameLevelDefinition tt_pluto_past + Harmony patches
    VetFlow.cs                 the one-node DungeonFlow
    ClinicRoom.cs              loads Resources/Rooms/vet_clinic.newroom
    ClinicObjects.cs           the clinic prop prefabs (and the NPC prefabs through ClinicNpc)
    ClinicDoor.cs              the sliding zone door: collider on/off, closed/open sprite
    ClinicNpc.cs               placed bystanders: idle/talk/walk clips, one comment line, driven by the intro
    ClinicLayout.cs            generated room-space coordinates, zones, spawn cells + object specs (do not edit by hand)
    CastLayout.cs              generated cast facts: canvases, hitboxes, shoot points, clip lists (do not edit by hand)
    VetTech.cs                 the Vet Tech (regular enemy) and the Nurse (mini-boss): EnemyBuilder prefabs
    VetBoss.cs                 The Vet: prefab, stats, clips, bullet bank, behaviours
    VetAttacks.cs              the Vet's, the Tech's and the Nurse's bullet scripts
    VetVisitController.cs      the three acts: intro, sealed ward waves, the Vet; reinforcements; ending
    PlutoLink.cs                finds Pluto via Alexandria, attaches the past
  Resources/
    Rooms/vet_clinic.newroom               the clinic room, generated JSON
    Boss/vet/{idle,move,tell,fire,intro,die}/vet_<clip>_NNN.png   The Vet's animation frames
    Boss/vet_bosscard.png                   boss card (427 x 240)
    Objects/*.png                            clinic prop sprites (+ clinic_door_open, the door's open frame)
    Enemies/{tech,nurse}/<clip>/*.png        Vet Tech and Nurse animation frames
    Npcs/{owner,receptionist,rex,grandma}/<clip>/*.png   bystander animation frames
    SpriteRoot/ProjectileCollection/*.png    syringe, droplet and pill projectile sprites
    past_win_pic.png                         win-page picture (115 x 71)
  reference/gemini/            Gemini-generated references, checked in (clinic + Vet sheets, boss card / win pic / icon raws)
  docs/
    checklist.md                in-game test checklist per milestone, with Result: lines
    preview/                     room and sprite-sheet previews rendered by the Python tools
  tools/
    clinic_room.py, clinic_objects.py, vet_poses.py, tech_poses.py, nurse_poses.py, npc_poses.py   ASCII pixel-art sources
    cast_layout.py, cards.py, icon.py, projectiles.py, vetpixel.py, make_art.py, gemini_art.py, gemini_past_concepts.py, validate.py
    tests/                       unit tests (room, objects, vet, tech, nurse, npcs, cast, gemini, past_concepts)
  thunderstore/                 manifest.json, README.md, CHANGELOG.md, icon.png — the r2modman test package
```

## Build and test

```
python3 -m unittest discover -s tools/tests -v
./build.sh
```
`build.sh` regenerates the art, restores NuGet packages, builds with Mono msbuild, validates the output,
and packages `dist/Pluto_Vet_Visit-<version>.zip`.

## Integration

See the spec, milestone 5: `../docs/superpowers/specs/2026-09-13-vet-visit-past-design.md`.
