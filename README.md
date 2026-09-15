# The Vet Visit — Pluto's custom past (standalone project)

Current version: **0.14.2** (`thunderstore/manifest.json`, `src/PastPlugin.cs`). A separate BepInEx plugin
(`bogdan.etg.plutovetvisit`) and Thunderstore package (`Pluto_Vet_Visit`) that attaches a custom past to Pluto the
Cat. It is developed apart from `../PlutoTheCat`; merging into one DLL is still pending the user's approval (original
plan: `../docs/superpowers/specs/2026-09-13-vet-visit-past-design.md`, now historical). Full history:
`thunderstore/CHANGELOG.md`.

## What the past is

Pluto gets the Bullet That Can Kill The Past from the Blacksmith, fires it at the Ark, and lands in one clinic room
(36 x 63 cells) in three zones, gated by sliding doors:

1. **Waiting room**: Bogdan and Bianca check Pluto in with the receptionist and leave; Rex and Grandma comment; the
   intercom calls Pluto.
2. **Ward**: the door seals behind Pluto and two waves attack (Vet Techs, Syringe Techs and vanilla enemies) among
   living kennels. Co-op partners left behind a sealed door are brought through.
3. **Theatre**: the Vet (boss card, three phases, the Nurse and Techs as reinforcements, the masked Vet in his last
   quarter, lamp and red room mood).
4. **Rescue and ending**: after the Vet falls Pluto opens every kennel, the animals run out, Bogdan and Bianca take him
   home, then the credits and the win picture.

Beating the past records a progress file, places the Vet's broken syringe as a Breach trophy and unlocks Pluto's
Samurai costume (Pluto the Cat 2.16.0+). In the past the samurai keeps his Taiyaki Cannon and Katana.

Console: `vet_visit` (jump to the past from the Breach), `vet_loadout` (loadout snapshot and repair),
`vet_trophy_here` (place the trophy), `vet_reset_past` (forget the win), `spawn pluto:the_vet`, `spawn pluto:nurse`,
`spawn pluto:vet_tech`. Config: `BepInEx/config/bogdan.etg.plutovetvisit.cfg` (sections General, Boss, Balance,
Patterns, Waves, Cast, Story, Room, Mood, Props, Breach, Debug).

## Requires Pluto the Cat

The plugin declares `[BepInDependency("bogdan.etg.plutothecat")]` and does nothing without Pluto. The Thunderstore
manifest does **not** list Pluto as a dependency: the repos record no Thunderstore namespace for Pluto_The_Cat (both
packages are distributed as local zips / GitHub releases), so there is no `Namespace-Pluto_The_Cat-<version>` coordinate
to declare. Until one exists, install by hand in r2modman: import
`Pluto_The_Cat-2.16.2.zip` first, then `Pluto_Vet_Visit-0.14.2.zip` (Settings → Import local mod). Built against:
Pluto the Cat 2.16.2 + Vet Visit 0.14.2 (the samurai loadout needs 2.16.0 or later).

## Layout

```
PlutoVetVisit/
  PlutoVetVisit.csproj, packages.config, nuget.config   net35 project, same package set as PlutoTheCat
  requirements.txt            pinned Python packages for tools/ and tests (Pillow)
  build.sh                    art -> nuget restore -> msbuild -> validate -> dist/Pluto_Vet_Visit-<version>.zip
  vet_check.sh                greps a BepInEx log for [VetVisit] lines, prints PASS/FAIL
  src/
    PastPlugin.cs, PastConfig.cs          entry point (depends on Pluto's GUID) and config bindings
    PastLevel.cs, VetFlow.cs, BlacksmithBullet.cs   level definition, one-node flow, Blacksmith bullet flag
    ClinicRoom.cs, ClinicLayout.cs        room loader; generated room coordinates, zones and object specs (do not edit)
    ClinicObjects.cs, ClinicDoor.cs, ClinicNpc.cs, KennelCritter.cs, FreedAnimal.cs   props, doors, bystanders, kennel animals
    CastLayout.cs                         generated cast facts: canvases, hitboxes, shoot points, clips (do not edit)
    VetTech.cs, VetBoss.cs, VetAttacks.cs, VetMask.cs   Techs and Nurse, the Vet, bullet scripts, masked last phase
    VetVisitController*.cs                intro, ward waves, boss fight, rescue and ending; Loadout and Combat partials
    EncounterRoster.cs                    owns encounter actors and their bullets until cleanup
    PastTalk.cs, ClinicSound.cs, TheatreMood.cs   on-screen dialogue, game sound events, lamp and room colour
    LoadoutChoice.cs, PlutoLink.cs        which guns Pluto gets back (costume-aware); finds Pluto via Alexandria
    VetProgress.cs, BreachTrophy.cs, PastReset.cs   progress file, Breach trophy, vet_reset_past
  Resources/
    Rooms/vet_clinic.newroom              the clinic room, generated JSON
    Boss/vet/<clip>/, Boss/vet_bosscard.png   the Vet's frames and boss card
    Enemies/{tech,stech,nurse}/<clip>/    Vet Tech, Syringe Tech and Nurse frames
    Npcs/{bogdan,bianca,receptionist,rex,grandma}/<clip>/   bystanders
    Objects/*.png                         props, doors, kennels, freed animals, trophy
    SpriteRoot/ProjectileCollection/*.png syringe, droplet, pill and other bullet sprites
    past_win_pic.png                      win-page picture (115 x 71)
  reference/gemini/, reference/art/       Gemini references and approved converted art, checked in
  docs/
    checklist.md                          in-game results per milestone (historical record)
    past-concepts.md, preview/, prompts/  concept notes, rendered previews, old session prompts
  tools/
    clinic_room.py, clinic_objects.py, clinic_colliders.py   room map, props, collider audit
    vet_poses.py, tech_poses.py, nurse_poses.py, npc_poses.py, vetpixel.py   hand-drawn cast sources and palette
    cards.py, vet_card.py, win_pic.py, icon.py, projectiles.py, cast_layout.py, sounds.py
    art_sources.py, build_art.py, cut_frames.py, gemini_art.py, gemini_past_concepts.py, concept_v2.py   Gemini-first art
    make_art.py, validate.py              regenerate everything; validate the package
    tests/                                unit tests
  thunderstore/                           manifest.json, README.md, CHANGELOG.md, icon.png
```

## Build and test

```
python3 -m pip install -r requirements.txt
python3 -m unittest discover -s tools/tests -v
./build.sh
```

`build.sh` regenerates the art, restores NuGet packages, builds with Mono msbuild, validates the output and packages
`dist/Pluto_Vet_Visit-<version>.zip`. It does not run the unit tests; run them first.

## Gemini art

Put `GEMINI_API_KEY=...` in `.env` here (gitignored — never commit it) or export it in `~/.zshenv`, then
`python3 tools/gemini_art.py`. Outputs land in `reference/gemini/` and are checked in; existing files are skipped
unless you pass `--force`. `--dry-run` prints the plan; `--force --only <name>` redoes one piece (e.g.
`--only vet_bosscard_raw.png`), then `python3 tools/make_art.py` rebuilds the card, win picture and icon.
