from src.actors.arthur import Arthur
from src.actors.enemies import Plant
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
    def __init__(self, size: Point, hero_start_pos: Point, file_path: str | None):
        super().__init__(size)
        # self._hero = Arthur(hero_start_pos)
        # self.spawn(self._hero)

        if file_path:
            with open(file_path, "r") as f:
                while (line := f.readline().strip()) != "":
                    print(f"Line: {line}")
                    if line[0] != "#":
                        option, value = line.split(": ")
                        match option:
                            case "Hero_Start_Pos":
                                hero_start_pos = tuple(float(v) for v in value.split(", "))
                                print(hero_start_pos)
                            case "Enemies":
                                enemies = []
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
                                                enemies.append(Plant(pos))

                            case "Platforms":
                                platforms = []
                                if value != "[": raise ValueError("File is not well-formed")
                                lines = []
                                while (l := f.readline().strip()) != "]":
                                    lines.append(l)

                                for l in lines:
                                    if l != "" and l[0] != "#":
                                        option, value = l.split(": ")
                                        x, y, w, h = (float(v) for v in value.split(", "))
                                        match option:
                                            case "Ground": platforms.append(Ground((x, y), (w, h)))
                                            case "Platform": platforms.append(BackgroundPlatform((x, y), (w, h)))
                                            case "Ladder": platforms.append(BackgroundLadder((x, y), (w, h)))
                                            case "Grave": platforms.append(Grave((x, y), (w, h)))


if __name__ == "__main__":
    GngGame((1, 1), (0, 0), "prova.txt")