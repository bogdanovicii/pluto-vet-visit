"""Static validation of the Vet Visit package. Run: python3 tools/validate.py  Exits non-zero on failure."""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
RES = os.path.join(PROJECT, 'Resources')
DLL = os.path.join(PROJECT, 'bin', 'Release', 'PlutoVetVisit.dll')
sys.path.insert(0, HERE)
from PIL import Image  # noqa: E402

errors = []


def err(msg):
    errors.append(msg)
    print('FAIL', msg)


def ok(msg):
    print(' ok ', msg)


def check_thunderstore():
    ts = os.path.join(PROJECT, 'thunderstore')
    m = json.load(open(os.path.join(ts, 'manifest.json')))
    if not re.match(r'^[A-Za-z0-9_]+$', m['name']):
        err('manifest name has invalid characters')
    if len(m['description']) > 250:
        err('manifest description > 250 chars')
    if Image.open(os.path.join(ts, 'icon.png')).size != (256, 256):
        err('thunderstore icon must be 256x256')
    if not os.path.exists(os.path.join(ts, 'README.md')):
        err('thunderstore README.md missing')
    ok('thunderstore manifest/icon/readme')


def check_room():
    import clinic_room
    path = os.path.join(RES, 'Rooms', 'vet_clinic.newroom')
    if not os.path.exists(path):
        err('vet_clinic.newroom missing (run tools/make_art.py)')
        return
    data = json.load(open(path))
    w, h = data['roomSize']['x'], data['roomSize']['y']
    if len(data['tileInfo']) != w * h:
        err('tileInfo length %d != %d' % (len(data['tileInfo']), w * h))
    if data['category'] != 'ENTRANCE':
        err('room category must be ENTRANCE')
    if data != clinic_room.room_data():
        err('vet_clinic.newroom is stale (run tools/make_art.py)')
    cs = open(os.path.join(PROJECT, 'src', 'ClinicLayout.cs')).read()
    if cs != clinic_room.layout_cs():
        err('ClinicLayout.cs is stale (run tools/make_art.py)')
    import cast_layout
    known = {o.name for o in clinic_room.O.OBJECTS} | {clinic_room.CONTROLLER, clinic_room.DOOR} | set(cast_layout.NPC_OBJECTS)
    unknown = sorted(set(data['placeableGUIDs']) - known)
    if unknown:
        err('room places unknown objects: %s' % unknown)
    ok('room %dx%d, %d placeables' % (w, h, len(data['placeableGUIDs'])))


