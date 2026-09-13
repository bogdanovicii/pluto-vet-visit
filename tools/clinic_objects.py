"""Props of the vet clinic: ASCII sprites, collider specs and where they stand in the room.

OBJECTS: every prop prefab (name -> art + collider). PROPS: placements (name, (x, y)) in room cells,
x to the right and y up from the room's bottom-left corner, as the game places objects.
Task 6 fills both lists; the controller object is placed by clinic_room.py itself.
"""


class Obj:
    def __init__(self, name, png, rows, collider=None, height_off_ground=0.0):
        self.name = name                        # StaticReferences.customObjects key, e.g. pluto_exam_table
        self.png = png                          # file stem under Resources/Objects/
        self.rows = rows                        # ASCII map
        self.collider = collider                # None or (layer, off_x, off_y, w, h) in pixels; layer 'low'|'high'
        self.height_off_ground = height_off_ground

    @property
    def size(self):
        return (max(len(r) for r in self.rows), len(self.rows))


OBJECTS = []
PROPS = []
