from random import randrange, choice
import src.framework.g2d as g2d

from src.actors.arthur import Arthur

from src.actors.enemies import Plant, Zombie
from src.actors.platforms import Ground, BackgroundPlatform, BackgroundLadder, Grave
from src.framework.actor import Arena, Point
from src.framework.gui import View
from src.framework.utilities import remove_pos

"""
STRUTTURA DEI FILE
# - Riga commentata, ignorata

-- Struttura --
Opzione: valore\n
Opzione: valore\n
...
Opzione: valore\n
---------------

-- Grammatica --
<pos> := <int>, <int>
<size> := <int>, <int>
----------------

-- Esempio --
Hero_Start_Pos: <pos>\n
Enemies: [
    Plant: <pos>\n
    ...
]\n
Background_Objects: [\n
    Platform: <pos>, <size>\n
    Ground: <pos>, <size>\n
    Ladder: <pos>, <size>\n
    ...
]\n
-------------
"""


class GngGame(Arena):
    def __init__(self, size: Point = None, hero_start_pos: Point = None, file_path: str = None):

        self._hero_start_pos = hero_start_pos
        self._size = size

        # File input
        self._static_enemies = []
        self._platforms = []

        if file_path:
            self._manage_file(file_path)

        if self._size is None:
            raise ValueError("Size must be specified either through the arguments or a file.")
        if self._hero_start_pos is None:
            raise ValueError("Hero starting position must be specified either through the arguments or a file.")

        super().__init__(self._size)

        self._spawn_static_actors()

        # Arthur
        self._hero = Arthur(self._hero_start_pos)
        self.spawn(self._hero)
        self._total_lives = 3

        # Game
        self._game_over = False
        self._game_won = False

    def tick(self, keys=[]):
        super().tick(keys)

        if not self._game_over and not self._game_won:
            # Dynamic zombie spawning:
            if randrange(500) == 0:
                player_x, player_y = self._hero.pos()
                direction = choice(("Right", "Left"))
                if direction == "Right":
                    self.spawn(Zombie((player_x - randrange(50, 200), player_y), direction))
                else:
                    self.spawn(Zombie((player_x + randrange(50, 200), player_y), direction))

            # Check if Arthur died
            if self._hero not in self.actors():
                if self._total_lives > 0:
                    self.reset_game()
                else:
                    self._game_over = True
                    self._hero = None

        if self._game_over:
            print("Game over!")

    def game_over(self):
        return self._game_over
    def game_won(self): #TODO: Condizione di vittoria.
        return self._game_won

    def reset_game(self):

        # Si resettano tutti i nemici
        self._kill_all()
        self._spawn_static_actors()

        # Si resetta Arthur
        self._total_lives -= 1
        self._hero = Arthur(self._hero_start_pos)
        self.spawn(self._hero)

    def get_hero(self):
        return self._hero

    def _kill_all(self):
        for a in self.actors():
            self.kill(a)

    def _spawn_static_actors(self):
        for a in self._static_enemies + self._platforms:
            self.spawn(a)

    def _manage_file(self, file_path: str):
        with open(file_path, "r") as f:
            while (line := f.readline().strip()) != "":
                print(f"Line: {line}")
                if line[0] != "#":
                    option, value = line.split(": ")
                    match option:
                        case "Hero_Start_Pos":
                            self._hero_start_pos = tuple(int(v) for v in value.split(", "))
                        case "Size":
                            self._size = tuple(int(v) for v in value.split(", "))
                        case "Enemies":
                            if value != "[": raise ValueError("File is not well-formed")
                            lines = []
                            while (l := f.readline().strip()) != "]":
                                lines.append(l)

                            for l in lines:
                                if l != "" and l[0] != "#":
                                    option, value = l.split(": ")
                                    match option:
                                        case "Plant":
                                            vals = value.split(", ")
                                            pos = int(vals[0]), int(vals[1])
                                            self._static_enemies.append(Plant(pos))

                        case "Platforms":
                            if value != "[": raise ValueError("File is not well-formed")
                            lines = []
                            while (l := f.readline().strip()) != "]":
                                lines.append(l)

                            for l in lines:
                                if l != "" and l[0] != "#":
                                    option, value = l.split(": ")
                                    x, y, w, h = (int(v) for v in value.split(", "))
                                    match option:
                                        case "Ground":
                                            self._platforms.append(Ground((x, y), (w, h)))
                                        case "Platform":
                                            self._platforms.append(BackgroundPlatform((x, y), (w, h)))
                                        case "Ladder":
                                            self._platforms.append(BackgroundLadder((x, y), (w, h)))
                                        case "Grave":
                                            self._platforms.append(Grave((x, y), (w, h)))

