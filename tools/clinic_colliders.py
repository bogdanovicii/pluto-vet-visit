"""Collider audit of the clinic: where Pluto's feet can go, and whether a prop's drawing can end up over him.

Enter the Gungeon rules this models (decompiled PlayerController / tk2dBaseSprite):
- a standing sprite sorts by 2 * base - HeightOffGround at every screen pixel; the player's sprite HeightOffGround is -0.5,
  so he sorts by 2 * feet + 0.5. A prop at HeightOffGround 0 TIES with a player pressed against its collider from the south
  (his 4 px movement collider puts his feet 0.25 cell under the prop's base): the two sprites z-fight and the prop's front
  panel is drawn over him. That was the 0.12.0 reception counter (in-game screenshot 19.44.02). Standing props with a
  collider therefore stand at clinic_objects.STAND_HOG (-0.5), which sorts them exactly like the player.
- a prop's collider must cover its drawing's footprint: from the lowest opaque row, across the opaque width (a small margin
  allowed), so nobody's feet reach a spot inside the drawing; and no reachable pocket may sit behind furniture where the
  drawing covers the actor's feet (the space behind the counter where the receptionist stands).

PLUTO_FEET is Pluto's movement collider as the screenshot shows it (8 x 4 px, feet at the bottom). It is on the small side
on purpose: a smaller box reaches more of the room, so the reachability checks err towards flagging.
"""
import os
from collections import deque

import clinic_objects as O
import clinic_room as C

PX = 16
PLUTO_FEET = (8, 4)             # w, h in pixels
PLAYER_HOG = -0.5               # PlayerController keeps the primary player's sprite at -0.5
TIE_MARGIN = 0.25               # depth units a prop must stay behind a player pressed against it from the south
BOTTOM_TOLERANCE = 2            # px: collider bottom at most this far above the sprite's lowest opaque row
WIDTH_MARGIN = 4                # px: opaque drawing allowed outside the collider's sides within its rows
PLUTO_BODY_H = 16               # px above his feet box that must stay visible somewhere: less and he has vanished into a drawing


def spec(name):
    return next(o for o in O.OBJECTS if o.name == name)


def rects(o):
    """All collider rectangles (layer, off_x, off_y, w, h) of a prop spec."""
    return list(getattr(o, 'colliders', [o.collider] if o.collider else []))


def placed():
    """(name, (x, y)) of every placed prop, the two zone doors included (they stand in the wall gaps)."""
    return list(O.PROPS) + [(C.DOOR, C.NAMED['WardDoor']), (C.DOOR, C.NAMED['TheatreDoor'])]


def world_boxes(include_doors=False):
    """Collider boxes in room pixels: (name, (x, y), layer, x0, y0, x1, y1)."""
    out = []
    for name, (x, y) in placed():
        if name == C.DOOR and not include_doors:
            continue
        for layer, ox, oy, w, h in rects(spec(name)):
            x0, y0 = int(round(x * PX)) + ox, int(round(y * PX)) + oy
            out.append((name, (x, y), layer, x0, y0, x0 + w, y0 + h))
    return out


def blocked_grid(include_doors=False):
    """bytearray W*H (room pixels, row 0 = the room's south edge): 1 where walls or colliders block walking."""
    W, H = C.WIDTH * PX, C.HEIGHT * PX
    g = bytearray(W * H)
    for cy in range(C.HEIGHT):
        for cx in range(C.WIDTH):
            if not C.is_floor(cx, cy):
                for py in range(cy * PX, (cy + 1) * PX):
                    g[py * W + cx * PX:py * W + (cx + 1) * PX] = b'\x01' * PX
    for _, _, _, x0, y0, x1, y1 in world_boxes(include_doors):
        x0, y0, x1, y1 = max(0, x0), max(0, y0), min(W, x1), min(H, y1)
        for py in range(y0, y1):
            g[py * W + x0:py * W + x1] = b'\x01' * (x1 - x0)
    return g


def reachable(start=None, feet=PLUTO_FEET, include_doors=False):
    """Set-like bytearray of feet lower-left pixels Pluto's movement box can reach from `start` (cells; default his spawn).
    Doors are open (every zone is visited in turn)."""
    W, H = C.WIDTH * PX, C.HEIGHT * PX
    fw, fh = feet
    g = blocked_grid(include_doors)
    # summed-area table: the box at (x, y) is free when its sum is 0
    S = [0] * ((W + 1) * (H + 1))
    for y in range(H):
        run = 0
        row, prev, cur = y * W, y * (W + 1), (y + 1) * (W + 1)
        for x in range(W):
            run += g[row + x]
            S[cur + x + 1] = S[prev + x + 1] + run

    def free(x, y):
        if x < 0 or y < 0 or x + fw > W or y + fh > H:
            return False
        a, b = y * (W + 1), (y + fh) * (W + 1)
        return S[b + x + fw] - S[a + x + fw] - S[b + x] + S[a + x] == 0

    sx, sy = start if start is not None else C.NAMED['Spawn']
    sx, sy = int(sx * PX) - fw // 2, int(sy * PX)
    seen = bytearray(W * H)
    if not free(sx, sy):
        raise ValueError('start %s is blocked' % ((sx, sy),))
    seen[sy * W + sx] = 1
    q = deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < W and 0 <= ny < H and not seen[ny * W + nx] and free(nx, ny):
                seen[ny * W + nx] = 1
                q.append((nx, ny))
    return seen


