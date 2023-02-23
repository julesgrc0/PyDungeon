from core import *
from utility import TILE_SIZE

class Doors(SpecialTileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('doors')

    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)

        if self.name == "doors_leaf_open" or self.name == "doors_leaf_closed":
            self.size = Vec(2, 2) * TILE_SIZE
        elif self.name == "doors_frame_left" or self.name == "doors_frame_righ":
            self.size = Vec(1, 2) * TILE_SIZE
