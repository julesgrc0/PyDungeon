from BTP.BTP import *
from BTP.util import *
from BTP.gui import *


from textures import *
from utility import *
from objects import *

import random
import threading
import copy
import math
import uuid


class MapData:

    def __init__(self) -> None:
        self.chunks: list[ChunkData] = []


class ChunkData:

    def __init__(self) -> None:
        # chunk position (chunk_pos * chunk_size * tile_size)
        self.position: Vec
        self.tiles: list[TileData] = []


class TileData:

    def __init__(self) -> None:
        self.size: Vec
        self.position: Vec  # chunk_pos + (tile_pos * tile_size)
        self.name: str
        self.flip: Vec
        self.collision: bool


class Chunk:
    TILE_SIZE = 16 * SCALE
    DEFAULT_SIZE = 6

    def __init__(self, btp: Win, atlas: ObjectsAtlas, position: Vec) -> None:
        self.btp = btp
        self.atlas = atlas
        self.tiles: list[AnimatedTextures | StaticTexture] = []
        self.tiles_view: list[AnimatedTextures | StaticTexture] = []

        self.tile_size = Vec(Chunk.TILE_SIZE)
        self.position = position
        self.size = Vec(Chunk.DEFAULT_SIZE) * self.tile_size

        self.creator_info = False

    @staticmethod
    def create_from_data(btp: Win, atlas: ObjectsAtlas, data: ChunkData):
        chunk = Chunk(btp, atlas, data.position)
        for tile in data.tiles:
            if texture_check_name(tile.name, Wall):
                chunk.add_item_type(tile, Wall, atlas.walls)
            elif texture_check_name(tile.name, Floor):
                chunk.add_item_type(tile, Floor, atlas.floors)
            elif texture_check_name(tile.name, Column):
                chunk.add_item_type(tile, Column, atlas.columns)
            elif texture_check_name(tile.name, Doors):
                chunk.add_item_type(tile, Doors, atlas.doors)
            elif texture_check_name(tile.name, Chest):
                chunk.add_item_type(tile, Chest, atlas.chests)

        return chunk

    def get_data(self) -> ChunkData:
        data = ChunkData()
        data.position = self.position
        for tile in self.tiles:
            tdata = TileData()
            tdata.name = type(tile).__name__.lower() + "_" + tile.name
            tdata.position = tile.position
            tdata.flip = tile.flip
            tdata.size = tile.size
            tdata.collision = tile.collision
            data.tiles.append(tdata)

        return data

    def add_item_type(self, tile: TileData, cls, array: list):
        obj = self.atlas.search(array, texture_get_name(tile.name, cls))

        if obj is not None:
            it = copy.copy(obj)
            it.position = tile.position
            it.size = self.tile_size
            it.flip = tile.flip
            it.size = tile.size
            it.collision = tile.collision
            self.tiles.append(it)

    def creator_mode(self, show):
        self.creator_info = show

    def collide(self, position: Vec, size: Vec):
        return self.btp.col_rect_rect(self.position, self.size, position, size)

    def update_view(self):
        tmp = []
        for tile in self.tiles:
            if is_in_view(self.btp, tile.position, tile.size):
                tmp.append(tile)
        self.tiles_view = tmp

    def on_draw(self, dt: float):
        # if self.btp.col_rect_rect(self.btp.camera_pos - self.btp.camera_offset, self.btp.get_render_size(), self.position, self.size):
        if self.creator_info:
            dupli_tile = {}
            collisions = []

            for tile in self.tiles:
                tile.on_draw(dt)
                if tile.collision:
                    collisions.append(tile)

                if dupli_tile.get(str(tile.position)) is None:
                    dupli_tile[str(tile.position)] = 1
                else:
                    dupli_tile[str(tile.position)] += 1

            for pos, count in dupli_tile.items():
                if count > 1:
                    self.btp.draw_text("x{}".format(
                        count), from_vec_str(pos), 10, WHITE)

            for col in collisions:
                self.btp.draw_line(col.position, col.position +
                                   col.size, Color(255, 255, 255, 255))
                self.btp.draw_line(col.position + Vec(col.size.x, 0),
                                   col.position + Vec(0, col.size.y), Color(255, 255, 255, 255))
                self.btp.draw_rectline(
                    col.position, col.size, Color(255, 255, 255, 255))

            self.btp.draw_rectline(
                self.position, self.size, Color(255, 0, 0, 255))
        else:
            for tile in self.tiles_view:
                tile.on_draw(dt)


