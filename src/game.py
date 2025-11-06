from random import choice, randrange
from framework.actor import Arena

from actors.arthur import Arthur
from actors.zombie import Zombie
from src.actors.platforms import Grave, Ground, BackgroundPlatform

FPS = 30 # Frame per secondo, usati per animazioni in caso si potrà modificare

def tick():
    g2d.clear_canvas()
    g2d.draw_image("ghosts-goblins-bg.png", (0, 0))

    if randrange(500) == 0:
        player_x, player_y = player.pos()
        direction = choice(("Right", "Left"))
        if direction == "Right":
            arena.spawn(Zombie((player_x - randrange(50, 200), player_y), direction))
        else:
            arena.spawn(Zombie((player_x + randrange(50, 200), player_y), direction))

    for a in arena.actors():
        if a.sprite() is not None:
            g2d.draw_image("ghosts-goblins.png", a.pos(), a.sprite(), a.size())
        else:
            pass  # g2d.draw_rect(a.pos(), a.size())

    arena.tick(g2d.current_keys())  # Game logic


def main():
    global g2d, arena, player
    import framework.g2d as g2d  # game classes do not depend on g2d

    arena = Arena((800, 250))

    player = Arthur((700, 20))
    arena.spawn(player)
    arena.spawn(Zombie((50, 200), "Right"))

    ground = [
        Ground((0, 202), (1665, 48))
    ]
    platforms = [
        BackgroundPlatform((600, 125), (535, 12))
    ]
    graves = [
        Grave((50, 186), (16, 16)),
        Grave((242, 186), (16, 16))
    ]

    for g in ground + platforms + graves:
        arena.spawn(g)


    g2d.init_canvas(arena.size(), 2)
    g2d.main_loop(tick)

if __name__ == "__main__":
    main()
