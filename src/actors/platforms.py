from src.framework.actor import Actor, Arena, Point

class BackgroundActor(Actor):
    """
    Generic class for an actor which has collisions but doesn't have a sprite, because it is already rendered
    in the background image.
    """
    def __init__(self, pos: Point, size: Point):
        self._x, self._y = pos
        self._w, self._h = size

    def pos(self) -> Point:
        return self._x, self._y

    def move(self, arena: Arena):
        pass

    def size(self) -> Point:
        return self._w, self._h

    def sprite(self):
        return None


"""
Ho creato questo sistema di sottoclassi per poter distinguere bene i vari tipi di piattaforma che ci sono nel gioco-
(ad esempio, distinguere per lo zombie il terreno (Ground) dalle tombe o altri ostacoli (Grave)).
Sebbene potessi creare per una singola classe un attributo (ad esempio, self._type = "Grave"), ho preferito creare
delle sottoclassi, seppur eventualmente vuote, perché più flessibili nella possibilità di estendere i loro comportamenti.
"""
class BackgroundPlatform(BackgroundActor):
    pass

class BackgroundSolid(BackgroundActor):
    pass

class Grave(BackgroundSolid):
    pass

class Ground(BackgroundSolid):
    pass