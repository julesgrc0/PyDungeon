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

from textures import *
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
        file = [f.replace('.dat', '')
                for f in os.listdir(".") if f.endswith('.dat')]
        self.input_map.build(file[0] if len(
            file) > 0 else "", wt + position, margin, fontsize)

        position.y += 100
        self.btn_select.build("Load & Play", wt + position, margin, fontsize)

    def reset_input(self):
        self.input_map.build("", self.input_map.position,
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


class Game(Win):

    def __init__(self) -> None:
        super().__init__()
        self.atlas = ObjectsAtlas(self)

        self.menu = Menu(self)
        self.loading = Loading(self)
        self.stats = Stats(self)

        self.state = GameState.MENU

        self.index = 0
        self.last_key = 0

        self.map = Map(self, self.atlas)
        self.map_creator = MapCreator(self, self.atlas)

    def on_ready(self) -> None:
        self.atlas.on_ready()

        self.camera_follow_rect(
            Vec(),
            Vec(Chunk.TILE_SIZE),
            0.0, 0.0, 0.0
        )

        self.map_creator.on_ready()
        self.map.on_ready()

    def on_close(self) -> None:
        pass

    def on_draw_background(self, dt: float) -> None:
        pass

    def on_draw(self, dt: float) -> None:
        match self.state:
            case GameState.MAP_CREATOR:
                self.map_creator.on_draw(dt)
            case GameState.GAME:
                current_char: Character = self.atlas.characters[self.index]
                if self.is_key_pressed(Keyboard.SPACE):
                    pos = current_char.position

                    self.index += 1
                    if self.index >= len(self.atlas.characters):
                        self.index = 0

                    current_char = self.atlas.characters[self.index]
                    current_char.position = pos

                self.camera_follow_rect(
                    current_char.position,
                    current_char.size,
                    0.0, 0.0, 0.0
                )

                self.map.on_draw(dt)
                current_char.on_draw(dt)

    def on_draw_ui(self, dt: float) -> None:
        if self.is_loading():
            return

        match self.state:
            case GameState.MENU:
                self.state = self.menu.on_draw_ui(dt)
                if self.state == GameState.MAP_CREATOR:
                    self.map.stop_update_thread()

                    self.map_creator.clear_map()
                    self.map_creator.load_map(self.menu.get_selected_map())
                    self.map_creator.start_update_thread()
                    self.map_creator.force_update_view()

                elif self.state == GameState.GAME:
                    self.map_creator.stop_update_thread()

                    self.map.clear_map()
                    self.map.load_map(self.menu.get_selected_map())
                    self.map.start_update_thread()
                    self.map.force_update_view()

            case GameState.MAP_CREATOR:
                if self.map_creator.on_draw_ui(dt):
                    self.state = GameState.MENU
                return
            case GameState.GAME:
                key = self.get_key_code()
                if key != 0:
                    self.last_key = key

                self.stats["FPS"] = round(1/dt) if dt != 0 else 0
                self.stats["Key"] = self.last_key
                self.stats.on_draw(Vec(), 20, BLACK)

    def on_draw_loading(self, dt: float) -> None:
        self.loading.on_draw(dt)

    def on_load(self) -> None:
        self.atlas.load_animations()
        self.menu.on_load()
        # time.sleep(3)


def main(args):
    print(BTP.__doc__)
    Game().start(1680, 1050, "Demo - BTP v{}".format(BTP.__version__), False)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[:1]))
