from core import *


class Weapon(CollectableItem):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('weapon')
    
    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)

        self.size *= 0.6
