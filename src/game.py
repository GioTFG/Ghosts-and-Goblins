from random import choice, randrange
from framework.actor import Arena

from actors.arthur import Arthur
from actors.zombie import Zombie

FPS = 30 # Frame per secondo, usati per animazioni in caso si potrà modificare

def tick():
    g2d.clear_canvas()

    if randrange(500) == 0:
        player_x, player_y = player.pos()
        direction = choice(("Right", "Left"))
        if direction == "Right":
            arena.spawn(Zombie((player_x - randrange(50, 200), player_y), direction))
        else:
            arena.spawn(Zombie((player_x + randrange(50, 200), player_y), direction))

    for a in arena.actors():
        if a.sprite() != None:
            g2d.draw_image("ghosts-goblins.png", a.pos(), a.sprite(), a.size())
        else:
            pass  # g2d.draw_rect(a.pos(), a.size())

        if isinstance(a, Zombie) and a.is_despawned():
            arena.kill(a)

    arena.tick(g2d.current_keys())  # Game logic


def main():
    global g2d, arena, player
    import framework.g2d as g2d  # game classes do not depend on g2d

    arena = Arena((480, 360))
    # arena.spawn(Ball((40, 80)))
    # arena.spawn(Ball((80, 40)))
    # arena.spawn(Ghost((120, 80)))
    # arena.spawn(Turtle((230, 170)))

    player = Arthur((400, 0))
    arena.spawn(player)
    arena.spawn(Zombie((50, 200), "Right"))

    g2d.init_canvas(arena.size(), 2)
    g2d.main_loop(tick)

if __name__ == "__main__":
    main()
