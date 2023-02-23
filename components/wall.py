from core import *

class Wall(Tileset):
    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('wall')

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
