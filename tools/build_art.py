"""Convert the chosen Gemini generations into candidate game art (pluto-artist step 3), piece by piece.

Every piece names its chosen generation, the frames to take, the target canvas and how the art sits on it. Frames are
cut with cut_frames.py, each frame is copied into pixels with the skill's pixelize.py at one shared scale per clip (so the
character does not change size between frames), and placed feet-down on the canvas. Output goes to a build folder
(default the session scratchpad); only a reviewed pass is copied to reference/art/<piece>/ by --approve.

Usage:
  python3 tools/build_art.py --out <build dir> [piece ...]
  python3 tools/build_art.py --out <build dir> --approve piece [piece ...]
"""
import argparse
import os
import shutil
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.normpath(os.path.join(HERE, '..'))
REPO = os.path.normpath(os.path.join(PROJECT, '..'))
PIXELIZE = os.path.join(REPO, '.claude', 'skills', 'pluto-artist', 'scripts', 'pixelize.py')
GEMINI = os.path.join(PROJECT, 'reference', 'gemini')
sys.path.insert(0, HERE)
import art_sources  # noqa: E402
import cut_frames  # noqa: E402

OUTLINE = '1E1614'

# piece: (generation, frame indices (1-based, in cut order) or None for a single image, figure height in px,
#         outline colour or None, colours, keep colours, pre-crop of the sheet as fractions or None)
CLIPS = {
    'bianca_kneel': ('bianca_ending/bianca_ending_c3.png', [1, 2, 3], 38, OUTLINE, 20, ['F2C230'], None),
    'bianca_carry': ('bianca_ending/bianca_ending_c3.png', [4, 5], 38, OUTLINE, 22, ['F2C230'], None),
    'bianca_carry_walk': ('bianca_ending/bianca_ending_c3.png', [7, 8, 9, 10, 11, 12], 38, OUTLINE, 22, ['F2C230'], None),
    'bogdan_pat': ('bogdan_pat/bogdan_pat_c2.png', [1, 2, 3], 38, OUTLINE, 18, [], None),
    'vet_mask_on': ('vet_mask_on/vet_mask_on_c2.png', [1, 2, 3, 4, 5], 39, None, 24, ['8EC8E8'], None),
    'vet_mask_idle': ('vet_mask_idle/vet_mask_idle.png', [1, 2, 3, 4, 5], 39, None, 24, ['8EC8E8'], None),
    'vet_mask_move': ('vet_mask_move/vet_mask_move_c2.png', [1, 2, 3, 4, 5, 6], 39, None, 24, ['8EC8E8'], (0, 0, 1, 0.93)),
    'vet_mask_tell': ('vet_mask_tell/vet_mask_tell.png', [1, 2, 3, 4], 39, None, 24, ['8EC8E8'], None),
    'vet_mask_fire': ('vet_mask_fire/vet_mask_fire_c2.png', [1, 2, 3, 4], 39, None, 24, ['8EC8E8'], None),
    'vet_mask_die': ('vet_mask_die/vet_mask_die.png', [1, 2, 3, 4, 5, 6, 7, 9], 39, None, 24, ['8EC8E8'], None),
}

# single images: (generation, crop fractions or None, grid WxH, place X,Y, colours, outline)
SINGLES = {
    'vet_bosscard': ('vet_bosscard/vet_bosscard_c2.png', (0.36, 0.0, 1.0, 1.0), (232, 229), (193, 6), 38, OUTLINE),
    'past_win_pic': ('past_win_pic/past_win_pic.png', (0.0, 0.03, 1.0, 1.0), (115, 71), (0, 0), 38, None),
    'breach_trophy': ('breach_trophy/breach_trophy.png', (0.08, 0.12, 0.92, 1.0), (30, 36), (1, 4), 16, OUTLINE),
}


def pixelize(src, grid, out, colours, outline, keep, canvas, place, bg='auto'):
    cmd = [sys.executable, PIXELIZE, src, '--grid', '%dx%d' % grid, '--out', out, '--colors', str(colours), '--bg', bg,
           '--canvas', '%dx%d' % canvas, '--place=%d,%d' % place]
    if outline:
        cmd += ['--outline', outline]
    for k in keep:
        cmd += ['--keep', k]
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL)


