import threading
import time
from BTP.BTP import *
from components.character import Character
from core import *
from map import *
from utility import center_rect


class GameMap(MapBase):

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        super().__init__(btp, atlas)
        self.player_tiles_collision: list[ComponentObject] = []
        self.view_tile_count = 0
        

    def on_character_view_update(self, position: Vec, size: Vec, zone: Vec = Vec(1,1)):
        chunks = []
        collisions = []
        tcount = 0

        screen_size = self.btp.get_render_size()
        screen_position = position - (self.btp.get_render_size() - size)/2
        
        zone_size = size * zone
        zone_position = center_rect(position, size, zone_size)

        for chunk in self.map:
            if self.btp.col_rect_rect(screen_position, screen_size, chunk.position, chunk.size):
                chunks.append(chunk)

                chunk.update_view()
                tcount += len(chunk.tiles_view)

                for tile in chunk.tiles_view:
                    if tile.collision and self.btp.col_rect_rect(tile.position, tile.size, zone_position, zone_size) and isinstance(tile, ComponentObject):
                        collisions.append(tile)

                if len(chunks) >= (self.max_chunks.x * self.max_chunks.y):
                    break


        return (chunks, collisions, tcount)

    def on_view_update(self):
        size = (self.btp.get_render_size() - self.btp.camera_offset*2)
        position = self.btp.camera_pos
        
        self.view_chunks, self.player_tiles_collision, self.view_tile_count = self.on_character_view_update(position, size, Vec(3))
        

    def on_draw_ui(self, dt: float):
        self.player_ref.on_draw_ui(dt)

    def start_update_thread(self):
        super().start_update_thread()

        if self.update_thread:
            threading.Thread(target=self.entities_update_thread).start()            

    def entities_update_thread(self):
        start_time = time.time()
        end_time = time.time()

        while self.update_thread and self.btp.is_running():
            dt = start_time - end_time
            end_time = start_time
            start_time = time.time()

            for entity in self.entities_refs:
                chunks, collisions, tcount = self.on_character_view_update(*entity.get_rect())
                entity.on_update_control(dt, collisions)
            

    def on_draw(self, dt: float):
        super().on_draw(dt)

        for entity in self.entities_refs:
            entity.on_draw(dt)

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
