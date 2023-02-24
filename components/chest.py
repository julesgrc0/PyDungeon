import random
from core import *
from utility import DemoActionData, DemoActionTypes, DemoRoleTypes, Keyboard, draw_key_interract

class Chest(Tileset):

    def __init__(self, texture: Texture | AnimatedTexture) -> None:
        super().__init__(texture)
        self.state = "closed"
        self.animation_speed = 4

        self.valid = is_animated(self.texture) and len(self.texture.textures) >= 2
        self.collect = False
        self.interact = 0

        self.player_ref: ComponentObject | None = None

    @staticmethod
    def check_name(name: str) -> bool:
        return name.startswith('chest')

    def on_ready(self, btp: Win) -> None:
        super().on_ready(btp)


    def on_action(self, action: ActionEvent) -> Any:
        if self.state != "closed":
            return
        
        if action.name == DemoActionTypes.AROUND and isinstance(action.data, DemoActionData):
            if action.data.role == DemoRoleTypes.PLAYER:
                self.interact = 20
                self.player_ref = action.object
        
        
    def get_frame(self, dt: float) -> int:
        if not self.valid:
            return
        
        match self.state:
            case "closed":
                return self.texture.textures[0]
            case "animation":
                if self.accept_action(DemoActionTypes.AROUND):
                    self.accepted_actions.remove(DemoActionTypes.AROUND)

                frame = super().get_frame(dt)
                if int(self.animation_index)%len(self.texture.textures) == 0:
                    self.state = "opened"
                return frame
            case "opened":
                return self.texture.textures[-1]
            
    def get_items(self, atlas: ObjectBaseAtlas) -> list[CollectableItem]:
        if self.collect:
            return []
        
        self.collect = True
        collectable = atlas.from_instance(CollectableItem)
        items = []
    
        for i in range(random.randint(1, 6)):
            item: CollectableItem = random.choice(collectable)
            items.append(item.copy())

        return items
        

    def on_draw(self, dt: float) -> None:
        super().on_draw(dt)

        if self.state != "closed":
            return
        
        self.interact -= 100 * dt
        if self.interact <= 0:
            return
        
        draw_key_interract(self.btp, "CTRL-R", self.position)
        if self.btp.is_key_pressed(Keyboard.CTRL_R):
            self.state = "animation"
            self.animation_index = 1
            if self.player_ref is not None:
                self.player_ref.on_action(ActionEvent.create(DemoActionTypes.COLLECT, self, DemoActionData()))
        


