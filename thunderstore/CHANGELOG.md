# Changelog

## 0.10.1
- Enemies shoot. Every enemy shot since 0.3.0 threw a NullReferenceException in `AIBulletBank.CreateProjectileFromBank`: each bullet copy was cloned a second time, Alexandria's instantiate hook switched that clone on, the live projectile flew off and destroyed itself, and the bank entry was left empty (our actors have no gun to fall back on). The copy is now made once and kept switched off, and every Tech, Nurse and the Vet checks its bank when it appears and rebuilds any entry that went missing (`... bank: syringe ok inactive`).
- Pluto shoots when started with `vet_visit`. Loading the past straight from the Breach skipped the game's "left the Breach" step, so the game still thought Pluto was in the Breach (no firing) and his gun stayed switched off. The loadout check now does what leaving the Breach does and switches the gun back on; the watchdog prints a short line every 15 s.
- The engage error on the ward greeter is gone (its brain is no longer switched off before it starts).
- Look, from the first in-game screenshots: the wall faces now stand in front of the lab's purple wall blocks, with the wall decor hung on them; calmer floor tiles; a stacked, occupied kennel bank along both ward walls with swung-open doors (the ward side doors are gone); a brown paw-print doormat; spaced waiting-room chairs; a readable clock; the theatre toys moved out of the fight into the corner.

## 0.10.0
- Armed, verified against the game's own code: the Ark hands the starting guns back before the past loads and nothing strips them afterwards, so an unarmed Pluto means a hidden gun renderer or a stuck input state. The loadout check now repairs all three (gun, renderer, input), runs after the level's fall-spawn, after every cutscene and every 3 s, and logs a full before/after snapshot (`loadout ...: before[...] after[...]`). `vet_loadout` prints it on demand.
- The staff fight, root cause found: EnemyBuilder enemies are born `Inactive` (the visibility manager that wakes vanilla enemies is stripped from the template) and their brain never ticks. Every spawned Tech, patient and the Nurse is now woken explicitly, re-woken if a heartbeat finds it asleep, and wakes itself when spawned from the console. Each actor logs one diagnostic line at 0.2, 2 and 6 s (state, brain, target, path, lists, health).
- Story: a Tech greets Pluto at the ward door and sends him to the far door before the wave attacks; Rex and Grandma react when the ward door opens; the Vet answers the Nurse's arrival. Every cutscene locks and unlocks the camera and input symmetrically, even if a line throws.
- Fight shaped like a vanilla boss (measured against the Bullet King, Gorgun, Beholster and Gatling Gull): a 2 s walk before the first tell, bread-and-butter attacks every 1.5-2.5 s, signature patterns on longer cooldowns with a breather after them, three phases at 60 % and 25 %, the droplet wall's gap opens on Pluto and walks, a "full course" (wall then spiral) in the last quarter, pills pop when shot. Shots make a sound. Techs fire Hegemony-soldier bursts (0.2 s between rounds, ~1.8 s cycle, line of sight required); the Nurse's fan is pumped twice with a 0.5 s gap and her net lingers.
- Balance knobs in `[Balance]`: bullet speed scale, boss cooldown scale, walking speeds, Tech/Nurse cooldowns. Vet 800 HP.
- Look: the room now follows the Gemini concepts. White tiled floors per zone (drain, paw and cracked tiles), white-and-teal wall faces with the decor hung on them, a big surgical lamp head over a strapped exam table, barred kennels (two with cone patients), nine orange chairs, a long reception desk, double glass cabinets, the nurse station with the bowls on it, the fish tank on a stand. A paler ambient light (`[Room] AmbientR/G/B`); `FloorTiles` and `WallFaces` really switch their props off now.

## 0.9.0
- Pluto arrives armed, for real this time: the loadout is checked on arrival and again at 1, 3, 6, 10, 20, 40 and 60 s; the sack is given through the game's own inventory call first and the loot engine second; every step is logged; `vet_loadout` in the console re-runs it.
- The staff fight now: every spawned Tech, patient, the Nurse and the Vet is explicitly engaged (state, brain, damage) the moment it appears, and anyone without a target after 2 s is pointed at Pluto. A heartbeat line in the log shows each actor's state at 2 s and 8 s.
- Vet Techs fire three-round syringe bursts like the Hegemony soldiers of the Convict's past, with a longer cooldown and a keep-your-distance stance.
- Character interactions: a Tech greets Pluto at the ward door ("Pluto? This way. Hold still...") before the first wave; the intercom calls the ward and then sends Pluto to the doctor; the Vet dialogue in the theatre stays; mid-fight lines: the Vet at half health, the Nurse arriving, the Vet at a fifth of his health. All lines are in the config.
- Balance: Vet 1000 HP, Techs 18, Nurse 150, wave 2 trimmed to five, syringes a touch slower, phase-one cooldowns a touch longer.
- Look: white clinic floor tiles laid over the past tileset in all three zones (config `FloorTiles` turns them off if they ever draw over Pluto).

## 0.8.0
- Dressing: PREP sign, surgical lamp over the table, monitor cart, vaccine fridge, intercom speaker over the ward door, a wall TV in the waiting room, side doors in the ward, leather straps on the exam table.
- Two hearts appear on the nurse station once the ward is clear. Doors play the door sound. Tech and Nurse health in the config (`[Cast]`).

