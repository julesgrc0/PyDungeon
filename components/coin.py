from core import * 


class Coin(CollectableItem):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
        self.animation_speed = 5

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('coin')
    
    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)

        self.size /= 3
