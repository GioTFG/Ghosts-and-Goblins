"""
Module created by Giovanni Ancora for a project at UniPr.
@author Giovanni Ancora (https://github.com/GioTFG and https://github.com/GiovanniAncora)
This project on GitHub: https://github.com/GioTFG/Ghosts-and-Goblins
"""

import os.path
from random import randrange, choice
import src.framework.g2d as g2d

from src.actors.arthur import Arthur

from src.actors.enemies import Plant, Zombie, Magician
from src.actors.platforms import Ground, BackgroundPlatform, BackgroundLadder, Grave, BackgroundWinArea
from src.framework.actor import Arena, Point
from src.framework.gui import View, TextElement, GuiElement
from src.framework.utilities import remove_pos

from path_util import ROOT_PATH

VIEW_W, VIEW_H = 420, 240


class GngGame(Arena):
    """
    Game initializer class.
    This class manages the actual game, controls when the game begins/finishes, if the player has won or lost, etc.
    It manages the initial configuration of the game, allowing it to be done from a file or directly from the code.
    It also manages all the UI elements (even if the actual single elements are generically defined in their own class).
    """
    def __init__(self, size: Point = None, hero_start_pos: Point = None, file_path: str = None):
        """
        The parameters must be passed in one of the ways.
        It is better to initialize the game from a file, as it is more dynamic and allows the configuration of static enemies.
        """

        # Gameplay attributes
        self._hero_start_pos = hero_start_pos
        self._size = size

        self._static_enemies = []
        self._platforms = []
        self._current_lives = self._max_lives = 2

        # File input
        if file_path:
            self._manage_file(file_path)

        if self._size is None:
            raise ValueError("Size must be specified either through the arguments or a file.")
        if self._hero_start_pos is None:
            raise ValueError("Hero starting position must be specified either through the arguments or a file.")

        # Arena initialization
        super().__init__(self._size)

        self._spawn_static_actors()

        # Arthur
        self._hero = Arthur(self._hero_start_pos)
        self.spawn(self._hero)

        # Game
        self._game_over = False
        self._game_won = False
        self._paused = False

    # -- GAME ENGINE METHODS --
    def tick(self, keys=[]):
        super().tick(keys)

        # Checks done when the game is still running and hasn't finished
        if not self._game_over and not self._game_won:

            # Dynamic zombie spawning:
            if randrange(500) == 0:
                player_x, player_y = self._hero.pos()
                direction = choice(("Right", "Left"))
                if direction == "Right":
                    self.spawn(Zombie((player_x - randrange(50, 200), player_y), direction))
                else:
                    self.spawn(Zombie((player_x + randrange(50, 200), player_y), direction))

            # Check if Arthur reached a Winning Area
            if self._hero.has_won():
                self._game_won = True

            # Check if Arthur died
            if self._hero not in self.actors():
                if self._current_lives > 0:
                    self.reset_game()
                else:
                    self._game_over = True
                    self._hero = None


    def reset_game(self):
        """
        Thus method is called upon Arthur's death to respawn all enemies and kill the current ones.
        It also resets platforms.
        """

        # Si resettano tutti i nemici
        self._kill_all()
        self._spawn_static_actors()

        # Si resetta Arthur
        self._current_lives -= 1
        self._hero = Arthur(self._hero_start_pos)
        self.spawn(self._hero)

    # -- GETTER METHODS --
    def get_hero(self):
        return self._hero
    def game_over(self):
        return self._game_over
    def game_won(self):
        return self._game_won
    def get_lives(self):
        return self._current_lives
    def get_max_lives(self):
        return self._max_lives

    # -- UTILITY METHODS --
    def _kill_all(self):
        for a in self.actors():
            self.kill(a)

    def _spawn_static_actors(self):
        for a in self._static_enemies + self._platforms:
            self.spawn(a)

    def _manage_file(self, file_path: str):
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line != "" and line[0] != "#":
                    option, value = line.split(": ")
                    match option:   # Logic for every possible entry
                        case "Hero_Start_Pos":
                            self._hero_start_pos = tuple(int(v) for v in value.split(", "))
                        case "Size":
                            self._size = tuple(int(v) for v in value.split(", "))
                        case "Lives":
                            self._max_lives = self._current_lives = int(value)
                        case "Enemies":
                            if value != "[": raise ValueError("File is not well-formed")
                            lines = []
                            while (l := f.readline().strip()) != "]":
                                lines.append(l)

                            for l in lines:
                                if l != "" and l[0] != "#":
                                    option, value = l.split(": ")
                                    match option: # Match for every possible static enemy
                                        case "Plant":
                                            vals = value.split(", ")
                                            pos = int(vals[0]), int(vals[1])
                                            self._static_enemies.append(Plant(pos))
                                        case "Zombie":
                                            vals = value.split(", ")
                                            pos = int(vals[0]), int(vals[1])
                                            direction = vals[2].strip()
                                            self._static_enemies.append(Zombie(pos, direction))
                                        case "Magician":
                                            vals = value.split(", ")
                                            pos = int(vals[0]), int(vals[1])
                                            self._static_enemies.append(Magician(pos))

                        case "Platforms":
                            if value != "[": raise ValueError("File is not well-formed")
                            lines = []
                            while (l := f.readline().strip()) != "]":
                                lines.append(l)

                            for l in lines:
                                if l != "" and l[0] != "#":
                                    option, value = l.split(": ")
                                    x, y, w, h = (int(v) for v in value.split(", "))
                                    match option: # Match for every possible platform type
                                        case "Ground":
                                            self._platforms.append(Ground((x, y), (w, h)))
                                        case "BackgroundPlatform":
                                            self._platforms.append(BackgroundPlatform((x, y), (w, h)))
                                        case "BackgroundLadder":
                                            self._platforms.append(BackgroundLadder((x, y), (w, h)))
                                        case "Grave":
                                            self._platforms.append(Grave((x, y), (w, h)))
                                        case "BackgroundWinArea":
                                            self._platforms.append(BackgroundWinArea((x, y), (w, h)))

