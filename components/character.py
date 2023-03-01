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
        self.inventory_grid: list[list] = []

        self.inventory_selection: int = -1
        self.inventory_item_angle = 0
        self.inventory_item_angle_dir = True

    @staticmethod
    def is_grouped() -> bool:
        return True

    @staticmethod
    def get_group_name(name: str) -> str:
        return name.replace('_idle', '').replace('_run', '').replace('_hit', '')

    @staticmethod
    def check_name(name: str):
        return name.endswith('idle') or name.endswith('run') or name.endswith('hit')

    def copy(self):
        copy_obj: Character = super().copy()
        copy_obj.inventory = copy.copy(copy_obj.inventory)
        copy_obj.inventory_grid = copy.copy(copy_obj.inventory_grid)
        return copy_obj

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

        margin = 10
        posix = (self.btp.get_render_size().x - ((TILE_SIZE + margin) * 8))/2

        posx = posix
        posy = TILE_SIZE * 2

        x = 0
        for i in range(0, 32):
            self.inventory_grid.append(
                [Vec(posx, posy), Vec(TILE_SIZE), None, 0])
            posx += TILE_SIZE + margin
            x += 1
            if x >= 8:
                x = 0
                posx = posix
                posy += TILE_SIZE + margin

    def update_inventory(self):
        unique: list[list] = []

        for it in self.inventory:
            for uit in unique:
                if uit[0].name == it.name:
                    uit[1] += 1
                    break
            else:
                unique.append([it.copy(), 1])

        i = 0
        it_margin = TILE_SIZE - 20
        for it, count in unique:
            if i >= len(self.inventory_grid):
                break

            it.angle = 0
            it.size.x = (it.size.x*it_margin) / it.size.y
            it.size.y = it_margin
            it.position = center_rect(
                self.inventory_grid[i][0], Vec(TILE_SIZE), it.size)

            self.inventory_grid[i][2] = it
            self.inventory_grid[i][3] = count
            i += 1

        if len(self.inventory) == 0:
            self.inventory_selection = -1
        elif self.inventory_selection >= len(self.inventory):
            self.inventory_selection = 0

    def is_alive(self):
        return self.life > 0

    def on_action(self, action: ActionEvent) -> Any:
        if action.name == DungeonActionTypes.COLLECT:
            if isinstance(action.object, Chest) and self.atlas is not None:
                items: list[CollectableItem] = action.object.get_items(
                    self.atlas)
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

            if self.btp.is_key_pressed(Keyboard.CTRL_L):
                if len(self.inventory) == 0:
                    self.inventory_selection = -1
                elif self.inventory_selection + 1 >= len(self.inventory):
                    self.inventory_selection = 0
                else:
                    self.inventory_selection += 1

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

        for pos, size, item, count in self.inventory_grid:
            self.btp.draw_rectline(pos, size, WHITE)
            if item is not None:
                item.on_draw(dt)

            if count > 1:
                self.btp.draw_text("x"+str(count), pos + Vec(5), 20, WHITE)

    def on_draw(self, dt: float):
        self.btp.draw_image(self.get_frame(
            dt), self.position, self.size * self.flip, 0)

        if self.inventory_selection != -1:
            item: CollectableItem = self.inventory[self.inventory_selection]

            item.position = self.position + self.size * Vec(0.95, 0.55)
            item.angle = self.inventory_item_angle

            angle_move = 200 * dt
            if not self.inventory_item_angle_dir:
                angle_move = -300 * dt

            self.inventory_item_angle += angle_move
            if self.inventory_item_angle >= 70:
                self.inventory_item_angle_dir = False
            elif self.inventory_item_angle <= -10:
                self.inventory_item_angle_dir = True

            self.inventory[self.inventory_selection].on_draw(dt)
