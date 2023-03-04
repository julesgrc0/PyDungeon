from BTP.BTP import *
from core import *
from components.character import Character, CharacterPlugin
from utility import Keyboard


class CharacterControlPlugin(CharacterPlugin):

    def __init__(self, character: Character) -> None:
        super().__init__(character)
       

    def get_name(self) -> str:
        return "control"

    def on_update_control(self, dt: float, collision_tiles: list[ComponentObject]):
        speed = dt * 200
        move = Vec()

        if self.character.force_timer > 0:
            move += self.character.force * dt
            self.character.force_timer -= 100 * dt
            self.character.position += move
        else:
            if self.character.state == "hit":
                self.character.state = "idle"

            if self.character.btp.is_key_down(Keyboard.RIGHT):
                move.x += speed
                self.character.flip.x = 1
                self.character.state = "run"
            elif self.character.btp.is_key_down(Keyboard.LEFT):
                move.x -= speed
                self.character.flip.x = -1
                self.character.state = "run"
            elif self.character.state == "run":
                self.character.state = "idle"

            if self.character.btp.is_key_down(Keyboard.UP):
                move.y -= speed/2
            elif self.character.btp.is_key_down(Keyboard.DOWN):
                move.y += speed/2

            # if not move.is_zero():
            if self.character.can_move(move, collision_tiles):  # if collsion in
                if not move.is_zero():
                    self.character.position += move
                    self.character.inventory.inventory_open = False

            if self.character.btp.is_key_pressed(Keyboard.CTRL_L) and len(self.character.inventory) != 0:
                self.character.select_inventory()
