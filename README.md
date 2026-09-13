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
    ClinicObjects.cs           the 13 clinic prop prefabs
    ClinicLayout.cs            generated room-space coordinates + object specs (do not edit by hand)
    VetBoss.cs                 The Vet: prefab, stats, clips, bullet bank, behaviours
    VetAttacks.cs              Booster Shot, Spray Bottle, Pill Time, Cone of Shame bullet scripts
    VetVisitController.cs      fade-in, dialogue, boss trigger, ending sequence
    PlutoLink.cs                finds Pluto via Alexandria, attaches the past
  Resources/
    Rooms/vet_clinic.newroom               the clinic room, generated JSON
    Boss/vet/{idle,move,tell,fire,intro,die}/vet_<clip>_NNN.png   The Vet's animation frames
    Boss/vet_bosscard.png                   boss card (427 x 240)
    Objects/*.png                            13 clinic prop sprites
    SpriteRoot/ProjectileCollection/*.png    syringe, droplet and pill projectile sprites
    past_win_pic.png                         win-page picture (115 x 71)
  reference/gemini/            Gemini-generated references, checked in (clinic + Vet sheets, boss card / win pic / icon raws)
  docs/
    checklist.md                in-game test checklist per milestone, with Result: lines
    preview/                     room and sprite-sheet previews rendered by the Python tools
  tools/
    clinic_room.py, clinic_objects.py, vet_poses.py   ASCII pixel-art sources (single source of truth)
    cards.py, icon.py, projectiles.py, vetpixel.py, make_art.py, gemini_art.py, validate.py
    tests/                       33 unit tests (test_room, test_objects, test_vet, test_gemini)
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
