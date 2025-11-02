from random import choice, randrange
from framework.actor import Actor, Arena, Point

FPS = 30 # Frame per secondo, usati per animazioni in caso si potrà modificare

class Arthur(Actor):
    def __init__(self, pos):
        self._x, self._y = pos
        self._w, self._h = 20, 31
        self._speed = 5
        self._gravity = 2
        self._dy = 0
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
        # Collisioni
        # for other in arena.collisions():
        #     if isinstance(other, Ball):
        #         self.hit(arena)

        self._dx = 0    # Serve per capire se c'è movimento negli sprite

        # Tasti
        keys = arena.current_keys()
        if "ArrowLeft" in keys:
            self._x -= self._speed
            self._direction = "Left"
        if "ArrowRight" in keys:
            self._x += self._speed
            self._direction = "Right"

        aw, ah = arena.size()

        # Gravità
        if "ArrowUp" in keys and self.is_on_ground():
            self._dy = -15

        if self._dy > 0:
            self._dy += self._gravity

        if self.is_on_ground() and not "ArrowUp" in keys:
            self._dy = 0
        else:
            self._dy += self._gravity
            self._y += self._dy

        # Controllo out of bounds
        self._x = min(max(self._x, 0), aw - self._w)
        self._y = min(max(self._y, 0), ah - self._h)

        self.set_state()
        # print(self._dy)

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

    def is_on_ground(self) -> bool:
        aw, ah = arena.size()
        return self._y >= ah - self._h

    def set_state(self):
        keys = g2d.current_keys()

        current_state = self._state
        self._state = "Idle" + self._direction

        if "ArrowLeft" in keys or "ArrowRight" in keys:
            self._state = "Running" + self._direction + str(self._running_state + 1)
            self._running_state = ((self._running_state + 1) % 4)

        if "ArrowLeft" in keys and "ArrowRight" in keys:
            self._state = "IdleRight"
            self._direction = "Right"

        if not self.is_on_ground():
            if self._dy > 0:
                self._state = "JumpDown" + self._direction
            elif self._dy < 0:
                self._state = "JumpUp" + self._direction

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
                self._distance -= self._dx
        else:
            self._dx = 0
            if self._spawn_countdown[2] < self._spawn_countdown_start[2]:
                self._spawn_countdown[2] += 1
            elif self._spawn_countdown[1] < self._spawn_countdown_start[1]:
                self._spawn_countdown[1] += 1
            elif self._spawn_countdown[0] < self._spawn_countdown_start[0]:
                self._spawn_countdown[0] += 1
            else: #Caso in cui è finito il countdown del despawn
                self._despawn()

        # Gravità
        if self.is_on_ground():
            self._dy = 0
        else:
            self._dy += self._gravity
            self._y += self._dy

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

    def _despawn(self):
        self._despawned = True

    def is_despawned(self):
        return self._despawned

    def is_on_ground(self):
        aw, ah = arena.size()
        return self._y >= ah - self.size()[1]

def tick():
    g2d.clear_canvas()

    if randrange(500) == 0:
        player_x, player_y = player.pos()
        direction = choice(("Right", "Left"))
        if direction == "Right":
            arena.spawn(Zombie((player_x - randrange(50, 200), player_y), direction))
        else:
            arena.spawn(Zombie((player_x + randrange(50, 200), player_y), direction))

    for a in arena.actors():
        if a.sprite() != None:
            g2d.draw_image("ghosts-goblins.png", a.pos(), a.sprite(), a.size())
        else:
            pass  # g2d.draw_rect(a.pos(), a.size())

        if isinstance(a, Zombie) and a.is_despawned():
            arena.kill(a)

    arena.tick(g2d.current_keys())  # Game logic


def main():
    global g2d, arena, player
    import framework.g2d as g2d  # game classes do not depend on g2d

    arena = Arena((480, 360))
    # arena.spawn(Ball((40, 80)))
    # arena.spawn(Ball((80, 40)))
    # arena.spawn(Ghost((120, 80)))
    # arena.spawn(Turtle((230, 170)))

    player = Arthur((400, 0))
    arena.spawn(player)
    arena.spawn(Zombie((50, 200), "Right"))

    g2d.init_canvas(arena.size(), 2)
    g2d.main_loop(tick)

if __name__ == "__main__":
    main()
