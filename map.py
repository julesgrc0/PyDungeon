from BTP.BTP import *
from BTP.util import *
from BTP.gui import *

from core import *
from utility import TILE_SIZE, WHITE, from_vec_str, is_in_view, vec_ceil

import threading


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
        self.object: Any
        self.position: Vec  # chunk_pos + (tile_pos * tile_size)
        self.flip: Vec
        self.name: str
        self.collision: bool


class Chunk(Component):
    DEFAULT_SIZE = 6

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas, position: Vec) -> None:
        self.btp = btp
        self.atlas = atlas

        self.tiles: list[ComponentObject] = []
        self.tiles_view: list[ComponentObject] = []
        self.tile_size = Vec(TILE_SIZE)

        self.position = position
        self.size = Vec(Chunk.DEFAULT_SIZE) * self.tile_size

        self.creator_info = False

    @staticmethod
    def from_data(data: ChunkData, btp: Win, atlas: ObjectBaseAtlas) -> Self:
        chunk = Chunk(btp, atlas, data.position)
        for tile in data.tiles:
            obj_tile = atlas.copy(tile.object, tile.name)
            if obj_tile is not None:
                obj_tile.position = tile.position
                obj_tile.flip = tile.flip
                obj_tile.collision = tile.collision
                chunk.tiles.append(obj_tile)
        return chunk

    def to_data(self) -> ChunkData:
        data = ChunkData()
        data.position = self.position
        for tile in self.tiles:
            data_tile = TileData()
            data_tile.object = tile.__class__
            data_tile.flip = tile.flip
            data_tile.name = tile.name
            data_tile.collision = tile.collision
            data_tile.position = tile.position
            data.tiles.append(data_tile)
        return data

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
        if self.creator_info:
            dupli_tile = {}
            collisions = []

            for tile in self.tiles_view:
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

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
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

    def on_ready(self):
        self.max_chunks = vec_ceil(
            (self.btp.get_render_size()/(Chunk.DEFAULT_SIZE * TILE_SIZE))) + 1

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
            chunkdata: ChunkData = chunk.to_data()
            map_data.chunks.append(chunkdata)

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

        for chunkdata in map_data.chunks:
            chunk: Chunk = Chunk.from_data(chunkdata, self.btp, self.atlas)
            chunk.creator_mode(self.creator_mode)
            self.map.append(chunk)

        return True


class Map(MapBase):

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        super().__init__(btp, atlas)
        self.collision_tiles: list[ComponentObject] = []
        self.collision_update = False
        self.view_tile_count = 0


    def on_view_update(self):
        tmp = []
        size = (self.btp.get_render_size() - self.btp.camera_offset*2)
        position = self.btp.camera_pos

        size *= 2
        position -= size/4

        tcount = 0
        for chunk in self.view_chunks:
            chunk.update_view()
            for tile in chunk.tiles_view:
                if tile.collision and self.btp.col_rect_rect(tile.position, tile.size, position, size) and isinstance(tile, ComponentObject):
                    tmp.append(tile)

            tcount += len(chunk.tiles_view)
        self.view_tile_count = tcount

        self.collision_tiles = tmp
        self.collision_update = True

    def has_collision_update(self):
        return self.collision_update

    def get_collision_tiles(self) -> list[ComponentObject]:
        self.collision_update = False
        return self.collision_tiles


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
