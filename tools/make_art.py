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


def main():
    print('icon      ', icon.write(PROJECT))
    for p in clinic_objects.write(PROJECT):
        print('object    ', p)
    print('preview   ', clinic_objects.preview(PROJECT))
    for p in clinic_room.write(PROJECT):
        print('room      ', p)
    print('done')


if __name__ == '__main__':
    main()