def opaque(o):
    """Opaque pixel test of a prop's first frame in its own pixels, y up from the sprite's bottom."""
    rows, (w, h) = o.rows, o.size

    def at(px, py):
        if not (0 <= px < w and 0 <= py < h):
            return False
        r = rows[h - 1 - py]
        return px < len(r) and r[px] != '.'
    return at


def spec_problems(objects=None):
    """Static checks of every standing prop with a collider (the zone door is part of the wall and exempt)."""
    problems = []
    for o in (O.OBJECTS if objects is None else objects):
        if not o.collider or not o.stand or o.name == C.DOOR:
            continue
        w, h = o.size
        at = opaque(o)
        low = min(py for py in range(h) for px in range(w) if at(px, py))
        boxes = rects(o)
        bottom = min(oy for _, _, oy, _, _ in boxes)
        if bottom > low + BOTTOM_TOLERANCE:
            problems.append('%s: collider starts %d px above the drawing\'s lowest row %d' % (o.name, bottom, low))
        # the opaque drawing within the main collider's rows (the footprint band) must lie inside the colliders' columns, plus
        # the margin. Extra rectangles only add blocking; they may leave a gap on purpose (the receptionist's strip).
        for layer, ox, oy, cw, ch in boxes[:1]:
            for py in range(oy, oy + ch):
                cols = [px for px in range(w) if at(px, py)]
                if not cols:
                    continue
                covered = [any(bx - WIDTH_MARGIN <= px < bx + bw + WIDTH_MARGIN and by <= py < by + bh
                               for _, bx, by, bw, bh in boxes) for px in cols]
                if not all(covered):
                    miss = [px for px, c in zip(cols, covered) if not c]
                    problems.append('%s: drawing at x %d..%d on row %d is outside its collider' % (o.name, miss[0], miss[-1], py))
                    break
        # depth: a player pressed against the collider from the south must sort in front, from the north behind
        fh = PLUTO_FEET[1] / float(PX)
        prop_z = -o.height_off_ground                     # relative to 2 * base
        south = 2 * (bottom / float(PX) - fh) - PLAYER_HOG
        if prop_z - south < TIE_MARGIN:
            problems.append('%s: HeightOffGround %.2f ties with Pluto pressed against it from the south (margin %.2f < %.2f)'
                            % (o.name, o.height_off_ground, prop_z - south, TIE_MARGIN))
        top = max(oy + ch for _, _, oy, _, ch in boxes)
        north = 2 * (top / float(PX)) - PLAYER_HOG
        if north - prop_z < TIE_MARGIN:
            problems.append('%s: Pluto pressed against its back sorts in front of it (collider %d px deep)' % (o.name, top))
    return problems


def _standing_drawings():
    """(name, cell, x0, y0, w, h, depth, opaque) of every standing prop an actor can be drawn behind (walls and their decor excluded)."""
    out = []
    for name, (x, y) in placed():
        o = spec(name)
        if not o.stand or name == C.DOOR or name.startswith('pluto_wall_face') or C.cell(x, y) == '#':
            continue                                  # the zone doors are walked through once open
        w, h = o.size
        out.append((name, (x, y), int(round(x * PX)), int(round(y * PX)), w, h, 2 * y - o.height_off_ground, opaque(o)))
    return out


POCKET_PX = 8                   # a hidden spot is a pocket when something solid is this close north of Pluto's feet box


def hidden_spots(seen=None):
    """Reachable feet positions where Pluto vanishes: his feet box and the PLUTO_BODY_H pixels above it are all covered by the
    drawings of props sorted in front of him (a strip behind tall furniture, a pocket behind the counter).
    {prop placement: (count, sample feet cell)} keyed by the prop whose drawing covers his feet."""
    seen = reachable() if seen is None else seen
    W, H = C.WIDTH * PX, C.HEIGHT * PX
    fw, _ = PLUTO_FEET
    bh = PLUTO_BODY_H
    grid = blocked_grid()

    def blocked(x, y, w, h):
        return any(yy >= H or grid[yy * W + xx] for yy in range(y, y + h) for xx in range(max(0, x), min(W, x + w)))
    drawings = _standing_drawings()
    found = {}
    for name, cell, bx, by, w, h, depth, at in drawings:
        near = [d for d in drawings if d[2] < bx + w + fw and bx - fw < d[2] + d[4] and d[3] < by + h + bh and by - bh < d[3] + d[5]]
        for py in range(by, by + h):
            pz = 2 * (py / float(PX)) - PLAYER_HOG
            front = [d for d in near if d[6] < pz]
            if not any(d[0] == name and d[1] == cell for d in front):
                continue
            for px in range(bx - fw + 1, bx + w):
                if px < 0 or not seen[py * W + px]:
                    continue
                if not at(px - bx, py - by):
                    continue
                covered = True
                for iy in range(bh - 1, -1, -1):              # the head row first: most spots fail there
                    for ix in range(fw):
                        qx, qy = px + ix, py + iy
                        if not any(d[7](qx - d[2], qy - d[3]) for d in front):
                            covered = False
                            break
                    if not covered:
                        break
                # only a pocket counts: something solid within POCKET_PX north of his feet box (a wall, the next prop), so
                # he is squeezed in between the drawing and it. Free-standing tall props you walk round are fine.
                if covered and blocked(px, py + PLUTO_FEET[1], fw, POCKET_PX):
                    count, sample = found.get((name, cell), (0, (px / float(PX), py / float(PX))))
                    found[(name, cell)] = (count + 1, sample)
    return found


