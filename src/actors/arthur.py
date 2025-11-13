from src.actors.platforms import BackgroundSolid, BackgroundPlatform, BackgroundActor, BackgroundLadder
from src.actors.weapons import Torch
from src.framework.actor import Actor, Arena, Point
from src.framework.utilities import center


class Arthur(Actor):
    def __init__(self, pos: Point):
        # Position and movement
        self._x, self._y = pos
        self._dx, self._dy = 0, 0
        self._speed = 5
        self._gravity, self._max_dy = 2, 8
        self._jump_power = -10
        self._climb_speed = 4

        # Gameplay status
        self._grabbing_ladder = False

        # Action countdowns (in frames)
        self._torch_countdown_start, self._torch_countdown = 10, 0

        # Animation info
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

            "ClimbingRight": (133, 642),
            "ClimbingLeft": (358, 642)
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
            "JumpDownLeft": (27, 27),

            "ClimbingLeft": (21, 30),
            "ClimbingRight": (21, 30)
        }

    def move(self, arena: Arena):
        self._dx = 0    # Serve per capire se c'è movimento negli sprite
        keys = arena.current_keys()

        # Azioni
        if self._torch_countdown == 0:
            if "f" in keys:
                self.use_torch(arena)
                self._torch_countdown = self._torch_countdown_start
        else:
            self._torch_countdown -= 1

        # Tasti
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

        if (l := self.is_by_ladder(arena)) is not None:
            self.use_ladder(arena, l)
        else:
            self._grabbing_ladder = False

        for other in arena.collisions():
            if isinstance(other, BackgroundSolid):
                self._solid_collision(arena, other)
            elif isinstance(other, BackgroundPlatform):
                self._platform_collision(arena, other)

        self._x += self._dx
        self._y += self._dy

        # Controllo out of bounds
        aw, ah = arena.size()
        self._x = min(max(self._x, 0), aw - w)
        self._y = min(max(self._y, 0), ah - h)

        self.set_state(arena)

        self._dy = min(self._dy + self._gravity, self._max_dy)

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

    # Metodi di stato
    def is_on_ground(self, arena: Arena) -> bool:
        for other in arena.collisions():
            if isinstance(other, BackgroundActor) and other.is_jumpable():
                other_x, other_y = other.pos()
                # other_w, other_h = other.size()
                if self._y < other_y and self._dy >= 0:
                    return True
        return False

    def is_by_ladder(self, arena: Arena) -> BackgroundLadder | None:
        for other in arena.collisions():
            if isinstance(other, BackgroundLadder):
                return other
        return None

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

        if self._grabbing_ladder:
            if {"ArrowUp", "ArrowDown"} & set(keys):
                count = (arena.count() // 4) % 2
                self._state = "ClimbingRight" if count == 0 else "ClimbingLeft"
            else:
                self._state = "ClimbingRight"
        elif not self.is_on_ground(arena):
            if self._dy > 0:
                self._state = "JumpDown" + self._direction
            elif self._dy < 0:
                self._state = "JumpUp" + self._direction
        elif not self.is_on_ground(arena):
            if self._dy > 0:
                self._state = "JumpDown" + self._direction
            elif self._dy < 0:
                self._state = "JumpUp" + self._direction

    def jump(self, arena: Arena):
        keys = arena.current_keys()
        if "Spacebar" in keys and self.is_on_ground(arena) and not self._grabbing_ladder:
            self._dy = self._jump_power

    # Actions
    def use_torch(self, arena: Arena):
        if not self._grabbing_ladder:
            torch_pos = center(self.pos(), self.size())
            arena.spawn(Torch(self._direction, torch_pos))

    # Collision Methods
    def _solid_collision(self, arena: Arena, other: BackgroundSolid):
        """
        Logica delle collisioni con oggetti solidi
        """
        w, h = self.size()

        other_x, other_y = other.pos()
        other_w, other_h = other.size()

        # Tentativo di implementare questa, ma ci sono comportamenti strani, quindi opterò comunque per il metodo originale, anche se
        # non copre tutti i casi
        # move_x = min(other_x - self._x - w, other_x + other_w - self._x, key=abs)
        # move_y = min(other_y - self._y - h, other_y + other_h - self._y, key=abs)
        #
        # if abs(move_x) < abs(move_x):
        #     self._x += move_x
        #     self._dx = 0
        # elif move_y != 0:
        #     self._y += move_y
        #     self._dy = 0
        #     self.jump(arena)

        # Altro tentativo ancora
        # if isinstance(other, Ground) and self._y + h > other_y and move_y != 0:
        #     self._y = other_y - h
        #     self._dy = 0
        #     self.jump(arena)
        # elif abs(move_y) < abs(move_x):
        #     self._y += move_y
        #     self._dy = 0
        #     self.jump(arena)
        # else:
        #     self._x += move_x
        #     self._dx = 0

        if self._y + h / 2 < other_y and self._dy >= 0:
            # Non copre tutti i casi, infatti gli ostacoli sufficientemente piccoli verrebbero scavalcati.
            # Potrebbe comunque essere una feature per eventuali scalini...
            self._y = other_y - h
            self._dy = 0
            self.jump(arena)
        elif self._y + h > other_y + other_h and self._dy < 0:
            self._y = other_y + other_h
            self._dy = 0
        elif self._x < other_x and self._dx >= 0:
            self._x = other_x - w
            self._dx = 0
        elif self._x + w > other_x + other_w and self._dx < 0:
            self._x = other_x + other_w
            self._dx = 0

    def _platform_collision(self, arena: Arena, other: BackgroundPlatform):
        """
        Logica delle collisioni con le piattaforme (passabili da sotto ma non da sopra).
        """
        other_x, other_y = other.pos()
        w, h = self.size()

        if self._y < other_y and self._dy >= 0 and not self._grabbing_ladder:
            self._y = other_y - h
            self._dy = 0
            self.jump(arena)

    def use_ladder(self, arena: Arena, ladder: BackgroundLadder):
        # self.is_by_ladder DEVE essere True
        # i.e. Arthur è in collisione con l'oggetto scala.

        keys = arena.current_keys()
        if {"Spacebar", "ArrowLeft", "ArrowRight"} & set(keys): # Se nessuno tra i tasti specificati è premuto, ho l'insieme vuoto, che è Falsey
            # Voglio saltare nei pressi della scala, smetto di arrampicarmici
            self._grabbing_ladder = False

        if "ArrowUp" in keys or "ArrowDown" in keys:
            self._grabbing_ladder = True

        if self._grabbing_ladder:
            # Allineo il centro di Arthur al centro della scala
            lx, ly, lw, lh = ladder.pos() + ladder.size()
            w, h = self.size()
            # center_sx = center_lx
            # sx + w / 2 = lx + wl / 2
            # sx + w = lx + wl
            # sx = lx + wl - w
            self._x = lx + lw - w

            # Mi sto già arrampicando sulla scala
            self._dy = 0 # Quindi la gravità non deve funzionare
            if "ArrowDown" in keys:
                self._grabbing_ladder = True
                self._dy += self._climb_speed
            if "ArrowUp" in keys:
                self._grabbing_ladder = True
                self._dy -= self._climb_speed

# Parte di programma usata per test di codice
import unittest
import unittest.mock
class ArthurTest(unittest.TestCase):
    def test_grave(self):
        grave = unittest.mock.Mock(spec= BackgroundSolid)
        grave.pos.return_value = (242, 186)
        grave.size.return_value = (16, 16)
        arena = unittest.mock.Mock()
        arena.collisions.return_value = [grave]
        arena.current_keys.return_value = []
        arena.size.return_value = (500, 500)

        arthur = Arthur((216, 161))

        for _ in range(100):
            arthur.move(arena)
            print(arthur.pos())
            self.assertTrue(arthur._state == "IdleRight")




if __name__ == "__main__":
    unittest.main()