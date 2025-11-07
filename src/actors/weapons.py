from src.actors.platforms import Ground, BackgroundSolid, BackgroundPlatform
from src.actors.zombie import Zombie
from src.framework.actor import Actor, Point, Arena


class Torch (Actor):
    def __init__(self, direction: str, pos: Point):
        # Movement
        self._x, self._y = pos
        self._direction = direction
        self._dx = 8 if direction == "Right" else -8
        self._dy = -10
        self._gravity = 2
        self._max_dy = 8

        # Animations
        self._anim_count = 0

    # Actor methods
    def pos(self) -> Point:
        return self._x, self._y
    def sprite(self) -> Point:
        count = (self._anim_count // 8) % 2 # Ciclo ogni 8 frame su 2 immagini
        if count == 0: return 0, 896
        else: return 19, 896
    def size(self) -> Point:
        count = (self._anim_count // 8) % 2
        if count == 0: return 14, 13
        else: return 13, 14
    def move(self, arena: Arena):
        self._x += self._dx
        self._y += self._dy

        for o in arena.collisions():
            if isinstance(o, Zombie): # Gli zombie vengono uccisi se colpiti direttamente
                #?  Qui ho imparato che se lo zombie è stato creato in un altro modulo e l'import è diverso rispetto a quello che ho fatto
                #   per poter usare "Zombie" qui nell'instance of (tipo in game, dove c'era from actors.zombie import Zombie
                #   e qui from src.actors.zombie import Zombie, l'instanceof non li considera della stessa classe perché usano
                #   diverso namespace.
                arena.kill(o)
                arena.kill(self)
            elif isinstance(o, Ground) or isinstance(o, BackgroundPlatform): # Se la fiaccola tocca terra crea la fiamma
                self._ground_collision(arena)
                print("Torcia a terra, creo la fiamma (Work In Progress...)")
            elif isinstance(o, BackgroundSolid): # Altrimenti, qualsiasi altra cosa ho colpito, despawno
                arena.kill(self)


        self._dy = min(self._dy + self._gravity, self._max_dy)

        # Aggiornamento del count per l'animazione
        self._anim_count += 1

    def _ground_collision(self, arena: Arena):
        arena.spawn(Flame(self.pos()))
        arena.kill(self)

class Flame (Actor):
    def __init__(self, pos: Point):
        self._x, self._y = pos
    def pos(self) -> Point:
        return self._x, self._y
    def sprite(self):
        return None
    def size(self):
        return 0, 0
    def move(self, arena: Arena):
        pass