from dataclasses import dataclass, field
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

@dataclass
class NextScreen:
    name: str = field(default="none")

class Screen:

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        self.btp: Win = btp
        self.atlas: ObjectBaseAtlas = atlas

    def on_load(self):
        pass

    def on_draw(self, dt: float) -> NextScreen:
        return NextScreen()
    
    def on_draw_ui(self, dt: float) -> NextScreen:
        return NextScreen()

    def on_ready(self):
        pass
