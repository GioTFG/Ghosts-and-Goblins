from .actor import Arena, Actor, Point
from .utilities import remove_pos


class View:
    def __init__(self, pos: Point = (0, 0), size: Point = (200, 100), actor: Actor = None):
        self._x, self._y = pos
        self._w, self._h = size
        self._speed = 2
        self._actor = actor


    def pos(self):
        return self._x, self._y

    def size(self):
        return self._w, self._h

    def move(self, arena: Arena):

        if self._actor is not None:
            self._x, self._y = remove_pos(self._actor.pos(), (self._w / 2, self._h / 2))
        else:
            # Se non è "attaccata" a un actor, posso usare i tasti [I, J, K, L] per muoverla
            keys = arena.current_keys()
            if keys is not None:
                dx, dy = 0, 0

                if "i" in keys:
                    dy = -self._speed
                if "k" in keys:
                    dy = self._speed
                if "j" in keys:
                    dx = -self._speed
                if "l" in keys:
                    dx = self._speed

                self._x += dx
                self._y += dy

        self._x = max(self._x, 0)
        self._y = max(self._y, 0)
        self._x = min(self._x, int(arena.size()[0] - self._w))
        self._y = min(self._y, int(arena.size()[1] - self._h))