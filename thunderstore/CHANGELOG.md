# Changelog

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