class MapBase:

    def __init__(self, btp: Win, atlas: ObjectsAtlas) -> None:
        self.btp = btp
        self.atlas = atlas

        self.map: list[Chunk] = []
        self.view_chunks: list[Chunk] = []

        self.max_chunks: Vec = Vec()

        self.last_position: Vec = Vec()
        self.last_offset: Vec = Vec()

        self.creator_mode = False
        self.update_thread = False
        self.force_update = False
        # self.layer_mode = False

    # optimizations -> thread
    def on_ready(self):
        self.max_chunks = vec_ceil(
            (self.btp.get_render_size()/(Chunk.DEFAULT_SIZE * Chunk.TILE_SIZE))) + 1

    def start_update_thread(self):
        if not self.update_thread:
            threading.Thread(target=self.update_chunks_view).start()

    def stop_update_thread(self):
        self.update_thread = False

    def force_update_view(self):
        self.force_update = True

    def on_view_update(self):
        for chunk in self.view_chunks:
            chunk.update_view()

    def update_chunks_view(self):
        self.update_thread = True
        while self.btp.is_running() and self.update_thread:
            if self.btp.camera_pos != self.last_position or self.btp.camera_offset != self.last_offset or self.force_update:
                self.last_position = self.btp.camera_pos
                self.last_offset = self.btp.camera_offset

                if self.force_update:
                    self.force_update = False

                tmp = []
                for chunk in self.map:
                    if self.btp.col_rect_rect(self.btp.camera_pos - self.btp.camera_offset, self.btp.get_render_size(), chunk.position, chunk.size):
                        tmp.append(chunk)
                        if len(tmp) >= (self.max_chunks.x * self.max_chunks.y):
                            break

                self.view_chunks = tmp
                self.on_view_update()

    # draw chunks

    def on_draw(self, dt: float):
        for chunk in self.view_chunks:
            chunk.on_draw(dt)

    # map utility

    def clear_map(self):
        self.map.clear()

    def export_map(self):
        map_data = MapData()

        for chunk in self.map:
            data = chunk.get_data()
            map_data.chunks.append(data)

        storage = Storage()
        storage.state = map_data

    def load_map(self, name):
        map_storage = Storage(name)
        if map_storage.state is None:
            return False

        map_data: MapData = map_storage.state
        if not hasattr(map_data, 'chunks'):
            map_storage.reset_state(MapData())
            return False

        for chunk in map_data.chunks:
            chunk = Chunk.create_from_data(self.btp, self.atlas, chunk)
            chunk.creator_mode(self.creator_mode)
            self.map.append(chunk)

        return True


class MapCreator(MapBase):

    def __init__(self, btp: Win, atlas: ObjectsAtlas) -> None:
        super().__init__(btp, atlas)
        self.creator_mode = True

        self.selectable_tiles_normal: list[StaticTexture | AnimatedTextures] = [
        ]
        self.selectable_tiles_special: list[StaticTexture | AnimatedTextures] = [
        ]
        self.selectable_mode = True

        self.selected: StaticTexture | AnimatedTextures | None = None

        self.save_btn = Button(self.btp)
        self.info_btn = Button(self.btp)
        self.type_btn = Button(self.btp)

        self.infos = Stats(self.btp)
        self.show_info = False

        self.flip = Vec(1)
        self.collision_mode = False

    # setup -> thread + ui
    def on_ready(self):
        tile_types = self.atlas.floors + self.atlas.walls + self.atlas.columns

        x = 0.5
        y = 5
        tile_size = Chunk.TILE_SIZE/2
        for t in tile_types:
            cpt = copy.copy(t)

            cpt.size = Vec(tile_size)
            cpt.position = Vec(x, y) * tile_size

            self.selectable_tiles_normal.append(cpt)

            y += 1
            if y >= int(self.btp.get_render_size().y/tile_size) - 1:
                y = 5
                x += 1

        x = 0.5 * tile_size
        y = 5 * tile_size
        tile_types = self.atlas.doors + self.atlas.chests
        for t in tile_types:
            cpt = copy.copy(t)
            cpt.size /= 2
            cpt.position = Vec(x, y)

            self.selectable_tiles_special.append(cpt)

            y += cpt.size.y
            if y >= int(self.btp.get_render_size().y) - 1:
                y = 5 * tile_size
                x += tile_size

        self.info_btn.build("Show/Hide Infos", Vec(30, 50), Vec(20, 10))
        self.save_btn.build("Export & exit", Vec(30, 100), Vec(20, 10))
        self.type_btn.build("Normal/Special tiles", Vec(30, 150), Vec(20, 10))

        self.btp.camera_pos = Vec(-(Chunk.DEFAULT_SIZE * Chunk.TILE_SIZE))
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
                int(self.btp.mouse.x/Chunk.TILE_SIZE) * Chunk.TILE_SIZE,
                int(self.btp.mouse.y/Chunk.TILE_SIZE) * Chunk.TILE_SIZE
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
                    int(self.btp.mouse.x/Chunk.TILE_SIZE) * Chunk.TILE_SIZE,
                    int(self.btp.mouse.y/Chunk.TILE_SIZE) * Chunk.TILE_SIZE
                ) + self.btp.camera_pos

                if self.selected is not None:
                    cp = copy.copy(self.selected)
                    cp.position = pos
                    if self.selectable_mode or isinstance(self.selected, Chest):
                        cp.size = Vec(Chunk.TILE_SIZE)
                    else:
                        size = self.selected.size
                        if isinstance(self.selected, Doors):
                            if self.selected.name == "all":
                                size = Vec(4, 2) * Chunk.TILE_SIZE
                            elif self.selected.name == "leaf_open" or self.selected.name == "leaf_closed":
                                size = Vec(2, 2) * Chunk.TILE_SIZE
                            elif self.selected.name == "frame_left" or self.selected.name == "frame_righ":
                                size = Vec(1, 2) * Chunk.TILE_SIZE

                        cp.size = size

                    cp.flip = Vec(self.flip.x, self.flip.y)
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

            self.btp.draw_rectline(pos, Vec(Chunk.TILE_SIZE), color)

    def on_draw_ui(self, dt: float):
        self.btp.draw_rect(Vec(), self.btp.get_render_size()
                           * Vec(0.22, 1), BLACK)

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
            return True

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
        return False

    # remove add tile
    def map_add(self, item: AnimatedTextures | StaticTexture):
        c_pos: Vec = vec_floor(item.position/(Chunk.TILE_SIZE *
                               Chunk.DEFAULT_SIZE)) * (Chunk.TILE_SIZE * Chunk.DEFAULT_SIZE)

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
                               Chunk.TILE_SIZE)) * (Chunk.DEFAULT_SIZE * Chunk.TILE_SIZE)

        chunk = list(filter(lambda chunk: chunk.position == c_pos, self.map))
        if chunk is not None and len(chunk) == 1:
            chunk = chunk[0]

            tile = list(
                filter(lambda tile: tile.position == position, chunk.tiles))
            if tile is not None and len(tile) >= 1:
                chunk.tiles.remove(tile[0])
                if len(chunk.tiles) <= 0:
                    self.map.remove(chunk)

    def fix_camera_pos(self):
        self.btp.camera_pos = Vec(
            int(self.btp.camera_pos.x/Chunk.TILE_SIZE) * Chunk.TILE_SIZE,
            int(self.btp.camera_pos.y/Chunk.TILE_SIZE) * Chunk.TILE_SIZE
        )


