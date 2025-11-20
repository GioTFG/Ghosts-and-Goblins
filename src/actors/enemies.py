from src.actors.platforms import Grave, BackgroundSolid, BackgroundPlatform
from src.framework.actor import Actor, Arena, Point
from random import randrange, randint
from math import atan, sin, cos, pi

FPS = 30

class Enemy(Actor):
    """
    Generic class that represents all the Enemies (everything that can hurt Arthur).
    All the real actual methods will be used by the subclasses, this is only an interface.
    (I made this because I wanted to avoid multi-inheritance)
    """
    pass

class Zombie(Enemy):
    """
    The most basic enemy in the game.
    It randomly spawns at a certain horizontal distance from Arthur.
    When it spawns, it rises from the ground, then it starts walking, and then he digs back underground to despawn.
    It never changes its direction, so it can be easily avoided by jumping from above.
    """

    # Dictionary that contains all the top-left coordinates of a sprite in the spritesheet.
    # For each state, there are two values: one for each direction.
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

    # Since the size of any sprite doesn't change when mirrored from the left to the right, there's only one size for each state.
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

        ## - Position and movement
        self._x, self._y = pos
        self._direction: str = direction # It can only be "Right" or "Left"
        self._dx = 0
        self._x_speed = 3
        self._dy = 0
        self._gravity = 2
        self._max_dy = 8 # So it doesn't pass through when falling too fast

        ## - Gameplay status
        self._distance = randrange(150, 301) # How many pixels the Zombie must travel before despawning
        self._state = "Spawn" + direction


        ## - Animation countdowns
        self._spawn_countdown: list[int] | None = None
        """
            Three number tuple: time (in frames) taken by each of the three stages of spawning of the Zombies
        """

        self._walk_anim_countdown_start = 1 * FPS
        self._walk_anim_countdown = self._walk_anim_countdown_start

        # Spawn animation
        self._spawn()

    def pos(self) -> tuple[float, float]:
        return self._x, self._y

    def size(self):
        if self._state in self._sizes:
            return self._sizes[self._state]
        return self._sizes["Walk3"] # Default state to avoid the game crashing if an invalid state is calculated.

    def sprite(self):
        if self._state + self._direction in self._sprites:
            return self._sprites[self._state + self._direction]
        else:
            return self._sprites["Walk3" + self._direction]

    def move(self, arena: Arena):
        if self._distance > 0: # If the zombies still hasn't travelled enough pixels...
            # The zombie has a tuple of frames for each state of spawning
            # For example, (100, 200, 50) means that the zombie, before walking has to:
            # Wait 100 frames for its first spawning stage
            # Wait 200 frames for its second spawning stage
            # Wait 50 frames for its third spawning stage
            # A similar system is used to manage its despawning.
            if self._spawn_countdown[0] > 0:
                self._spawn_countdown[0] -= 1
            elif self._spawn_countdown[1] > 0:
                self._spawn_countdown[1] -= 1
            elif self._spawn_countdown[2] > 0:
                self._spawn_countdown[2] -= 1
            else: # When every number in the tuple is zero (0, 0, 0), the zombie can finally walk.
                self._dx = self._x_speed if self._direction == "Right" else -self._x_speed
                self._x += self._dx
                self._distance -= abs(self._dx)
        else: # The zombie travelled all the pixel assigned to him, so he can despawn
            self._dx = 0
            if self._spawn_countdown[2] < self._spawn_countdown_start[2]:
                self._spawn_countdown[2] += 1
            elif self._spawn_countdown[1] < self._spawn_countdown_start[1]:
                self._spawn_countdown[1] += 1
            elif self._spawn_countdown[0] < self._spawn_countdown_start[0]:
                self._spawn_countdown[0] += 1
            else: #When he went through all the despawning animations, he can actually despawn.
                self._despawn(arena)

        w, h = self.size()

        # Collisions
        for other in arena.collisions():
            if (isinstance(other, BackgroundSolid) or isinstance(other, BackgroundPlatform)) and not isinstance(other, Grave):
                other_x, other_y = other.pos()

                if self._y + h + 1 > other_y and self._dy >= 0:
                    self._y = other_y - h
                    self._dy = 0

        # Gravity
        self._y += self._dy
        self._dy = min(self._dy + self._gravity, self._max_dy)

        # Check if out of bounds
        sw, sh = self.size()
        aw, ah = arena.size()

        if self._y + sh > ah: # Despawn if fallen in a pit
            arena.kill(self)

        self._x = min(max(self._x, 0), aw - self.size()[0])
        self._y = min(max(self._y, 0), ah - self.size()[1])

        # The state decides the sprite used for the next frame
        self._set_state()

    def _spawn(self):
        """
        This method initializes the attributes for the zombie spawning animation
        """

        self._state = "Spawn1"

        # Each of the zombie's spawning stage takes a random amount of time from one to three seconds.
        self._spawn_countdown = (randrange(1, 3), randrange(1, 3), randrange(1,4))
        self._spawn_countdown = [c * FPS for c in self._spawn_countdown]
        self._spawn_countdown_start = self._spawn_countdown[:] # I save a copy of the generated tuple so that it can be reused for the despawning

        self._spawned = True
        self._despawned = False

    def _set_state(self):
        """
        The state decides the sprite used in the following frame.
        It is calculated based on the zombie characteristics.
        """

        if self._despawned:
            self._state = "Despawned"

        elif self._dx != 0:
            # The zombies have three sprites they cycle through when walking.
            # This implementation uses an internal countdown.
            self._state = "Walk"
            if self._walk_anim_countdown > self._walk_anim_countdown_start * 2 / 3:
                self._state += "1"
            elif self._walk_anim_countdown > self._walk_anim_countdown_start * 1 / 3:
                self._state += "2"
            else:
                self._state += "3"
            self._walk_anim_countdown = (self._walk_anim_countdown - 1) % self._walk_anim_countdown_start

        elif any(self._spawn_countdown): # If any of the three spawning counters is acrive...
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
    """
    A really, really annoying plant that throws skulls (eyeballs in the original game) at Arthur.
    At least, it doesn't move... phew :)
    """

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

        # The plant throws a projectile at random intervals of time, between min_count and max_count
        self._min_count, self._max_count = 1, 10 # In seconds, then it will multiplied by the FPS
        self._shooting = False
        self._shoot_countdown = self._max_count * FPS # The first time, the plant waits the max amount of time before shooting
        self._current_start_shoot_countdown = self._shoot_countdown
        self._projectile_speed = 4
        self._max_distance = 400

        self._state, self._direction = "Idle", "Right"

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
        This method is used to get Arthur's position, so the plant know where to shoot its projectile
        If Arthur doesn't exist, it returns None.
        """
        from src.actors.arthur import Arthur # Lazy import per evitare import circolare
        for a in arena.actors():
            if isinstance(a, Arthur):
                return a
        return None

    def move(self, arena: Arena):
        # The plant doesn't move, but if the hero exists, when the cooldown goes to 0 it shoots towards him.

        hero = self.get_hero(arena)
        if hero is None or hero.has_won():
            return


        hx, hy = hero.pos() # Arthur's position

        if abs(self._x - hx) > self._max_distance:
            return # Arthur must be close enough to the plant for it to begin to shoot him

        self._direction = "Right" if self._x < hx else "Left" # Used to render the correct sprite

        self.shoot(arena)
        self._set_state(arena)

    def shoot(self, arena: Arena):
        """
        Called when a new projectile is shot by the plant.
        Manages the shoot cooldown.
        """

        if self._shoot_countdown > 0:
            self._shoot_countdown -= 1
        else:

            hx, hy = self.get_hero(arena).pos()
            angle = atan((hy - self._y) / ((hx - self._x) or 1)) # or 1 to avoid division by 0

            if hx < self._x:
                angle += pi

            eyeball_dx, eyeball_dy = self._projectile_speed * cos(angle), self._projectile_speed * sin(angle)

            Eyeball(self.pos(), (eyeball_dx, eyeball_dy), arena)

            # The countdown is actually in seconds, then multiplied by the FPS number to get the frames.
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
    """
    The projectile shot by the plant at random intervals.
    Starts from the plant position and always moves at the same speed and direction.
    """
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