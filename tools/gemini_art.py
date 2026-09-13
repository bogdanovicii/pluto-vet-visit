"""Generates the painted pieces with Google Gemini through the image-generation skill's CLI.

Usage: python3 tools/gemini_art.py [--dry-run] [--force] [--only NAME]
Key: GEMINI_API_KEY from the environment, else from PlutoVetVisit/.env (KEY=VALUE lines). The value is never printed.
Outputs go to reference/gemini/; existing files are skipped unless --force. Then run tools/make_art.py so
cards.py and icon.py pick them up.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
OUT_DIR = os.path.join(PROJECT, 'reference', 'gemini')
CLI = os.environ.get('GEMINI_CLI', os.path.expanduser('~/.claude/skills/image-generation/mcp-server-build/cli.bundle.js'))
RATIOS = ('1:1', '16:9', '9:16', '4:3', '3:4', '2:3', '3:2')


class Prompt:
    def __init__(self, name, ratio, text):
        self.name, self.ratio, self.text = name, ratio, text


STYLE = ('Enter the Gungeon art style: chunky pixel-art inspired illustration, bold dark outlines, flat cel shading, '
         'saturated colours, slightly grim humour. ')

PROMPTS = [
    Prompt('vet_bosscard_raw.png', '16:9', STYLE +
           'Boss introduction card painting of a tall, slightly sinister cartoon veterinarian: white lab coat over teal scrubs, '
           'round glasses catching the light, dark hair, one gloved hand holding an enormous syringe full of glowing blue liquid, '
           'the other hand beckoning. He stands in a white clinic with glass cabinets of jars behind him. Dramatic low angle, '
           'the figure fills the right two thirds of the frame, dark teal vignette background. No text, no letters, no watermark.'),
    Prompt('past_win_pic_raw.png', '3:2', STYLE +
           'Victory illustration: a chunky tabby-and-white cat with a white spot between the ears sits proudly on a steel '
           'veterinary exam table; a knocked-out veterinarian in a white coat lies on the white tiled floor with his glasses '
           'askew; a plastic cone of shame is kicked into a corner; cat toys on the floor; a cabinet of syringes behind. '
           'Warm, triumphant lighting. No text.'),
    Prompt('icon_raw.png', '1:1', STYLE +
           'Square app icon: the face of a chunky tabby-and-white cat with a white spot between the ears, eyes wide, '
           'staring at a large syringe with blue liquid held just in frame; teal background with a white medical cross. '
           'Thick outlines, centred, readable at small size. No text.'),
    Prompt('vet_reference_sheet.png', '1:1', STYLE +
           'Character reference sheet for a 2D game boss: a veterinarian in a white lab coat over teal scrubs, round glasses, '
           'dark hair, oversized syringe with blue liquid. One row with front view, side view and back view standing; a second row '
           'of small poses: aiming the syringe, spraying a water bottle, tossing pills, lying knocked out. Plain white background. No text.'),
    Prompt('clinic_reference.png', '16:9', STYLE +
           'Top-down three-quarter view of a game room: a white veterinary clinic with white tiled floor and walls, glass cabinets '
           'full of jars and syringe boxes along the back wall, a steel examination table in the centre, a rolling cart with a tray '
           'of syringes, a sink counter, a pet scale, a blue cat carrier in a corner, a scratching post, cat toys (toy mouse, ball, '
           'feather wand) scattered on the floor, a cone of shame, an anatomy poster. No characters, no text.'),
]


def load_env(path):
    """Set KEY=VALUE pairs from a .env file into os.environ (missing names only). Returns the names set, never values."""
    if not os.path.exists(path):
        return []
    names = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value
                names.append(key)
    return names


def has_key():
    return bool(os.environ.get('GEMINI_API_KEY'))


def plan(force=False, only=None):
    return [p for p in PROMPTS if (only is None or p.name == only) and (force or not os.path.exists(os.path.join(OUT_DIR, p.name)))]


def run_cli(args):
    """The only place node is called. Returns the CLI's JSON result."""
    proc = subprocess.run(['node', CLI] + args, capture_output=True, text=True)
    for line in reversed(proc.stdout.strip().splitlines()):
        line = line.strip()
        if line.startswith('{'):
            try:
                return json.loads(line)
            except ValueError:
                pass
    return {'success': False, 'error': (proc.stderr or proc.stdout or 'no output').strip()[-400:]}


def generate(prompt, force=False):
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, prompt.name)
    if os.path.exists(out) and not force:
        return out
    result = run_cli(['-p', prompt.text, '-o', out, '-a', prompt.ratio])
    if not result.get('success'):
        print('FAIL', prompt.name, result.get('error', 'unknown error'))
        return None
    print(' ok ', prompt.name)
    return out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    dry = '--dry-run' in argv
    force = '--force' in argv
    only = argv[argv.index('--only') + 1] if '--only' in argv else None
    load_env(os.path.join(PROJECT, '.env'))
    todo = plan(force, only)
    if not todo:
        print('nothing to generate (all outputs exist; use --force to redo)')
        return 0
    if dry or not has_key():
        if not dry:
            print('GEMINI_API_KEY is not set: export it in ~/.zshenv or put GEMINI_API_KEY=... in PlutoVetVisit/.env')
        print('would generate:')
        for p in todo:
            print('  %-26s %-5s %s...' % (p.name, p.ratio, p.text[:60]))
        return 0
    if not os.path.exists(CLI):
        print('FAIL image-generation CLI not found at', CLI, '(set GEMINI_CLI)')
        return 1
    failed = [p.name for p in todo if generate(p, force) is None]
    if failed:
        print('failed:', ', '.join(failed))
        return 1
    print('done; now run tools/make_art.py to rebuild the card, win picture and icon from the references')
    return 0


if __name__ == '__main__':
    sys.exit(main())