def check_look():
    """0.10.0: three zone floors that cover their zones, wall faces on the divider rows, lamp head above the actors."""
    import clinic_room
    import clinic_objects
    placed = {}
    for name, (x, y) in clinic_objects.PROPS:
        placed.setdefault(name, []).append((x, y))
    sizes = {o.name: o.size for o in clinic_objects.OBJECTS}
    hog = {o.name: o.height_off_ground for o in clinic_objects.OBJECTS}
    zones = {'pluto_floor_waiting': (0, 13), 'pluto_floor_ward': (15, 32), 'pluto_floor_theatre': (34, 52)}
    for name, (y0, y1) in zones.items():
        if name not in placed:
            err('%s not placed' % name)
            continue
        x, y = placed[name][0]
        w, h = sizes[name]
        if w != clinic_room.WIDTH * 16 or y > y0 or y + h / 16.0 < y1:
            err('%s is %dx%d at (%s, %s); must span x 0..%d and y %d..%d' % (name, w, h, x, y, clinic_room.WIDTH, y0, y1))
        if hog[name] >= 0:
            err('%s must have a negative HeightOffGround to lie under actors' % name)
    faces = placed.get('pluto_wall_face', []) + placed.get('pluto_wall_face_solid', [])
    for x, y in faces:
        if clinic_room.cell(x, y) != '#':
            err('wall face at (%s, %s) is not on a wall row' % (x, y))
    if len(faces) < 3:
        err('expected 3 wall faces, found %d' % len(faces))
    if hog.get('pluto_lamp_head', 0) < 1.0:
        err('the lamp head must draw over the actors (HeightOffGround >= 1)')
    # 0.10.1: the lab tileset's wall face sorts like a standing sprite on the upper wall row, so a FLAT face prop loses
    # to it (the in-game screenshots showed purple wall blocks over our face). Faces must stand, slightly below the
    # ground (Pluto hugging the wall stays in front), and wall decor must stand a hair in front of the face.
    stand = {o.name: getattr(o, 'stand', o.collider is not None) for o in clinic_objects.OBJECTS}
    face_hog = None
    for name in ('pluto_wall_face', 'pluto_wall_face_solid'):
        if not stand.get(name):
            err('%s must stand (perpendicular), or the tileset wall draws over it' % name)
        if hog.get(name, 0) >= 0:
            err('%s must have a small negative HeightOffGround so actors against the wall stay in front' % name)
        face_hog = hog.get(name, face_hog)
    bases = sorted({y for _, y in faces})
    decor = 0
    for name, (x, y) in clinic_objects.PROPS:
        if name.startswith('pluto_wall_face') or clinic_room.cell(x, y) != '#' or name == 'pluto_clinic_door':
            continue
        base = max(b for b in bases if b <= y) if any(b <= y for b in bases) else None
        if base is None:
            continue
        decor += 1
        if not stand.get(name):
            err('wall decor %s at (%s, %s) must stand, or the wall face covers it' % (name, x, y))
        if face_hog is not None:
            want = face_hog + 2 * (y - base) + 0.05
            if hog.get(name, 0.0) <= face_hog + 2 * (y - base):
                err('wall decor %s at (%s, %s): HeightOffGround %.2f draws behind the face (needs about %.2f)' % (name, x, y, hog.get(name, 0.0), want))
    ok('zone floors, %d standing wall faces, %d wall decor in front of them, lamp head' % (len(faces), decor))


def check_objects():
    import clinic_objects
    for o in clinic_objects.OBJECTS:
        p = os.path.join(RES, 'Objects', o.png + '.png')
        if not os.path.exists(p):
            err('object PNG missing: ' + p)
        elif Image.open(p).size != o.size:
            err('%s: PNG size %s != %s' % (o.png, Image.open(p).size, o.size))
    for stem, rows in clinic_objects.EXTRA_PNGS.items():
        p = os.path.join(RES, 'Objects', stem + '.png')
        if not os.path.exists(p):
            err('extra PNG missing: ' + p)
        elif Image.open(p).size != (max(len(r) for r in rows), len(rows)):
            err('%s: PNG size does not match its rows' % stem)
    ok('%d object sprites + %d extra frames' % (len(clinic_objects.OBJECTS), len(clinic_objects.EXTRA_PNGS)))


def check_boss():
    import vet_poses
    root = os.path.join(RES, 'Boss', 'vet')
    for clip, frames in vet_poses.CLIPS.items():
        d = os.path.join(root, clip)
        files = sorted(f for f in os.listdir(d)) if os.path.isdir(d) else []
        if len(files) != len(frames):
            err('%s: %d files != %d frames' % (clip, len(files), len(frames)))
        if not all(re.match(r'^vet_%s_\d{3}\.png$' % clip, f) for f in files):
            err('%s: bad frame names %s' % (clip, files))
        if any(Image.open(os.path.join(d, f)).size != vet_poses.CANVAS for f in files):
            err('%s: frame size != %s' % (clip, vet_poses.CANVAS))
    names = list(vet_poses.CLIPS)
    for a in names:
        for b in names:
            if a != b and b.startswith(a):
                err('clip folder %s is a prefix of %s (Alexandria matches by StartsWith)' % (a, b))
    if Image.open(os.path.join(RES, 'Boss', 'vet_bosscard.png')).size != (427, 240):
        err('boss card must be 427x240')
    if Image.open(os.path.join(RES, 'past_win_pic.png')).size != (115, 71):
        err('past win pic must be 115x71')
    for name in ('vet_syringe_001', 'vet_droplet_001', 'vet_pill_001'):
        if not os.path.exists(os.path.join(RES, 'SpriteRoot', 'ProjectileCollection', name + '.png')):
            err('projectile sprite missing: ' + name)
    ok('boss: %d clips, card, win pic' % len(names))


