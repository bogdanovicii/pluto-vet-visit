"""Enemy projectile sprites for the Vet Visit (right-facing, MiddleCenter anchored in game).

0.12: one readable sprite per attack family, sized like vanilla enemy bullets (7-16 px), each with a dark outline,
a bright core and its own colour, so a pattern can be told apart at a glance:

  syringe  steel barrel, glowing blue dose, needle forward   aimed bursts (Booster Shot, Snip Time, Tech burst, Syringe Tech)
  dart     orange tuft, red body, steel tip                  the Vet Tech's dart rifle
  vaccine  bright blue orb                                   rings and spirals (Cone of Shame, Vaccination Spiral, Snip ring)
  droplet  teal teardrop pointing forward                    fans and walls (Spray Bottle, Droplet Wall, the Nurse's fan)
  tranq    lime green bubble                                 the Nurse's tranquilizer spray and IV line
  pill     red and white capsule                             Pill Time (shoot it to pop it)
  tablet   white tablet with a red cross                     what a pill bursts into
  scalpel  teal handle, steel blade                          the scalpel ring
  stitch   red suture X                                      stitches (stop, hang, re-aim)
  net      orange hoop, steel mesh                           the Nurse's net
  cloud    white puff, plum rim                              anesthesia clouds

BANK is the single source of truth for bank name -> sprite, hitbox and orientation; src/*.cs Entry calls must match it
(tools/tests/test_projectiles.py and tools/validate.py check). Hitboxes are Manual boxes centred on the projectile,
a little smaller than the art (vanilla hitboxes sit inside the sprite); the game rotates them with the bullet.
"""
import os

from PIL import Image, ImageDraw

from vetpixel import R, save, image

SPRITES = {
    # needle forward: plunger, rod, glass barrel with a glowing dose (light top-left), hub, two-pixel needle
    'vet_syringe_001': R([
        "oo.oooooooo...",
        "o&.o^K^^^^ooo.",
        "o&#o>>>***%KKo",
        "o&#o>*****%&&o",
        "o&.o**[[[[ooo.",
        "oo.oooooooo...",
    ]),
    # tranquilizer dart: orange tuft, red body with a highlight, steel tip
    'vet_dart_001': R([
        "ooo..........",
        "o:?ooooooooo.",
        "o??!``!!!!&&o",
        "o?7}!!}}}}oo.",
        "oooooooooo...",
    ]),
    # vaccine orb: white glint, glow ring, blue body, deep blue shade bottom-right
    'vet_vaccine_001': R([
        "..oooo..",
        ".o>>**o.",
        "o>KK>**o",
        "o>K>***o",
        "o>>***[o",
        "o****[[o",
        ".o*[[[o.",
        "..oooo..",
    ]),
    # teal teardrop, point forward
    'vet_droplet_001': R([
        "..ooo....",
        ".o<<$oo..",
        "o<KK<$$oo",
        "o<K<$$$~o",
        "o<<$$$~oo",
        ".o$$~oo..",
        "..ooo....",
    ]),
    # lime green tranquilizer bubble
    'vet_tranq_001': R([
        "..ooo..",
        ".o]]5o.",
        "o]K]55o",
        "o]]55{o",
        "o555{{o",
        ".o5{{o.",
        "..ooo..",
    ]),
    # two-tone capsule: red half, white half
    'vet_pill_001': R([
        ".oooooooo.",
        "o``!!KKWWo",
        "o`!!!WWWwo",
        "o!!!}WWwwo",
        "o}}}}wwwwo",
        ".oooooooo.",
    ]),
    # the pill's fragments: a white tablet scored with a red cross
    'vet_tablet_001': R([
        "..ooo..",
        ".oKWWo.",
        "oKW!Wwo",
        "oW!!!wo",
        "oWw!wwo",
        ".owwwo.",
        "..ooo..",
    ]),
    # scalpel: teal handle, dark bolster, steel blade with a bright edge, tip forward
    'vet_scalpel_001': R([
        ".oooooooooooo.",
        "o<<<<$~#&KKK&o",
        "o$$$$~~#&&&%oo",
        ".ooooooo%%oo..",
        "........oo....",
    ]),
    # suture X: red thread, light upper strands, dark lower strands
    'vet_stitch_001': R([
        "oo.....oo",
        "o`o...o!o",
        ".o`o.o!o.",
        "..o`!!o..",
        "...o!o...",
        "..o!!}o..",
        ".o!o.o}o.",
        "o!o...o}o",
        "oo.....oo",
    ]),
    # the Nurse's butterfly net, thrown hoop first: an orange hoop around a steel mesh with open holes
    'vet_net_001': R([
        "....oooooo....",
        "..oo??::??oo..",
        ".o?.%..%..%7o.",
        ".o?.%..%..%7o.",
        "o?%%&%%&%%&%7o",
        "o?..%..%..%.7o",
        "o?..%..%..%.7o",
        "o?%%&%%&%%&%7o",
        "o?..%..%..%.7o",
        "o?..%..%..%.7o",
        ".o7%&%%&%%&7o.",
        ".o7.%..%..%7o.",
        "..oo777777oo..",
        "....oooooo....",
    ]),
    # the Vet's anesthesia cloud: a slow, lingering puff, white core, plum rim, solid outline so it reads on white tiles
    'vet_cloud_001': R([
        ".....oooooo.....",
        "...oo((WW((oo...",
        "..o((WWKKWW((o..",
        ".o((WWKKKKWW((o.",
        ".o(WWKKKKKKWW(o.",
        "o((WWKKKKKKWW((o",
        "o(WWKKKKKKKKWW(o",
        "o(WWKKKKKKKKWW(o",
        "o(wWWKKKKKKWWw(o",
        "o((wWWKKKKWWw((o",
        "o)(wwWWWWWWww()o",
        ".o)(wwWWWWww()o.",
        ".o))((wwww(())o.",
        "..o))((((())o...",
        "...oo))))))oo...",
        ".....oooooo.....",
    ]),
}

