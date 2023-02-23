from core import *
from utility import DemoActionTypes

class Chest(Tileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
        self.state = "closed"
        self.animation_speed = 4

        self.valid = is_animated(self.texture) and len(self.texture.textures) >= 2

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('chest')

    def on_action(self, action: ActionEvent) -> Any:
        if action.name == DemoActionTypes.COLLISION:
            if self.state == "closed":
                self.state = "animation"
                self.animation_index = 1
            

    def get_frame(self, dt: float) -> int:
        if not self.valid:
            return
        
        match self.state:
            case "closed":
                return self.texture.textures[0]
            case "animation":
                frame = super().get_frame(dt)
                if int(self.animation_index)%len(self.texture.textures) == 0:
                    self.state = "opened"
                return frame
            case "opened":
                return self.texture.textures[-1]
