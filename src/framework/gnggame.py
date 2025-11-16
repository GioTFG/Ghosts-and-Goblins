from random import randrange, choice

from src.actors.arthur import Arthur
from src.actors.enemies import Plant, Zombie
from src.actors.platforms import Ground, BackgroundPlatform, BackgroundLadder, Grave
from src.framework.actor import Arena, Point

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

        for a in self._static_enemies + self._platforms:
            self.spawn(a)


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
                    self._total_lives -= 1
                    self._hero = Arthur(self._hero_start_pos)
                else:
                    self._game_over = True

        if self._game_over:
            print("Game over!")

    def game_over(self):
        return self._game_over
    def game_won(self): #TODO: Condizione di vittoria.
        return self._game_won

    def _manage_file(self, file_path: str):
        with open(file_path, "r") as f:
            while (line := f.readline().strip()) != "":
                print(f"Line: {line}")
                if line[0] != "#":
                    option, value = line.split(": ")
                    match option:
                        case "Hero_Start_Pos":
                            self._hero_start_pos = tuple(float(v) for v in value.split(", "))
                        case "Size":
                            self._size = tuple(float(v) for v in value.split(", "))
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
                                            pos = float(vals[0]), float(vals[1])
                                            self._static_enemies.append(Plant(pos))

                        case "Platforms":
                            if value != "[": raise ValueError("File is not well-formed")
                            lines = []
                            while (l := f.readline().strip()) != "]":
                                lines.append(l)

                            for l in lines:
                                if l != "" and l[0] != "#":
                                    option, value = l.split(": ")
                                    x, y, w, h = (float(v) for v in value.split(", "))
                                    match option:
                                        case "Ground":
                                            self._platforms.append(Ground((x, y), (w, h)))
                                        case "Platform":
                                            self._platforms.append(BackgroundPlatform((x, y), (w, h)))
                                        case "Ladder":
                                            self._platforms.append(BackgroundLadder((x, y), (w, h)))
                                        case "Grave":
                                            self._platforms.append(Grave((x, y), (w, h)))

if __name__ == "__main__":
    GngGame(None, (0, 0), "prova.txt")