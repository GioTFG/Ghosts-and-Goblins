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

class BackgroundPlatform(BackgroundActor):
    pass

class BackgroundSolid(BackgroundActor):
    pass