from core import *
from components import *

from screens.gamemap import GameMap
from components import Hearts

from utility import Stats, DungeonActionData, DungeonRoleTypes, BLACK, Keyboard, DungeonScreens

class Game(Screen):

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        super().__init__(btp, atlas)

        self.last_key = 0
        self.index = 0
        self.stats = Stats(self.btp)
        self.map = GameMap(self.btp, self.atlas)

        # self.character: Optional[Character] = None
        self.hearts: Optional[Hearts] = None

    
    def close_game(self):
        self.map.stop_update_thread()

    def new_game(self, name):
        self.map.clear_map()
        self.map.load_map(name)
        self.map.start_update_thread()
        self.map.force_update_view()

    def on_ready(self):
        self.map.on_ready()

        # characters: list[Character] = self.atlas.from_instance(Character)
        # random.choice(characters).copy()
        # self.character = self.atlas.copy(Character, "knight_m")
        # self.character.atlas = self.atlas
        # self.character.action_data = DungeonActionData(role=DungeonRoleTypes.PLAYER)

        self.hearts = self.atlas.copy(Hearts, "hearts")
        self.hearts.position = self.btp.get_render_size() * Vec(0.1, 0.9)
        self.hearts.on_ready(self.btp)

    def on_draw(self, dt: float):
        self.btp.camera_follow_rect(
            self.map.player_ref.position,
            self.map.player_ref.size,
            0.0,  # min distance
            0.0,  # speed
            0.0  # min speed
        )

        self.map.on_draw(dt)

        return NextScreen()

    def on_draw_ui(self, dt: float) -> NextScreen:
        key = self.btp.get_key_code()
        if key != 0:
            self.last_key = key

        self.stats["FPS"] = round(1/dt) if dt != 0 else 0
        self.stats["Key"] = self.last_key
        self.stats["View chunk"] = len(self.map.view_chunks)
        self.stats["View tile"] = self.map.view_tile_count

        self.stats.on_draw(Vec(), 20, BLACK)

        self.map.on_draw_ui(dt)

        self.hearts.update_hearts(self.map.player_ref.life)
        self.hearts.on_draw(dt)

        if self.btp.is_key_pressed(Keyboard.ENTER) or not self.map.player_ref.is_alive():
            return NextScreen(DungeonScreens.MENU)
        
        return NextScreen(DungeonScreens.GAME)
