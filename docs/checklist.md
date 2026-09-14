# In-game checklist (Steam machine, SteamOS/Proton, r2modman)

Nothing here can run on the build Mac. Each milestone is a test zip; send back `vet_check.sh` output and screenshots.

## Milestone 1 — plumbing (Pluto_Vet_Visit-0.1.0.zip)

Setup: import the latest `Pluto_The_Cat-*.zip` and `dist/Pluto_Vet_Visit-0.1.0.zip` (r2modman -> Settings -> Import local mod).
Launch once, then set `[Debug] DebugEndAfterSeconds = 20` in `BepInEx/config/bogdan.etg.plutovetvisit.cfg` (the debug
ending now runs in parallel with the ~10 s dialogue, so this must be at least 20; alternatively also set
`[Debug] SkipIntro = true` so the dialogue is skipped instead).

1. Launch. Console shows `[VetVisit] found Pluto`, `registered level tt_pluto_past`, `The Vet Visit is ready`, and no `step "..." failed`.
2. In the Breach select Pluto, open the console and run `vet_visit`. Expected: fade to black, then a white/grey lab-tiled
   room 26 x 18 with a doorway at the bottom middle; Pluto near the bottom-left. Log: `built past dungeon`, `clinic ready`.
3. After 20 s: freeze frame, credits tube, the win page with Pluto's win picture. Log: `past killed`.
   The main-menu button returns to the Breach.
4. Back in the Breach, Pluto's info panel shows the past as killed.
5. The real route: as Pluto, talk to the Blacksmith (Bullet That Can Kill The Past), beat the Lich, fire the Gun in the Ark.
   Expected: the clinic loads instead of the win page.
6. Session hygiene: in the same session pick the Marine and run `load_level fs_soldier`. Expected: the Primerdyne lab, not the clinic.

Send back: `./vet_check.sh` output, a screenshot of step 2, and whether steps 4-6 passed.

**Result:** pending

## Milestone 2 — the clinic

Same setup; keep `DebugEndAfterSeconds = 20` so the past still ends by itself after the dialogue.
1. `vet_visit`: the room is dressed: six glass cabinets and a poster along the top, the steel exam table in the middle,
   a cart with syringes, a sink, a scale, the carrier bottom-left, toys and a cone on the floor.
