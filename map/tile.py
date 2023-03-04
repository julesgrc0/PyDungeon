from typing import Any
from BTP.BTP import *

class TileData:

    def __init__(self) -> None:
        self.object: Any
        self.position: Vec  # chunk_pos + (tile_pos * tile_size)
        self.flip: Vec
        self.name: str
        self.collision: bool
