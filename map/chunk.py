from BTP.BTP import *
from core import *

from map.tile import TileData
from utility import TILE_SIZE, WHITE, from_vec_str, is_in_view


class ChunkData:

    def __init__(self) -> None:
        # chunk position (chunk_pos * chunk_size * tile_size)
        self.position: Vec
        self.tiles: list[TileData] = []


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
