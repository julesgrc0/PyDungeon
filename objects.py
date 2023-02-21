from core import *
from utility import *


class Tileset(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)


class SpecialTileset(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)


class Character(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
        self.name = Character.get_group_name(self.name)

        self.hit = []
        self.run = []
        self.idle = []

        self.state = "idle"

    @staticmethod
    def is_grouped() -> bool:
        return True

    @staticmethod
    def get_group_name(name: str) -> str:
        return name.replace('_idle', '').replace('_run', '').replace('_hit', '')

    @staticmethod
    def check_name(name: str):
        return name.endswith('idle') or name.endswith('run') or name.endswith('hit')

    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)

        if is_animated(self.texture) and len(self.texture.textures) == len(self.texture.textures_names):
            for index in range(0, len(self.texture.textures)):
                last = self.texture.textures_names[index].split('_')

                if "hit" in last:
                    self.hit.append(self.texture.textures[index])
                elif "idle" in last:
                    self.idle.append(self.texture.textures[index])
                elif "run" in last:
                    self.run.append(self.texture.textures[index])

    def can_move(self, move: Vec, collision_rects: list[tuple[Vec, Vec]]):
        rect = None
        for pos, size in collision_rects:
            if self.btp.col_rect_rect(pos, size, self.position + move, self.size):
                rect = (pos, size)
                break
        else:
            return True

        if rect is not None and self.btp.col_rect_rect(rect[0], rect[1], self.ch.position, self.ch.size):
            return True

        return False

    def on_update_control(self, dt: float, collision_rects: list[tuple[Vec, Vec]]):
        speed = dt * 200
        move = Vec()

        if self.btp.is_key_down(Keyboard.RIGHT):
            move.x += speed
            self.flip.x = 1
            self.state = "run"
        elif self.btp.is_key_down(Keyboard.LEFT):
            move.x -= speed
            self.flip.x = -1
            self.state = "run"
        elif self.state == "run":
            self.state = "idle"

        if self.btp.is_key_down(Keyboard.UP):
            move.y -= speed/2
        elif self.btp.is_key_down(Keyboard.DOWN):
            move.y += speed/2

        if not move.is_zero():
            if self.can_move(move, collision_rects):
                self.position += move

    def get_frame(self, dt: float):
        frames = getattr(self, self.state)
        frame = int(self.animation_index) % len(frames)
        self.animation_index += dt * 8
        return frames[frame-1]

    def on_draw(self, dt: float):
        self.btp.draw_image(self.get_frame(
            dt), self.position, self.size * self.flip, 0)


class Wall(Tileset):
    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('wall')

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)


class Floor(Tileset):

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('floor')

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)


class Column(Tileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('colum')


class Chest(Tileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('chest')


class SingleItem(Tileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name == 'skull' or name == 'crate' or name == 'hole'


class Doors(SpecialTileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('doors')

    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)

        if self.name == "doors_leaf_open" or self.name == "doors_leaf_closed":
            self.size = Vec(2, 2) * TILE_SIZE
        elif self.name == "doors_frame_left" or self.name == "doors_frame_righ":
            self.size = Vec(1, 2) * TILE_SIZE


class Coin(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('coin')


class Flask(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('flask')


class Weapon(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('weapon')


class UI(ComponentObject):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('ui')
