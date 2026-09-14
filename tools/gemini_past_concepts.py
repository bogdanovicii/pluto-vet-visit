"""Generates the three-zone past concept set (level maps, cast sheets, prop sheets, story beats) with Gemini.

Usage: python3 tools/gemini_past_concepts.py [--dry-run] [--force] [--only NAME[,NAME..]] [--candidates N] [--model ID] [--jobs N]
       python3 tools/gemini_past_concepts.py --sheet   (rebuild docs/past-concepts-sheet.png from the chosen images)

Reuses Prompt / load_env from gemini_art.py. Unlike gemini_art.py it does NOT go through the image-generation
skill's CLI: that CLI has no image-size flag and cannot attach a reference image, and the brief asks for the largest
size the model allows plus the boss card as a reference for every image that shows the Vet. So this script posts to
the Gemini REST endpoint directly (curl, because this Mac's Python has no CA bundle) with imageSize=2K and the boss
card inlined for the Vet prompts. GEMINI_API_KEY comes from the environment or PlutoVetVisit/.env and is never printed.

Outputs go to reference/gemini/past_concepts/<name>.png (candidate 2 and up: <name>_c2.png ...), each with a
<name>.json sidecar recording the model version, prompt, ratio, reference and timestamp. Existing files are skipped
unless --force. Generated images are references only: never pixelize them into sprites or copy them into Resources/.
"""
import base64
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gemini_art import Prompt, load_env, has_key, PROJECT  # noqa: E402

OUT_DIR = os.path.join(PROJECT, 'reference', 'gemini', 'past_concepts')
VET_REF = os.path.join(PROJECT, 'reference', 'gemini', 'vet_bosscard_raw.png')
WIN_REF = os.path.join(PROJECT, 'reference', 'gemini', 'past_win_pic_raw.png')
DEFAULT_MODEL = 'gemini-3-pro-image'   # the newest "pro" image model listed by the API on 2026-09-14
IMAGE_SIZE = '2K'                      # largest size gemini-3-pro-image accepts through imageConfig
ENDPOINT = 'https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent'

# ---------------------------------------------------------------- shared prompt blocks

STYLE = (
    'Pixel-art concept painting in the style of Enter the Gungeon (Dodge Roll Games, 2016), specifically the Marine\'s '
    'Primerdyne R&D lab past (white tile floor, glass, steel, computers, lab benches). '
    'CAMERA: fixed top-down three-quarter view exactly like the game: floors seen from above as a flat grid of tiles; '
    'walls drawn as a thin dark top strip plus a vertical wall face about two tiles tall on the north wall only; the '
    'south wall shows only its dark top edge; characters and props stand upright on the floor as if drawn from the '
    'front, each casting a small soft ellipse shadow at its feet. No vanishing-point perspective, no camera tilt, no '
    'isometric angle, no fisheye. '
    'SCALE: one floor tile is one game unit (16 pixels); a person is about 1.4 tiles tall, a chair or cabinet one to '
    'two tiles, a boss two to four tiles. '
    'RENDERING: crisp hard-edged pixels, no anti-aliasing, no gradients, no dithering, no blur, no photographic '
    'texture. Flat cel shading, two or three tones per material (base, cooler greyer shadow, warmer highlight), one '
    'shadow shape per mass from a top-left light. Small controlled palette. Characters and enemies have a crisp 1-px '
    'black outline; floor tiles and wall faces have none. '
    'CHARACTER LANGUAGE: big heads about half the body height, thin stick legs, tiny dot eyes, small hands, chunky '
    'readable silhouettes, exaggerated oversized props (syringes, guns); enemies read from silhouette plus one accent '
    'colour, like Bullet Kin and Hegemony soldiers. '
    'PALETTE: tile white #F4F6F8 with shade #DCE0E6, scrubs teal #3F9E8F with dark #2C7367, steel #3A3F4A / #8C94A2 / '
    '#C9CFD8, carrier blue #6F8FBF / #4A6390, syringe liquid #4FA8E8, medical red #D83A3A, plastic orange #F08A24, '
    'plastic yellow #F5D547, wood #A97B4F / #7A5A3A. '
    'MOOD: bright clinical clean white and pale grey, teal and steel accents, a faint pink-red tint in the ambient '
    'light like the Primerdyne lab; friendly on the surface, faintly menacing (syringes everywhere, straps, cones). '
    'Grim humour, no gore, no blood. '
)

