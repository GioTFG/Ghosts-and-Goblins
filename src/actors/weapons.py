from src.actors.platforms import Ground, BackgroundSolid, BackgroundPlatform
from src.actors.enemies import Zombie, Enemy
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
            if isinstance(o, Enemy): # Gli zombie vengono uccisi se colpiti direttamente
                #?  Qui ho imparato che se lo zombie è stato creato in un altro modulo e l'import è diverso rispetto a quello che ho fatto
                #   per poter usare "Zombie" qui nell'instance of (tipo in game, dove c'era from actors.zombie import Zombie
                #   e qui from src.actors.zombie import Zombie, l'instanceof non li considera della stessa classe perché usano
                #   diverso namespace.
                arena.kill(o)
                arena.kill(self)
            elif isinstance(o, Ground) or isinstance(o, BackgroundPlatform): # Se la fiaccola tocca terra crea la fiamma
                self._ground_collision(arena, o)
            elif isinstance(o, BackgroundSolid): # Altrimenti, qualsiasi altra cosa ho colpito, despawno
                arena.kill(self)


        self._dy = min(self._dy + self._gravity, self._max_dy)

        # Aggiornamento del count per l'animazione
        self._anim_count += 1

    def _ground_collision(self, arena: Arena, other: Ground):
        x, y = self.pos()
        w, h = self.size()
        gx, gy = other.pos()

        cx = x + w / 2 # Posizione x del pixel centrale della fiaccola
        arena.spawn(Flame((x, gy))) # Devo passare il punto di collisione per terra, quindi altezza terra e x del centro della fiaccola
        arena.kill(self)

class Flame (Actor):
    def __init__(self, ground_pos: Point):
        # Movement
        self._start_x, self._start_y = ground_pos # Posizione "sul terreno", cioè la posizione del pixel centrale più in basso dello sprite
        self._x, self._y = ground_pos # Verranno aggiornati al pixel in alto a sinistra nel metodo move

        # Gameplay
        self._life = 60 # Frame di durata della fiaccola

        # Animations
        self._anim_count = 0

    def pos(self) -> Point:
        return self._x, self._y
    def sprite(self):
        if self._anim_count == 0: return 228, 744
        else: return 192, 736
    def size(self):
        if self._anim_count == 0: return 23, 23
        else: return 32, 32
    def move(self, arena: Arena):
        # Porto la posizione al pixel in alto a sinistra
        # Questo lo devo ripetere a ogni frame perché usando sprite diversi per animare, la posizione cambierà
        # Dato che usiamo come "anchor point" dell'immagine il pixel in alto a sinistra.
        self._anim_count = (arena.count() // 4) % 2
        w, h = self.size()
        self._x = self._start_x - w / 2
        self._y = self._start_y - h

        # Uccisione dei nemici
        for o in arena.collisions():
            if isinstance(o, Zombie): arena.kill(o)

        # Logica di despawn
        if self._life > 0:
            self._life -= 1
        else:
            arena.kill(self)