def npc_spots_reachable(seen=None):
    """NPCs standing behind furniture (their feet inside a standing prop's drawing): the ones Pluto's feet can reach."""
    import cast_layout
    import npc_poses
    seen = reachable() if seen is None else seen
    W = C.WIDTH * PX
    out = []
    for npc, (x, y) in C.NPCS:
        cw, _ = npc_poses.NPCS[cast_layout.NPC_OBJECTS[npc]]['canvas']
        fx, fy = int(round(x * PX + cw / 2.0)), int(round(y * PX))
        behind = False
        for name, (px, py) in placed():
            o = spec(name)
            if o.stand and o.collider and name != C.DOOR and py < y and opaque(o)(fx - int(round(px * PX)), fy - int(round(py * PX))):
                behind = True
        if not behind:
            continue
        fw, fh = PLUTO_FEET
        if any(seen[yy * W + xx] for yy in range(fy - fh + 1, fy + 1) for xx in range(fx - fw + 1, fx + 1) if yy >= 0):
            out.append((npc, (x, y)))
    return out


def problems():
    seen = reachable()
    out = spec_problems()
    for (name, cell), (count, sample) in sorted(hidden_spots(seen).items()):
        out.append('%s at %s: Pluto vanishes inside its drawing at %d feet positions, e.g. %s' % (name, cell, count, sample))
    for npc, cell in npc_spots_reachable(seen):
        out.append('%s at %s stands behind furniture, but Pluto can walk there' % (npc, cell))
    return out


# test points drawn on the preview: (label, feet lower-left in cells)
TEST_POINTS = [
    ('counter south', (29.25, 13.0 - PLUTO_FEET[1] / 16.0)),
    ('receptionist', (29.25, 14.3)),
    ('counter west end', (25.5, 14.5)),
    ('counter east end', (33.0, 14.5)),
    ('kennel door', (3.0, 22.0)),
    ('exam table side', (14.75, 46.5)),
]


def preview_image(project, scale=2):
    from PIL import Image, ImageDraw
    base = C.sprite_preview_image(project).convert('RGBA')
    W, H = C.WIDTH * PX, C.HEIGHT * PX
    seen = reachable()
    shade = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sp = shade.load()
    for y in range(H):
        row = y * W
        for x in range(W):
            if not seen[row + x] and C.is_floor(x // PX, y // PX):
                sp[x, H - 1 - y] = (0x30, 0x60, 0xD0, 70)      # floor Pluto's feet (lower-left) never reach: blue tint
    base.alpha_composite(shade)
    im = base.resize((W * scale, H * scale), Image.NEAREST)
    d = ImageDraw.Draw(im)
    for name, cell, layer, x0, y0, x1, y1 in world_boxes(include_doors=True):
        colour = (0xE0, 0x10, 0x10, 255) if layer == 'high' else (0xFF, 0x60, 0x60, 255)
        d.rectangle((x0 * scale, (H - y1) * scale, x1 * scale - 1, (H - y0) * scale - 1), outline=colour)
    fw, fh = PLUTO_FEET
    for label, (cx, cy) in TEST_POINTS:
        x0, y0 = int(round(cx * PX)), int(round(cy * PX))
        ok = 0 <= y0 < H and 0 <= x0 < W and seen[y0 * W + x0]
        colour = (0x10, 0xB0, 0x30, 255) if ok else (0xF0, 0xB0, 0x00, 255)
        d.rectangle((x0 * scale, (H - y0 - fh) * scale, (x0 + fw) * scale - 1, (H - y0) * scale - 1), outline=colour, width=2)
        d.text(((x0 + fw) * scale + 2, (H - y0 - fh) * scale - 10), label + (' reachable' if ok else ' blocked'), fill=colour)
    return im


def write_preview(project):
    p = os.path.join(project, 'docs', 'preview', 'clinic-colliders.png')
    preview_image(project).save(p)
    return p


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    for line in problems():
        print('PROBLEM', line)
    print(write_preview(os.path.dirname(here)))
