from core import *


class Weapon(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('weapon')
