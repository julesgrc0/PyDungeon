import math
import time
from BTP.BTP import *
from functools import wraps

SCALE = 6
TILE_SIZE = 16 * SCALE


class Keyboard:
    LEFT = 263
    RIGHT = 262
    UP = 265
    DOWN = 264
    SPACE = 32
    CTRL_R = 345
    CTRL_L = 341
    ENTER = 257


BLACK = Color(20, 20, 20, 255)
WHITE = Color(250, 249, 246, 255)


def from_vec_str(s: str) -> Vec:
    cls = s.replace('Vec(x=', '').replace(')', '').replace('y=', '').split(';')
    return Vec(float(cls[0]), float(cls[1]))


def vec_floor(vec: Vec):
    return Vec(math.floor(vec.x), math.floor(vec.y))


def vec_ceil(vec: Vec):
    return Vec(math.ceil(vec.x), math.ceil(vec.y))


def vec_abs(vec: Vec):
    return Vec(abs(vec.x), abs(vec.y))


class Stats:

    def __init__(self, btp: Win) -> None:
        self.btp = btp
        self.data = {}

    def __setitem__(self, item, value):
        self.data[item] = value

    def on_draw(self, position: Vec, size: float, color: Color):
        text = ""
        for key, val in self.data.items():
            text += "{}: {}\n".format(key, val)
        self.btp.draw_text(text, position, size, color)
        self.data.clear()


def is_in_view(btp: Win, position: Vec, size: Vec):
    return btp.col_rect_rect(btp.camera_pos - btp.camera_offset, btp.get_render_size(), position, size)


def timedbg(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = round((end_time - start_time) * 1000, 2)

        print(f'{func.__name__} -> {total_time}ms')
        return result
    return timeit_wrapper