class Map(MapBase):

    def __init__(self, btp: Win, atlas: ObjectsAtlas) -> None:
        super().__init__(btp, atlas)
        self.collision_rects: list[tuple[Vec, Vec]] = []
        self.collision_update = False

    def on_view_update(self):
        tmp = []
        position = self.btp.camera_pos - self.btp.camera_offset
        size = self.btp.get_render_size() - self.last_offset*2

        for chunk in self.view_chunks:
            if chunk.collide(position, size):
                for tile in chunk.tiles_view:
                    if tile.collision:
                        tmp.append((tile.position, tile.size))

        self.collision_rects = tmp
        self.collision_update = True

        # TODO: join rects who are close to each other

    def has_collision_update(self):
        return self.collision_update

    def get_collision_rects(self):
        self.collision_update = False
        return self.collision_rects


"""
    # Layer system 

    self.tiles_layer: list[AnimatedTextures | StaticTexture] = []
    self.tiles_after_layer: list[AnimatedTextures | StaticTexture] = []

    def on_draw_layer(self, dt):
        for tile in self.tiles_layer:
            tile.on_draw(dt)

    def on_draw_layer_after(self, dt):
        for tile in self.tiles_after_layer:
            tile.on_draw(dt)

    def on_draw_layer_before(self, dt, position: Vec, size: Vec):

        self.tiles_after_layer.clear()  
        for tile in self.tiles_layer:
            if self.is_before_layer(tile, position, size):
                tile.on_draw(dt)
            else:
                self.tiles_after_layer.append(tile)
        
    def is_before_layer(self, tile: AnimatedTextures | StaticTexture, position: Vec, size: Vec) -> bool: # True = before
        xalign = tile.position.x < position.x + size.x and tile.position.x + tile.size.x > position.x
        if not xalign:
            return True  

        return position.y + size.y >= tile.position.y + tile.size.y
    
    
    def init_layer(self):
        dupli_tile = {}
        for tile in self.tiles:
            if dupli_tile.get(str(tile.position)) is None:
                dupli_tile[str(tile.position)] = [tile]
            else:
                dupli_tile[str(tile.position)].append(tile)

        for tiles in dupli_tile.values():
            if len(tiles) > 1:
                self.tiles_layer += tiles[1:]

        for tile in self.tiles_layer:
            self.tiles.remove(tile)


"""
