from core import *

class SingleItem(Tileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name == 'skull' or name == 'crate' or name == 'hole'
