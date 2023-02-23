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

        self.force = Vec()
        self.force_timer = 0

        self.action_data = DemoActionData()

    @staticmethod
    def is_grouped() -> bool:
        return True

    @staticmethod
    def get_group_name(name: str) -> str:
        return name.replace('_idle', '').replace('_run', '').replace('_hit', '')

    @staticmethod
    def check_name(name: str):
        return name.endswith('idle') or name.endswith('run') or name.endswith('hit')

    def damage(self, value: float):
        print("Character({}) damage: {}".format(self.name, value))
        if len(self.hit) != 0:
            self.state = "hit"

    def repulce(self, force: Vec, duration: float):
        if self.force_timer <= 0:
            self.force = force
            self.force_timer = duration

    def repulce_oposite(self, position:Vec, size:Vec, force: float, duration: float):
        if self.force_timer <= 0:
            center = rect_rect_center(position, size, self.position, self.size)
            center.x = 1 if center.x > 0 else -1
            center.y = 1 if center.y > 0 else -1
            self.repulce(center * force, duration)
            
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

    
    def can_move(self, move: Vec, collision_tiles: list[ComponentObject]) -> bool:
        ref: Optional[ObjectBase] = None
        for tile in collision_tiles:
            if self.btp.col_rect_rect(tile.position, tile.size, self.position + move, self.size):
                ref = tile
                break
        else:
            return True

        if ref is not None and self.btp.col_rect_rect(ref.position, ref.size, self.position, self.size):
            # TODO: action data in class
            can = ref.on_action(ActionEvent.create(DemoActionTypes.COLLISION_IN, self, self.action_data))
            return isinstance(can, bool) and  can

        can = ref.on_action(ActionEvent.create(DemoActionTypes.COLLISION, self, self.action_data))
        return isinstance(can, bool) and can

    def on_update_control(self, dt: float, collision_tiles: list[ComponentObject]) -> Optional[ComponentObject]:
        speed = dt * 200
        move = Vec()

        if self.force_timer > 0:
            move += self.force * speed
            self.force_timer -= 100 * dt
            self.position += move
        else:
            if self.state == "hit":
                self.state = "idle"

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

            # if not move.is_zero():
            if self.can_move(move, collision_tiles): # if collsion in
                if not move.is_zero():
                    self.position += move


    def get_frame(self, dt: float):
        frames = getattr(self, self.state)
        if len(frames) != 0:
            frame = int(self.animation_index) % len(frames)
            self.animation_index += dt * 8
            return frames[frame-1]
        return 0

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
        if self.name == "floor_spikes":
            self.animation_speed = 1

    def trap_damage(self, action: ActionEvent):
        if action.name != DemoActionTypes.COLLISION and action.name != DemoActionTypes.COLLISION_IN:
            return
        
        if not isinstance(action.object, Character) or not isinstance(action.data, DemoActionData):
            return
        
        if action.data.role != "player":
            return
        
        frame = int(self.animation_index) % len(self.texture.textures)
        if frame == 0 or frame == 3:
            char: Character = action.object
            char.damage(10)
            char.repulce_oposite(self.position, self.size, 4, 10)

        return True


    def on_action(self, action: ActionEvent):
        if self.name == "floor_spikes":
            return self.trap_damage(action)

                    


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
