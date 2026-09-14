"""The built-in Enter the Gungeon sound events the clinic plays (spec A5). Every name was seen as a literal in the
decompiled game; an unknown name is silent in game, so ClinicSound logs each event once for the tester."""
import os
import re

ALLOWED = [
    'Play_PET_dog_bark_02',            # kennel dog reacts
    'Play_UI_menu_confirm_01',         # intercom chime
    'Play_OBJ_door_open_01', 'Play_OBJ_door_close_01',
    'Play_UI_cooldown_ready_01',       # heart monitor during the fight
    'Play_ENM_lighten_world_01', 'Play_ENM_darken_world_01',
    'Play_ENM_deathray_charge_01',     # the Vet charges a big pattern
    'Play_OBJ_glassbottle_shatter_01', # his tray crashes when he falls
    'Play_OBJ_item_spawn_01',          # nurse station hearts
    'Play_MUS_Ending_State_02',        # the ending
]

SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
_CALL = re.compile(r'ClinicSound\.Play\(\s*(?:open\s*\?\s*)?"(Play_[A-Za-z0-9_]+)"(?:\s*:\s*"(Play_[A-Za-z0-9_]+)")?')


def used_in_source(src=SRC):
    found = set()
    for name in os.listdir(src):
        if name.endswith('.cs'):
            for m in _CALL.finditer(open(os.path.join(src, name), encoding='utf-8').read()):
                found.update(g for g in m.groups() if g)
    return found