PLUTO = (
    'Pluto is a chunky tabby-and-white cat: grey-brown taupe tabby fur #8B7A66 (light #B4A180, shadow #66524A), '
    'near-black mackerel stripes, a forehead "M" marking, a tabby mask around the eyes, a white blaze between the eyes '
    'running down to a white muzzle and chest, a small white oval on the crown surrounded by tabby, big pink ears, '
    'hazel-green eyes with slit pupils, a ringed tail. About 1.2 tiles tall, rounder than a human. '
)

VET = (
    'The Vet matches the attached reference image exactly: tall, slightly sinister, white lab coat over teal scrubs, '
    'round glasses catching the light, short dark hair, teal gloves, one hand holding an enormous syringe of glowing '
    'blue liquid #4FA8E8. '
)

TECH = (
    'Vet Tech: a human enemy with the Bullet Kin body plan (big head, short body, stick legs), teal scrubs #3F9E8F '
    'with dark teal #2C7367 folds, a teal surgical cap, a white mask over the mouth, holding a syringe pistol (a syringe '
    'with a pistol grip, blue liquid). About 1.4 tiles tall. '
)

NURSE = (
    'The Nurse: the Vet Tech design at twice the size (about 2.8 tiles tall), a white nurse cap with a red cross, '
    'teal scrubs, a shotgun-sized syringe with a pump grip in both hands and a butterfly net on her back. '
)

MAP_ROOM = (
    'The room is a tall rectangle of white tiles with a dark chunky steel-grey wall border. The two sliding clinic doors '
    'that separate the zones sit on the room\'s vertical centre line, drawn as a gap in a horizontal wall segment with a '
    'steel door frame and a teal sliding door panel. Keep one consistent tile grid across the whole picture. '
)

SHEET_BG = (
    'Plain flat neutral grey background #6C6C7A, no floor, no scene, no shadows on the background except each figure\'s '
    'small ellipse. Equal generous spacing, nothing overlapping, everything drawn at the same scale. '
)

NEG = (
    'No text, no letters, no numbers, no labels, no captions, no signage lettering, no logos, no watermark, no UI, '
    'no health bars, no borders, no frame, no perspective tilt, no gradients, no blur, no 3D render, no photograph. '
    'The subject fills the frame. No text. '
)

BEAT = (
    'A painted in-game screenshot: still the fixed top-down three-quarter game camera, letterboxed with thin black '
    'bars top and bottom like a cutscene, no UI. '
)

# ---------------------------------------------------------------- the image set


def P(name, ratio, body, ref=None):
    p = Prompt(name + '.png', ratio, STYLE + body + NEG)
    p.ref = ref
    return p


