from core.system import *
from BTP.BTP import *
import BTP.BTP

class Tileset(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)


class SpecialTileset(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)


class CollectableItem(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)


class UI(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('ui')
