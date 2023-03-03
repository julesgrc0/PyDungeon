from components.chest import Chest
from components.coin import Coin
from components.flask import Flask
from components.weapon import Weapon
from core import *
from utility import TILE_SIZE, DungeonActionData, DungeonActionTypes, DungeonRoleTypes, Keyboard, rect_rect_center, center_rect, WHITE, rotate_around


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

        self.action_data = DungeonActionData()
        self.life = 100

        self.atlas: Optional[ObjectBaseAtlas] = None

        self.inventory: list[CollectableItem] = []
        self.inventory_open: bool = False
        self.inventory_grid: list[list] = [[None, 0] for i in range(0, 32)]

        self.inventory_selection: Optional[CollectableItem] = None
        
        self.item_angle = 0
        self.item_angle_max = 0


    @staticmethod
    def is_grouped() -> bool:
        return True

    @staticmethod
    def get_group_name(name: str) -> str:
        return name.replace('_idle', '').replace('_run', '').replace('_hit', '')

    @staticmethod
    def check_name(name: str):
        return name.endswith('idle') or name.endswith('run') or name.endswith('hit')

    # def copy(self):
    #     copy_obj: Character = super().copy()
    #     copy_obj.inventory = copy.copy(copy_obj.inventory)
    #     copy_obj.inventory_grid = copy.copy(copy_obj.inventory_grid)
    #     return copy_obj

    def damage(self, value: float):
        self.life -= value
        if len(self.hit) != 0:
            self.state = "hit"

    def repulce(self, force: Vec, duration: float):
        if self.force_timer <= 0:
            self.force = force
            self.force_timer = duration

    def repulce_oposite(self, position: Vec, size: Vec, force: float, duration: float):
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

    def draw_inventory(self):
        TILE_SIZE_MARGIN = TILE_SIZE + 10
        base_x = (self.btp.get_render_size().x - (TILE_SIZE_MARGIN * 8))/2
        item_position = Vec(
            base_x,
            TILE_SIZE * 2
        )

        i = 0
        for item, count in self.inventory_grid:
            if item is not None:
                item.position = center_rect(item_position, Vec(TILE_SIZE), item.size)
                item.on_draw(0)
            self.btp.draw_rectline(item_position, Vec(TILE_SIZE), WHITE)

            if count > 1:
                self.btp.draw_text(f"x{count}", item_position + Vec(5), 20, WHITE)

            item_position.x += TILE_SIZE_MARGIN
            
            if i+1 == 8:
                i = 0
                item_position.x = base_x
                item_position.y += TILE_SIZE_MARGIN
            else:
                i += 1
            
    def update_inventory(self):
        unique: list[list] = []
        it_margin = TILE_SIZE - 20
        
        for it in self.inventory:
            for uit in unique:
                if uit[0].name == it.name:
                    uit[1] += 1
                    break
            else:
                item = it.copy()

                item.angle = 0
                item.size.x = (it.size.x*it_margin) / it.size.y
                item.size.y = it_margin

                unique.append([item, 1])

        self.inventory_grid = unique + [[None, 0]for i in range(32 - len(unique))]

        if self.inventory_selection is not None:
            for it in self.inventory_grid:
                if it[0] is not None and it[0].name == self.inventory_selection.name:
                    break
            else:
                self.inventory_selection = None

    def select_inventory(self):
        if self.inventory_selection is None:
            self.inventory_selection = self.inventory[0].copy()
        else:
            for i in range(0, len(self.inventory)):
                if self.inventory[i].name == self.inventory_selection.name:
                    if i + 1 >= len(self.inventory):
                       continue 
                    else:
                        for k in range(i, len(self.inventory)):
                            if self.inventory[k].name != self.inventory_selection.name:
                                self.inventory_selection = self.inventory[k].copy()
                                break
                        else:
                            continue
                        break
            else:
                self.inventory_selection = self.inventory[0].copy()

    def is_alive(self):
        return self.life > 0

    def on_action(self, action: ActionEvent) -> Any:
        if action.name == DungeonActionTypes.COLLECT:
            if isinstance(action.object, Chest) and self.atlas is not None:
                items: list[CollectableItem] = action.object.get_items(self.atlas)
                self.inventory += items
                self.update_inventory()

    def can_move(self, move: Vec, collision_tiles: list[ComponentObject]) -> bool:
        ref: Optional[ObjectBase] = None
        for tile in collision_tiles:
            if self.btp.col_rect_rect(tile.position, tile.size, self.position + move, self.size):
                ref = tile
                continue
            elif tile.accept_action(DungeonActionTypes.AROUND):
                tile.on_action(ActionEvent.create(
                    DungeonActionTypes.AROUND, self, self.action_data))

        if ref is None:
            return True

        if self.btp.col_rect_rect(ref.position, ref.size, self.position, self.size):
            can = ref.on_action(ActionEvent.create(
                DungeonActionTypes.COLLISION_IN, self, self.action_data))
            return True if not isinstance(can, bool) else can

        can = ref.on_action(ActionEvent.create(
            DungeonActionTypes.COLLISION, self, self.action_data))
        return False if not isinstance(can, bool) else can

    def on_update_control(self, dt: float, collision_tiles: list[ComponentObject]):
        speed = dt * 200
        move = Vec()

        if self.force_timer > 0:
            move += self.force * dt
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
            if self.can_move(move, collision_tiles):  # if collsion in
                if not move.is_zero():
                    self.position += move
                    self.inventory_open = False

            if self.btp.is_key_pressed(Keyboard.CTRL_L) and len(self.inventory) != 0:
                self.select_inventory()
                

    def get_frame(self, dt: float):
        frames = getattr(self, self.state)
        if len(frames) != 0:
            frame = int(self.animation_index) % len(frames)
            self.animation_index += dt * 8
            return frames[frame-1]
        return 0

    def on_draw_ui(self, dt: float):
        if self.action_data.role != DungeonRoleTypes.PLAYER:
            return

        if self.btp.is_key_pressed(Keyboard.SPACE):
            self.inventory_open = not self.inventory_open

        if not self.inventory_open:
            return

        self.btp.draw_rect(Vec(), self.btp.get_render_size(),
                           Color(0, 0, 0, 100))

        self.draw_inventory()

    def on_draw(self, dt: float):
        self.btp.draw_image(self.get_frame(
            dt), self.position, self.size * self.flip, 0)

        if self.inventory_selection is not None:
            item: CollectableItem = self.inventory_selection

            item.position.x = self.position.x
            item.position.y = self.position.y - item.size.y/2
           

            item.flip.x = self.flip.x
            item.angle = self.item_angle if self.flip.x == 1 else 360 - self.item_angle

            item_margin = 5
            if self.flip.x == -1:
                item.position += Vec(-(item_margin + item.size.x), self.size.y * 0.55)
                item.origin = Vec(item.size.x, item.size.y)
            else:        
                item.position += Vec(self.size.x + item_margin, self.size.y * 0.55)
                item.origin = Vec(0, item.size.y)

            if self.btp.is_mouse_pressed() and self.item_angle_max == 0:
               self.item_angle = 0
               self.item_angle_max = 70
                    
            if self.item_angle_max != 0:
                speed_angle = 100 * dt
            
                if self.item_angle_max == 1:
                    self.item_angle -= speed_angle
                    if self.item_angle <= 0:
                        self.item_angle = 0
                        self.item_angle_max = 0
                elif self.item_angle >= 70:
                    self.item_angle_max = 1
                else:
                    self.item_angle += speed_angle
                    

            self.inventory_selection.on_draw(dt)