PROMPTS = [
    # -- level maps
    P('level_overview', '9:16', MAP_ROOM +
      'Whole-level map of one big room 30 tiles wide and 52 tiles tall, seen entirely in one image, three zones stacked '
      'south (bottom) to north (top), separated by two horizontal wall segments each with a sliding clinic door in the '
      'centre. BOTTOM ZONE, the waiting room (about 14 tiles tall): a blue plastic cat carrier #6F8FBF by a row of '
      'orange plastic chairs along the west wall, a reception desk with a computer, a bell and a jar of treats against '
      'the north wall of the zone with the Receptionist behind it, a wall TV, a potted plant, a fish tank, a clock, a '
      'yellow wet-floor sign, a floor mat with paw prints, a window with daylight on the east wall, a trembling dog on a '
      'chair, a grey cat loaf on another chair, a chick, a rabbit and a squirrel loose on the floor. Pluto the cat '
      'standing beside the carrier for scale. ' + PLUTO +
      'MIDDLE ZONE, the ward (about 18 tiles tall): kennel cages lined along both long walls, some open and some closed, '
      'a few holding patients in cones, a nurse station in the middle with a treat jar and two cat-food bowls, an X-ray '
      'light box, a medicine shelf, an IV stand, a red sharps bin, two side doors on the east and west walls. '
      'TOP ZONE, the operating theatre (about 18 tiles tall): a big open floor as a boss arena, a large overhead '
      'surgical lamp, a steel exam table with straps in the upper middle, a monitor cart, a vaccine fridge, glass '
      'cabinets with jars and syringe boxes, a sink counter, a pet scale, a cone of shame and cat toys along the walls. '
      + VET + 'He stands behind the exam table at the very top. '
      'Every prop is a separate small sprite on the floor, walls are chunky and dark, the whole room fills the frame '
      'edge to edge. ', VET_REF),

    P('zone1_waiting_room', '4:3', MAP_ROOM +
      'Map of the south zone only: the veterinary clinic waiting room, a rectangle about 30 tiles wide and 14 tiles '
      'tall, the north wall face two tiles tall visible at the top with a sliding clinic door in its centre. Along the '
      'west wall a row of five orange plastic chairs #F08A24 on steel legs; a blue plastic cat carrier #6F8FBF with a '
      'wire door sits on the floor beside them. Against the north wall a wood-and-steel reception desk with a computer '
      'monitor, a small desk bell and a glass jar of treats; the Receptionist, an office worker with a headset and a '
      'cardigan, sits behind it. On the east wall a window with pale daylight, a wall-mounted TV, a round clock, a '
      'poster. A potted plant in the corner, a fish tank on a stand, a yellow wet-floor sign, a rectangular floor mat '
      'with paw prints in front of the desk. Patients: Rex, a nervous brown dog with big eyes, trembling on a chair; '
      'Grandma Cat, an ancient grey cat in a loaf on the next chair with half-closed unimpressed eyes; a yellow chick, '
      'a brown rabbit and a grey squirrel loose on the floor. The Owner, a human in a grey hoodie and jeans, standing '
      'by the carrier with an arm out having just set it down. ' + PLUTO + 'Pluto sits inside the open carrier. '),

    P('zone2_ward', '4:3', MAP_ROOM +
      'Map of the middle zone only: the clinic ward, a rectangle about 30 tiles wide and 18 tiles tall, the north wall '
      'face two tiles tall visible at the top with a sliding clinic door in its centre and a second door gap in the '
      'south wall at the bottom centre. Kennel cages with steel bars line both long walls: some doors open, some '
      'closed, a few holding small patients wearing plastic cones of shame. In the middle a rectangular nurse station '
      'counter with a glass treat jar and two cat-food bowls on it. An X-ray light box glowing pale blue on the north '
      'wall, a medicine shelf with bottles, a steel IV stand with a bag, a red sharps bin, a litter box, a small teal '
      'sign panel on the wall. A plain steel side door in the east wall and one in the west wall. Three Vet Techs are '
      'mid-attack, spread across the floor, each firing a blue syringe dart from a syringe pistol. ' + TECH +
      PLUTO + 'Pluto is near the south door dodge-rolling, a small kibble gun in his paws, with a few tan kibble '
      'pellet bullets in the air. '),

    P('zone3_theatre', '4:3', MAP_ROOM +
      'Map of the north zone only: the operating theatre as a boss arena, a rectangle about 30 tiles wide and 18 tiles '
      'tall with a door gap in the south wall at the bottom centre. A big open white-tile floor in the middle kept '
      'empty for the fight; all props sit along the walls: a steel exam table with brown leather straps against the '
      'north wall centre with a large overhead surgical lamp on an arm above it, a monitor cart with a green heartbeat '
      'screen, a white vaccine fridge with a glass door, glass cabinets full of jars and syringe boxes, a sink counter, '
      'a pet scale, a poster of a cat anatomy diagram, a plastic cone of shame, a rolling cart with a tray of syringes, '
      'and scattered cat toys (a toy mouse, a ball, a feather wand, a small scratching post) in the corners. '
      + VET + 'He stands behind the exam table, about 2.5 tiles tall, syringe raised. ' + NURSE +
      'The Nurse and two Vet Techs are entering through a side door in the east wall. ' + TECH +
      'The ambient light has the faint pink-red Primerdyne tint. '
      # round 2: round 1 lettered the fridge and the poster and gave the Nurse a real shotgun.
      'The vaccine fridge is a plain white cabinet with a glass door and NO label or lettering on it; the anatomy '
      'poster is a cat silhouette with coloured organ blobs and NO writing; nothing in the room carries letters. '
      'The Nurse\'s weapon is a giant medical syringe (glass barrel with blue liquid, plunger, needle), not a gun. ',
      VET_REF),

    # -- cast sheets
    P('cast_vet_tech', '16:9', SHEET_BG +
      'Character reference sheet for a 2D game enemy sprite, drawn at game proportions as if 32 pixels tall then shown '
      'large. ' + TECH +
      'Top row: front view, side view and back view standing, in one line. Bottom row: a walking pose mid-stride, an '
      'attack pose aiming the syringe pistol forward with a glowing blue dart leaving it, and a hit-flinch pose leaning '
      'back with the cap flying off. Six figures total, same size, evenly spaced. '),

    P('cast_nurse', '16:9', SHEET_BG +
      'Character reference sheet for a 2D game mini-boss sprite, drawn at game proportions as if 64 pixels tall then '
      'shown large. ' + NURSE + 'She is stern, with a small tight mouth and tiny dot eyes. ' +
      'Top row: front view, side view and back view standing, in one line, with one Vet Tech at half her height '
      'standing beside the front view for scale. ' + TECH +
      'Bottom row: a walking pose, an attack pose pumping the shotgun syringe with a fan of blue droplets spraying '
      'out, and a net-throw pose swinging the butterfly net. Evenly spaced. '),

    P('cast_vet_boss', '16:9', SHEET_BG +
      'Character reference sheet for a 2D game boss sprite, drawn at game proportions as if 64 pixels tall then shown '
      'large. ' + VET +
      'Top row: front view, side view and back view standing, in one line. Bottom row, four attack tells: aiming the '
      'giant syringe straight forward with a glowing blue bolt about to fire (booster shot); holding a white spray '
      'bottle out and spraying a fan of blue droplets; tossing a handful of white and red pill capsules into the air '
      'with both hands (pill time); winding up to throw a plastic cone of shame like a frisbee. Seven figures total, '
      'same scale, evenly spaced. ', VET_REF),

    P('cast_owner_receptionist', '16:9', SHEET_BG +
      'Character reference sheet for two 2D game NPC sprites, drawn at game proportions as if 32 pixels tall then '
      'shown large, both with the Bullet Kin-like body plan (big head, stick legs). LEFT: the Owner, a human in a '
      'grey hoodie with the hood down, blue jeans and sneakers, tired kind face, carrying a blue plastic cat carrier '
      '#6F8FBF by its handle; shown front, side and back. RIGHT: the Receptionist, an office worker with a headset, a '
      'beige cardigan over a teal shirt, a name badge shape with no text, shown front view standing and a second pose '
      'seated behind a small reception desk with a computer and a bell. Evenly spaced, same scale. '),

    P('cast_patients', '16:9', SHEET_BG +
      'Reference sheet of the waiting-room patients and ward escapees for a 2D game, drawn at game proportions as if '
      '16 to 32 pixels tall then shown large, all in one row with generous spacing. From left: Rex, a nervous brown '
      'dog with big worried eyes, trembling on an orange plastic chair with motion lines; Grandma Cat, an ancient grey '
      'cat in a loaf pose with half-closed unimpressed eyes and a wispy white chin; a small yellow chick; a brown '
      'rabbit; a grey squirrel with a bushy tail; then two mutant patients: lumpy pale Bullet Kin-like creatures with '
      'bandages, each wearing a plastic cone of shame, one holding a tiny syringe. Front views. '
      # round 2: round 1 painted a tiled clinic wall and floor behind the figures instead of the flat grey sheet.
      'IMPORTANT: this is a character sheet, not a scene: the background is one flat solid grey #6C6C7A edge to edge, '
      'with no wall, no floor tiles, no windows, no room at all. '),

    # -- prop sheets
    P('props_waiting_room', '1:1', SHEET_BG +
      'Flat-lay prop sheet for a 2D top-down game, each prop drawn upright as it would sit in the top-down room, with a '
      'crisp 1-px dark outline, at game scale (a chair about one tile, a desk two tiles wide), grouped in a loose grid '
      'with generous spacing. Props: a blue plastic cat carrier #6F8FBF with a wire door, shown once closed and once '
      'with the door open; a row of four orange plastic chairs #F08A24 on steel legs; a wood-and-steel reception desk '
      'with a computer monitor and a small desk bell; a glass jar of treats; a wall-mounted TV; a potted plant in a '
      'terracotta pot; a fish tank on a stand with two orange fish; a round wall clock; a yellow folding wet-floor sign; '
      'a rectangular floor mat with paw prints; a window with pale daylight and a sill; two blank posters with a pet '
      'silhouette. '),

    P('props_ward', '1:1', SHEET_BG +
      'Flat-lay prop sheet for a 2D top-down game, each prop drawn upright as it would sit in the top-down room, with a '
      'crisp 1-px dark outline, at game scale, grouped in a loose grid with generous spacing. Props: a steel kennel '
      'cage with bars, shown three times: door closed, door open, and with a small patient in a cone of shame inside; '
      'a nurse station counter with a glass treat jar and two cat-food bowls; a small teal wall sign panel (blank); an '
      'X-ray light box glowing pale blue with a cat skeleton silhouette; a medicine shelf with bottles; a steel IV '
      'stand with a hanging bag; a red sharps bin; two cat-food bowls; a litter box; a sliding clinic door with a steel '
      'frame and teal panel, shown closed and open; an intercom speaker box for the wall. '),

    P('props_theatre', '1:1', SHEET_BG +
      'Flat-lay prop sheet for a 2D top-down game, each prop drawn upright as it would sit in the top-down room, with a '
      'crisp 1-px dark outline, at game scale, grouped in a loose grid with generous spacing. Props: a large overhead '
      'surgical lamp on a jointed steel arm; a steel exam table with brown leather straps; a monitor cart with a green '
      'heartbeat screen; a white vaccine fridge with a glass door and vials inside; a glass cabinet full of jars and '
      'syringe boxes; a sink counter with a tap; a pet scale with a tray; a poster of a cat anatomy diagram (drawn as '
      'shapes, no lettering); a plastic cone of shame; a rolling cart with a tray of syringes; a small grey toy mouse; '
      'a red ball; a feather wand toy; a small carpeted scratching post. '),

    P('tiles_and_walls', '1:1', SHEET_BG +
      'Tileset study for a 2D top-down game, laid out as separate swatches with generous spacing on the grey '
      'background, each swatch a square of tiles at the same scale. Swatches: the plain white clinic floor tile '
      '#F4F6F8 with grout lines in #DCE0E6 (a 4 by 4 block); the same floor with a round steel drain tile; the same '
      'floor with a paw-print tile; the same floor with a cracked tile; the north wall face two tiles tall, pale '
      'grey-white with a teal skirting board and a dark top strip, shown as a 4-tile-wide strip; the wall top strip '
      'alone; an outer corner of wall where a north face meets a side wall; a door gap in the wall with a steel door '
      'frame; a floor-to-wall shadow line where the floor darkens for one tile against the wall base. Flat cel colour, '
      'crisp pixels. '),

    # -- story beats
    P('beat_intro', '16:9', BEAT +
      'Scene in the clinic waiting room, white tiles, orange plastic chairs along the wall, a reception desk with a '
      'computer at the back. The Owner, a human in a grey hoodie and jeans, is bending to set a blue plastic cat '
      'carrier #6F8FBF down on the floor by the chairs; ' + PLUTO + 'Pluto\'s wide eyes peer through the carrier\'s '
      'wire door. Behind the desk the Receptionist, an office worker with a headset, looks up. On a chair Rex, a '
      'nervous brown dog, shakes with motion lines; Grandma Cat, a grey loaf, ignores everything; a chick, a rabbit and '
      'a squirrel wander the floor. A fish tank, a plant, a yellow folding floor sign with only a triangle symbol '
      'and no words on it. Daylight from a window. '
      # round 2: round 1 wrote WET FLOOR on the sign and tilted the east wall into perspective.
      'All four walls are straight and axis-aligned: the north wall is a flat vertical face at the top, the east and '
      'west walls are thin vertical strips, nothing recedes toward a vanishing point. '),

    P('beat_ward_fight', '16:9', BEAT +
      'Scene in the clinic ward, white tiles, steel kennel cages along the wall with patients in cones watching. '
      + PLUTO + 'Pluto is mid dodge-roll, a tumbling ball of tabby fur with motion lines, a small kibble gun (a tan '
      'plastic kibble dispenser shaped like a pistol) in his paws and a stream of tan kibble pellets flying from it. '
      'Two Vet Techs fire glowing blue syringe darts at him from the side, a third reloads. ' + TECH +
      'A nurse station with a treat jar in the middle, an IV stand knocked over, a red sharps bin. '),

    P('beat_boss_intro', '16:9', BEAT +
      'Scene in the operating theatre, white tiles with a faint pink-red ambient tint, a big overhead surgical lamp '
      'shining a pool of light onto a steel exam table with brown leather straps. ' + VET + 'He stands behind the '
      'table, syringe raised high, glasses gleaming, a thin smile. In the foreground at the bottom, in the open sliding '
      'doorway, ' + PLUTO + 'Pluto stands with his back arched, fur bristling, ears flat, mouth open in a hiss. Glass '
      'cabinets of jars, a monitor cart and a vaccine fridge along the walls, a cone of shame on the floor. '
      # round 2: round 1 lettered the fridge.
      'The vaccine fridge is a plain white cabinet with a glass door and NO label or lettering; no words anywhere. ',
      VET_REF),

    P('beat_victory', '16:9', BEAT +
      'Match the attached reference victory picture but redrawn in the top-down game camera. ' + PLUTO +
      'Pluto sits smug and proud on top of a steel exam table, eyes half closed, tail curled. The Vet lies flat on his '
      'back on the white tiled floor beside the table, glasses askew, the giant syringe rolled away, arms out. ' + VET +
      'A plastic cone of shame is kicked into a corner, cat toys (a toy mouse, a ball, a feather wand) scattered on the '
      'floor, a cabinet of syringes and jars behind, the surgical lamp overhead. Warm triumphant light. '
      # round 2: round 1 drew the floor in vanishing-point perspective with a desk lamp and a bare corner.
      'The floor grid is perfectly axis-aligned, seen straight from above like every other room in the game, the '
      'table is a rectangle with vertical sides, the walls are a flat north face; the lamp is a round multi-bulb '
      'surgical lamp on a jointed arm, not a desk lamp. Pluto has the small white oval on his crown. ', WIN_REF),
]

