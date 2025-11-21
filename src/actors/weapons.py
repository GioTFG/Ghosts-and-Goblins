"""
Module created by Giovanni Ancora for a project at UniPr.
@author Giovanni Ancora (https://github.com/GioTFG and https://github.com/GiovanniAncora)
This project on GitHub: https://github.com/GioTFG/Ghosts-and-Goblins
"""

from src.actors.platforms import Ground, BackgroundSolid, BackgroundPlatform
from src.actors.enemies import Enemy
from src.framework.actor import Actor, Point, Arena

FPS = 30

class Weapon(Actor):
    """
    Generic class to group all the weapons together in a common class.
    """
    pass


class Torch (Weapon):
    """
    One of the many weapons Arthur can use to kill enemies.
    The torch has a parabolic movement when thrown.
    If it collides with an enemy, it is killed.
    If it collides with a gravestone, it just disappears.
    If it falls on the ground, it creates a flame that stays on the ground for a few seconds and kills any enemy that touches it.
    """

    def __init__(self, direction: str, pos: Point):
        # Movement
        self._x, self._y = pos
        self._direction = direction
        self._dx = 8 if direction == "Right" else -8
        self._dy = -10
        self._gravity = 2
        self._max_dy = 8

        # Animations
        self._anim_count = 0

    # -- INHERITED METHODS --
    def pos(self) -> Point:
        return self._x, self._y

    def sprite(self) -> Point:
        count = (self._anim_count // 8) % 2 # Ciclo ogni 8 frame su 2 immagini
        if count == 0: return 0, 896
        else: return 19, 896

    def size(self) -> Point:
        count = (self._anim_count // 8) % 2
        if count == 0: return 14, 13
        else: return 13, 14

    def move(self, arena: Arena):
        self._x += self._dx
        self._y += self._dy

        # Collisions
        for o in arena.collisions():
            if isinstance(o, Enemy): # Enemies get killed when hit by the torch
                #DEVLOG: Qui ho imparato che se lo zombie è stato creato in un altro modulo e l'import è diverso rispetto a quello che ho fatto
                #        per poter usare "Zombie" qui nell'instance of (tipo in game, dove c'era from actors.zombie import Zombie
                #        e qui from src.actors.zombie import Zombie, l'instanceof non li considera della stessa classe perché usano
                #        diverso namespace.

                arena.kill(o)
                arena.kill(self)

            elif isinstance(o, Ground) or isinstance(o, BackgroundPlatform): # If the torch touches the ground, it creates a flame
                self._ground_collision(arena, o)

            elif isinstance(o, BackgroundSolid): # If I touched anything else, I disappear
                arena.kill(self)

        aw, ah = arena.size()
        if self._y > ah: arena.kill(self)

        self._dy = min(self._dy + self._gravity, self._max_dy)

        # Update to the animation counter
        self._anim_count += 1

    def _ground_collision(self, arena: Arena, other: Ground):
        """
        Method called when colliding with the ground.
        Spawns a Flame.
        """
        x, y = self.pos()
        w, h = self.size()
        gx, gy = other.pos()

        cx = x + w / 2 # Centre pixel of the torch
        arena.spawn(Flame((cx, gy))) # The collision point with the ground must be passed as coordinates.
        arena.kill(self) # The torch disappears

class Flame (Weapon):
    """
    The flame created by the torch upon hitting the ground.
    """

    def __init__(self, ground_pos: Point):
        # Movement
        self._start_x, self._start_y = ground_pos # Position on the ground, i.e. the bottom-centre pixel of the sprite
        self._x, self._y = ground_pos # They will be updated to the top-left pixel by the move method

        # Gameplay
        self._life = 2 * FPS # Frames the flame stays active

        # Animations
        self._anim_count = 0

    def pos(self) -> Point:
        return self._x, self._y

    def sprite(self):
        if self._anim_count == 0: return 228, 744
        else: return 192, 736

    def size(self):
        if self._anim_count == 0: return 23, 23
        else: return 32, 32

    def move(self, arena: Arena):
        # Bringing the position (x, y) to the top left pixel
        # This must be done every frame because the sprites have a different sizes, so its position will always change
        # since we use the top-left pixel as anchor points

        self._anim_count = (arena.count() // 4) % 2
        w, h = self.size()
        self._x = self._start_x - w / 2
        self._y = self._start_y - h

        # Enemies touched get killed
        for o in arena.collisions():
            if isinstance(o, Enemy): arena.kill(o)

        # Despawning logic
        if self._life > 0:
            self._life -= 1
        else:
            arena.kill(self)