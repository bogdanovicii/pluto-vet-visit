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

### 0.10.1 result (Steam machine, 2026-09-14)
The whole past ran start to finish: 0 CreateProjectileFromBank exceptions, Pluto fired, everyone shot, `past killed`. Fight ~60-90 s,
past ~3 min, 1.5 of 3 hearts lost. But enemy bullets passed through Pluto (no hits), the wave-2 "rat" was the harmless Candle Rat,
`Duplicate prefab name` appeared in the fight, the boss card showed the Vet for a second and then Pluto's portrait covered it, and some
dialogue boxes were off screen.

## Milestone 11 — a hard past (Pluto_Vet_Visit-0.11.0.zip)

Delete `BepInEx/config/bogdan.etg.plutovetvisit.cfg` once (new defaults for waves, health and the new `[Balance]`, `[Waves]`, `[Props]`
and `[Story]` keys). Use Pluto_The_Cat with the transparent boss card (the character session's fix) for the card check.

Checked in the decompiled game before this build:
- Bullets: Alexandria's `SetProjectileSpriteRight` moves the sprite into ETGMod's ProjectileCollection; the vanilla bullet's BagelCollider
  looks up the frame `10x10_projectile_dubred_dark_001` in its own collection, the lookup fails and `PixelCollider.RegenerateEmptyCollider`
  makes the hitbox 0x0. Every copy now gets a Manual box sized to its sprite. `SpawnPool.CreatePrefabPool` logs `Duplicate prefab name`
  when copies share a GameObject name; each copy is now named `PlutoVet_<bank>_<n>`.
- Boss card: `BossCardUIController` stretches the boss art and the player's card over the whole screen and draws the player's on top
  (ZOrder 14 over 6) from about 1.0 s. Pluto's card must be transparent except bottom-left (character session); the Vet's card is now a
  transparent hand-drawn portrait in the right half, like the Beholster card.
- Dialogue: TextBox and ThoughtBubble prefabs have `fitToScreen` off; the letterbox leaves ~70 % of the height. Lines now anchor at the head,
  the locked camera pans to show each box, boxes are nudged into view outside cutscenes, the intercom is a LetterBox over Pluto.
- AI: `FleeTargetBehavior` triggers on every hit and ended the Vet's interruptible attacks; vanilla floor bosses use a Seek leash only.
  `DashBehavior` reads `ShadowObject` every tick; `AIActor.Start` creates it only with `HasShadow` on (BossBuilder turns it off).
- Waves: `6ad1cafc...` is the Candle Rat (harmless, no brain, `#KILLEDBYDEFAULT` = "Your own slow reflexes"); every wave GUID was checked
  against the prefab data and the ETGMod id map.

Log lines to look for:
- At launch: `bank syringe: go PlutoVet_syringe_0, ... colliders 1 [Projectile Manual manual 10x4 at -5,-2 ...]` (one per bank entry:
  syringe 10x4, droplet 5x5, pill 6x4, net 10x10, cloud 12x12), `Syringe Tech built: 25 HP`, `registered N custom objects (A animated, E examinable)`.
- First shot of each actor: `Vet Tech first shot: go PlutoVet_syringe_..., ... built 10x4 ...`. `built 0x0` = the hitbox bug is back: send the line.
- No `Duplicate prefab name`, no `warning: ... harmless critter`, no `line failed` / `bubble failed`.

Steps:
1. Hits: stand in front of a Tech burst. Pluto takes half a heart per syringe, flashes and is knocked back; dodge-rolling through a bullet
   does not hurt. Same for the Nurse's droplets and net and the Vet's patterns.
2. Waiting room: the intro pans to every speaker (Receptionist, Owner, Rex, Grandma, the intercom) and every box is fully on screen;
   Pluto thinks "Food?" and "Traitor." in thought bubbles. Advance: the first press completes the text, the second closes it. After the
   intro, bystanders chat every 8-12 s; talking to the Receptionist, Rex or Grandma gives a different line each time. Examine props
   (outlined in white when close): a thought bubble over Pluto.
3. Ward: when the door opens Rex and Grandma react; the greeting Tech's lines are on screen; intercom lines appear as a parchment box over
   Pluto. Wave 1 (two Vet Techs, a Syringe Tech): Techs strafe instead of standing, side-step, sometimes lunge, and a Tech shouts when the
   wave starts or a crewmate falls. Wave 2 (mutant shotgun kin, mutant bullet kin, shroomer, poisbulon, creech, syringe tech): all attack.
4. Theatre: the boss card shows the Vet's portrait on the right and Pluto's on the left together (with the fixed character card).
   The Vet strafes and hops sideways between patterns; being hit no longer cancels his tell. 60 %: "Hold STILL." and the phase-two set
   (droplet wall, spiral, cone, stitches that stop and re-aim, the scalpel ring with a gap, anesthesia clouds, leap-in ring).
   50 %: the Nurse and a Syringe Tech come in; the Nurse sprays, hops back and throws the net, sweeps a tranquilizer spray, and below
   half her health adds the IV line; she shouts every 7-10 s; if she falls the Vet reacts. 25 %: "Just... a little... snip!", a
   poisbulon and a fungun come in, phase three (snip time, hard wall, full course, double hops).
5. Difficulty report: hearts lost in the ward and in the fight, time to kill the Vet, whether any pattern felt unfair (no visible gap,
   no tell), and whether the camera ever panned somewhere confusing.
6. Room: the three zones follow a grid. Waiting room: two rows of five orange chairs on a rug facing a coffee table, a carrier at each end,
   plants framing the south exit, the reception counter with a back cabinet, a water cooler and the fish tank on the east wall, signs
   "WAITING ROOM" and "WARD" on the wall. Ward: the kennel banks, a nurse-station island with a stool, a teal floor stripe door to door,
   supply shelf and scrubs rack on the north wall, IV stands flanking the door, the "SURGERY" sign. Theatre: the table centred under the
   lamp on a floor mat with instrument trolleys either side, the anaesthesia machine (breathing) and the heart monitor (ECG) at its head,
   counters left and right, a biohazard bin, toys in the south-west corner. Report anything floating, overlapping or drawn over Pluto.
7. Animated props: fish swim and bubbles rise, the clock ticks, the reception screen blinks, the IV drips, the monitor scrolls, the
   anaesthesia bellows move. Examinable props (white outline when close, interact): 20 props give Pluto a thought, e.g. the fish tank,
   the lost-cat notice, the supply shelf, the cone counter. Lines are in `[Props] Comment_*`.

Balance knobs (no rebuild): `[Balance] BulletSpeedScale`, `BossCooldownScale`, `BossSpeed`, `BossHopCooldown` (2.6), `TechSpeed`,
`TechRange` (9), `TechCooldown` (2.0), `TechDartCooldown` (5.5), `SyringeTechHealth` (25), `SyringeTechSpeed` (5), `SyringeTechRange` (4.5),
`SyringeFanCooldown` (2.4), `NurseSpeed`, `NurseFanCooldown` (2.2), `NurseNetCooldown` (4.5), `NurseSprayCooldown` (4), `NurseIVCooldown` (5);
`[Boss] BossHealth` (800); `[Cast] TechHealth` (20), `NurseHealth` (160), `BossReinforcements`; `[Waves] Wave1`, `Wave2`, `Reinforce2`,
`Reinforce3`; easier: `BulletSpeedScale = 0.85`, `BossCooldownScale = 1.25`, `Wave2 = mutant_bullet_kin,shroomer,syringe_tech`.

**Result:** pending

### 0.11.1 — the Vet redrawn
Same steps as milestone 11. Also check: the Vet's new sprite in the theatre (tell crouch, star flash on firing, the intro flick, the death),
that his shots leave from the needle tip and that Pluto's shots hit his body but not the air in front of the gun.
Log: `The Vet prefab bank: ...`, `the Vet first shot: ... built ...`.

## 0.12.0 — readable bullets

Delete `BepInEx/config/bogdan.etg.plutovetvisit.cfg` once (new `[Patterns]` section). Preview of every bullet with its hitbox:
`docs/preview/projectiles-sheet.png`.

Bullets: one hand-drawn sprite per attack family, vanilla-sized with a dark outline, a bright core and their own colour. Long ones
point along their flight (`shouldRotate` on; the Manual hitbox turns with them). Hitboxes are a little smaller than the art.

| Bank | Sprite | Hitbox | Look | Used by |
|---|---|---|---|---|
| syringe | 14x6 | 10x4 | steel barrel, blue dose, needle forward | Vet Booster Shot, Snip Time, follow-ups; Tech burst; Syringe Tech shotgun |
| dart | 13x5 | 9x3 | orange tuft, red body, steel tip | Vet Tech dart rifle |
| vaccine | 8x8 | 6x6 | bright blue orb | Cone of Shame, Vaccination Spiral, Snip Time ring |
| droplet | 9x7 | 7x5 | teal teardrop | Spray Bottle, Droplet Wall, the Nurse's fan |
| tranq | 7x7 | 5x5 | lime green bubble | the Nurse's tranquilizer hose and IV line |
| pill | 10x6 | 8x4 | red/white capsule | Pill Time |
| tablet | 7x7 | 5x5 | white tablet, red cross | what a pill bursts into |
| scalpel | 14x5 | 10x3 | teal handle, steel blade | scalpel ring |
| stitch | 9x9 | 5x5 | red suture X | stitches |
| net | 14x14 | 10x10 | orange hoop, steel mesh | the Nurse's net |
| cloud | 16x16 | 12x12 | white puff, plum rim | anesthesia |

Patterns (speeds in tiles/s before `BulletSpeedScale`; old -> new):

| Enemy | Pattern | Change |
|---|---|---|
| Vet Tech | 3-round burst | speed 8 -> 9 (`TechBurstSpeed`) |
| Vet Tech | dart rifle | darts instead of syringes; 12 (`TechDartSpeed`), second dart 8 -> 12 frames later |
| Syringe Tech | shotgun | 5 at 9 over 36 deg -> 5 at 8 over 40 deg (`SyringeFanSpeed`, `SyringeFanSpread`), re-pump 4 at 6 in the gaps 24 frames later; waits the lead-in first (the lunge-landing fan was point-blank) |
| Nurse | fan | 7+7 at 8 over 50 deg -> 6 at 7 over 60 deg, then 5 in the gaps re-aimed 32 frames later (`NurseFanSpeed`, `NurseFanSpread`) |
| Nurse | net | 5 -> 6 (`NurseNetSpeed`), settles at 2.5 |
| Nurse | tranquilizer hose | 14 droplets every 3 frames over 70 deg at 8 -> lead-in, 12 green bubbles every 4 frames over 80 deg at 9 (`NurseSpraySpeed`) |
| Nurse | IV line | 7 -> 6.5, green bubbles (`IVLineSpeed`) |
| Vet p1 | Booster Shot | 10 -> 11, 6 -> 7 frames apart (`BoosterSpeed`) |
| Vet p1 | Spray Bottle | 9+9 at 7 over 80 deg -> lead-in, 7 at 7 over 84 deg, then 6 at 5.25 in the gaps (`SprayBottleSpeed`, `SprayBottleSpread`) |
| Vet p1 | Pill Time | pills 8 frames apart, burst after 50 (was 40) frames into 6 tablets at 5.5 (was 6) (`PillBurstSpeed`) |
| Vet p2/p3 | Cone of Shame | 16+16 syringe rings, no gap -> lead-in, 20-orb rings with a 3-slot (54 deg) hole, second ring half-offset through the same hole, 28 frames apart (`RingSpeed`, `RingGapSlots`) |
| Vet p2/p3 | Droplet Wall | lead-in; gap width is a knob (`WallGapSlots`, 3 of 15), waves 30 -> 34 frames (hard wall 26 -> 28, +1 speed) (`WallSpeed`) |
| Vet p2/p3 | Vaccination Spiral | lead-in; orbs; 5 -> 5.5 (`SpiralSpeed`) |
| Vet p2/p3 | Scalpel ring | lead-in; 24 scalpels at 6 with a 60 deg hole 45-90 deg off Pluto (`ScalpelSpeed`, `ScalpelGapDegrees`); follow-up syringes at 10 |
| Vet p2/p3 | Stitches | sutures; fan 100 -> 110 deg; re-aim ripple 5 -> 6 frames apart at 9 (`StitchSpeed`) |
| Vet p2/p3 | Anesthesia | unchanged clouds; follow-up syringes at 10 |
| Vet p3 | Snip Time | 5 syringes at 12, 5 -> 6 frames apart (`SnipSpeed`); ring of 12 droplets -> 16 orbs with a 3-slot hole at 6 |

`PatternLeadIn` (8 frames) is the pause after the tell before a ring, wall, spiral, the spray bottle, the Syringe Tech shotgun or the
tranquilizer hose.

Log lines to look for:
- At launch, one per bank entry: `bank syringe: ... colliders 1 [Projectile Manual manual 10x4 at -5,-2 ...]`, `bank dart ... 9x3 at -4,-1`,
  `bank vaccine ... 6x6`, `bank droplet ... 7x5`, `bank tranq ... 5x5`, `bank pill ... 8x4`, `bank tablet ... 5x5`, `bank scalpel ... 10x3`,
  `bank stitch ... 5x5`, `bank net ... 10x10`, `bank cloud ... 12x12`.
- `The Vet prefab bank: syringe ok inactive, vaccine ok inactive, droplet ok inactive, pill ok inactive, tablet ok inactive, scalpel ok inactive, stitch ok inactive, cloud ok inactive`;
  `Vet Tech prefab bank: syringe ok inactive, dart ok inactive`; `The Nurse prefab bank: droplet ok inactive, tranq ok inactive, net ok inactive`.
- No `warning: projectile sprite ... is not in ProjectileCollection`, no `built 0x0`, no `Duplicate prefab name`, no `BROKEN`.

Steps (what the tester should see):
1. Ward, Vet Tech: blue-dosed syringes in threes, needle first; every few seconds a single red dart with an orange tuft, then a second.
   Syringe Tech: a short pause after its tell or lunge, then a 5-syringe fan and a slower 4 in the gaps.
2. Theatre, the Nurse: teal droplet fan of 6, then 5 re-aimed in the gaps; an orange net that stops and drifts; a sweeping hose of
   green bubbles; below half her health, braided green IV lines.
3. The Vet, phase 1: fast blue syringe triplets; when close, a teal spray in two layers; red/white pills that burst into white tablets.
   Phase 2-3: blue orb rings with one clear hole, teal walls with a hole near Pluto that walks, a 4-arm blue spiral, a ring of scalpels
   with a wide hole beside Pluto, red X sutures that stop and re-aim one by one, white clouds.
4. Every long bullet points where it flies (a syringe going down points down). A bullet grazing the outline of its sprite does not hit;
   the core does. Every bullet still takes half a heart.
5. Difficulty report as in milestone 11: hearts lost, time to kill the Vet, any pattern with no visible hole or no pause after its tell.

Knobs (`[Patterns]`, no rebuild): `PatternLeadIn` (8), `TechBurstSpeed` (9), `TechDartSpeed` (12), `SyringeFanSpeed` (8), `SyringeFanSpread` (40),
`NurseFanSpeed` (7), `NurseFanSpread` (60), `NurseSpraySpeed` (9), `NurseNetSpeed` (6), `IVLineSpeed` (6.5), `BoosterSpeed` (11),
`SprayBottleSpeed` (7), `SprayBottleSpread` (84), `PillBurstSpeed` (5.5), `RingSpeed` (5.5), `RingGapSlots` (3), `WallSpeed` (6),
`WallGapSlots` (3), `SpiralSpeed` (5.5), `SnipSpeed` (12), `ScalpelSpeed` (6), `ScalpelGapDegrees` (60), `StitchSpeed` (9).
Harder: `PatternLeadIn = 4`, `RingGapSlots = 2`, `WallGapSlots = 2`. Easier: `PatternLeadIn = 14`, `BulletSpeedScale = 0.9`.

**Result:** pending

### 0.12.0 — boss card, theatre and room
- [ ] Boss intro: title reads "THE VET", subtitle "DOCTOR'S ORDERS!" with every letter present; the Vet is a full-body figure lunging left with a syringe pistol and scalpel, no straight cut edge anywhere on him.
- [ ] Theatre entry: the Vet stands north of the operating table, fully visible; no lamp disc or table drawn over him during "Right on time, Pluto."
- [ ] Fight: walking behind the table or past the anaesthesia machine never hides him or Pluto for more than the feet.
- [ ] Log: `clinic room 36x63`, the Vet spawns at (29.0, 62.0) world with origin (11, 11).
- [ ] Walls: X-ray, anatomy poster, vaccination chart, weight chart, flea poster, cork board, diplomas, whiteboard hang on the north walls and give thoughts when examined.
- [ ] Room feels roomier: doors centred, Rex and Grandma on chairs, receptionist behind the counter, kennels on both ward walls, waves spawn off the kennels.
