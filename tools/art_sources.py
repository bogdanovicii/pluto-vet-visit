"""Approved art made with the pluto-artist skill (Gemini first, converted to pixel art, reviewed).

Sources live in reference/art/<piece>/final.png (or final_001.png ... for clips). install() copies them to the
Resources path the game loads; make_art.py runs it last so approved art always replaces drawn stand-ins."""
import os
import shutil
from collections import OrderedDict

from PIL import Image

import clinic_objects as O

PROJECT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
ART_ROOT = 'reference/art'
MAX_COLOURS = {'sprite': 40, 'card': 64, 'picture': 64}
KENNEL_CLIPS = OrderedDict([('idle', 4), ('react', 4), ('rattle', 3), ('freed', 2)])
FREED_ANIMALS = ('cat', 'dog', 'cone')        # 0.14.2 rescue: the animals that run out of their cages
KENNEL_STEMS = ('kennel_cat', 'kennel_dog', 'kennel_cone', 'kennel_open_r', 'kennel_open_l')
MASK_CLIPS = OrderedDict([('mask_on', 5), ('mask_idle', 5), ('mask_move', 6), ('mask_tell', 4), ('mask_fire', 4), ('mask_die', 8)])
ENDING_CLIPS = OrderedDict([('bianca', OrderedDict([('kneel', 3), ('carry', 2), ('carry_walk', 6)])),
                            ('bogdan', OrderedDict([('pat', 3)]))])


def _size_of(png):
    for o in O.OBJECTS:
        if o.png == png:
            return o.size
    raise KeyError(png)


def _pieces():
    p = OrderedDict()
    p['vet_bosscard'] = dict(dest='Resources/Boss/vet_bosscard.png', canvas=(427, 240), frames=None, kind='card')
    p['past_win_pic'] = dict(dest='Resources/past_win_pic.png', canvas=(115, 71), frames=None, kind='picture')
    p['breach_trophy'] = dict(dest='Resources/Objects/breach_trophy.png', canvas=(32, 40), frames=None, kind='sprite')
    for who, clips in ENDING_CLIPS.items():
        for clip, n in clips.items():
            p['%s_%s' % (who, clip)] = dict(dest='Resources/Npcs/%s/%s/%s_%s_{k:03d}.png' % (who, clip, who, clip),
                                            canvas=(48, 40), frames=n, kind='sprite')
    for clip, n in MASK_CLIPS.items():
        p['vet_' + clip] = dict(dest='Resources/Boss/vet/%s/vet_%s_{k:03d}.png' % (clip, clip), canvas=(48, 40), frames=n, kind='sprite')
    for stem in KENNEL_STEMS:
        for clip, n in KENNEL_CLIPS.items():
            p['%s_%s' % (stem, clip)] = dict(dest='Resources/Objects/%s_%s_f{k}.png' % (stem, clip),
                                             canvas=_size_of(stem), frames=n, kind='sprite')
    for kind in FREED_ANIMALS:
        p['freed_' + kind] = dict(dest='Resources/Objects/freed_%s_f{k}.png' % kind, canvas=O.freed_animal_size(kind), frames=2, kind='sprite')
    return p


PIECES = _pieces()


def source_paths(piece):
    n = PIECES[piece]['frames']
    if not n:
        return ['%s/%s/final.png' % (ART_ROOT, piece)]
    return ['%s/%s/final_%03d.png' % (ART_ROOT, piece, k) for k in range(1, n + 1)]


def dest_paths(project, piece):
    spec = PIECES[piece]
    n = spec['frames']
    if not n:
        return [os.path.join(project, spec['dest'])]
    return [os.path.join(project, spec['dest'].format(k=k)) for k in range(1, n + 1)]


def check(piece, root=PROJECT):
    spec = PIECES[piece]
    problems = []
    for rel in source_paths(piece):
        path = os.path.join(root, rel)
        if not os.path.exists(path):
            problems.append('%s: missing %s' % (piece, rel))
            continue
        im = Image.open(path).convert('RGBA')
        if im.size != tuple(spec['canvas']):
            problems.append('%s: canvas %s, expected %s (%s)' % (piece, im.size, tuple(spec['canvas']), rel))
            continue
        alphas = set(a for (_, _, _, a) in im.getdata())
        if not alphas <= {0, 255}:
            problems.append('%s: semi-transparent alpha %s (%s)' % (piece, sorted(alphas - {0, 255})[:4], rel))
        colours = set(px[:3] for px in im.getdata() if px[3] == 255)
        if len(colours) > MAX_COLOURS[spec['kind']]:
            problems.append('%s: %d colours > %d (%s)' % (piece, len(colours), MAX_COLOURS[spec['kind']], rel))
        if spec['kind'] == 'picture' and alphas != {255}:
            problems.append('%s: picture must be fully opaque (%s)' % (piece, rel))
        if spec['kind'] == 'card':
            w, h = im.size
            if any(im.getpixel((x, y))[3] for x in range(190) for y in range(h)):
                problems.append('%s: card pixels at x < 190 must be transparent (%s)' % (piece, rel))
            clear = sum(1 for px in im.getdata() if px[3] == 0)
            if clear < 0.5 * w * h:
                problems.append('%s: card must be at least 50%% transparent (%s)' % (piece, rel))
    return problems


def missing(root=PROJECT):
    return [p for piece in PIECES for p in check(piece, root) if ': missing ' in p]


def install(project):
    written = []
    for piece in PIECES:
        srcs = [os.path.join(project, s) for s in source_paths(piece)]
        if not all(os.path.exists(s) for s in srcs):
            continue
        for src, dst in zip(srcs, dest_paths(project, piece)):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copyfile(src, dst)
            written.append(dst)
    return written


if __name__ == '__main__':
    for p in install(PROJECT):
        print('art', p)
    for m in missing(PROJECT):
        print('todo', m)
