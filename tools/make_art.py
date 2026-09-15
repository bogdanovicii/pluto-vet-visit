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
import art_sources  # noqa: E402


def main():
    print('icon      ', icon.write(PROJECT))
    # cast first: the room preview renders the NPC and enemy PNGs, so a renamed sprite must exist before it
    print('tech      ', len(tech_poses.write(PROJECT)), 'frames', tech_poses.preview(PROJECT))
    print('nurse     ', len(nurse_poses.write(PROJECT)), 'frames', nurse_poses.preview(PROJECT))
    print('npcs      ', len(npc_poses.write(PROJECT)), 'frames', npc_poses.preview(PROJECT))
    print('cast      ', cast_layout.write(PROJECT))
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
    print('preview   ', projectiles.preview(PROJECT))
    print('preview   ', projectiles.floor_preview(PROJECT))
    # hand-copied sprite clips (Gemini designs copied onto the cast's own rows) refresh their approved sources first
    print('art src   ', len(vet_poses.write_mask_art(PROJECT)) + len(npc_poses.write_pat_art(PROJECT))
          + len(npc_poses.write_ending_art(PROJECT)) + len(clinic_objects.write_kennel_art(PROJECT)), 'frames')
    for p in art_sources.install(PROJECT):   # approved Gemini-first art replaces the drawn stand-ins
        print('art       ', p)
    print('done')


if __name__ == '__main__':
    main()
