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