def dechroma(path, outline=None):
    """Remove chroma-key green left on the silhouette edge by the background removal: a lime pixel (green far above red
    and blue) becomes transparent, or the outline colour when it sits inside the art. Teal scrubs are not lime."""
    im = Image.open(path).convert('RGBA')
    px = im.load()
    w, h = im.size
    oc = tuple(int(outline[i:i + 2], 16) for i in (0, 2, 4)) + (255,) if outline else None
    fixed = 0
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a and g > 150 and g > r + 70 and g > b + 70:
                inside = all(0 <= x + dx < w and 0 <= y + dy < h and px[x + dx, y + dy][3]
                             for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                px[x, y] = oc if (inside and oc) else (0, 0, 0, 0)
                fixed += 1
    im.save(path)
    return fixed


def build_clip(piece, out_dir):
    gen, take, fig_h, outline, colours, keep, precrop = CLIPS[piece]
    canvas = art_sources.PIECES[piece]['canvas']
    sheet = os.path.join(GEMINI, gen)
    if precrop:
        im = Image.open(sheet)
        w, h = im.size
        tmp = os.path.join(out_dir, piece + '_sheet.png')
        im.crop((int(precrop[0] * w), int(precrop[1] * h), int(precrop[2] * w), int(precrop[3] * h))).save(tmp)
        sheet = tmp
    frames = cut_frames.cut(sheet)
    if max(take) > len(frames):
        raise SystemExit('%s: needs frame %d, sheet has %d' % (piece, max(take), len(frames)))
    picked = [frames[i - 1] for i in take]
    row_h = max(f.height for f in picked)          # one scale for the whole clip
    scale = fig_h / float(row_h)
    written = []
    for n, f in enumerate(picked, 1):
        src = os.path.join(out_dir, '%s_src_%03d.png' % (piece, n))
        # bottom-align every frame on a common-height strip so the feet land on the same row
        strip = Image.new('RGB', (f.width, row_h), (0, 255, 0))
        strip.paste(f, (0, row_h - f.height))
        strip.save(src)
        # the clip's scale, unless this frame would overflow the canvas width (a body lying down): then only it shrinks
        s_f = min(scale, (canvas[0] - 1) / float(f.width))
        gw = max(1, int(round(f.width * s_f)))
        gh = max(1, int(round(row_h * s_f)))
        place = ((canvas[0] - gw) // 2, canvas[1] - gh)
        dst = os.path.join(out_dir, piece, 'final_%03d.png' % n)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        pixelize(src, (gw, gh), dst, colours, outline, keep, canvas, place)
        dechroma(dst, outline)
        written.append(dst)
    return written


def build_single(piece, out_dir):
    gen, crop, grid, place, colours, outline = SINGLES[piece]
    canvas = art_sources.PIECES[piece]['canvas']
    src = os.path.join(GEMINI, gen)
    if crop:
        im = Image.open(src)
        w, h = im.size
        src = os.path.join(out_dir, piece + '_src.png')
        im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h))).save(src)
    dst = os.path.join(out_dir, piece, 'final.png')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    bg = 'none' if art_sources.PIECES[piece]['kind'] == 'picture' else 'auto'
    pixelize(src, grid, dst, colours, outline, [], canvas, place, bg=bg)
    if bg != 'none':
        print('%s: %d chroma pixels removed' % (piece, dechroma(dst, outline)))
    return [dst]


def approve(piece, out_dir):
    dest_dir = os.path.join(PROJECT, art_sources.ART_ROOT, piece)
    os.makedirs(dest_dir, exist_ok=True)
    for rel in art_sources.source_paths(piece):
        name = os.path.basename(rel)
        shutil.copyfile(os.path.join(out_dir, piece, name), os.path.join(PROJECT, rel))
    problems = art_sources.check(piece)
    print('approved %s: %s' % (piece, 'ok' if not problems else problems))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pieces', nargs='*')
    ap.add_argument('--out', required=True)
    ap.add_argument('--approve', action='store_true')
    a = ap.parse_args()
    names = a.pieces or list(SINGLES) + list(CLIPS)
    os.makedirs(a.out, exist_ok=True)
    for piece in names:
        if a.approve:
            approve(piece, a.out)
            continue
        files = build_single(piece, a.out) if piece in SINGLES else build_clip(piece, a.out)
        print('%s: %d file(s)' % (piece, len(files)))


if __name__ == '__main__':
    main()
