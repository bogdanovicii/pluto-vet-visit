"""Cut animation frames out of a Gemini sprite sheet on a flat chroma background (pluto-artist step 3 helper).

Sheets come back in one or more rows with uneven spacing, so frames are found by their gaps: rows are separated by
background-only lines, and sprites inside a row by background-only columns. Each frame is cropped with the row's
common top and bottom (so the ground line stays aligned across frames) and written as <out>/frame_<n>.png, in
reading order. Pass --take to pick frames by index (1-based, e.g. 1,2,3 or 4-5) and their output numbering.

Usage: python3 tools/cut_frames.py sheet.png --out build/bianca_carry --take 4-5
"""
import argparse
import os

from PIL import Image


def is_bg(px, bg, tol):
    return all(abs(int(a) - int(b)) <= tol for a, b in zip(px[:3], bg))


def spans(flags, min_gap):
    """[(start, end)] runs of True, merging runs separated by fewer than min_gap False entries."""
    runs, start, gap = [], None, 0
    for i, f in enumerate(flags + [False] * (min_gap + 1)):
        if f:
            if start is None:
                start = i
            gap = 0
            end = i
        elif start is not None:
            gap += 1
            if gap > min_gap:
                runs.append((start, end + 1))
                start = None
    return runs


def parse_take(text, count):
    if not text:
        return list(range(1, count + 1))
    out = []
    for part in text.split(','):
        if '-' in part:
            a, b = part.split('-')
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def cut(path, bg=(0, 255, 0), tol=90, min_gap=6, min_size=24):
    im = Image.open(path).convert('RGB')
    w, h = im.size
    px = im.load()
    fg_row = [any(not is_bg(px[x, y], bg, tol) for x in range(0, w, 2)) for y in range(h)]
    frames = []
    for top, bottom in spans(fg_row, min_gap):
        if bottom - top < min_size:
            continue
        # column gaps are read above the feet (the top 80 % of the row): shadows and ground lines join frames at the bottom
        scan_bottom = top + max(1, int((bottom - top) * 0.8))
        fg_col = [any(not is_bg(px[x, y], bg, tol) for y in range(top, scan_bottom, 2)) for x in range(w)]
        for left, right in spans(fg_col, min_gap):
            if right - left < min_size // 2:
                continue
            frames.append(im.crop((left, top, right, bottom)))
    return frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sheet')
    ap.add_argument('--out', required=True)
    ap.add_argument('--take', default='')
    ap.add_argument('--tol', type=int, default=90)
    ap.add_argument('--min-gap', type=int, default=6)
    args = ap.parse_args()
    frames = cut(args.sheet, tol=args.tol, min_gap=args.min_gap)
    os.makedirs(args.out, exist_ok=True)
    picked = parse_take(args.take, len(frames))
    print('%s: %d frames found, taking %s' % (args.sheet, len(frames), picked))
    for n, idx in enumerate(picked, 1):
        if idx < 1 or idx > len(frames):
            raise SystemExit('frame %d not found (only %d)' % (idx, len(frames)))
        p = os.path.join(args.out, 'frame_%d.png' % n)
        frames[idx - 1].save(p)
        print('  ', p, frames[idx - 1].size)


if __name__ == '__main__':
    main()
