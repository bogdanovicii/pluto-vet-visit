# Pluto the Cat - The Vet Visit (test package)

Pluto's past: a white veterinary clinic (waiting room, ward, operating theatre) and The Vet, a doctor with a syringe
gun.

**Requires Pluto_The_Cat.** It is not listed as a manifest dependency (Pluto_The_Cat has no Thunderstore coordinate yet), so
install it by hand: r2modman -> Settings -> Import local mod -> Pluto_The_Cat zip first (built against 2.16.2), then
this zip. From the Breach, as Pluto, open the console and run
`vet_visit` to jump straight into the past for testing.

**Normal run:** play as Pluto, reach the Forge (chamber 5) and talk to the Blacksmith — she gives Pluto the
Bullet That Can Kill The Past, exactly like a vanilla Gungeoneer. Beat the High Dragun and fire the gun at the
Ark; Pluto drops into his past, The Vet Visit. Run `vet_check.sh` after playing to grade the log.

## Config

Settings live in `BepInEx/config/bogdan.etg.plutovetvisit.cfg`, in sections General (`Enabled`,
`GuaranteePastAccess`), Boss, Balance, Patterns, Waves, Cast, Story (every dialogue line), Room, Mood, Props, Breach and
Debug (`SkipIntro`, `SkipWaves`, `DebugEndAfterSeconds`). Each key has its description in the file.

The plugin does nothing if Pluto_The_Cat is missing.
