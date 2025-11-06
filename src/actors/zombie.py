from src.actors.platforms import BackgroundSolid, Grave, Ground
from src.framework.actor import Actor, Arena
from random import randrange

FPS = 30

class Zombie(Actor):

    _sprites: dict[str, tuple[int, int]] = {
        "Spawn1Left": (512, 88),
        "Spawn2Left": (533, 85),
        "Spawn3Left": (562, 73),
        "Spawn1Right": (778, 88),
        "Spawn2Right": (748, 85),
        "Spawn3Right": (725, 73),

        "Walk1Left": (585, 66),
        "Walk2Left": (610, 65),
        "Walk3Left": (631, 66),
        "Walk1Right": (699, 66),
        "Walk2Right": (677, 65),
        "Walk3Right": (654, 66),

        "DespawnedLeft": None,
        "DespawnedRight": None
    }

    _sizes: dict[str, tuple[int, int]] = {
        "Spawn1": (16, 9),
        "Spawn2": (24, 12),
        "Spawn3": (19, 24),
        "Walk1": (22, 31),
        "Walk2": (19, 32),
        "Walk3": (21, 31),

        "Despawned": (0,0)
    }

    def __init__(self, pos: tuple[float, float], direction: str):
        self._x, self._y = pos

        self._direction: str = direction
        """
        Può essere "Right" oppure "Left"
        """

        self._dx = 0
        self._dy = 0
        self._gravity = 2

        self._distance = randrange(150, 301)
        self._state = "Spawn" + direction

        self._spawn_countdown: list[int] | None = None
        """
            Tupla di tre interi: tempo (frame) per ognuna delle tre fasi di spawn dello zombie 
        """

        self._x_speed = 3

        self._walk_anim_countdown_start = 1 * FPS
        self._walk_anim_countdown = self._walk_anim_countdown_start

        self._spawn()

    def pos(self) -> tuple[float, float]:
        return self._x, self._y

    def size(self):
        if self._state in self._sizes:
            return self._sizes[self._state]
        return self._sizes["Walk3"]

    def sprite(self):
        # print(f"Dist:{self._distance}, State:{self._state}, SpCtdwn:{self._spawn_countdown}, SeCtStart:{self._spawn_countdown_start}\n\n")
        if self._state + self._direction in self._sprites:
            return self._sprites[self._state + self._direction]
        else:
            return self._sprites["Walk3" + self._direction]

    def move(self, arena: Arena):
        # print(self._distance)
        if self._distance > 0:
            "Il campo distance contiene il numero di pixel che ancora deve percorrere lo zombie prima di poter despawnare."
            if self._spawn_countdown[0] > 0:
                self._spawn_countdown[0] -= 1
            elif self._spawn_countdown[1] > 0:
                self._spawn_countdown[1] -= 1
            elif self._spawn_countdown[2] > 0:
                self._spawn_countdown[2] -= 1
            else:
                self._dx = self._x_speed if self._direction == "Right" else -self._x_speed
                self._x += self._dx
                self._distance -= abs(self._dx)
        else:
            self._dx = 0
            if self._spawn_countdown[2] < self._spawn_countdown_start[2]:
                self._spawn_countdown[2] += 1
            elif self._spawn_countdown[1] < self._spawn_countdown_start[1]:
                self._spawn_countdown[1] += 1
            elif self._spawn_countdown[0] < self._spawn_countdown_start[0]:
                self._spawn_countdown[0] += 1
            else: #Caso in cui è finito il countdown del despawn
                self._despawn(arena)

        w, h = self.size()

        for other in arena.collisions():
            if isinstance(other, Ground):
                other_x, other_y = other.pos()
                other_w, other_h = other.size()
                #
                # x_center, y_center = utils.center((self._x, self._y), (self._w, self._h))
                # x_other_center, y_other_center = utils.center((other_x, other_y), (other_w, other_y))

                if self._y + h + 1 > other_y and self._dy >= 0:
                    self._y = other_y - h
                    self._dy = 0


        self._y += self._dy
        self._dy += self._gravity

        # Controllo out of bounds
        aw, ah = arena.size()
        self._x = min(max(self._x, 0), aw - self.size()[0])
        self._y = min(max(self._y, 0), ah - self.size()[1])

        self._set_state()

    def _spawn(self):
        """
        Metodo per inizializzare le statistiche di spawn dello zombie
        """

        self._state = "Spawn1"

        self._spawn_countdown = (randrange(1, 3), randrange(1, 3), randrange(1,4))
        self._spawn_countdown = [c * FPS for c in self._spawn_countdown]
        self._spawn_countdown_start = self._spawn_countdown[:] # Faccio una copia per riutilizzare i valori iniziali

        self._spawned = True
        self._despawned = False

    def _set_state(self):

        if self._despawned:
            self._state = "Despawned"

        elif self._dx != 0:
            self._state = "Walk"
            if self._walk_anim_countdown > self._walk_anim_countdown_start * 2 / 3:
                self._state += "1"
            elif self._walk_anim_countdown > self._walk_anim_countdown_start * 1 / 3:
                self._state += "2"
            else:
                self._state += "3"
            self._walk_anim_countdown = (self._walk_anim_countdown - 1) % self._walk_anim_countdown_start

        elif any(self._spawn_countdown):
            if self._spawn_countdown[0] > 0:
                self._state = "Spawn1"
            elif self._spawn_countdown[1] > 0:
                self._state = "Spawn2"
            elif self._spawn_countdown[2] > 0:
                self._state = "Spawn3"

        else:
            self._state = "Idle"

    def _despawn(self, arena: Arena):
        self._despawned = True
        arena.kill(self)

    def is_despawned(self):
        return self._despawned

    def is_on_ground(self, arena: Arena):
        return self._dy == 0
