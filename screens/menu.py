from core import *
from components import *

import os
from utility import BLACK, WHITE, DungeonScreens
from BTP.gui import Button, Input

class Menu(Screen):
    

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        super().__init__(btp, atlas)

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

    def on_draw_ui(self, dt: float) -> NextScreen:
        state = DungeonScreens.MENU
        self.btp.draw_rect(Vec(), self.btp.get_render_size(), WHITE)

        bgalpha = 0 if self.btn_mapcr.is_hover() else 20
        if self.btn_mapcr.draw(BLACK, Color(0, 0, 0, bgalpha)):
            if os.path.exists(self.selected_map+".dat"):
                self.last_selected = self.selected_map
                self.reset_input()
            state = DungeonScreens.MAP_CREATOR

        bgalpha = 0 if self.btn_select.is_hover() else 20
        if self.btn_select.draw(BLACK, Color(0, 0, 0, bgalpha)):
            if os.path.exists(self.selected_map+".dat"):
                self.last_selected = self.selected_map
                state = DungeonScreens.GAME

            self.reset_input()

        self.selected_map = self.input_map.draw(BLACK)
        self.btp.draw_text(".dat", self.input_map.position + Vec(self.input_map.button.size.x +
                           20, self.input_map.button.size.y/2), self.input_map.button.text.fontsize, BLACK)

        self.btp.draw_rect(self.btn_mapcr.position -
                           self.btn_mapcr.margin, Vec(5, 280), BLACK)

        return NextScreen(state)

    def get_selected_map(self):
        return self.last_selected
