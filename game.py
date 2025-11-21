"""
Module created by Giovanni Ancora for a project at UniPr.
@author Giovanni Ancora (https://github.com/GioTFG and https://github.com/GiovanniAncora)
This project on GitHub: https://github.com/GioTFG/Ghosts-and-Goblins
"""

import os

from src.framework.gnggame import GngGui
from path_util import ROOT_PATH

def main():
    game = GngGui(
        config_path= os.path.join(ROOT_PATH, "configs/level1.txt"),
        bg_image= os.path.join(ROOT_PATH, "img/ghosts-goblins-bg.png"),
        bg_crop_pos=(2, 10),
        bg_size=(3584, 240),
        zoom=3
    )

if __name__ == "__main__":
    main()
