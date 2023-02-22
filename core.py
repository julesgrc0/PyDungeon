from BTP.BTP import *
from typing import Any, Protocol, Self, runtime_checkable
import copy

from utility import SCALE, timedbg


class Texture:
    def __init__(self) -> None:
        self.texture: int
        self.name: str


class AnimatedTexture:
    def __init__(self) -> None:
        self.textures: list[int]
        self.textures_names: list[str]
        self.name: str


class TextureAtlas:

    def __init__(self) -> None:
        self.textures: list[Texture | AnimatedTexture] = []

    def add(self, filename: str, texture_id: int):
        parts = filename.split('_')

        if len(parts) >= 3 and parts[-1].startswith('f') and parts[-2].lower() == 'anim':
            name = "_".join(parts[:-2])
            for texture in self.textures:
                if texture.name == name:
                    texture.textures.append(texture_id)
                    texture.textures_names.append(filename)
                    break
            else:
                texture = AnimatedTexture()
                texture.name = name
                texture.textures = [texture_id]
                texture.textures_names = [filename]
                self.textures.append(texture)
            return

        name = filename.replace('.png', "")
        texture = Texture()
        texture.name = name
        texture.texture = texture_id
        self.textures.append(texture)


def is_animated(texture: Texture | AnimatedTexture):
    return isinstance(texture, AnimatedTexture) and hasattr(texture, 'textures')


def to_animated(texture: Texture | AnimatedTexture):
    if is_animated(texture):
        return texture
    else:
        animated = AnimatedTexture()
        animated.name = texture.name
        animated.textures_names = [texture.name]
        animated.textures = [texture.texture]
        return animated


class ObjectBase:

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        self.texture: Texture | AnimatedTexture = texture
        self.name: str = self.texture.name

        self.position: Vec = Vec()
        self.size: Vec = Vec()
        self.flip: Vec = Vec(1)

        self.animation_speed: float = 10.0
        self.animation_index: float = 0.0

        self.collision: bool = False

    @staticmethod
    def is_grouped() -> bool:
        return False

    @staticmethod
    def get_group_name(name: str) -> str:
        return name

    @staticmethod
    def check_name(name: str) -> bool:
        return True


class ObjectBaseAtlas:

    def __init__(self) -> None:
        self.types: list[ObjectBase] = []
        self.objects: list[ObjectBase] = []

    def register(self, object: ObjectBase):
        self.types.append(object)

    def __add_single(self, type: ObjectBase, texture: AnimatedTexture | Texture, grpname: str) -> ObjectBase:
        animated = to_animated(texture)
        for obj in self.objects:
            if isinstance(obj, type) and obj.name == grpname:
                obj.texture.textures_names += animated.textures_names
                obj.texture.textures += animated.textures
                return obj
        else:
            obj = type(animated)
            self.objects.append(obj)
            return obj

    def add(self, texture: AnimatedTexture | Texture) -> ObjectBase:
        ref = None
        for type in self.types:
            if type.check_name(texture.name):
                if type.is_grouped():
                    ref = self.__add_single(
                        type, texture, type.get_group_name(texture.name))
                else:
                    ref = type(texture)
                    self.objects.append(ref)
                break
        else:
            ref = ObjectBase(texture)
            self.objects.append(ref)
        return ref

    def copy(self, classbase, name) -> None | ObjectBase:
        for obj in self.objects:
            if isinstance(obj, classbase) and obj.name == name:
                return copy.copy(obj)
        return None

    def from_instance(self, classbase) -> list[Any]:
        return [obj for obj in self.objects if isinstance(obj, classbase)]


@runtime_checkable
class Component(Protocol):

    def on_draw(self, dt: float) -> None: ...

    def on_ready(self, btp: Win) -> None: ...


class ComponentObject(ObjectBase, Component):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
        self.btp: Win | None = None

    def get_frame(self, dt: float) -> int:
        if not is_animated(self.texture):
            return self.texture.texture

        if len(self.texture.textures) <= 0:
            return

        frame = int(self.animation_index) % len(self.texture.textures)
        self.animation_index += dt * self.animation_speed

        return self.texture.textures[frame - 1]

    def on_draw(self, dt: float) -> None:
        self.btp.draw_image(self.get_frame(
            dt), self.position, self.size * self.flip, 0)

    def on_ready(self, btp: Win) -> None:
        self.btp = btp
        self.size = self.btp.get_image_size(self.texture.textures[0] if is_animated(
            self.texture) else self.texture.texture) * SCALE
