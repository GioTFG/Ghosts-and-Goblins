from src.actors.platforms import BackgroundSolid
from src.framework.actor import Actor, Arena, Point
import src.framework.utilities as utils

class Arthur(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._speed = 5
        self._gravity = 2
        self._dx, self._dy = 0, 0
        self._state = "IdleRight"
        self._running_state = 1

        self._direction = "Right"

        self._sprites = {
            "IdleRight": (134, 609),
            "IdleLeft": (358, 609),

            "RunningRight1": (5, 608),
            "RunningRight2": (39, 608),
            "RunningRight3": (72, 608),
            "RunningRight4": (102, 608),
            "RunningLeft1": (484, 608),
            "RunningLeft2": (454, 608),
            "RunningLeft3": (421, 608),
            "RunningLeft4": (386, 608),

            "JumpUpRight": (160, 613),
            "JumpDownRight": (194, 613),
            "JumpUpLeft": (320, 613),
            "JumpDownLeft": (291, 613),
        }

        self._sizes = {
            "IdleRight": (20, 31),
            "IdleLeft": (20, 31),
            "RunningRight1": (23, 32),
            "RunningRight2": (18, 32),
            "RunningRight3": (19, 32),
            "RunningRight4": (24, 32),
            "RunningLeft1": (23, 32),
            "RunningLeft2": (18, 32),
            "RunningLeft3": (19, 32),
            "RunningLeft4": (24, 32),

            "JumpUpRight": (32, 27),
            "JumpDownRight": (27, 27),
            "JumpUpLeft": (32, 27),
            "JumpDownLeft": (27, 27)
        }

    def move(self, arena: Arena):
        self._dx = 0    # Serve per capire se c'è movimento negli sprite

        # Tasti
        keys = arena.current_keys()
        if "ArrowLeft" in keys:
            self._dx -= self._speed
            self._direction = "Left"
        if "ArrowRight" in keys:
            self._dx += self._speed
            self._direction = "Right"

        w, h = self.size()

        # Collisioni
        #TODO: Risolvere un problema con le collisioni: quando Arthur è posizionato più a sinistra possibile sulla tomba, cambia a spam l'animazione.
        # Questo perché vengono considerate delle dimensioni dinamiche, e quando Arthur comincia quindi a cadere giù dal lato sinistro della tomba
        # l'animazione di caduta lo fa collidere nuovamente con la tomba, facendolo risalire su ma riportandolo allo sprite (e quindi alle dimensioni) standard.
        # Questo lo porta poi a non collidere più, quindi cadendo di nuovo, facendo ripetere in loop questo a ogni tick.
        # Un possibile modo è il considerare la dimensione statica, ma porterebbe a problemi con la rappresentazione degli sprite e ad eventuali collisioni ingiuste.
        # i.e. "Sono morto ma lo zombie non mi ha toccato."
        for other in arena.collisions():
            if isinstance(other, BackgroundSolid):

                other_x, other_y = other.pos()
                other_w, other_h = other.size()

                if self._y + h / 2 < other_y and self._dy >= 0:
                    # Non copre tutti i casi, infatti gli ostacoli sufficientemente piccoli verrebbero scavalcati.
                    # Potrebbe comunque essere una feature per eventuali scalini...
                    self._y = other_y - h
                    self._dy = 0
                    if "ArrowUp" in keys and self.is_on_ground(arena):
                        self._dy = -10

                elif self._y + h > other_y + other_h and self._dy < 0:
                    self._y = other_y + other_h + 1
                    self._dy = 0
                elif self._x < other_x and self._dx >= 0:
                    self._x = other_x - w
                    self._dx = 0
                elif self._x + w > other_x + other_w and self._dx < 0:
                    self._x = other_x + other_w + 1
                    self._dx = 0

        self._x += self._dx
        self._y += self._dy

        # Controllo out of bounds
        aw, ah = arena.size()
        self._x = min(max(self._x, 0), aw - w)
        self._y = min(max(self._y, 0), ah - h)

        self.set_state(arena)

        self._dy += self._gravity

    def hit(self, arena: Arena):
        arena.kill(self)

    def pos(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        if self._state in self._sizes:
            return self._sizes[self._state]
        return self._sizes["IdleRight"]

    def sprite(self) -> Point:
        if self._state in self._sprites:
            return self._sprites[self._state]
        else:
            return self._sprites["IdleRight"]

    def is_on_ground(self, arena: Arena) -> bool:
        for other in arena.collisions():
            if isinstance(other, BackgroundSolid):
                other_x, other_y = other.pos()
                other_w, other_h = other.size()
                if self._y < other_y and self._dy >= 0:
                    return True
        return False

    def set_state(self, arena: Arena):
        keys = arena.current_keys()

        # current_state = self._state
        self._state = "Idle" + self._direction

        if "ArrowLeft" in keys or "ArrowRight" in keys:
            self._state = "Running" + self._direction + str(self._running_state + 1)
            self._running_state = ((self._running_state + 1) % 4)

        if "ArrowLeft" in keys and "ArrowRight" in keys:
            self._state = "IdleRight"
            self._direction = "Right"

        if not self.is_on_ground(arena):
            if self._dy > 0:
                self._state = "JumpDown" + self._direction
            elif self._dy < 0:
                self._state = "JumpUp" + self._direction
