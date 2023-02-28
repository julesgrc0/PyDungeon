from core import *
from components import *

from utility import BLACK, WHITE

class Loading(Screen):

    def __init__(self, btp: Win, atlas: ObjectBaseAtlas) -> None:
        super().__init__(btp, atlas)
        self.loading = 0

    def center_text(self, text: str, size: int):
        tsize = self.btp.text_size(text, size)
        return (self.btp.get_render_size() - tsize)/2, tsize

    def on_draw_error(self, error: str):
        self.btp.draw_rect(Vec(), self.btp.get_render_size(), WHITE)

        pos_err, size_err = self.center_text(error, 40)
        pos_err.y -= 50
        self.btp.draw_text(error, pos_err, 40, BLACK)

        info = "Please restart your game, or update it!"
        pos_inf, size_inf = self.center_text(info, 20)
        pos_inf.y += 30
        self.btp.draw_text(info, pos_inf, 20, BLACK)

        self.btp.draw_line(pos_err + Vec(0, 60), pos_err +
                           Vec(size_err.x, 60), BLACK)
        
        return NextScreen()

    def on_draw(self, dt) -> NextScreen:
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

        return NextScreen()