# bank name -> (sprite, hitbox width, hitbox height, points along travel)
BANK = {
    'syringe': ('vet_syringe_001', 10, 4, True),
    'dart': ('vet_dart_001', 9, 3, True),
    'vaccine': ('vet_vaccine_001', 6, 6, False),
    'droplet': ('vet_droplet_001', 7, 5, True),
    'tranq': ('vet_tranq_001', 5, 5, False),
    'pill': ('vet_pill_001', 8, 4, True),
    'tablet': ('vet_tablet_001', 5, 5, False),
    'scalpel': ('vet_scalpel_001', 10, 3, True),
    'stitch': ('vet_stitch_001', 5, 5, False),
    'net': ('vet_net_001', 10, 10, False),
    'cloud': ('vet_cloud_001', 12, 12, False),
}


def size(sprite):
    rows = SPRITES[sprite]
    return len(rows[0]), len(rows)


def write(project):
    out = os.path.join(project, 'Resources', 'SpriteRoot', 'ProjectileCollection')
    paths = []
    for name, rows in SPRITES.items():
        p = os.path.join(out, name + '.png')
        save(rows, p)
        paths.append(p)
    return paths


def preview(project, scale=6):
    """docs/preview/projectiles-sheet.png: every bank sprite at 6x on a clinic-white and a dark tile, its name, size and
    its hitbox outline (red) as the game centres it (MiddleCenter anchor, offset -hitbox/2 in integer pixels)."""
    cell_w, cell_h, cols = 17 * scale * 2 + 30, 17 * scale + 34, 3
    rows_n = (len(BANK) + cols - 1) // cols
    sheet = Image.new('RGBA', (cols * cell_w, rows_n * cell_h), (70, 70, 90, 255))
    d = ImageDraw.Draw(sheet)
    for i, (bank, (sprite, hw, hh, rotates)) in enumerate(BANK.items()):
        w, h = size(sprite)
        cx, cy = (i % cols) * cell_w + 8, (i // cols) * cell_h + 6
        d.text((cx, cy), '%s  %s  %dx%d  hit %dx%d%s' % (bank, sprite, w, h, hw, hh, '  rotates' if rotates else ''),
               fill=(255, 255, 255, 255))
        big = image(SPRITES[sprite]).resize((w * scale, h * scale), Image.NEAREST)
        for k, ground in enumerate(((244, 246, 248, 255), (40, 40, 48, 255))):
            ox, oy = cx + k * (17 * scale + 10), cy + 16
            d.rectangle([ox, oy, ox + 17 * scale - 1, oy + 17 * scale - 1], fill=ground)
            sx, sy = ox + (17 - w) * scale // 2, oy + (17 - h) * scale // 2
            sheet.alpha_composite(big, (sx, sy))
            # hitbox: projectile position is the sprite centre; C# offset is -hw/2 truncated, in world pixels (y up),
            # so in image rows (y down) the box starts hh - hh//2 above the centre
            bx = sx + (w / 2.0 - hw // 2) * scale
            by = sy + (h / 2.0 - (hh - hh // 2)) * scale
            d.rectangle([bx, by, bx + hw * scale - 1, by + hh * scale - 1], outline=(255, 40, 40, 255), width=2)
    path = os.path.join(project, 'docs', 'preview', 'projectiles-sheet.png')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path)
    return path
