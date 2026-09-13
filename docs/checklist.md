# In-game checklist (Steam machine, SteamOS/Proton, r2modman)

Nothing here can run on the build Mac. Each milestone is a test zip; send back `vet_check.sh` output and screenshots.

## Milestone 1 — plumbing (Pluto_Vet_Visit-0.1.0.zip)

Setup: import the latest `Pluto_The_Cat-*.zip` and `dist/Pluto_Vet_Visit-0.1.0.zip` (r2modman -> Settings -> Import local mod).
Launch once, then set `[Debug] DebugEndAfterSeconds = 8` in `BepInEx/config/bogdan.etg.plutovetvisit.cfg`.

1. Launch. Console shows `[VetVisit] found Pluto`, `registered level tt_pluto_past`, `The Vet Visit is ready`, and no `step "..." failed`.
2. In the Breach select Pluto, open the console and run `vet_visit`. Expected: fade to black, then a white/grey lab-tiled
   room 26 x 18 with a doorway at the bottom middle; Pluto near the bottom-left. Log: `built past dungeon`, `clinic ready`.
3. After 8 s: freeze frame, credits tube, the win page (Pluto's win picture once Task 9 ships it). Log: `past killed`.
   The main-menu button returns to the Breach.
4. Back in the Breach, Pluto's info panel shows the past as killed.
5. The real route: as Pluto, talk to the Blacksmith (Bullet That Can Kill The Past), beat the Lich, fire the Gun in the Ark.
   Expected: the clinic loads instead of the win page.
6. Session hygiene: in the same session pick the Marine and run `load_level fs_soldier`. Expected: the Primerdyne lab, not the clinic.

Send back: `./vet_check.sh` output, a screenshot of step 2, and whether steps 4-6 passed.

## Milestone 2 — the clinic

Same setup; `DebugEndAfterSeconds` may stay at 8 so the past still ends by itself.
1. `vet_visit`: the room is dressed: six glass cabinets and a poster along the top, the steel exam table in the middle,
   a cart with syringes, a sink, a scale, the carrier bottom-left, toys and a cone on the floor.
2. Pluto cannot walk through the table, cabinets, sink, carrier or scratching post; he walks over toys, the tray, the cone and the scale.
3. Bullets fired at the table fly over it; bullets at a cabinet stop.
4. Two speech bubbles appear behind the table (the Vet's lines from the config), then a hiss from Pluto; the camera
   returns and Pluto can move. `[Debug] SkipIntro = true` skips them.
5. Props render above the floor and below Pluto when he walks in front of them (report anything drawn on top of Pluto).
Send back: screenshot of the room, and any prop that looks wrong.
