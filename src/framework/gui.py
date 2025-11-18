from . import g2d
from .actor import Arena, Actor, Point
from .utilities import remove_pos


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
    color = tuple[int, int, int]
    def __init__(self, pos: Point, size: Point, bg_colour: color = (255, 255, 255), text_colour: color = (0, 0, 0)):
        super().__init__(pos, size)
        self._text = ""
        self._bg_colour = bg_colour
        self._text_colour = text_colour
        self._text_size = 15
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

        g2d.draw_text(self._text, text_pos, self._text_size)

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