# Images that get a second candidate by default (the four level maps).
MULTI = {'level_overview.png', 'zone1_waiting_room.png', 'zone2_ward.png', 'zone3_theatre.png'}

# ---------------------------------------------------------------- generation


def out_path(prompt, candidate):
    base = prompt.name[:-4]
    return os.path.join(OUT_DIR, base + ('' if candidate == 1 else '_c%d' % candidate) + '.png')


def plan(force=False, only=None, candidates=2):
    jobs = []
    wanted = None if only is None else {n.strip().removesuffix('.png') for n in only.split(',')}
    for p in PROMPTS:
        if wanted is not None and p.name[:-4] not in wanted:
            continue
        n = candidates if p.name in MULTI else 1
        for c in range(1, n + 1):
            out = out_path(p, c)
            if force or not os.path.exists(out):
                jobs.append((p, c, out))
    return jobs


def build_body(prompt):
    parts = []
    if prompt.ref and os.path.exists(prompt.ref):
        with open(prompt.ref, 'rb') as fh:
            parts.append({'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(fh.read()).decode()}})
        parts.append({'text': 'Reference image attached: keep this character\'s design identical. ' + prompt.text})
    else:
        parts.append({'text': prompt.text})
    return {'contents': [{'parts': parts}],
            'generationConfig': {'responseModalities': ['IMAGE'],
                                 'imageConfig': {'aspectRatio': prompt.ratio, 'imageSize': IMAGE_SIZE}}}


def call_api(body, model, timeout=600):
    """The only place the network is touched. The key goes in a header, never on the command line or in output."""
    tmp = os.path.join(OUT_DIR, '.req_%d_%d.json' % (os.getpid(), time.time_ns()))
    with open(tmp, 'w') as fh:
        json.dump(body, fh)
    try:
        proc = subprocess.run(['curl', '-s', '--max-time', str(timeout), '-X', 'POST',
                               '-H', 'Content-Type: application/json',
                               '-H', 'x-goog-api-key: ' + os.environ['GEMINI_API_KEY'],
                               '-d', '@' + tmp, ENDPOINT % model], capture_output=True, text=True)
    finally:
        os.remove(tmp)
    try:
        return json.loads(proc.stdout)
    except ValueError:
        return {'error': {'message': (proc.stderr or proc.stdout or 'no output').strip()[-400:]}}


def generate(job, model):
    prompt, candidate, out = job
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.time()
    result = call_api(build_body(prompt), model)
    if 'error' in result:
        print('FAIL', os.path.basename(out), str(result['error'].get('message', result['error']))[:200])
        return None
    parts = result.get('candidates', [{}])[0].get('content', {}).get('parts', [])
    data = next((p['inlineData']['data'] for p in parts if 'inlineData' in p), None)
    if not data:
        reason = result.get('candidates', [{}])[0].get('finishReason', 'no image part')
        print('FAIL', os.path.basename(out), reason)
        return None
    with open(out, 'wb') as fh:
        fh.write(base64.b64decode(data))
    with open(out[:-4] + '.json', 'w') as fh:
        json.dump({'model': result.get('modelVersion', model), 'ratio': prompt.ratio, 'image_size': IMAGE_SIZE,
                   'reference': os.path.relpath(prompt.ref, PROJECT) if prompt.ref else None,
                   'candidate': candidate, 'seconds': round(time.time() - t0),
                   'generated': time.strftime('%Y-%m-%d %H:%M'), 'prompt': prompt.text}, fh, indent=1)
    print(' ok ', os.path.basename(out), '%ds' % (time.time() - t0))
    return out


SHEET = os.path.join(PROJECT, 'docs', 'past-concepts-sheet.png')


def sheet(cell=360, cols=4):
    """Downscaled contact sheet of the chosen (non-candidate) images, in PROMPTS order, with the name under each."""
    from PIL import Image, ImageDraw
    names = [p.name[:-4] for p in PROMPTS if os.path.exists(out_path(p, 1))]
    rows = (len(names) + cols - 1) // cols
    pad, label = 8, 14
    im = Image.new('RGB', (cols * (cell + pad) + pad, rows * (cell + label + pad) + pad), (0x2A, 0x2C, 0x33))
    d = ImageDraw.Draw(im)
    for i, name in enumerate(names):
        src = Image.open(os.path.join(OUT_DIR, name + '.png')).convert('RGB')
        src.thumbnail((cell, cell), Image.LANCZOS)
        x = pad + (i % cols) * (cell + pad)
        y = pad + (i // cols) * (cell + label + pad)
        im.paste(src, (x + (cell - src.width) // 2, y + (cell - src.height) // 2))
        d.text((x, y + cell + 2), name, fill=(0xDC, 0xE0, 0xE6))
    im.save(SHEET)
    print('wrote', os.path.relpath(SHEET, PROJECT), im.size, '%d images' % len(names))


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--sheet' in argv:
        sheet()
        return 0
    dry = '--dry-run' in argv
    force = '--force' in argv
    only = argv[argv.index('--only') + 1] if '--only' in argv else None
    candidates = int(argv[argv.index('--candidates') + 1]) if '--candidates' in argv else 2
    model = argv[argv.index('--model') + 1] if '--model' in argv else DEFAULT_MODEL
    jobs = int(argv[argv.index('--jobs') + 1]) if '--jobs' in argv else 3
    load_env(os.path.join(PROJECT, '.env'))
    todo = plan(force, only, candidates)
    if not todo:
        print('nothing to generate (all outputs exist; use --force to redo)')
        return 0
    if dry or not has_key():
        if not dry:
            print('GEMINI_API_KEY is not set: export it or put GEMINI_API_KEY=... in PlutoVetVisit/.env')
        print('model %s, size %s; would generate:' % (model, IMAGE_SIZE))
        for p, c, out in todo:
            print('  %-28s %-5s ref=%-4s %s...' % (os.path.basename(out), p.ratio, 'yes' if p.ref else 'no', p.text[:50]))
        return 0
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(lambda j: generate(j, model), todo))
    failed = [os.path.basename(j[2]) for j, r in zip(todo, results) if r is None]
    if failed:
        print('failed:', ', '.join(failed))
        return 1
    print('done: %d images in %s' % (len(results), os.path.relpath(OUT_DIR, PROJECT)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
