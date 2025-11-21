from src.actors.enemies import Enemy, MagicProjectile
from src.actors.platforms import BackgroundSolid, BackgroundPlatform, BackgroundActor, BackgroundLadder, \
    BackgroundWinArea, Grave
from src.actors.weapons import Torch
from src.framework.actor import Actor, Arena, Point
from src.framework.utilities import center, remove_pos

FPS = 30

class Arthur(Actor):
    """
    Arthur is the protagonist of the game.
    He is a knight that took on this journey to save his beloved princess.
    He is controlled by the player, can attack and be attacked by other enemies.
    """

    def __init__(self, pos: Point):
        # Position and movement
        self._x, self._y = pos
        self._dx, self._dy = 0, 0
        self._speed = 5
        ## max._dy is needed so that Arthur can't fall at an ever-increasing speed.
        ## Reaching high speeds of fall means that he could technically be placed under platforms where he should have landed on.
        self._gravity, self._max_dy = 2, 8
        self._human_max_dy = 8
        self._frog_max_dy = 3
        self._jump_power = -10
        self._climb_speed = 4

        # Gameplay status
        self._grabbing_ladder = False
        self._armour = True
        self._dead = False
        self._won = False

        # Action countdowns (in frames)
        ## Each one of these is actually a pair of attributes: the first one being the initial value, and the second one the actual one.
        self._torch_countdown_start, self._torch_countdown = 10, 0
        self._invincibility_frames, self._iframes_count = 90, 0
        self._start_dying_countdown = self._dying_countdown = 150

        # Animation info
        ## The state is calculated every tick and determines which sprite and size must be used in that said tick.
        self._state = "IdleRight"
        self._direction = "Right"

        # Frog easter egg
        self._frog = False
        self._max_frog_countdown = self._frog_count = 5 * FPS # How many frames the frog state lasts

        ## A (static) dictionary of all the coordinates of the sprite in the spritesheet based on the state it has been assigned to.
        ### As these value are different based on the direction Arthur is facing, for each state there are two values: one for each direction.
        self._sprites = {
            "IdleRight": (134, 609),
            "IdleLeft": (358, 609),

            "Running1Right": (5, 608),
            "Running2Right": (39, 608),
            "Running3Right": (72, 608),
            "Running4Right": (102, 608),
            "Running1Left": (484, 608),
            "Running2Left": (454, 608),
            "Running3Left": (421, 608),
            "Running4Left": (386, 608),

            "JumpUpRight": (160, 613),
            "JumpDownRight": (194, 613),
            "JumpUpLeft": (320, 613),
            "JumpDownLeft": (291, 613),

            "ClimbingRight": (133, 642),
            "ClimbingLeft": (358, 642),

            "HurtRight": (0, 740),
            "HurtLeft": (487, 740),

            "Dead1Right": (64, 740),
            "Dead2Right": (96, 740),
            "Dead3Right": (128, 743),
            "Dead4Right": (160, 740),
            "Dead5Right": (160, 756),
            "Dead1Left": (423, 740),
            "Dead2Left": (385, 740),
            "Dead3Left": (354, 743),
            "Dead4Left": (324, 740),
            "Dead5Left": (324, 756),

            "WonLeft": (224, 704),
            "WonRight": (256, 704),

            "FrogWalk1Right": (99, 903),
            "FrogWalk2Right": (128, 903),
            "FrogWalk3Right": (166, 903),
            "FrogWalk4Right": (198, 903),
            "FrogWalk1Left": (388, 903),
            "FrogWalk2Left": (355, 903),
            "FrogWalk3Left": (325, 903),
            "FrogWalk4Left": (294, 903),
        }
        # Here even just one value for each state could be used, since no matter the direction, the size of the sprite is the same.
        # An improved implementation that observes this can be seen in the Zombie class.
        self._sizes = {
            "IdleRight": (20, 31),
            "IdleLeft": (20, 31),
            "Running1Right": (23, 32),
            "Running2Right": (18, 32),
            "Running3Right": (19, 32),
            "Running4Right": (24, 32),
            "Running1Left": (23, 32),
            "Running2Left": (18, 32),
            "Running3Left": (19, 32),
            "Running4Left": (24, 32),

            "JumpUpRight": (32, 27),
            "JumpDownRight": (27, 27),
            "JumpUpLeft": (32, 27),
            "JumpDownLeft": (27, 27),

            "ClimbingLeft": (21, 30),
            "ClimbingRight": (21, 30),

            "HurtLeft": (25, 28),
            "HurtRight": (25, 28),

            "Dead1Right": (25, 28),
            "Dead2Right": (31, 28),
            "Dead3Right": (29, 25),
            "Dead4Right": (28, 12),
            "Dead5Right": (28, 12),
            "Dead1Left": (25, 28),
            "Dead2Left": (31, 28),
            "Dead3Left": (29, 25),
            "Dead4Left": (28, 12),
            "Dead5Left": (28, 12),

            "WonLeft": (32, 32),
            "WonRight": (32, 32),

            "FrogWalk1Right": (25, 25),
            "FrogWalk2Right": (29, 25),
            "FrogWalk3Right": (20, 25),
            "FrogWalk4Right": (20, 25),
            "FrogWalk1Left": (25, 25),
            "FrogWalk2Left": (29, 25),
            "FrogWalk3Left": (20, 25),
            "FrogWalk4Left": (20, 25),
        }

        # This is basically a dictionary that maps each action that Arthur can do to a set of keys.
        # This allows to expand the project and add customization: for example, using a menu, the player could set
        # his own keys to each action, just like you can do in modern games.
        # A key concept kept in mind while making this project has been exactly this: modularity, scalability and customization.
        self._actions = {
            "RunLeft": {"a", "ArrowLeft"},
            "RunRight": {"d", "ArrowRight"},
            "Jump": {"Spacebar", "left alt"},
            "ClimbLadder": {"w", "ArrowUp"},
            "DescendLadder": {"s", "ArrowDown"},
            "Attack": {"f", "left ctrl"}
        }

        # This is a list of states whose values can be added to a certain number (66) to obtain the same sprite but without the armour.
        self._no_armour_states = [
            "IdleLeft", "IdleRight",
            "Running1Left", "Running2Left", "Running3Left", "Running4Left",
            "Running1Right", "Running2Right", "Running3Right", "Running4Right",
            "JumpUpLeft", "JumpDownLeft",
            "JumpUpRight", "JumpDownRight",
            "ClimbingLeft", "ClimbingRight",
        ]

    # -- INHERITED METHODS --
    def move(self, arena: Arena):

        # Each frame the horizontal speed is set to zero, as it is re-calculated each tick.
        self._dx = 0
        keys = arena.current_keys()

        # Death management
        if self._dead and self._dying_countdown == 0:
            arena.kill(self)
        elif self._dead and self._dying_countdown > 0:
            self._dying_countdown -= 1

        # Player actions

        ## Attacking
        if self._torch_countdown == 0:
            if set(keys) & self._actions["Attack"] and self._iframes_count == 0 and not self._dead and not self._frog:
                self.use_torch(arena)
                self._torch_countdown = self._torch_countdown_start
        else:
            self._torch_countdown -= 1

        # Moving right and left
        if not self._dead and not self._won:
            if set(keys) & self._actions["RunLeft"] and not (set(keys) & self._actions["RunRight"]):
                self._dx = -self._speed
                self._direction = "Left"
            if set(keys) & self._actions["RunRight"] and not set(keys) & self._actions["RunLeft"]:
                self._dx = self._speed
                self._direction = "Right"
            # Se si cliccano sia sx che dx, non succede niente

        w, h = self.size()

        # Climbing
        if (l := self.is_by_ladder(arena)) is not None and not self._frog:
            self.use_ladder(arena, l)
        else:
            self._grabbing_ladder = False

        # Collisions
        for other in arena.collisions():
            if isinstance(other, BackgroundSolid):
                self._solid_collision(arena, other)
            elif isinstance(other, BackgroundPlatform):
                self._platform_collision(arena, other)
            elif isinstance(other, Enemy):
                self.hurt(arena, other)
            elif isinstance(other, BackgroundWinArea):
                self._won = True

        self._x += self._dx
        self._y += self._dy

        # Check if Arthur went outside the arena (for example, if he fell in a bottomless pit).
        aw, ah = arena.size()
        if self._y + h > ah:
            self.instant_die(arena)
        self._x = min(max(self._x, 0), aw - w)
        self._y = min(max(self._y, 0), ah - h)

        # The state is calculated each tick, as it defines which sprite will be used for the next frame.
        self.set_state(arena)

        self._dy = min(self._dy + self._gravity, self._max_dy)

        if self._iframes_count > 0:
            self._iframes_count -= 1

        # Debug
        if "l" in keys:
            self._frog = True
            self._frog_count = 15000


        if self._frog and self._frog_count > 0:
            self._frog_count -= 1
            self._max_dy = self._frog_max_dy
        else:
            self._frog = False
            self._frog_count = self._max_frog_countdown
            self._max_dy = self._human_max_dy


    def pos(self) -> Point:
        return self._x, self._y

    def size(self) -> Point:
        if self._state in self._sizes:
            size_value = self._sizes[self._state]

        # To avoid possible bugs, if the program somehow calculates a state not present in the dictionary, "IdleRight" is used as a default.
        else: size_value = self._sizes["IdleRight"]

        if not self._armour:
            size_value = size_value[0], size_value[1] - 2 # Height difference without the armour.

        return size_value

    def sprite(self) -> Point | None:

        # If Arthur is hit, he will "blink", so on some frames he will not be visible.
        if not self._dead and self._iframes_count > 0 and self._iframes_count % 2 == 0:
            return None

        if self._state in self._sprites:
            sprite_pos = self._sprites[self._state]
        else:
            sprite_pos = self._sprites["IdleRight"] # IdleRight is the default state, if a size for the current one can't be found.

        if not self._armour and self._state in self._no_armour_states:
            sprite_pos = sprite_pos[0], sprite_pos[1] + 66 #Offset for sprites without armour.

        return sprite_pos

    # -- STATE METHODS --
    def is_on_ground(self, arena: Arena) -> bool:
        """
        Returns true if Arthur has landed on the ground and not moving vertically.
        This is used to check if he can jump and to calculate the state.
        """
        for other in arena.collisions():
            if isinstance(other, BackgroundActor) and other.is_jumpable():
                other_x, other_y = other.pos()
                # other_w, other_h = other.size()
                if self._y < other_y and self._dy >= 0:
                    return True
        return False

    def is_by_ladder(self, arena: Arena) -> BackgroundLadder | None:
        """
        Returns true if Arthur is colliding with a ladder object (he mustn't necessarily be climbing it for this to be true).
        """
        for other in arena.collisions():
            if isinstance(other, BackgroundLadder):
                return other
        return None

    def set_state(self, arena: Arena):
        """
        This method calculates Arthur's state based on his paramethers.
        The calculated state is very important, as it represents the sprite that must be used for the current frame.
        """
        keys = arena.current_keys()

        # Default state
        self._state = "Idle" + self._direction

        # Running states
        """
        This is a fast way to check if any of the elements present on the first list are present in the second list.
        It basically checks the intersection of the two corresponding sets:
        - if there aren't pressed keys present to make Arthur move left (or right), we get an empty set, which is Falsey.
        - Otherwise, we would get a set containing the pressed keys correct for this action, and since it's not an empty set, it's Truthy.
        """
        if set(keys) & self._actions["RunLeft"] or set(keys) & self._actions["RunRight"]:
            ### Every three frames the sprite cycles to the next.
            self._state = "Running" + str(((arena.count() // 3) % 4) + 1) + self._direction

        # If both of the keys to go left and right are pressed at the same time, right is chosen as a default direction.
        # (even if Arthur won't actually move)
        if set(keys) & self._actions["RunLeft"] and set(keys) & self._actions["RunRight"]:
            self._state = "IdleRight"
            self._direction = "Right"

        if self._won:
            self._state = "Won" + self._direction
        elif self._dead:
            # Upon death, Arthur goes through many states, depending on the values of his death_countdown:
            # - Since there are six total death states, each state will be the total countdown divided by six
            state_time = self._start_dying_countdown / 6

            # We check which is the stage we are in currently, and produce the corresponding state.
            if self._dying_countdown > state_time * 5:
                ## In this stage, Arthur actually cycles between two inner states: "Hurt" and "Dead1"
                iterations = 6 # Number of sprite cycles between "Hurt" and "Dead1".
                iteration_frames = self._start_dying_countdown / 6 / iterations # Number of frames the sprite has to cycle between the two states.
                c = (arena.count() // iteration_frames) % 2 # Variable that decides the actual state.
                if c == 0:
                    self._state = "Hurt" + self._direction
                else:
                    self._state = "Dead1" + self._direction

            elif self._dying_countdown > state_time * 4:
                self._state = "Dead2" + self._direction
            elif self._dying_countdown > state_time * 3:
                self._state = "Dead3" + self._direction
            elif self._dying_countdown > state_time * 2:
                self._state = "Dead4" + self._direction
            else:
                self._state = "Dead5" + self._direction

        # Frog easter egg
        elif self._frog and self._frog_count > 0:
            if not set(keys) & (self._actions["RunLeft"] | self._actions["RunRight"]):
                self._state = "FrogWalk4" + self._direction
            else:
                count = ((arena.count() // 5) % 4) + 1
                self._state = "FrogWalk" + str(count) + self._direction

        # If arthur is not dead, we check if he's been hurt (we know if he has, as he has some invincibility frames).
        elif not self._armour and self._iframes_count > 0:
            self._state = "Hurt" + self._direction

        # Here we cycle between the two directions so it seems that Arthur is climbing the ladder.
        elif self._grabbing_ladder:
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

    def has_won(self) -> bool:
        return self._won

    def has_armour(self):
        return self._armour

    # -- PLAYER ACTION METHODS --
    def jump(self, arena: Arena):
        """
        Here the program checks if the correct key for jumping is used, if Arthur can actually jump, and in that case, jump.
        """
        keys = arena.current_keys()
        if set(keys) & self._actions["Jump"] and self.is_on_ground(arena) and not self._grabbing_ladder:
            self._dy = self._jump_power

    def use_torch(self, arena: Arena):
        """
        Check if Arthur can actually attack, and in that case spawn the weapon used to attack.
        For example: Graves, Ground
        """
        if not self._grabbing_ladder and not self._won:
            torch_pos = center(self.pos(), self.size()) # The weapon is spawned at the center of Arthur's sprite.
            arena.spawn(Torch(self._direction, torch_pos))


    # -- COLLISION METHODS --
    def _solid_collision(self, arena: Arena, other: BackgroundSolid):
        """
        Collision logic against solid objects (objects that can't be passed through in any way)
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

        offset_y = 3 # Offset for lower graves
        if offset_y + self._y + h / 2 < other_y and self._dy >= 0:
            # Non copre tutti i casi, infatti gli ostacoli sufficientemente piccoli verrebbero scavalcati.
            # Potrebbe comunque essere una feature per eventuali scalini...
            self._y = other_y - h
            self._dy = 0

            if not self._dead:
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
        Collision logic against platforms (that can be passed through from below but not from above).
        """
        other_x, other_y = other.pos()
        w, h = self.size()

        if self._y < other_y and self._dy >= 0 and not self._grabbing_ladder:
            self._y = other_y - h
            self._dy = 0

            if not self._dead:
                self.jump(arena)

    def hurt(self, arena: Arena, other: Enemy | None):
        """
        This method is called if in the current frame Arthur is colliding with an Enemy.
        It checks if the player has any i-frames (invincibility frames).
        This number is decremented in the move method and not here as this method isn't called every tick, but only
        when colliding against an enemy.
        If Arthur has been hit when vulnerable, and he still has his armour, he loses it.
        If he's been hit when vulnerable, and he already lost his armour, he dies.
        """
        if self._iframes_count <= 0 and not self._dead and not self._won:
            # In this case Arthur has been hit when vulnerable

            # When hurt, Arthur gets knocked back
            self._dx = -30 if self._direction == "Right" else 30
            self._dy = -10

            # If he's a frog, he turns back into a human
            self._frog = False

            if isinstance(other, MagicProjectile): # If it's the frog spell, he must not take damage
                self._frog = True
            else:
                # Arthur loses his armour / his life
                if self._armour:
                    self.lose_armour(arena)
                else:
                    self.die(arena)
                    self._max_dy = 3 # Arthur's fall is slowed down, just to be more dramatic

            # Since he's just been hit, we reset his iframes
            self._iframes_count = self._invincibility_frames

    def lose_armour(self, arena: Arena):
        self._armour = False

    def die(self, arena: Arena):
        self._dead = True

    def instant_die(self, arena: Arena):
        """
        Instantly skips to Arthur's death animation.
        As of now, this is only called when he falls in bottomless pits.
        """
        self._armour = False
        self._iframes_count = 0
        self.hurt(arena, None)

    def use_ladder(self, arena: Arena, ladder: BackgroundLadder):

        if not self.is_by_ladder(arena):
            # Arthur MUST collide with a ladder object to use it
            return

        if self._dead or self._won:
            return

        keys = arena.current_keys()
        if self._actions["Jump"].union(self._actions["RunRight"].union(self._actions["RunLeft"])) & set(keys):
            # If the player jumps while climbing the ladder, he stops climbing it to jump
            self._grabbing_ladder = False

        if set(keys) & self._actions["ClimbLadder"] or set(keys) & self._actions["DescendLadder"]:
            self._grabbing_ladder = True

        if self._grabbing_ladder:
            # Arthur's centre is aligned to the ladder's centre
            lx, ly, lw, lh = ladder.pos() + ladder.size()
            w, h = self.size()

            self._x = lx + (lw / 2) - (w / 2)

            # If Arthur's climbing the ladder
            self._dy = 0 # he shouldn't be affected by gravity

            if set(keys) & self._actions["DescendLadder"]:
                self._grabbing_ladder = True
                self._dy += self._climb_speed
            if set(keys) & self._actions["ClimbLadder"]:
                self._grabbing_ladder = True
                self._dy -= self._climb_speed

# TESTING
import unittest
import unittest.mock
class ArthurTest(unittest.TestCase):
    def test_gravity(self):
        arthur = Arthur((100, 100))
        arena = unittest.mock.Mock()
        arena.collisions.return_value = []
        arena.current_keys.return_value = []
        arena.size.return_value = (500, 500)

        arthur.move(arena)
        self.assertEqual(arthur.pos(), (100, 100))
        arthur.move(arena)
        self.assertEqual(arthur.pos(), (100, 102))
        arthur.move(arena)
        self.assertEqual(arthur.pos(), (100, 106))
        arthur.move(arena)
        self.assertEqual(arthur.pos(), (100, 112))

    def test_collision_from_up(self):
        grave = unittest.mock.Mock(spec= BackgroundSolid)
        grave.pos.return_value = (242, 186)
        grave.size.return_value = (16, 16)
        arena = unittest.mock.Mock()
        arena.collisions.return_value = [grave]
        arena.current_keys.return_value = []
        arena.size.return_value = (500, 500)

        arthur = Arthur((242, 158))

        arthur.move(arena)
        self.assertEqual(arthur.pos(), (242, 155))




    def test_grave_from_left(self):
        grave = unittest.mock.Mock(spec= Grave)
        grave.pos.return_value = (242, 186)
        grave.size.return_value = (16, 16)

        ground = unittest.mock.Mock(spec= BackgroundSolid)
        ground.pos.return_value = (0, 202)
        ground.size.return_value = (500, 20)

        arena = unittest.mock.Mock()
        arena.collisions.return_value = [grave, ground]
        arena.current_keys.return_value = []
        arena.size.return_value = (500, 500)

        arthur = Arthur((225, 171))

        arthur.move(arena)
        self.assertEqual(arthur.pos(), (242 - arthur.size()[0], 171))

    def test_platform_from_top(self):
        platform = unittest.mock.Mock(spec= BackgroundPlatform)
        platform.pos.return_value = (622, 122)
        platform.size.return_value = (100, 20)

        arena = unittest.mock.Mock()
        arena.collisions.return_value = [platform]
        arena.current_keys.return_value = []
        arena.size.return_value = (1000, 1000)

        arthur = Arthur((678, 118))

        arthur.move(arena)
        arthur.move(arena)
        arthur.move(arena)

        self.assertEqual((678, 91), arthur.pos())

    def test_platform_from_bottom(self):
        platform = unittest.mock.Mock(spec= BackgroundPlatform)
        platform.pos.return_value = (622, 122)
        platform.size.return_value = (100, 20)

        arena = unittest.mock.Mock()
        arena.collisions.return_value = [platform]
        arena.size.return_value = (1000, 1000)
        arena.current_keys.return_value = []

        a = Arthur((678, 152))
        a._dy = -15 # Simulo salto

        for _ in range(20):
            a.move(arena)

        self.assertEqual((678, 91), a.pos())

if __name__ == "__main__":
    unittest.main()