from core import *
from map import MapBase, Chunk

from BTP.gui import Button
from utility import TILE_SIZE, WHITE, BLACK, Stats, Keyboard, vec_floor, from_vec_str, is_in_view, vec_ceil, DungeonScreens


class MapCreator(MapBase):

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        super().__init__(btp, atlas)

        self.creator_mode = True

        self.selectable_tiles_normal: list[ComponentObject] = []
        self.selectable_tiles_special: list[ComponentObject] = []
        self.selectable_mode = True

        self.selected: ComponentObject | None = None

        self.exit_btn = Button(self.btp)
        self.save_btn = Button(self.btp)
        self.info_btn = Button(self.btp)
        self.type_btn = Button(self.btp)

        self.infos = Stats(self.btp)
        self.show_info = False

        self.flip = Vec(1)
        self.collision_mode = False

    # setup -> thread + ui
    def on_ready(self):
        tile_size = TILE_SIZE/2

        tile_types: list[Tileset] = self.atlas.from_instance(Tileset)
        x = 0.5
        y = 5
        for tile in tile_types:
            cpt = tile.copy()
            cpt.size /= 2
            cpt.position = Vec(x, y) * tile_size

            self.selectable_tiles_normal.append(cpt)
            y += 1
            if y >= int(self.btp.get_render_size().y/tile_size) - 1:
                y = 5
                x += 1

        x = 0.5 * tile_size
        y = 5 * tile_size
        tile_types = self.atlas.from_instance(SpecialTileset)

        for tile in tile_types:
            cpt = tile.copy()
            cpt.position = Vec(x, y)
            cpt.size /= 2
            self.selectable_tiles_special.append(cpt)

            y += cpt.size.y
            if y >= int(self.btp.get_render_size().y):
                y = 5 * tile_size
                x += tile_size

        self.exit_btn.build("Quitter", Vec(30, 10), Vec(20, 10))
        self.info_btn.build("Show/Hide Infos", Vec(30, 60), Vec(20, 10))
        self.save_btn.build("Exporter & Quitter", Vec(30, 110), Vec(20, 10))
        self.type_btn.build("Normal/Special tiles", Vec(30, 160), Vec(20, 10))

        self.btp.camera_pos = Vec(-(Chunk.DEFAULT_SIZE * TILE_SIZE))
        self.btp.camera_offset = Vec()

        super().on_ready()
        self.last_position = Vec(1, 1)  # update chunk view

    # draw
    def on_draw(self, dt: float):
        speed = dt * 300
        move = Vec()
        show_mouse_rect = False
        pos = None

        if self.btp.is_key_down(Keyboard.LEFT):
            move.x -= speed
        elif self.btp.is_key_down(Keyboard.RIGHT):
            move.x += speed

        if self.btp.is_key_down(Keyboard.UP):
            move.y -= speed
        elif self.btp.is_key_down(Keyboard.DOWN):
            move.y += speed

        if move.is_zero():
            self.fix_camera_pos()
            pos = Vec(
                int(self.btp.mouse.x/TILE_SIZE) * TILE_SIZE,
                int(self.btp.mouse.y/TILE_SIZE) * TILE_SIZE
            ) + self.btp.camera_pos

        if self.btp.is_key_pressed(Keyboard.SPACE):
            self.selected = None
            self.flip = Vec(1)

        if self.btp.is_key_pressed(Keyboard.CTRL_R):
            self.flip.x *= -1
        if self.btp.is_key_pressed(Keyboard.CTRL_L):
            self.flip.y *= -1

        if self.btp.is_key_pressed(Keyboard.ENTER):
            self.collision_mode = not self.collision_mode

        self.btp.camera_pos += move

        if self.btp.camera_offset.x != 0 or self.btp.camera_offset.y != 0:
            self.btp.camera_offset = Vec()
        if self.btp.camera_zoom != 1:
            self.btp.camera_zoom = 1

        if self.btp.mouse.x > self.btp.get_render_size().x*0.22:

            if self.btp.is_mouse_pressed():
                self.fix_camera_pos()
                pos = Vec(
                    int(self.btp.mouse.x/TILE_SIZE) * TILE_SIZE,
                    int(self.btp.mouse.y/TILE_SIZE) * TILE_SIZE
                ) + self.btp.camera_pos

                if self.selected is not None:
                    cp = self.selected.copy()
                    cp.position = pos
                    cp.flip = Vec(self.flip.x, self.flip.y)
                    cp.size *= 2
                    if self.collision_mode:
                        cp.collision = True

                    self.map_add(cp)
                else:
                    self.map_remove(pos)
            else:
                show_mouse_rect = True

        super().on_draw(dt)

        if show_mouse_rect and pos is not None:
            color = Color(255, 0, 0, 255)
            if self.selected:
                color = Color(0, 255, 0, 255)
                if self.collision_mode:
                    color = Color(0, 0, 255, 255)

            self.btp.draw_rectline(pos, Vec(TILE_SIZE), color)
        
        return NextScreen()
        

    def on_draw_ui(self, dt: float):
        self.btp.draw_rect(Vec(), self.btp.get_render_size()
                           * Vec(0.22, 1), BLACK)

        btne_color = WHITE, Color(0, 0, 0, 50)
        if self.exit_btn.is_hover():
            btne_color = Color(230, 230, 230, 255), Color(0, 0, 0, 200)
        if self.exit_btn.draw(*btne_color):
            return NextScreen(DungeonScreens.MENU)

        btni_color = WHITE, Color(0, 0, 0, 50)
        if self.info_btn.is_hover():
            btni_color = Color(230, 230, 230, 255), Color(0, 0, 0, 200)
        if self.info_btn.draw(*btni_color):
            self.show_info = not self.show_info

        btns_color = WHITE, Color(0, 0, 0, 50)
        if self.save_btn.is_hover():
            btns_color = Color(230, 230, 230, 255), Color(0, 0, 0, 200)
        if self.save_btn.draw(*btns_color):
            self.export_map()
            return NextScreen(DungeonScreens.MENU)

        btnt_color = WHITE, Color(0, 0, 0, 50)
        if self.type_btn.is_hover():
            btnt_color = Color(230, 230, 230, 255), Color(0, 0, 0, 200)
        if self.type_btn.draw(*btnt_color):
            self.selectable_mode = not self.selectable_mode
            self.selected = None

        hover_item = None
        for it in (self.selectable_tiles_normal if self.selectable_mode else self.selectable_tiles_special):
            it.on_draw(dt)

            if self.btp.col_rect_point(it.position, it.size, self.btp.mouse):
                hover_item = it

        if hover_item is not None:
            self.btp.draw_rectline(hover_item.position,
                                   hover_item.size, Color(255, 0, 0, 255))
            if self.btp.is_mouse_down():
                self.selected = hover_item

        if self.selected is not None:
            self.btp.draw_rectline(
                self.selected.position, self.selected.size, Color(0, 255, 0, 255))

        if self.show_info:
            self.infos["FPS"] = round(1/dt) if dt != 0 else 0
            self.infos["Flip (x,y)"] = "{},{}".format(
                self.flip.x < 0, self.flip.y < 0)
            self.infos["Collision"] = str(self.collision_mode)
            self.infos["Keyboard"] = "\nMove camera = [Arrows]\nFlipX = [CTRL-R]\nFlipY = [CTRL-L]\nReset/Unselect = [SPACE]\nCollision = [ENTER]"
            self.infos["Position"] = self.btp.camera_pos
            self.infos["Chunk"] = len(self.map)
            if self.selected is not None:
                self.infos["Item Type"] = type(self.selected).__name__.lower()
                self.infos["Item Name"] = self.selected.name

            self.infos.on_draw(self.btp.get_render_size() *
                               Vec(0.22, 0) + Vec(10), 20, WHITE)
            
        return NextScreen(DungeonScreens.MAP_CREATOR)

    # remove add tile
    def map_add(self, item: ComponentObject):
        c_pos: Vec = vec_floor(item.position/(TILE_SIZE *
                               Chunk.DEFAULT_SIZE)) * (TILE_SIZE * Chunk.DEFAULT_SIZE)

        chunk = list(filter(lambda chunk: chunk.position == c_pos, self.map))
        if chunk is not None and len(chunk) >= 1:
            chunk[0].tiles.append(item)
        else:
            newc = Chunk(self.btp, self.atlas, c_pos)
            newc.creator_mode(True)
            newc.tiles.append(item)

            self.map.append(newc)

        self.force_update_view()

    def map_remove(self, position: Vec):
        c_pos: Vec = vec_floor(position/(Chunk.DEFAULT_SIZE *
                               TILE_SIZE)) * (Chunk.DEFAULT_SIZE * TILE_SIZE)

        chunk = list(filter(lambda chunk: chunk.position == c_pos, self.map))
        if chunk is not None and len(chunk) == 1:
            chunk = chunk[0]

            tile = list(
                filter(lambda tile: tile.position == position, chunk.tiles))
            if tile is not None and len(tile) >= 1:
                chunk.tiles.remove(tile[0])
                if len(chunk.tiles) <= 0:
                    self.map.remove(chunk)
        self.force_update_view()

    def fix_camera_pos(self):
        self.btp.camera_pos = Vec(
            int(self.btp.camera_pos.x/TILE_SIZE) * TILE_SIZE,
            int(self.btp.camera_pos.y/TILE_SIZE) * TILE_SIZE
        )
