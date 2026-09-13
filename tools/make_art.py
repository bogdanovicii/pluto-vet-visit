"""Regenerates every generated file of the Vet Visit project.

Usage: python3 tools/make_art.py   (from PlutoVetVisit/ or anywhere; paths are absolute)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
PROJECT = os.path.dirname(HERE)

import icon  # noqa: E402


def main():
    print('icon      ', icon.write(PROJECT))
    print('done')


if __name__ == '__main__':
    main()
