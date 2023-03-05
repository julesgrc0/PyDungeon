from BTP.BTP import *
from core import *
from map import *


class GameMap(MapBase):

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        super().__init__(btp, atlas)
        self.player_tiles_collision: list[ComponentObject] = []
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

        self.player_tiles_collision = tmp
    
    def on_draw_ui(self, dt: float):
        self.player_ref.on_draw_ui(dt)

    def on_draw(self, dt: float):
        super().on_draw(dt)

        # TODO: collision and ref for each entity + thread -> update_control
        # for entity in self.entities_refs:
        #     entity.on_update_control(dt, self.get_collision_tiles())
        #     entity.on_draw(dt)

        self.player_ref.on_update_control(dt, self.player_tiles_collision)
        self.player_ref.on_draw(dt)


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
