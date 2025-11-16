from src.actors.platforms import Grave, BackgroundSolid, BackgroundPlatform
from src.framework.actor import Actor, Arena, Point
from random import randrange, randint
from math import atan, sin, cos, pi

FPS = 30

class Enemy(Actor):
    """
    Classe generica per raggruppare tutti i nemici.
    Verrà usata per effettuare un controllo unico per le collisioni con ciò che fa danno ad Arthur.
    I vari metodi devono essere implementati dalle sottoclassi.
    (Volevo evitare di implementare la multi-ereditarietà)
    """
    pass

class Zombie(Enemy):

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

    def __init__(self, pos: Point, direction: str):
        self._x, self._y = pos

        self._direction: str = direction
        """
        Può essere "Right" oppure "Left"
        """

        self._dx = 0
        self._dy = 0
        self._gravity = 2
        self._max_dy = 8

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
            if (isinstance(other, BackgroundSolid) or isinstance(other, BackgroundPlatform)) and not isinstance(other, Grave):
                other_x, other_y = other.pos()

                if self._y + h + 1 > other_y and self._dy >= 0:
                    self._y = other_y - h
                    self._dy = 0


        self._y += self._dy
        self._dy = min(self._dy + self._gravity, self._max_dy)

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

class Plant(Enemy):
    _sprites = {
        "IdleLeft": (564, 207),
        "Shooting1Left": (582, 207),
        "Shooting2Left": (600, 207),
        "Shooting3Left": (618, 207),
        "Shooting4Left": (636, 207),

        "IdleRight": (726, 207),
        "Shooting1Right": (708, 207),
        "Shooting2Right": (690, 207),
        "Shooting3Right": (672, 207),
        "Shooting4Right": (654, 207)
    }

    def __init__(self, pos: Point):
        self._x, self._y = pos

        self._min_count, self._max_count = 1, 10
        self._state, self._direction = "Idle", "Right"
        self._shooting = False
        self._shoot_countdown = self._max_count
        self._current_start_shoot_countdown = self._shoot_countdown

        self._projectile_speed = 4

    def sprite(self):
        sprite = self._state + self._direction
        if sprite in self._sprites:
            return self._sprites[sprite]
        return self._sprites["IdleRight"]

    def size(self):
        return 16, 32

    def pos(self) -> Point:
        return self._x, self._y

    def get_hero(self, arena: Arena):
        """
        Metodo necessario per ottenere poi la posizione di Arthur, per calcolare la direzione dei proiettili.
        :return: Restituisce l'oggetto che rappresenta Arthur se esiste, altrimenti None.
        """
        from src.actors.arthur import Arthur # Lazy import per evitare import circolare

        for a in arena.actors():
            if isinstance(a, Arthur):
                return a
        return None

    def move(self, arena: Arena):
        hero = self.get_hero(arena)
        if hero is None:
            return

        hx, hy = hero.pos() # Posizione di Arthur
        self._direction = "Right" if self._x < hx else "Left"

        self.shoot(arena)
        self._set_state(arena)

    def shoot(self, arena: Arena):
        if self._shoot_countdown > 0:
            self._shoot_countdown -= 1
        else:

            hx, hy = self.get_hero(arena).pos()
            angle = atan((hy - self._y) / ((hx - self._x) or 1)) # or 1 per evitare divisione per 0

            if hx < self._x:
                angle += pi

            eyeball_dx, eyeball_dy = self._projectile_speed * cos(angle), self._projectile_speed * sin(angle)

            # print(f"Pianta spara!, ({eyeball_dx}, {eyeball_dy})")
            Eyeball(self.pos(), (eyeball_dx, eyeball_dy), arena)

            self._shoot_countdown = randint(self._min_count * FPS, self._max_count * FPS)
            self._current_start_shoot_countdown = self._shoot_countdown

    def _set_state(self, arena: Arena):
        shoot_frames = self._current_start_shoot_countdown / 4 # Number of frames taken by each shooting state
        if self._shoot_countdown > shoot_frames * 3:
            self._state = "Shooting1"
        elif self._shoot_countdown > shoot_frames * 2:
            self._state = "Shooting2"
        elif self._shoot_countdown > shoot_frames:
            self._state = "Shooting3"
        else:
            self._state = "Shooting4"

class Eyeball(Enemy):
    def __init__(self, pos: Point, movement: Point, arena: Arena):
        self._x, self._y = pos
        self._dx, self._dy = movement
        arena.spawn(self)

    def pos(self):
        return self._x, self._y

    def move(self, arena: Arena):
        self._x += self._dx
        self._y += self._dy

    def sprite(self):
        spr = (575, 51) if self._dx < 0 else (721, 51)
        return spr

    def size(self):
        return 10, 11