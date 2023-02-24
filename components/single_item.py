from core import *
from utility import TILE_SIZE

class SingleItem(Tileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
    
    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)
        if self.name == 'crate':
            self.size = Vec(TILE_SIZE)

    @staticmethod
    def check_name(name: str) -> bool:
        return name == 'skull' or name == 'crate' or name == 'hole'
