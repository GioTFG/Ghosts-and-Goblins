from src.framework import g2d
from src.framework.actor import Arena, Actor, Point
from src.framework.utilities import remove_pos


class View:
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
            self._x, self._y = remove_pos(self._actor.pos(), (self._w / 2, self._h / 2))
        else:
            # Se non è "attaccata" a un actor, posso usare i tasti [I, J, K, L] per muoverla
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

        self._x = max(self._x, 0)
        self._y = max(self._y, 0)
        self._x = min(self._x, int(arena.size()[0] - self._w))
        self._y = min(self._y, int(arena.size()[1] - self._h))

    def get_actor(self) -> Actor:
        return self._actor

    def set_actor(self, actor: Actor):
        self._actor = actor

class GuiElement:
    def __init__(self, pos: Point, size: Point):
        self._x, self._y = pos
        self._w, self._h = size
        self._sub_elements = []

    def draw(self):
        raise NotImplementedError("Abstract method")

    def get_pos(self):
        return self._x, self._y

    def get_size(self):
        return self._w, self._h

    def get_center(self):
        return self._x + self._w / 2, self._y + self._h / 2

class TextElement(GuiElement):

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
        "?": (694, 756)
    }
    CHARACTER_SIZE = 9, 9

    color = tuple[int, int, int]
    def __init__(self, pos: Point, size: Point, bg_colour: color = (255, 255, 255), text_colour: color = (0, 0, 0)):
        super().__init__(pos, size)
        self._text = ""
        self._bg_colour = bg_colour
        self._text_colour = text_colour
        self._text_align = "c"

    def draw(self):
        # Background
        g2d.set_color(self._bg_colour)
        g2d.draw_rect(self.get_pos(), self.get_size())

        # Testo
        g2d.set_color(self._text_colour)

        text_pos = self.get_center()
        match self._text_align:
            case "l":
                text_pos = self._x, self._y + self._h / 2
            case "r":
                text_pos = self._x + self._w * 2 / 3, self._y + self._h / 2
            case "c":
                text_pos = self.get_center()

        self._draw_text(text_pos)

    def set_text(self, text: str):
        self._text = text

    def set_text_size(self, size: Point):
        self._text_size = size

    # def set_text_align(self, alignment: str):
    # # Sarebbe da sistemare, trovando un modo per calcolare width e height del testo sapendo la font size.
    #     match alignment:
    #         case "Left":
    #             self._text_align = "l"
    #         case "Right":
    #             self._text_align = "r"
    #         case "Center":
    #             self._text_align = "c"
    #         case _:
    #             raise ValueError("Alignment not valid")

    def _draw_text(self, pos: Point):
        initial_pos = pos
        for c in self._text:
            if pos[0] >= self._x + self._w:
                pos = initial_pos[0], pos[1] + self.CHARACTER_SIZE[1] + 1
            g2d.draw_image("ghosts-goblins.png", pos, self._get_sprite_pos(c), self._get_sprite_size(c))
            new_x = pos[0] + self._get_sprite_size(c)[0]
            pos = (new_x, pos[1])


    def _get_sprite_pos(self, c: str):
        if c in self.CHARACTERS_SPRITES:
            return self.CHARACTERS_SPRITES[c]
        else:
            return self.CHARACTERS_SPRITES["SP"]

    def _get_sprite_size(self, c: str):
        if c in self.CHARACTERS_SPRITES:
            return self.CHARACTER_SIZE
        else:   # Caso di carattere speciale, "SP" viene mostrato, che ha dimensioni 9x9
            # Anche se in realtà è sempre 9x9, lascio così per una maggiore flessibilità in caso di nuovi caratteri con dimensioni diverse.
            return 9, 9