from textures import *
from utility import *

from BTP.BTP import *
import os

class ObjectsAtlas:
    ASSETS_DIR = "./assets/"

    def __init__(self, btp: Win) -> None:
        self.btp = btp

        self.characters: list[Character] = []
        self.weapons: list[Weapon] = []
        self.walls: list[Wall] = []
        self.floors: list[Floor] = []
        self.doors: list[Doors] = []
        self.chests: list[Chest] = []
        self.flasks: list[Flask] = []
        self.coins: list[Coin] = []
        self.columns: list[Column] = []
        self.single_items: list[SingleItem] = []
        self.ui: list[UI] = []

        self.animations = {}
        self.textures = {}

    def search(self, array: list[StaticTexture | AnimatedTextures], name: str):
        for it in array:
            if it.name == name:
                return it
        return None

    
    def on_ready(self):
        trigger_ready_event(self.weapons)
        trigger_ready_event(self.walls)
        trigger_ready_event(self.floors)
        trigger_ready_event(self.doors)
        trigger_ready_event(self.chests)
        trigger_ready_event(self.flasks)
        trigger_ready_event(self.characters)
        trigger_ready_event(self.columns)
        trigger_ready_event(self.single_items)
        trigger_ready_event(self.coins)
        trigger_ready_event(self.ui)



    def load_animations(self):
        files = os.listdir(ObjectsAtlas.ASSETS_DIR)
    
        for file in files:
            parts = file.split('_')
            full_path = os.path.abspath(ObjectsAtlas.ASSETS_DIR+file)

            image_id = self.btp.load_image(full_path)
            if len(parts) >= 3 and parts[-1].startswith('f') and parts[-2] == 'anim':
                name = "_".join(parts[:-2])
                
                char = set_animation_object(self.btp, Character, name, image_id, self.characters, Character.check_name, Character.get_name)
                wall = set_animation_object(self.btp, Wall, name, image_id, self.walls)
                ches = set_animation_object(self.btp, Chest, name, image_id, self.chests)
                floo = set_animation_object(self.btp, Floor, name, image_id, self.floors)
                coin = set_animation_object(self.btp, Coin, name, image_id, self.coins)

                if not char and not wall and not ches and not floo and not coin:
                    if self.animations.get(name) is None:
                        self.animations[name] = []
                    self.animations[name].append(image_id)
            else:
                name = file.replace('.png', "")

                wall = set_animation_object(self.btp, Wall, name, image_id, self.walls)
                floo = set_animation_object(self.btp, Floor, name, image_id, self.floors)

                colm = set_texture_object(self.btp, Column, name, image_id, self.columns)
                sing = set_texture_object(self.btp, SingleItem, name, image_id, self.single_items, SingleItem.check_name, SingleItem.get_name)
                weap = set_texture_object(self.btp, Weapon, name, image_id, self.weapons)
                door = set_texture_object(self.btp, Doors, name, image_id, self.doors)
                flas = set_texture_object(self.btp, Flask, name, image_id, self.flasks)
                uii = set_texture_object(self.btp, UI, name, image_id, self.ui)
                
                if not weap and not wall and not floo and not door and not flas and not sing and not colm and not uii:
                    self.textures[name] = image_id
        
        # print(self.textures)
        # print(self.animations)


#  character

class Character(AnimatedTextures):

    @staticmethod
    def check_name(name: str, obj):
        return name.endswith('idle') or name.endswith('run') or name.endswith('hit')

    @staticmethod
    def get_name(name, obj):
        return name.replace('_idle',"").replace('_run',"").replace('_hit', "")

    def __init__(self, btp: Win, name) -> None:
        super().__init__(btp, name)

        self.hit = []
        self.run = []
        self.idle = []

        self.state = "idle"
        self.factorx = 1

        self.last_move: Vec = Vec()


    def add_texture(self, name, image_id):
        last = name.split('_')[-1]

        if last == "hit":
            self.hit = [image_id]
        elif last == "idle":
            self.idle.append(image_id)
        elif last == "run":
            self.run.append(image_id)
        
    def get_frame(self, dt: float):
        frames = getattr(self, self.state)
        frame = int(self.index)%len(frames)
        self.index += dt * 8
        return frames[frame-1]
    
    def oposite_move(self):
        self.position -= self.last_move
        self.last_move = Vec()

    def on_draw(self, dt: float):
        speed = dt * 200        
        move = Vec()

        if self.btp.is_key_down(Keyboard.RIGHT):
            move.x += speed
            self.factorx = 1
            self.state = "run"
        elif self.btp.is_key_down(Keyboard.LEFT):
            move.x -= speed
            self.factorx = -1
            self.state = "run"
        elif self.state == "run":
            self.state = "idle"

        frame = self.get_frame(dt)
            
        if self.btp.is_key_down(Keyboard.UP):
            move.y -= speed/2
        elif self.btp.is_key_down(Keyboard.DOWN):
            move.y += speed/2

        if not move.is_zero():
            self.position += move
            self.last_move = move
            
        self.btp.draw_image(frame,self.position, self.size * Vec(self.factorx, 1), 0)

    def on_ready(self):
        self.size = self.btp.get_image_size(self.run[0]) * SCALE


#  map objects

class Wall(AnimatedTextures):

    def __init__(self, btp, name) -> None:
        super().__init__(btp, name)

class Floor(AnimatedTextures):

    def __init__(self, btp, name) -> None:
        super().__init__(btp, name)

class Column(StaticTexture):

    def __init__(self, btp: Win, name) -> None:
        super().__init__(btp, name)


# map objects -> size

class Doors(StaticTexture):
    
    def __init__(self, btp, name) -> None:
        super().__init__(btp, name)  
    
class Chest(AnimatedTextures):

    def __init__(self, btp, name) -> None:
        super().__init__(btp, name)


# items

class SingleItem(StaticTexture):

    @staticmethod
    def check_name(name: str, obj):
        return name == 'skull' or name == 'crate' or name == 'hole'

    @staticmethod
    def get_name(name, obj):
        return name

    def __init__(self, btp: Win, name) -> None:
        super().__init__(btp, name)

class Coin(AnimatedTextures):

    def __init__(self, btp: Win, name) -> None:
        super().__init__(btp, name)

class Flask(StaticTexture):

    def __init__(self, btp, name) -> None:
        super().__init__(btp, name)
       
class Weapon(StaticTexture):

    def __init__(self, btp, name) -> None:
        super().__init__(btp, name)  


# ui

class UI(StaticTexture):

    def __init__(self, btp: Win, name) -> None:
        super().__init__(btp, name)