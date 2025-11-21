from src.framework.actor import Actor, Arena, Point

FPS = 30

def check_if_hit(arena: Arena):
    """
    Checks if the tomb has been hit by a player projectile. In that case returns True. Otherwise, False.
    """

    from src.actors.weapons import Weapon # Lazy import to avoid circular import

    for a in arena.collisions():
        if isinstance(a, Weapon):
            return True
    return False


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

    def is_jumpable(self) -> bool:
        """
        Returns if the actor (Arthur) can jump off of the platform.
        """
        return False


"""
Ho creato questo sistema di sottoclassi per poter distinguere bene i vari tipi di piattaforma che ci sono nel gioco-
(ad esempio, distinguere per lo zombie il terreno (Ground) dalle tombe o altri ostacoli (Grave)).
Sebbene potessi creare per una singola classe un attributo (ad esempio, self._type = "Grave"), ho preferito creare
delle sottoclassi, seppur eventualmente vuote, perché più flessibili nella possibilità di estendere i loro comportamenti.
Esempio di questo è ciò che ho implementato per BackgroundPlatform e BackgroundSolid, che hanno la particolarità di
permettere ad Arthur di saltare da esse.

-- Translation --
I made this system of subclasses to better distinguish the various types of platforms (because for example, the Zombie has
to collide against terrain (Ground), but not against tombstones (Grave).
I chose this rather than creating an attribute because they are more flexible for any future features.
(For example, the is_jumpable method).
"""
class BackgroundPlatform(BackgroundActor):
    def is_jumpable(self) -> bool:
        return True

class BackgroundSolid(BackgroundActor):
    def is_jumpable(self) -> bool:
        return True

class Grave(BackgroundSolid):
    def __init__(self, pos: Point, size: Point):
        super().__init__(pos, size)

        # Everytime a tomb is hit by a weapon (with a cooldown), this counter increments.
        # When it reaches 15, it spawns the magician.
        self._times_hit = 0
        self._max_hit_cooldown = self._hit_cooldown = 1 * FPS

    def move(self, arena: Arena):
        super().move(arena)

        if self._hit_cooldown == 0:
            if check_if_hit(arena):
                self._hit_cooldown = self._max_hit_cooldown
                self._times_hit += 1
        else:
            self._hit_cooldown -= 1

        if self._times_hit >= 15:
            self._times_hit = 0
            self.spawn_magician(arena)

    def spawn_magician(self, arena: Arena):
        from src.actors.enemies import Magician # Lazy import to avoid circular imports
        m = Magician((self._x, self._y - 32))
        arena.spawn(m)

class Ground(BackgroundSolid):
    pass

class BackgroundLadder(BackgroundActor):
    pass

class BackgroundWinArea(BackgroundLadder):
    """
    If Arthur collides with this area, the game is won.
    """
    pass