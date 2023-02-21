from BTP.BTP import *
from BTP import BTP

from BTP.gui import *
from BTP.util import *

import os
import re
import sys
import random
import math
import time
import threading

from core import *
from objects import *
from utility import *
from map import *


class GameState:
    NONE = -1
    MENU = 0
    GAME = 1
    MAP_CREATOR = 2


class Loading:

    def __init__(self, btp: Win) -> None:
        self.btp = btp
        self.loading = 0

    def on_draw(self, dt):
        self.btp.draw_rect(Vec(), self.btp.get_render_size(), WHITE)

        text = "Loading textures..."
        tsize = self.btp.text_size(text, 40)
        pos = (self.btp.get_render_size() - tsize)/2
        pos.y -= 20

        self.btp.draw_text(text, pos, 40, BLACK)
        self.btp.draw_rect(Vec(pos.x, pos.y + 60),
                           Vec(tsize.x * (self.loading/100), 20), BLACK)

        self.loading += dt * 30
        if self.loading >= 100:
            self.loading = 0


class Menu:
    def __init__(self, btp: Win) -> None:
        self.btp = btp

        self.btn_mapcr = Button(self.btp)
        self.btn_select = Button(self.btp)
        self.input_map = Input(self.btp)
        self.selected_map = ""
        self.last_selected = ""

    def on_load(self):
        margin = Vec(40, 10)
        fontsize = 30

        position = Vec(0, -100)
        wt = (self.btp.get_render_size() -
              (self.btp.text_size("Map creator", fontsize) + margin*2))/2

        self.btn_mapcr.build("Map creator", wt + position, margin, fontsize)

        position.y += 100
        self.input_map.build(self.get_first_map(), wt +
                             position, margin, fontsize)

        position.y += 100
        self.btn_select.build("Load & Play", wt + position, margin, fontsize)

    def get_first_map(self):
        file = [f.replace('.dat', '')
                for f in os.listdir(".") if f.endswith('.dat')]
        return file[0] if len(file) > 0 else ""

    def reset_input(self, text=""):
        self.input_map.build(text, self.input_map.position,
                             self.input_map.margin, self.input_map.button.text.fontsize)

    def on_draw_ui(self, dt: float) -> GameState:
        state = GameState.MENU
        self.btp.draw_rect(Vec(), self.btp.get_render_size(), WHITE)

        bgalpha = 0 if self.btn_mapcr.is_hover() else 20
        if self.btn_mapcr.draw(BLACK, Color(0, 0, 0, bgalpha)):
            if os.path.exists(self.selected_map+".dat"):
                self.last_selected = self.selected_map
                self.reset_input()
            state = GameState.MAP_CREATOR

        bgalpha = 0 if self.btn_select.is_hover() else 20
        if self.btn_select.draw(BLACK, Color(0, 0, 0, bgalpha)):
            if os.path.exists(self.selected_map+".dat"):
                self.last_selected = self.selected_map
                state = GameState.GAME

            self.reset_input()

        self.selected_map = self.input_map.draw(BLACK)
        self.btp.draw_text(".dat", self.input_map.position + Vec(self.input_map.button.size.x +
                           20, self.input_map.button.size.y/2), self.input_map.button.text.fontsize, BLACK)

        self.btp.draw_rect(self.btn_mapcr.position -
                           self.btn_mapcr.margin, Vec(5, 280), BLACK)

        return state

    def get_selected_map(self):
        return self.last_selected


class Game:

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        self.btp = btp
        self.last_key = 0
        self.index = 0

        self.atlas = atlas
        self.stats = Stats(self.btp)
        self.map = Map(self.btp, self.atlas)

        self.character: Character

    def close_game(self):
        self.map.stop_update_thread()

    def new_game(self, name):
        self.map.clear_map()
        self.map.load_map(name)
        self.map.start_update_thread()
        self.map.force_update_view()

    def on_ready(self):
        self.map.on_ready()

        characters = self.atlas.from_instance(Character)
        self.character = self.atlas.copy(
            Character, random.choice(characters).name)

    def on_draw(self, dt: float):

        self.btp.camera_follow_rect(
            self.character.position,
            self.character.size,
            0.0, 0.0, 0.0
        )

        self.map.on_draw(dt)

        self.character.on_update_control(dt, self.map.get_collision_rects())
        self.character.on_draw(dt)

    def on_draw_ui(self, dt: float) -> bool:
        key = self.btp.get_key_code()
        if key != 0:
            self.last_key = key

        self.stats["FPS"] = round(1/dt) if dt != 0 else 0
        self.stats["Key"] = self.last_key
        self.stats.on_draw(Vec(), 20, BLACK)

        return self.btp.is_key_pressed(Keyboard.ENTER)


class Demo(Win):
    ASSETS_DIR = "./assets/"

    def __init__(self) -> None:
        super().__init__()
        print(BTP.__doc__)

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
            UI
        ]

        self.loading = Loading(self)
        self.menu = Menu(self)
        self.game = Game(self, self.objects_atlas)
        self.map_creator = MapCreator(self, self.objects_atlas)

        self.state = GameState.MENU

    def on_ready(self) -> None:
        for obj in self.objects_atlas.objects:
            if isinstance(obj, ComponentObject):
                obj.on_ready(self)

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
            case GameState.MAP_CREATOR:
                self.map_creator.on_draw(dt)
            case GameState.GAME:
                self.game.on_draw(dt)

    def on_draw_ui(self, dt: float) -> None:
        if self.is_loading():
            return

        match self.state:
            case GameState.MENU:
                self.state = self.menu.on_draw_ui(dt)
                if self.state == GameState.MAP_CREATOR:
                    self.game.close_game()

                    self.map_creator.clear_map()
                    self.map_creator.load_map(self.menu.get_selected_map())
                    self.map_creator.start_update_thread()
                    self.map_creator.force_update_view()

                elif self.state == GameState.GAME:
                    self.map_creator.stop_update_thread()
                    self.game.new_game(self.menu.get_selected_map())

            case GameState.MAP_CREATOR:
                if self.map_creator.on_draw_ui(dt):
                    self.state = GameState.MENU
                    self.menu.reset_input(self.menu.get_first_map())
            case GameState.GAME:
                if self.game.on_draw_ui(dt):
                    self.state = GameState.MENU
                    self.menu.reset_input(self.menu.get_first_map())

    def on_draw_loading(self, dt: float) -> None:
        self.loading.on_draw(dt)

    def on_load(self) -> None:
        try:
            files = os.listdir(Demo.ASSETS_DIR)
            for filename in files:
                texture_path = os.path.abspath(Demo.ASSETS_DIR + filename)
                texture_id = self.load_image(texture_path)

                self.texture_atlas.add(filename, texture_id)

            for type in self.object_base:
                self.objects_atlas.register(type)

            for texture in self.texture_atlas.textures:
                self.objects_atlas.add(texture)

            self.menu.on_load()
        except Exception as e:
            print(e)
        # time.sleep(3)


def main(args):
    Demo().start(1680, 1050, "Demo - BTP v{}".format(BTP.__version__), False)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[:1]))
