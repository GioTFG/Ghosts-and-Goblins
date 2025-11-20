import os

from src.framework import g2d
from src.framework.actor import Arena, Actor, Point
from src.framework.utilities import remove_pos

from path_util import ROOT_PATH

class View:
    """
    GUI Element: View
    The "portal" between real life and the game.
    It renders (draws) everything that is in its range.
    By default, it is static and can be moved using "IJKL" keys (similar to WASD).
    When assigned to an actor, it follows it instead (disabling the "IJKL" keys).
    """
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
            # If it's assigned to an actor, it will follow him.
            self._x, self._y = remove_pos(self._actor.pos(), (self._w / 2, self._h / 2))
        else:
            # If it's not "attached" to an actor, you can use ["I", "J", "K", "L"] to move it.
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

        self._x = max(min(self._x, int(arena.size()[0] - self._w)), 0)
        self._y = max(min(self._y, int(arena.size()[1] - self._h)), 0)

    def get_actor(self) -> Actor:
        return self._actor

    def set_actor(self, actor: Actor):
        self._actor = actor

class GuiElement:
    """
    Generic GUI Element.
    It is an interface.
    Each GUI element must have a position (x, y) and a size (w, h).
    They can change during the execution, so they must have getter methods for them.
    They also must have a draw function.
    """

    def __init__(self, pos: Point, size: Point):
        self._x, self._y = pos
        self._w, self._h = size
        self._sub_elements = []

    def draw(self):
        """
        This method will be called on all rendered GUI elements.
        It will use g2d to draw itself, with whatever logic the subclass may have.
        """
        raise NotImplementedError("Abstract method")

    def get_pos(self):
        return self._x, self._y

    def get_size(self):
        return self._w, self._h

    def get_center(self):
        return self._x + self._w / 2, self._y + self._h / 2

