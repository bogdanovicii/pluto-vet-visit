"""Regenerates every generated file of the Vet Visit project.

Usage: python3 tools/make_art.py   (from PlutoVetVisit/ or anywhere; paths are absolute)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PROJECT = os.path.dirname(HERE)

import icon  # noqa: E402
import clinic_objects  # noqa: E402
import clinic_room  # noqa: E402
import vet_poses  # noqa: E402
import cards  # noqa: E402
import projectiles  # noqa: E402
import tech_poses  # noqa: E402
import nurse_poses  # noqa: E402
import npc_poses  # noqa: E402
import cast_layout  # noqa: E402


def main():
    print('icon      ', icon.write(PROJECT))
    for p in clinic_objects.write(PROJECT):
        print('object    ', p)
    print('preview   ', clinic_objects.preview(PROJECT))
    for p in clinic_room.write(PROJECT):
        print('room      ', p)
    print('vet       ', len(vet_poses.write(PROJECT)), 'frames')
    print('preview   ', vet_poses.preview(PROJECT))
    for p in cards.write(PROJECT):
        print('card      ', p)
    for p in projectiles.write(PROJECT):
        print('projectile', p)
    print('tech      ', len(tech_poses.write(PROJECT)), 'frames', tech_poses.preview(PROJECT))
    print('nurse     ', len(nurse_poses.write(PROJECT)), 'frames', nurse_poses.preview(PROJECT))
    print('npcs      ', len(npc_poses.write(PROJECT)), 'frames', npc_poses.preview(PROJECT))
    print('cast      ', cast_layout.write(PROJECT))
    print('done')


if __name__ == '__main__':
    main()
