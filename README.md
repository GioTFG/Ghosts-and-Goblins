# Ghosts-and-Goblins
## Description
This is a "_remake_" of the 1985 game "Ghosts 'n Goblins" by CapCom made for a University Project at _UniPr_.

For now, it will only have the first level, as it's just a demonstration on how to implement
Object-Oriented Programming in a game, using Python.

## Default Keybinds
| Key(s)     | Action            |
|------------|-------------------|
| `←` / `A`  | Run left          |
| `→` / `D`  | Run right         |
| `Spacebar` | Jump              |
| `↑` / `W`  | Climb ladder      |
| `↓` / `S`  | Descend ladder    |
| `F`        | Attack            |
| `M`        | Mute/Unmute music |
| `P`        | Pause menu        |

## Technical Info
- **Python Version:** 3.13
### **Modules used:**
- g2d: [Fondinfo Github](https://github.com/fondinfo/fondinfo)
  - and its dependencies...
    - pygame
  - Used as a framework for the game
- actor: [Fondinfo Github](https://github.com/fondinfo/fondinfo)
  - Interface used by the framework
- random
  - Used for everything that happens randomly in the game
- os
  - Used to use relative file paths in the code (so it is portable on other machines)
- math
  - Used by the plants projectiles to obtain the correct direction to head towards Arthur
- unittest
  - There are Unit Tests that can be run in the single modules for moving actors (such as Arthur and the enemies).
### **Image sources:**
- [Spritesheet](https://github.com/fondinfo/sprites/blob/main/ghosts-goblins.png)
  - I personally made some edits on it:
    - Added a sprite for "1" and "0" in the HUD elements, as they were not present.
- [Background Image](https://github.com/fondinfo/sprites/blob/main/ghosts-goblins-bg.png)

### Software used to count pixels
- Piskel
  - [Site](https://www.piskelapp.com)
  - [GitHub](https://github.com/piskelapp/piskel)
- Aseprite (once I **_finally_** managed to compile it)
  - [Site](https://aseprite.org)
  - [GitHub](https://github.com/aseprite/aseprite)

### Other Software
- **IDE**: [JetBrains Pycharm](https://www.jetbrains.com/pycharm/)