## 0.7.0
- The intro: the Owner sets Pluto's carrier down and checks him in with the Receptionist; Rex and Grandma Cat have their say; the intercom calls "Pluto?"; the Owner says goodbye and walks out. Every line can be advanced with the interact key; `[Debug] SkipIntro` skips it all. Lines in `[Story]`.
- Bystanders: the Owner, the Receptionist, Rex (trembling on his chair) and Grandma Cat (a grey loaf) are hand-drawn placed NPCs; talk to them after the intro for a comment. A chick, a rabbit and a squirrel wander the waiting room.
- Epilogue line before the credits (`[Story] Epilogue`).

## 0.6.0
- Vet Techs: hand-drawn regular enemies on the Bullet Kin plan (teal scrubs, cap, mask, syringe pistol) with idle, walk, tell, fire and death clips. They seek Pluto and fire aimed syringes. Wave 1 is three Techs; wave 2 is two Techs plus escaped patients.
- The Nurse: a mini-boss at the Vet's scale with a shotgun syringe (droplet fans) and a net throw (a big slow net). Console `spawn pluto:nurse`, `spawn pluto:vet_tech`.
- Below half health the Vet calls the Nurse and two Techs in through the east door (`[Cast] BossReinforcements`).

## 0.5.0
- The past is now one 30 x 52 room in three zones, like the Marine's Primerdyne lab: the waiting room at the bottom (carrier, chairs, reception), the ward in the middle (kennels along both walls, a nurse station, the medical kit), and the operating theatre at the top (the old clinic dressing: cabinets, table, cart, sink, toys).
- Sliding clinic doors gate the zones. The ward door opens a second after the fade-in; it closes behind Pluto once he is inside, and the theatre door opens only when the ward is cleared. Each door is a hand-drawn prop with a closed and an open frame.
- The ward has two waves of vanilla enemies (config `[Waves] Wave1` / `Wave2`, names or GUIDs; default mutant bullet kin, rats and parrots) that stand up at the side doors and then at the kennels. A wave that is still alive after `WaveTimeoutSeconds` (90) is put down so the past cannot get stuck. Vet Techs and the Nurse replace them in 0.6.0.
- The Vet now spawns when Pluto enters the theatre; the dialogue and the fight are unchanged.
- New props: clinic door, kennel (closed and open), nurse station. Config `[Debug] SkipWaves` walks the zones without spawning.

## 0.4.0
- The Vet redrawn: glasses, stethoscope, coat pocket with pen and name tag, dark shoes, and a proper vaccine gun (syringe pistol with plunger, barrel, needle and grip) that he raises to shoot; walk cycle with shoes; shots leave from the needle. His frames ship without a drawn outline because the game outlines actors itself (he had a double outline).
- Sixteen new clinic props: reception desk with monitor and papers, two waiting chairs on a floor mat, a potted plant, a window with blinds, a wall clock, an X-ray light box, a medicine shelf, a fish tank, a sharps bin, an IV stand, a treat jar, Royal Canin food and water bowls, a litter box, paw prints and a wet-floor sign.
- Room re-dressed: cabinets, window, poster, X-ray box and shelf along the north wall; exam area with table, cart, IV stand and tray; sink, tank and bin on the right; waiting corner bottom-left; reception bottom-right.

## 0.3.0
- Pluto arrives armed: the past hands him his starting loadout (Royal Kibble Sack, Wet Food Can, Squeaky Toy, Nine Lives, Coco Blue, Puffed Up) if the run's reset left him empty-handed.
- The Vet's name no longer shows as an error: the boss card, boss bar and actor name use registered string-table keys.
- The fight always starts: if the intro never reports back, a watchdog wakes the Vet after 14 s. The walk-in is now directional, so he faces Pluto.
- Smarter Vet: he backs off when Pluto closes in, closes the gap when Pluto runs, and strafes in between. Attacks are range-gated and lead the target: Booster Shot at range, Spray Bottle up close, Pill Time with an aimed burst. Phase 2 (below half) adds the Droplet Wall (a curtain with a gap to step through), the Vaccination Spiral and the Cone of Shame; the last fifth is Snip Time: five fast leading syringes and a ring.

## 0.2.0
- Pluto now gets his past the vanilla way: the Blacksmith in the Forge gives him the Bullet That Can Kill The Past (Alexandria registers his hasPast identity with her).
- Guarantee: when Pluto takes the bullet, the flag the Ark checks (BLACKSMITH_BULLET_COMPLETE) is set, so firing the gun after the Dragun opens The Vet Visit. Config `GuaranteePastAccess` (default on); only affects Pluto.

## 0.1.0
- Pluto's past, The Vet Visit: a white veterinary clinic (exam table, cabinets, syringe cart, sink, scale, carrier, cat toys, cone of shame).
- Intro dialogue (lines editable in the config), then The Vet with four attacks: Booster Shot, Spray Bottle, Pill Time, and the Cone of Shame below half health.
- Beating him sets Pluto's past as killed, plays the credits tube and shows a Pluto win picture.
- Console: `vet_visit` jumps to the past from the Breach; `spawn pluto:the_vet` spawns the boss.
- Config `BepInEx/config/bogdan.etg.plutovetvisit.cfg`: boss health, DPS cap, music, room subtype, skip intro, debug ending, dialogue lines.