2. Pluto cannot walk through the table, cabinets, sink, carrier or scratching post; he walks over toys, the tray, the cone and the scale.
3. Bullets fired at the table fly over it; bullets at a cabinet stop.
4. Two speech bubbles appear behind the table (the Vet's lines from the config), then a hiss from Pluto; the camera
   returns and Pluto can move. `[Debug] SkipIntro = true` skips them.
5. Props render above the floor and below Pluto when he walks in front of them (report anything drawn on top of Pluto).
Send back: screenshot of the room, and any prop that looks wrong.

**Result:** pending

## Milestone 3 — The Vet

Set `DebugEndAfterSeconds = 0`.
1. `vet_visit`: The Vet stands behind the table during the dialogue and does nothing; the bubbles come from him.
2. After the hiss: the walk-in, the boss card "THE VET — Doctor's Orders" with the card art, the boss health bar, boss music.
   Log: `The Vet spawned`, `fight started`.
3. He paces behind the table and cycles three phase-one attacks: Booster Shot (three aimed syringes), Spray Bottle
   (two fans of droplets), and Pill Time (four slow pills that burst into six droplets). Below half health the tempo
   rises and the Cone of Shame rings appear (milestone 4 has the details). Pluto's kibble damages him (bar goes down).
   Contact with him hurts.
4. On death: death animation, harmless explosion ring, `The Vet is down`, then the ending from milestone 1 and the win page with
   the Pluto win picture.
5. `spawn pluto:the_vet` in any normal room spawns him without an intro (BossTriggerZone), fighting immediately is not expected there.
6. Expect the intro clip to play facing right even though the Vet faces Pluto on his left; if so, report it: the fix is introAnim = "" plus introDirectionalAnim = "intro" in VetBoss.cs.
Send back: whether the intro fired, whether damage registers, and how the fight feels (too easy / too hard).

**Result:** pending

## Milestone 4 — phase two and polish
1. Syringes, droplets and pills use their own sprites (not the red Bullet Kin bullet).
2. Above half health: aimed syringes, droplet fans, and slow pills that burst into six droplets.
3. Below half health: everything faster, plus rings of sixteen syringes (two rings, offset).
4. Fight length and difficulty with a full late-run loadout: report the time to kill; tune `[Boss] BossHealth` / `BossDpsCap`.
5. The Gemini boss card and win picture show (if generated).
6. Bullets leave from the syringe tip, not from the Vet's feet.
7. Syringe, droplet and pill hitboxes feel fair (they use full-sprite footprints).

**Result:** pending

## Milestone 5 — three zones and gates (Pluto_Vet_Visit-0.5.0.zip)

Set `DebugEndAfterSeconds = 0`. Log lines to look for: `doors found: 2`, `the ward door opens`, `the ward door closes behind Pluto`,
`wave 1: 3 enemies`, `wave 1 cleared`, `wave 2: 5 enemies`, `wave 2 cleared`, `the theatre door opens`, `The Vet spawned`, `fight started`.
1. `vet_visit`: Pluto starts bottom-left of a tall room beside the carrier; chairs along the left wall, the reception desk on the right,
   a closed teal double door in the wall above. After about a second the door slides open (frame only, floor visible through it).
2. Walk through the door into the ward (kennels on both walls, a counter in the middle). Once Pluto is a cell and a half inside, the
   door behind him closes and blocks the way back (walk into it; shoot it: bullets stop). Three enemies appear by the side walls.
3. Kill them: five more appear by the kennels. Kill those: the far door opens. If anything is stuck in a wall, note it; after 90 s the
   game puts the wave down by itself and logs it.
4. Walk into the theatre: the door closes behind Pluto, the Vet stands behind the table, the dialogue plays, the fight starts as before.
   Beat him: the ending as in milestone 1.
5. `[Debug] SkipWaves = true`: the ward door closes and the theatre door opens at once (no enemies).
6. Rendering: doors draw above the floor and below Pluto when he stands south of them; kennels and the station block movement; nothing
   from the ward is visible through the wall from the waiting room (report if the wall segments render as pillars or gaps instead of a wall).

**Result:** pending

## Milestones 6-8 — cast, story, dressing (Pluto_Vet_Visit-0.8.0.zip)

Set `DebugEndAfterSeconds = 0`, `SkipIntro = false`, `SkipWaves = false`. Log lines: `Vet Tech built`, `The Nurse built`, `registered 4x custom objects`,
`intro: owner True, receptionist True, rex True, grandma True`, `wave 1: 3 enemies`, `hearts on the nurse station`, `the Vet calls the Nurse`.
1. `vet_visit`: letterboxed intro in the waiting room. The Receptionist asks the name, the Owner answers, Rex and Grandma Cat speak, the
   intercom says "Pluto?", the Owner says "Be good." and walks down off the screen. Interact advances a line early. Then control returns,
   a chick, a rabbit and a squirrel run around, and the ward door opens.
2. Talk to the Receptionist, Rex and Grandma Cat (interact): one line each. Rex trembles; Grandma breathes.
3. Ward: three Vet Techs come from the side walls (teal scrubs, syringe pistols, aimed syringes). Kill them: two more Techs plus a rat, a
   parrot and two mutant kin from the kennels. Then two hearts appear on the nurse station and the far door opens.
4. Theatre: the lamp hangs over the strap table, a monitor cart and a vaccine fridge stand by the wall. The Vet fight as before; below
   half health the Nurse (big, white cap, shotgun syringe, net on her back) and two Techs come in from the right. Her fans are seven droplets,
   her net is one big slow projectile. Kill everyone; the Vet's death still ends the past. Epilogue line, then the credits.
5. `spawn pluto:vet_tech` and `spawn pluto:nurse` in a normal room: they fight; report whether their outline, shadow and death look right.
6. Report: are Tech/Nurse hitboxes fair, is the intro readable, does any NPC draw over Pluto, does the Owner leave cleanly.

**Result:** pending

## Milestone 9 — armed, engaged, talking (Pluto_Vet_Visit-0.9.0.zip)

Log lines: `loadout on arrival: N gun(s), current ...` (and `loadout at 1 s: ...` if anything changed), `wave 1: 3 enemies`,
`wave 1 Vet Tech: state Normal, brain True, engaged True, target True`, `the Vet calls the Nurse`, `fight started`.
1. Pluto has the Royal Kibble Sack in hand in the waiting room and can shoot. If not: run `vet_loadout` in the console and send the
   `loadout ...` lines.
2. The floor is white clinic tile in all three zones. If the tiles draw on top of Pluto or the props, set `[Room] FloorTiles = false` and say so.
3. Ward: a Tech steps up and speaks two lines (skippable), Pluto hisses, then wave 1 attacks: Techs keep their distance and fire
   three-syringe bursts. Report whether they move and shoot within a few seconds. If a `no target after 2 s, forcing Pluto` line
   appears, say so.
4. Intercom after wave 1; wave 2 (two Techs, a mutant kin, a rat, a parrot); intercom "The doctor will see you now."; theatre door opens.
5. Theatre: the Vet's lines, the hiss, boss card, fight. At half health: "Nurse! Hold him down!", the Nurse and two Techs arrive with
   a line. At a fifth: "Just... a little... snip!".
6. Difficulty: how many hearts did the whole past cost? Time to kill the Vet? (Target: a real fight, no wipe.)

**Result:** pending

## Milestone 10 — plays, looks and reads like a vanilla past (Pluto_Vet_Visit-0.10.0.zip)

Fresh config recommended (delete `BepInEx/config/bogdan.etg.plutovetvisit.cfg` once so the new `[Balance]` and `[Room]` keys appear).
`SkipIntro = false`, `SkipWaves = false`, `DebugEndAfterSeconds = 0`.

What was checked in the decompiled game before this build (so the tester knows what the log lines mean):
- Guns: `ArkController.ResetPlayers` calls `ResetToFactorySettings` (destroy all guns, re-add `startingGunIds`, clear every input
  override) before `LoadCustomLevel`; nothing in the level load strips guns (`Dungeon.StripPlayerOnArrival` is off on the Soldier
  template). Firing needs `AcceptingNonMotionInput` (no input override, `PreventPausing` false), `CurrentGun != null`, `!IsGunLocked`.
  Only `ToggleGunRenderers(true, "")` clears every hide key. The loadout check repairs all of it and logs a snapshot.
- Staff: `BehaviorSpeculator.Update` returns unless the actor `HasBeenAwoken` (State not Inactive/Awakening). `AIActor.State` is
  not copied to a clone; the `ObjectVisibilityManager` that wakes vanilla enemies is destroyed by `EnemyBuilder`; `AIActor.Spawn`'s
  `autoEngage` is consumed only by that manager. So every EnemyBuilder actor was born asleep. `HasBeenEngaged = true` runs
  `OnEngaged` (State Normal, brain on); a missing "spawn"/"awaken" clip is harmless; `ShootBehavior` needs no AIShooter.
- Patterns: measured against the Bullet King, Gorgun, Beholster and Gatling Gull prefabs (bullet speeds 5-12, fans 7-20 bullets,
  rings 16-64, cooldowns 1-1.5 s bread-and-butter, 3-12 s signature, `InitialAttackDelayBehavior` 2 s).

Log lines, in order:
`ambient light: N lab controller(s) disabled`, `loadout on arrival: before[...] after[...]`, `intro: camera locked`, `intro over: input AllInput`,
`the ward door opens`, `ward greeting: camera locked`, `ward greeting over: input AllInput`, `wave 1: 3 enemies`,
`wave 1 Vet Tech @(x, y): state Normal, awoken True, enabled True, brain True, engaged True, ... target True, ... passable True, pathed True`,
`wave 1 cleared`, `wave 2: 5 enemies`, `wave 2 cleared`, `hearts on the nurse station`, `the theatre door opens`, `The Vet spawned`,
`theatre dialogue over: input AllInput`, `fight started`, `the Vet calls the Nurse`, `reinforcements The Nurse ...: state Normal`, `The Vet is down`, `past killed`.
Bad signs: `state Inactive` or `awoken False` at 2 s (engagement failed: send the whole line), `pathed False` (bad spawn cell),
`not awake after`, `no target after`, `loadout ...: input was overridden`, any `NullReferenceException` near `BehaviorSpeculator`.

1. Waiting room: Pluto holds the Royal Kibble Sack and can shoot the moment control returns (during the intro he cannot, by design).
   If not, run `vet_loadout` and send the `loadout console:` line (it says whether the gun, its renderer or the input state was the problem).
2. Look: white tiled floor with a few drain / paw / cracked tiles, white-and-teal wall faces with the TV, window, clock and intercom on them,
   nine orange chairs (Rex and Grandma on two), the long reception desk with monitor and bell, the fish tank on its stand.
   Report anything drawn over Pluto; `[Room] FloorTiles = false` / `WallFaces = false` switch them off.
3. The ward door opens: Rex and Grandma each say a line. Walk in: the door closes, a Tech steps up: "Pluto? The doctor is through the far
   door." / "First, hold still..." (interact skips a line), Pluto hisses, then wave 1: three Techs walk toward Pluto, stop at range,
   raise the pistol (tell), fire a three-round burst, and die with a death animation and a corpse. Report movement within 2 s.
4. Intercom after wave 1; wave 2 (two Techs, mutant kin, rat, parrot) from the kennels; "The doctor will see you now."; two hearts on the station.
5. Ward look: barred kennels along both walls (two with a coned patient), the station with bowls on it, X-ray box and PREP sign on the wall.
6. Theatre: the lamp head hangs over the strapped table and draws over Pluto when he walks under it (report if it hides the Vet).
   Dialogue (three lines, skippable), then the boss card "THE VET — Doctor's Orders", health bar, music. He walks for ~2 s, then attacks.
7. Fight: phase 1 (to 60 %) aimed syringe bursts, droplet fans, slow pills (shoot a pill: it pops). Phase 2 (60-25 %): the droplet wall
   opens a gap on Pluto that shifts for the second wave; the spiral; the cone rings. At 50 % "Nurse! Hold him down!", the Nurse and two
   Techs come in from the right with a line, the Vet answers "About time, Nurse.". Phase 3 (< 25 %): "Just... a little... snip!",
   fast bursts, the wall then the spiral back to back. Every shot has a sound.
8. Balance: hearts lost for the whole past, time to kill the Vet (target 60-90 s), time for the Nurse (~10 s), Techs in a few hits.
9. `spawn pluto:vet_tech` and `spawn pluto:nurse` in a normal room: they now wake themselves (`... engaged itself` in the log) and fight.

Config knobs for balance (`[Balance]`, no rebuild needed): `BulletSpeedScale` (0.8 easier, 1.2 harder, scales every enemy bullet),
`BossCooldownScale` (1.3 slower fight), `BossSpeed` 3, `TechSpeed` 4.5, `NurseSpeed` 3.2, `TechCooldown` 1.8, `NurseFanCooldown` 2.2,
`NurseNetCooldown` 4.5; `[Boss] BossHealth` 800; `[Cast] TechHealth` 18, `NurseHealth` 150, `BossReinforcements`; `[Waves] Wave1/Wave2`.
Look: `[Room] FloorTiles`, `WallFaces`, `AmbientR/G/B` (0.96/0.84/0.84; the lab is 0.91/0.64/0.64).

**Result:** pending

### 0.10.0 result (Steam machine, 2026-09-14)
Techs woke, walked and started their tell, but every shot threw the `AIBulletBank.CreateProjectileFromBank` NullReferenceException
(188 times); Pluto had the sack but `active=False` and input `FoyerInputOnly`; the past stopped at wave 1. Screenshots: the lab's purple
wall blocks covered the wall faces, the floor variants looked like dirt, kennels stood apart.

## Milestone 10.1 — shots and the Breach state (Pluto_Vet_Visit-0.10.1.zip)

Checked in the decompiled game:
- `AIBulletBank.CreateProjectileFromBank` reads `GetBullet(name).BulletObject` and, when it is null, `aiShooter.CurrentGun` with no null check;
  our actors have no AIShooter. The entry was null because `VetBoss.Entry` cloned Alexandria's already-inactive fake-prefab copy again, and
  Alexandria's Instantiate hook activates any clone of a fake prefab, so the live projectile died in the world.
- `Foyer` sets `GameManager.IsFoyer`, `ForceNoGun` and `CurrentGun.gameObject.SetActive(false)`; only `Foyer.OnDepartedFoyer` undoes them.
  `PlayerController.CurrentInputState` returns `FoyerInputOnly` while `IsFoyer`, and `AcceptingNonMotionInput` is then false.
- `BehaviorSpeculator.RefreshBehaviors` initialises every behaviour with `m_aiActor`, which only the component's Start sets; the greeter's
  speculator was switched off before Start, so each behaviour started with a null actor: the engage NRE. Enabling it is enough.

Log lines to look for:
`Vet Tech prefab bank: syringe ok inactive`, `The Nurse prefab bank: droplet ok inactive, net ok inactive`, `The Vet prefab bank: syringe ok inactive, droplet ok inactive, pill ok inactive`,
`loadout on arrival: left the Breach state (IsFoyer); ForceNoGun off; gun object switched on ...` (only with `vet_visit`; the Ark route prints
`nothing to repair`), with the `after[...]` snapshot showing `current pluto_kibble_sack active=True`, `input AllInput`, `nonMotion True`, `isFoyer False`,
`Vet Tech spawned, bank: syringe ok inactive` for each Tech, `watchdog 15 s: gun pluto_kibble_sack active True, input AllInput, nonMotion True, isFoyer False`.
Bad signs: any `bank: ... BROKEN` or `REPAIRED` (send the line), `active!` on a bank entry, `input FoyerInputOnly`, the CreateProjectileFromBank exception,
or a `loadout watchdog: ...` line during normal play (it now acts only on a state that lasted two ticks: say what Pluto was doing).
Pluto's cardboard box and dodge rolls must still hide the gun normally.

1. `vet_visit` from the Breach: after the intro Pluto fires the kibble sack.
2. Ward: the greeting, then the Techs close in and their syringe bursts actually fly (with a sound) and hurt Pluto. No engage error line.
3. Clear both waves, reach the theatre, the Vet fires his patterns; the Nurse fires fans and nets.
4. Look: the divider walls show the white-and-teal face (no purple blocks), TV, window, clock and intercom on it; Pluto standing against a wall is drawn in
   front of it; the kennel bank is continuous with animals; the doormat is brown. Screenshot each zone again.
5. Report hearts lost and the time to kill the Vet (target 60-90 s).

**Result:** pending
