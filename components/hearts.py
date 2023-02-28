from core import *
from utility import split_num

class Hearts(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
        self.name = Hearts.get_group_name(self.name)
 

        self.heart_value = 20
        self.max_life = 100
        self.hearts_display = [[-1,Vec()] for i in range(int(self.max_life/self.heart_value))]
        self.last_life = 0
    
    @staticmethod
    def is_grouped() -> bool:
        return True

    @staticmethod
    def get_group_name(name: str) -> str:
        return 'hearts'

    @staticmethod
    def check_name(name: str):
        return name.startswith('ui_')

    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)
        self.size /= 2


    def update_hearts(self, life: float):
        if life == self.last_life:
            return
        self.last_life = life

        parts = split_num(life, self.heart_value)
        
        for index in range(int(self.max_life/self.heart_value)):
            if index >= len(parts):
                self.hearts_display[index][0] = self.texture.textures[0]
            elif parts[index] == self.heart_value:
                self.hearts_display[index][0] = self.texture.textures[1]
            else:
                self.hearts_display[index][0] = self.texture.textures[2]

            self.hearts_display[index][1] = self.position + Vec(self.size.x * index, 0)

    def on_draw(self, dt: float) -> None:
        for texture, pos in self.hearts_display:
            if texture != -1:
                self.btp.draw_image(
                    texture,  pos, self.size * self.flip, 0)