class GngGui:
    def __init__(self, config_path: str = None, bg_image: str = None, bg_crop_pos: tuple[int, int] = None, bg_size: tuple[int, int] = None, zoom = 1):
        """
        bg_image, bg_crop_pos and bg_size MUST be all specified, otherwise they will all be ignored
        :param config_path: Configuration file for enemies and platforms
        :param bg_image: Image file path
        :param bg_crop_pos: Top-left corner (pixel) of passed bg_image to consider as background.
        :param bg_size: Width and height in pixels of cropped bg_image considered as background.
        :param zoom: Zoom level of the game window
        """
        if not all((bg_image, bg_crop_pos, bg_size)):
            self._bg_image = None
            self._bg_crop_pos = None
            self._bg_size = 1000, 300
        else:
            self._bg_image = bg_image
            self._bg_crop_pos = bg_crop_pos
            self._bg_size = bg_size

        self._game = GngGame(bg_size, (112, 171), config_path)
        self._view = View((0, 0), (320, 240))

        import src.framework.g2d as g2d
        g2d.init_canvas(self._view.size(), zoom)
        g2d.main_loop(self.tick)

    def tick(self):
        if self._bg_image is not None:
            g2d.draw_image(self._bg_image, remove_pos((0, 0), self._view.pos()), self._bg_crop_pos, self._bg_size)
        else:
            g2d.clear_canvas()

        for a in self._game.actors():
            if a.sprite() is not None:
                g2d.draw_image("ghosts-goblins.png", remove_pos(a.pos(), self._view.pos()), a.sprite(), a.size())
            else:
                if self._bg_image is None: # Se non c'è un background, gli elementi di background saranno disegnati come rettangoli di colori diversi
                    g2d.set_color(self._type_colour(type(a).__name__))
                    g2d.draw_rect(remove_pos(a.pos(), self._view.pos()), a.size())

        self._view.set_actor(self._game.get_hero())

        #TODO: HUD
        #TODO: Game over / Game won
        self._view.move(self._game)
        self._game.tick(g2d.current_keys())

    def _type_colour(self, actor_type: str) -> tuple[int, int, int]:
        """
        Funziona che mappa a ogni sottoclasse di Actor un colore.
        Usata in particolare per le sottoclassi di "background", che cioè non hanno un proprio sprite nello spritesheet
        ma dovrebbero essere già disegnate nel background.
        Nel caso in cui il suddetto background non sia presente, queste vengono disegnate come rettangoli colorati.
        Il colore del rettangolo è dettato quindi dal loro tipo, in base al valore restituito da questa funzione.
        :param actor_type: Il tipo (la classe) dell'actor, in forma di stringa.
        :return: Una tupla di tre numeri: i valori RGB del valore corrispondente alla classe ricevuta.
        """
        # Cose interessanti sul match case: https://peps.python.org/pep-0636/#adding-conditions-to-patterns
        match actor_type:
            case "Ground": return 0, 112, 37
            case "Grave": return 60, 79, 69
            case "BackgroundLadder": return 79, 41, 0
            case "BackgroundPlatform": return 0, 138, 67
            case "BackgroundSolid": return 30, 30, 30
            case _: return 0, 0, 0

if __name__ == "__main__":
    gui = GngGui(
        config_path= "prova.txt",
        zoom= 3
    )