def _check_clips(label, root, prefix, clips, canvas, prefix_rule=True):
    for clip, frames in clips.items():
        d = os.path.join(root, clip)
        files = sorted(f for f in os.listdir(d)) if os.path.isdir(d) else []
        if len(files) != len(frames):
            err('%s %s: %d files != %d frames' % (label, clip, len(files), len(frames)))
        if not all(re.match(r'^%s_%s_\d{3}\.png$' % (prefix, clip), f) for f in files):
            err('%s %s: bad frame names %s' % (label, clip, files))
        if any(Image.open(os.path.join(d, f)).size != tuple(canvas) for f in files):
            err('%s %s: frame size != %s' % (label, clip, canvas))
    names = list(clips)
    for a in names:
        for b in names:
            if prefix_rule and a != b and b.startswith(a):
                err('%s clip folder %s is a prefix of %s' % (label, a, b))


def check_cast():
    import tech_poses, nurse_poses, npc_poses, cast_layout
    _check_clips('tech', os.path.join(RES, 'Enemies', 'tech'), 'tech', tech_poses.CLIPS, tech_poses.CANVAS)
    _check_clips('nurse', os.path.join(RES, 'Enemies', 'nurse'), 'nurse', nurse_poses.CLIPS, nurse_poses.CANVAS)
    for who, spec in npc_poses.NPCS.items():
        # NPC clips are loaded by explicit path (ClinicNpc.Build), so the StartsWith rule does not apply to them
        _check_clips(who, os.path.join(RES, 'Npcs', who), who, spec['clips'], spec['canvas'], prefix_rule=False)
        if not spec['clips']:
            err('%s has no clips (ClinicNpc.Build needs the first one as its rest pose)' % who)
    cs = open(os.path.join(PROJECT, 'src', 'CastLayout.cs')).read()
    if cs != cast_layout.layout_cs():
        err('CastLayout.cs is stale (run tools/make_art.py)')
    if not os.path.exists(os.path.join(RES, 'SpriteRoot', 'ProjectileCollection', 'vet_net_001.png')):
        err('projectile sprite missing: vet_net_001')
    ok('cast: tech %d clips, nurse %d clips, %d npcs' % (len(tech_poses.CLIPS), len(nurse_poses.CLIPS), len(npc_poses.NPCS)))


def dll_manifest():
    """Embedded resource names inside the built DLL, or None when not built / monodis missing."""
    if not os.path.exists(DLL):
        print('skip  DLL not built yet')
        return None
    try:
        return subprocess.run(['monodis', '--manifest', DLL], capture_output=True, text=True).stdout
    except FileNotFoundError:
        print('skip  monodis not available')
        return None


def check_dll(man):
    if man is None:
        return
    for name in ['PlutoVetVisit.Resources.Rooms.vet_clinic.newroom', 'PlutoVetVisit.Resources.Objects.exam_table.png',
                 'PlutoVetVisit.Resources.Boss.vet.idle.vet_idle_001.png', 'PlutoVetVisit.Resources.Boss.vet_bosscard.png',
                 'PlutoVetVisit.Resources.past_win_pic.png',
                 'PlutoVetVisit.Resources.SpriteRoot.ProjectileCollection.vet_syringe_001.png']:
        if name not in man:
            err('DLL lacks embedded resource ' + name)
    ok('DLL embeds %d PNGs' % man.count('.png'))


CHECKS = [check_thunderstore, check_room, check_objects, check_look, check_boss, check_cast]


def main():
    for check in CHECKS:
        check()
    check_dll(dll_manifest())
    if errors:
        print('\n%d problem(s)' % len(errors))
        sys.exit(1)
    print('\nall checks passed')


if __name__ == '__main__':
    main()
