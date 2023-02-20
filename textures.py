from utility import *
from BTP.BTP import *


class AnimatedTextures:

    def __init__(self, btp: Win, name) -> None:
        self.btp = btp
        self.name: str = name
        self.textures = []
        self.size = Vec()
        self.position = Vec()
        self.flip = Vec(1, 1)
        self.index = 0
        self.collision: bool = False

    def add_texture(self, name, image_id):
        self.textures.append(image_id)

    def on_draw(self, dt: float):
        frame = int(self.index) % len(self.textures)
        self.index += dt * 5

        self.btp.draw_image(
            self.textures[frame-1], self.position, self.size * self.flip, 0)

    def on_ready(self):
        if len(self.textures) >= 1:
            self.size = self.btp.get_image_size(self.textures[0]) * SCALE


class StaticTexture:

    def __init__(self, btp: Win, name) -> None:
        self.btp = btp
        self.name: str = name
        self.texture = -1
        self.size = Vec()
        self.position = Vec()
        self.flip = Vec(1, 1)
        self.collision: bool = False

    def set_texture(self, image_id):
        self.texture = image_id

    def on_draw(self, dt: float):
        self.btp.draw_image(self.texture, self.position,
                            self.size * self.flip, 0)

    def on_ready(self):
        self.size = self.btp.get_image_size(self.texture) * SCALE


def texture_check_name(name: str, cls):
    return name.startswith(cls.__name__.lower())


def texture_get_name(name: str, cls):
    return name.replace(cls.__name__.lower() + '_', "")


def set_animation_object(btp, obj: AnimatedTextures, name, image_id, obj_list: list[AnimatedTextures], check=texture_check_name, get=texture_get_name):
    if not check(name, obj):
        return False

    cname = get(name, obj)
    for char in obj_list:
        if char.name == cname:
            char.add_texture(name, image_id)
            return True

    char = obj(btp, cname)
    char.add_texture(name, image_id)
    obj_list.append(char)
    return True


def set_texture_object(btp, obj: StaticTexture, name, image_id, obj_list: list[StaticTexture], check=texture_check_name, get=texture_get_name):
    if not check(name, obj):
        return False

    wp = obj(btp, get(name, obj))
    wp.set_texture(image_id)
    obj_list.append(wp)
    return True


def trigger_ready_event(array: list[StaticTexture | AnimatedTextures]):
    for t in array:
        t.on_ready()
