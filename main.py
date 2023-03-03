from BTP.BTP import *
import BTP.BTP

import os
import sys

from core import *
from components import *
from utility import *
from map import *

from screens import *


class Dungeon(Win):
    ASSETS_DIR = "./assets/"

    def __init__(self) -> None:
        super().__init__()
        print(BTP.BTP.__doc__)

        self.texture_atlas = TextureAtlas()
        self.objects_atlas = ObjectBaseAtlas()
        self.object_base: list[ComponentObject] = [
            Character,
            Doors,
            Floor,
            Wall,
            Coin,
            Chest,
            SingleItem,
            Flask,
            Weapon,
            Hearts
        ]

        self.loading = Loading(self, self.objects_atlas)
        self.menu = Menu(self, self.objects_atlas)
        self.game = Game(self, self.objects_atlas)
        self.map_creator = MapCreator(self, self.objects_atlas)

        self.state = DungeonScreens.MENU
        self.no_assets = False

    def on_ready(self) -> None:
        if self.no_assets:
            return

        for obj in self.objects_atlas.objects:
            if isinstance(obj, ComponentObject):
                obj.on_ready(self)
                obj.accepted_actions = DungeonActionTypes.all()

        self.camera_follow_rect(
            Vec(),
            Vec(TILE_SIZE),
            0.0, 0.0, 0.0
        )

        self.map_creator.on_ready()
        self.game.on_ready()

    def on_close(self) -> None:
        pass

    def on_draw_background(self, dt: float) -> None:
        pass

    def on_draw(self, dt: float) -> None:
        match self.state:
            case DungeonScreens.MAP_CREATOR:
                self.map_creator.on_draw(dt)
            case DungeonScreens.GAME:
                self.game.on_draw(dt)

    def on_draw_ui(self, dt: float) -> None:
        if self.is_loading():
            return

        if self.no_assets:
            self.loading.on_draw_error("Assets not found")
            return
        
        match self.state:
            case DungeonScreens.MENU:
                self.state = self.menu.on_draw_ui(dt).name
                if self.state == DungeonScreens.MAP_CREATOR:
                    self.game.close_game()

                    self.map_creator.clear_map()
                    self.map_creator.load_map(self.menu.get_selected_map())
                    self.map_creator.start_update_thread()
                    self.map_creator.force_update_view()

                elif self.state == DungeonScreens.GAME:
                    self.map_creator.stop_update_thread()
                    self.game.new_game(self.menu.get_selected_map())

            case DungeonScreens.MAP_CREATOR:
                self.state = self.map_creator.on_draw_ui(dt).name
                if self.state == DungeonScreens.MENU:
                    self.menu.reset_input(self.menu.get_first_map())
            case DungeonScreens.GAME:
                self.state = self.game.on_draw_ui(dt).name
                if self.state == DungeonScreens.MENU:
                    self.menu.reset_input(self.menu.get_first_map())


    def on_draw_loading(self, dt: float) -> None:
        self.loading.on_draw(dt)

    def on_load(self) -> None:
        if not os.path.exists(Dungeon.ASSETS_DIR):
            self.no_assets = True
            return

        files = os.listdir(Dungeon.ASSETS_DIR)
        for filename in files:
            texture_path = os.path.abspath(Dungeon.ASSETS_DIR + filename)
            texture_id = self.load_image(texture_path)

            self.texture_atlas.add(filename, texture_id)

        for type in self.object_base:
            self.objects_atlas.register(type)

        for texture in self.texture_atlas.textures:
            self.objects_atlas.add(texture)

        self.menu.on_load()

        # time.sleep(3)


def main(args):
    size = (0,0)
    fullscreen = True
    if "--debug" in args:
        size = (1280,960)
        fullscreen = False

    Dungeon().start(*size, "Dungeon - BTP v{} | {}".format(BTP.BTP.__version__,BTP.BTP.__libvers__), fullscreen)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