class TextElement(GuiElement):
    """
    A GUI element that displays a text.
    The text can also dynamically change.
    The text will use the Ghost 'n Goblins' font present in the spritesheet (with some edits made by me, as there were some characters missing).
    A text alignment can also be set using the setter method, mimicking the behaviour of CSS text-align.
    """

    CHARACTERS_SPRITES = {
        "SP": (559, 765),
        "A": (568, 765),
        "B": (577, 765),
        "C": (586, 765),
        "D": (595, 765),
        "E": (604, 765),
        "F": (613, 765),
        "G": (622, 765),
        "H": (631, 765),
        "I": (640, 765),
        "J": (649, 765),
        "K": (658, 765),
        "L": (667, 765),
        "M": (676, 765),
        "N": (685, 765),
        "O": (694, 765),
        "P": (559, 774),
        "Q": (568, 774),
        "R": (577, 774),
        "S": (586, 774),
        "T": (595, 774),
        "U": (604, 774),
        "V": (613, 774),
        "W": (622, 774),
        "X": (631, 774),
        "Y": (640, 774),
        "Z": (649, 774),
        "[": (658, 774),
        "\\": (667, 774),
        "]": (676, 774),
        "↑": (685, 774),
        "→": (694, 774),
        "♥": (559, 783),
        "a": (568, 783),
        "b": (577, 783),
        "c": (586, 783),
        "d": (595, 783),
        "e": (604, 783),
        "f": (613, 783),
        "g": (622, 783),
        "h": (631, 783),
        "i": (640, 783),
        "j": (649, 783),
        "k": (658, 783),
        "l": (667, 783),
        "m": (676, 783),
        "n": (685, 783),
        "o": (694, 783),
        "p": (559, 792),
        "q": (568, 792),
        "r": (577, 792),
        "s": (586, 792),
        "t": (595, 792),
        "u": (604, 792),
        "v": (613, 792),
        "w": (622, 792),
        "x": (631, 792),
        "y": (640, 792),
        "z": (649, 792),
        "{": (658, 792),
        "|": (667, 792),
        "}": (676, 792),
        "↓": (685, 792),
        "←": (694, 792),

        "©": (559, 738),
        "®": (568, 738),
        "1": (586, 738),
        "2": (595, 738),
        "3": (604, 738),
        "4": (613, 738),
        "5": (622, 738),
        "6": (631, 738),
        "7": (640, 738),
        "8": (649, 738),
        "9": (658, 738),
        "\"": (667, 738),
        ".": (676, 738),
        " ": (559, 747),
        "!": (568, 747),
        "#": (586, 747),
        "$": (595, 747),
        "%": (604, 747),
        "&": (613, 747),
        "'": (622, 747),
        "(": (631, 747),
        ")": (640, 747),
        "*": (649, 747),
        "+": (658, 747),
        ",": (667, 747),
        "-": (676, 747),
        "/": (694, 747),
        ":": (649, 756),
        ";": (658, 756),
        "<": (667, 756),
        "=": (676, 756),
        ">": (685, 756),
        "?": (694, 756),

        "0": (577, 756)
    }
    CHARACTER_SIZE = 9, 9

    color = tuple[int, int, int]
    def __init__(self, pos: Point, size: Point, bg_colour: color = (255, 255, 255)):
        super().__init__(pos, size)

        self._text = ""
        self._bg_colour = bg_colour
        self._text_align = "c"
        self._margin = 2

    def draw(self):
        # Background
        g2d.set_color(self._bg_colour)
        g2d.draw_rect(self.get_pos(), self.get_size())

        # Text
        text_pos = self.get_center()
        match self._text_align:
            case "l":
                text_pos = self._x + self._margin, self._y + self._h / 2
            case "r":
                text_pos = self._x + self._w - self._margin - self.text_width(self._text), self._y + self._h / 2
            case "c":
                text_pos = self.get_center()[0] - self.text_width(self._text) / 2, self.get_center()[1]

        self._draw_text(text_pos)

    # -- SETTER METHODS --
    def set_text(self, text: str):
        self._text = text

    def set_text_align(self, alignment: str):
        match alignment:
            case "Left":
                self._text_align = "l"
            case "Right":
                self._text_align = "r"
            case "Center":
                self._text_align = "c"
            case _:
                raise ValueError("Alignment not valid")

    # -- UTILITY METHODS --
    def _draw_text(self, pos: Point):
        """
        Draws a specific text at a given position.
        """
        initial_pos = pos
        for c in self._text:
            if pos[0] >= self._x + self._w: # Go to next line
                pos = initial_pos[0], pos[1] + self.CHARACTER_SIZE[1] + 1
            g2d.draw_image(os.path.join(ROOT_PATH, "img", "ghosts-goblins.png"), pos, self._get_sprite_pos(c), self._get_sprite_size(c))
            new_x = pos[0] + self._get_sprite_size(c)[0]
            pos = (new_x, pos[1])
        return pos # For the next character sequence

    def _get_sprite_pos(self, c: str):
        if c in self.CHARACTERS_SPRITES:
            return self.CHARACTERS_SPRITES[c]
        else: # When the character is not recognised, the special character "SP" will be drawn instead.
            return self.CHARACTERS_SPRITES["SP"]

    def _get_sprite_size(self, c: str):
        if c in self.CHARACTERS_SPRITES:
            return self.CHARACTER_SIZE
        else:   # This is the case of the special character, which is 9x9 in size.
            # The size is actually always 9x9, but I'm going to leave this as it is just in case new characters will be added with different sizes.
            return 9, 9


    # -- GETTER METHODS --
    def text_width(self, text: str):
        size = 0
        for c in text:
            if c in self.CHARACTERS_SPRITES:
                size += self.CHARACTER_SIZE[0]
        return size

class LifeCounter(TextElement):
    """
    A special GUI text element that instead of writing some text, draws as many Arthur's heads as there are lives remaining.
    The max number of lives must be passed as arguments in the constructor.
    The current lives must also be passed in each frame using the setter method set_lives.
    """
    # Unused (for now)
    color = tuple[int, int, int]
    def __init__(self, pos: Point, size: Point, bg_colour: color = (255, 255, 255), max_lives: int = 0):
        super().__init__(pos, size, bg_colour)
        self._lives = 0
        self._max_lives = max_lives

    def set_lives(self, lives: int):
        self._lives = lives

    def _draw_text(self, pos: Point):
        if self._lives > 0:
            self._text = "("
            pos = super()._draw_text(pos)
        for _ in range(self._lives):
            g2d.draw_image(os.path.join(ROOT_PATH,"img","ghosts-goblins.png"), pos, (696, 696), (13, 13))
            pos = pos[0] + 14, pos[1]
        if self._lives > 0:
            self._text = ")"
            super()._draw_text(pos)

    def text_width(self, text: str):
        # 13x13 is the life icon sprite size, 2 is for the parenthesis.
        if self._lives > 0:
            return  13 * self._lives + 2 * self.CHARACTER_SIZE[0]

        return 0