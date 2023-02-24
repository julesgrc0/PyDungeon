from typing import Self
from BTP.BTP import Color, Vec, Win

from dataclasses import dataclass, field
from functools import wraps

import math
import time


SCALE = 6
TILE_SIZE = 16 * SCALE


class DemoActionTypes:
    COLLISION = "collision"
    COLLISION_IN = "collision_in"
    AROUND = "around"
    COLLECT = "collect"

    @staticmethod
    def all():
        return [DemoActionTypes.COLLISION, DemoActionTypes.COLLISION_IN, DemoActionTypes.AROUND, DemoActionTypes.COLLECT]


class DemoRoleTypes:
    NONE = "none"
    PLAYER = "player"
    MONSTER = "monster"

@dataclass
class DemoActionData:
    role: DemoRoleTypes = field(default=DemoRoleTypes.NONE)


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


def draw_key_interract(btp: Win, key: str, position: Vec):
    tsize = btp.text_size(key, 20)
    size = tsize + Vec(10)
    btp.draw_rectround(position, size, 0.1, BLACK)

    center = (size-tsize)/2
    btp.draw_text(key, position + center, 20, WHITE)


def rotate_around(pos: Vec, origin: Vec,  deg: float) -> Vec:
    theta = (deg*math.pi)/180

    newx = math.cos(theta) * (pos.x-origin.x) - \
        math.sin(theta) * (pos.y-origin.y) + origin.x
    newy = math.sin(theta) * (pos.x-origin.x) + \
        math.cos(theta) * (pos.y-origin.y) + origin.y

    return Vec(newx, newy)


def rect_rect_distance(p1: Vec, s1: Vec, p2: Vec, s2: Vec):
    dx = max(p1.x, p2.x) - min(p1.x + s1.x, p2.x + s2.x)
    dy = max(p1.y, p2.y) - min(p1.y + s1.y, p2.y + s2.y)

    return math.sqrt(dx**2 + dy**2)


def rect_rect_center(p1: Vec, s1: Vec, p2: Vec, s2: Vec):
    center1 = Vec(p1.x + s1.x/2, p1.y + s1.y/2)
    center2 = Vec(p2.x + s2.x/2, p2.y + s2.y/2)
    return Vec(center2.x - center1.x, center2.y - center1.y)


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