class GngGui:
    def __init__(self, config_path: str = None, bg_image: str = None, bg_crop_pos: tuple[int, int] = None, bg_size: tuple[int, int] = None, zoom = 1):
        """
        bg_image, bg_crop_pos and bg_size MUST be all specified, otherwise they will all be ignored.
        (The following notation is taken by JetBrains' IDEs (PyCharm, IntelliJ, ...), because I personally think they make everything clearer.
        Plus, there's the bonus of a clearer interface when hovering over code when using the mentioned IDEs).
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

        # Game
        self._game = GngGame(bg_size, (112, 171), config_path) # Default numbers (just in case they are not present anywhere else)
        self._view = View((0, 0), (VIEW_W, VIEW_H)) # Fixed numbers
        self._paused = False
        self._max_pause_cooldown, self._pause_cooldown = 5, 0

        self._game_won = self._game.game_won()
        self._game_over = self._game.game_over()

        ## GUI/HUD Elements
        view_w, view_h = self._view.size()
        self._gui_elements: list[GuiElement] = []
        ### --- HUD (Heads Up Display) ---
        self._hud = TextElement((0, view_h), (view_w, 30), (255, 50, 50))
        self._hud.set_text("Loading") # Temporary text, as it will be overwritten on every frame
        self._gui_elements.append(self._hud)

        ### --- Credits ---
        self._credits = TextElement((0, view_h + self._hud.get_size()[1]), (view_w, 30), (255, 50, 50))
        self._credits.set_text("Project made by Giovanni Ancora at UniPr")
        self._credits.set_text_align("Center")
        self._gui_elements.append(self._credits)

        ### --- Pause Menu ---
        self._pause_menu = TextElement(self._view.pos(), self._view.size(), (128, 50, 50))
        self._pause_menu.set_text("Paused")
        self._pause_menu.set_text_align("Center")
        # This will not be added to gui elements as it overrides the view if paused.

        self._total_height = self._view.size()[1]
        for e in self._gui_elements:
            self._total_height += e.get_size()[1]

        import src.framework.g2d as g2d # Lazy import just to be sure to avoid any circular imports (even it there aren't)

        g2d.init_canvas((view_w, self._total_height), zoom)

        ## Music elements
        g2d.play_audio(os.path.join(ROOT_PATH, "sounds/game_start.mp3"))
        self._music_playing = False

        g2d.main_loop(self.tick)

    def tick(self):
        # Clear background
        if self._bg_image is not None:
            g2d.draw_image(self._bg_image, remove_pos((0, 0), self._view.pos()), self._bg_crop_pos, self._bg_size)
        else:
            g2d.clear_canvas()

        # Check pause
        if "p" in g2d.current_keys() and self._pause_cooldown <= 0:
            self._paused = not self._paused
            self._pause_cooldown = self._max_pause_cooldown

        if self._pause_cooldown > 0:
            self._pause_cooldown -= 1

        # Draw actors
        if not self._paused:
            for a in self._game.actors():
                if a.sprite() is not None:
                    g2d.draw_image(os.path.join(ROOT_PATH, "img" , "ghosts-goblins.png"), remove_pos(a.pos(), self._view.pos()), a.sprite(), a.size())
                else:
                    ## Demo Background Mode
                    if self._bg_image is None: # If there is no background, all the elements that are pre-rendered in it will be drawn as colour-coded rectangles
                        g2d.set_color(self._type_colour(type(a).__name__)) # The colour codes are defined in the ._type_colour method
                        g2d.draw_rect(remove_pos(a.pos(), self._view.pos()), a.size())

            # The view can be assigned an actor to follow, so in case Arthur died, the new Arthur will be followed instead.
            self._view.set_actor(self._game.get_hero())

            # Text generation for the HUD
            if self._game.game_won():
                self._hud.set_text_align("Center")
                self._hud.set_text("Congratulations: you won!")
            elif self._game.game_over():
                self._hud.set_text_align("Center")
                self._hud.set_text("Game over!")
            else:
                self._hud.set_text_align("Center")
                self._hud.set_text(f"Lives: {self._game.get_lives()}/{self._game.get_max_lives()}")
        else:
            self._pause_menu.draw()

        ## HUD graphic update
        for e in self._gui_elements:
            e.draw()

        ## Muting/Unmuting music with the 'M' key
        if "m" in g2d.current_keys():
            g2d.pause_audio(os.path.join(ROOT_PATH, "sounds", "game_start.mp3"))
            if self._music_playing:
                g2d.pause_audio(os.path.join(ROOT_PATH, "sounds", "background_music.mp3"))
            else:
                g2d.play_audio(os.path.join(ROOT_PATH, "sounds", "background_music.mp3"), True)
            self._music_playing = not self._music_playing

        if self._music_playing and not self._game_won and self._game.game_won():
            # This would be the first tick where the game has finished and the player has won
            g2d.pause_audio(os.path.join(ROOT_PATH, "sounds", "game_start.mp3"))
            g2d.pause_audio(os.path.join(ROOT_PATH, "sounds", "background_music.mp3"))
            g2d.play_audio(os.path.join(ROOT_PATH, "sounds", "game_won.mp3"))
            self._game_won = True

        if self._music_playing and not self._game_over and self._game.game_over():
            # This would be the first tick where the game has finished and the player has lost
            g2d.pause_audio(os.path.join(ROOT_PATH, "sounds", "game_start.mp3"))
            g2d.pause_audio(os.path.join(ROOT_PATH, "sounds", "background_music.mp3"))
            g2d.play_audio(os.path.join(ROOT_PATH, "sounds", "game_over.mp3"))
            self._game_over = True

        self._view.move(self._game) # Camera update

        if not self._paused:
            self._game.tick(g2d.current_keys()) # Arena update

    def _type_colour(self, actor_type: str) -> tuple[int, int, int]:
        """
        This methods maps every Actor subclass to a specific colour.
        This is used for "background" subclasses, that don't have their own sprite in the spritesheet, but should have been already
        rendered in the background image.
        When said background is not present, these will be drawn as colour-coded rectangles.
        The colour of each rectangle is determined by the actor type.
        :param actor_type: The actor type, passed as a string. (using type.__name__)
        :return: Returns three numbers, the three RGB values of the assigned colour. The RGB values for black will be returned if there is no color for the passed actor type.
        """
        #DEVLOG Cose interessanti sul match case: https://peps.python.org/pep-0636/#adding-conditions-to-patterns
        match actor_type:
            case "Ground": return 0, 112, 37
            case "Grave": return 60, 79, 69
            case "BackgroundLadder": return 79, 41, 0
            case "BackgroundPlatform": return 0, 138, 67
            case "BackgroundSolid": return 30, 30, 30
            case "BackgroundWinArea": return 0, 255, 255
            case _: return 0, 0, 0

if __name__ == "__main__":
    gui = GngGui(
        config_path= os.path.join(ROOT_PATH, "configs", "demo.txt"),
        zoom= 3
    )