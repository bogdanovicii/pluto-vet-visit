"""Enemy projectile sprites for The Vet (right-facing, MiddleCenter anchored in game)."""
import os

from vetpixel import R, save

SPRITES = {
    'vet_syringe_001': R([
        "o&&&&&&&&o..",
        "o&****&&&o%%",
        "o&&&&&&&&o%%",
        "oooooooooo..",
    ]),
    'vet_droplet_001': R([
        "..o..",
        ".o*o.",
        "o***o",
        "o*K*o",
        ".ooo.",
    ]),
    'vet_pill_001': R([
        ".oooooo.",
        "o!!!KKKo",
        "o!!!KKKo",
        ".oooooo.",
    ]),
    # the Nurse's butterfly net, thrown hoop first: a steel ring with a white mesh
    'vet_net_001': R([
        "....oooo....",
        "..oo&&&&oo..",
        ".o&&wWwWw&o.",
        ".o&WwWwWwWo.",
        "o&wWwWwWwW&o",
        "o&WwWwWwWw&o",
        "o&wWwWwWwW&o",
        "o&WwWwWwWw&o",
        ".o&wWwWwW&o.",
        ".o&&WwWw&&o.",
        "..oo&&&&oo..",
        "....oooo....",
    ]),
}


def write(project):
    out = os.path.join(project, 'Resources', 'SpriteRoot', 'ProjectileCollection')
    paths = []
    for name, rows in SPRITES.items():
        p = os.path.join(out, name + '.png')
        save(rows, p)
        paths.append(p)
    return paths
