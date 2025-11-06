from random import choice, randrange

from framework.actor import Arena
from src.framework.gui import View

from actors.arthur import Arthur
from actors.zombie import Zombie
from src.actors.platforms import Grave, Ground, BackgroundPlatform

from framework.utilities import remove_pos


FPS = 30 # Frame per secondo, usati per animazioni in caso si potrà modificare

def tick():
    g2d.clear_canvas()
    g2d.draw_image("ghosts-goblins-bg.png", remove_pos((0, 0), view.pos()), (2, 10), (3584, 240))
    view.move(arena)

    if randrange(500) == 0:
        player_x, player_y = player.pos()
        direction = choice(("Right", "Left"))
        if direction == "Right":
            arena.spawn(Zombie((player_x - randrange(50, 200), player_y), direction))
        else:
            arena.spawn(Zombie((player_x + randrange(50, 200), player_y), direction))

    for a in arena.actors():
        if a.sprite() is not None:
            g2d.draw_image("ghosts-goblins.png", remove_pos(a.pos(), view.pos()), a.sprite(), a.size())
        else:
            pass  # g2d.draw_rect(a.pos(), a.size())

    arena.tick(g2d.current_keys())  # Game logic


def main():
    global g2d, arena, player, view
    import framework.g2d as g2d

    arena = Arena((3583, 240))
    player = Arthur((700, 20))

    view = View((0, 0), (320, 240), player)

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


    g2d.init_canvas(view.size(), 2)
    g2d.main_loop(tick)

if __name__ == "__main__":
    main()
