import random
from BTP.BTP import *
from BTP.util import *
from BTP.gui import *

from core import *
from utility import TILE_SIZE, DungeonRoleTypes, vec_ceil, DungeonActionData

import threading

from map.chunk import Chunk, ChunkData
from components.character import Character, CharacterData

class MapData:

    def __init__(self) -> None:
        self.chunks: list[ChunkData] = []
        self.entities: list[CharacterData] = []
        self.player: CharacterData


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

        self.entities_refs: list[Character] = []
        self.player_ref: Character

    def on_ready(self):
        self.max_chunks = vec_ceil(
            (self.btp.get_render_size()/(Chunk.DEFAULT_SIZE * TILE_SIZE))) + 1
        
        self.player_ref = self.atlas.copy(Character, random.choice(["knight_m", "knight_f"]))
        self.player_ref.action_data = DungeonActionData(role=DungeonRoleTypes.PLAYER)

    def start_update_thread(self):
        if not self.update_thread:
            threading.Thread(target=self.update_chunks_view).start()

    def stop_update_thread(self):
        self.update_thread = False

    def force_update_view(self):
        self.force_update = True


    def on_view_update(self):
        tmp = []
        for chunk in self.map:
            if self.btp.col_rect_rect(self.btp.camera_pos - self.btp.camera_offset, self.btp.get_render_size(), chunk.position, chunk.size):
                tmp.append(chunk)
                chunk.update_view()

                if len(tmp) >= (self.max_chunks.x * self.max_chunks.y):
                    break

        self.view_chunks = tmp

    # def on_entities_update(self, dt: float, collisions: list[ComponentObject]):
    #     for entity in self.entities_refs:
    #         entity.on_update_control(dt, collisions)

    def update_chunks_view(self):
        self.update_thread = True
        while self.btp.is_running() and self.update_thread:
            if self.btp.camera_pos != self.last_position or self.btp.camera_offset != self.last_offset or self.force_update:
                self.last_position = self.btp.camera_pos
                self.last_offset = self.btp.camera_offset

                if self.force_update:
                    self.force_update = False

                self.on_view_update()

    # draw chunks
    def on_draw(self, dt: float):
        for chunk in self.view_chunks:
            chunk.on_draw(dt)
    
    def clear_map(self):
        self.map.clear()

    def export_map(self):
        map_data = MapData()
        map_data.player = self.player_ref.to_data()

        for entity in self.entities_refs:
            map_data.entities.append(entity.to_data())

        for chunk in self.map:
            map_data.chunks.append(chunk.to_data())


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

        self.player_ref = Character.from_data(map_data.player, self.atlas)
        for entitydata in map_data.entities:
            entity: Character = Character.from_data(entitydata, self.atlas)
            self.entities_refs = entity

        for chunkdata in map_data.chunks:
            chunk: Chunk = Chunk.from_data(chunkdata, self.btp, self.atlas)
            chunk.creator_mode(self.creator_mode)
            self.map.append(chunk)

        return True
