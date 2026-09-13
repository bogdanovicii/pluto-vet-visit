# Pluto the Cat - The Vet Visit (test package)

Pluto's past: a white veterinary clinic and The Vet, a doctor with a syringe gun. Install Pluto_The_Cat first
(r2modman -> Settings -> Import local mod), then this zip. From the Breach, as Pluto, open the console and run
`vet_visit` to jump straight into the past for testing.

**Normal run:** play as Pluto, reach the Forge (chamber 5) and talk to the Blacksmith — she gives Pluto the
Bullet That Can Kill The Past, exactly like a vanilla Gungeoneer. Beat the High Dragun and fire the gun at the
Ark; Pluto drops into his past, The Vet Visit. Run `vet_check.sh` after playing to grade the log.

## Config

Settings live in `BepInEx/config/bogdan.etg.plutovetvisit.cfg`:
- `Enabled` - attach The Vet Visit to Pluto.
- `GuaranteePastAccess` - when Pluto takes the bullet from the Blacksmith, set the flag the Ark needs so his past opens.
- `BossHealth` - The Vet's health.
- `BossDpsCap` - boss damage-per-second cap for the past level (-1 = none).
- `BossMusic` - Wwise event played during the fight.
- `RoomVisualSubtype` - override the room's visual subtype in the lab tileset (-1 = default).
- `SkipIntro` - skip the dialogue before the fight.
- `DebugEndAfterSeconds` - if > 0, the past ends by itself after this many seconds (tests the ending without a boss).
- `Line1` - the Vet's first line.
- `Line2` - the Vet's second line.
- `Line3` - Pluto's answer.

The plugin does nothing if Pluto_The_Cat is missing.
