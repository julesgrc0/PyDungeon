from BTP.BTP import *

class Input:
    
    DELETE = 259

    KEYS = {
    32 : " ",
    81 : "a",
    66 : "b",
    67 : "c",
    68 : "d",
    69 : "e",
    70 : "f",
    71 : "g",
    72 : "h",
    73 : "i",
    74 : "j",
    75 : "k",
    76 : "l",
    59 : "m",
    78 : "n",
    79 : "o",
    80 : "p",
    65 : "q",
    82 : "r",
    83 : "s",
    84 : "t",
    85 : "u",
    86 : "v",
    90 : "w",
    88 : "x",
    89 : "y",
    87 : "z",
    48 : "0",
    49 : "1",
    50 : "2",
    51 : "3",
    52 : "4",
    53 : "5",
    54 : "6",
    55 : "7",
    56 : "8",
    57 : "9",
    }

    def __init__(self, btp) -> None:
        self.btp = btp
        self.button = Button(self.btp)
        self.focus = False
        self.position = Vec()
        self.margin = Vec()

    def build(self, text, position, margin, fontsize = 20):
        self.position = position
        self.margin = margin
        self.button.build(text, position, margin, fontsize)

    def draw(self, fg_color):
        self.button.draw(fg_color, Color(0,0,0,0))

        if self.btp.is_mouse_down():
            self.focus = self.button.is_hover()
        
        if self.focus:
            key = self.btp.get_key_code()
            
            if key == Input.DELETE:
                self.button.build(self.button.text.text[:-1], self.position, self.margin, self.button.text.fontsize)
            elif key != 0:
                char = Input.KEYS.get(key, None)
                if char is not None:
                    self.button.build(self.button.text.text + char, self.position, self.margin, self.button.text.fontsize)
            self.btp.draw_line(
                self.button.text.position + Vec(self.button.text.size.x, 0),
                self.button.text.position + self.button.text.size, fg_color)

        return self.button.text.text

class Text:

    def __init__(self,btp) -> None:
        self.btp = btp

        self.text = ""
        self.fontsize = 0
        self.position = Vec()
        self.size = Vec()

    def build(self, text, fontsize, position, center = (0, 0)):
        self.text = text
        self.fontsize = fontsize

        self.size = self.btp.text_size(self.text, self.fontsize)
        
        self.position.x = position.x + ((self.size.x/2) * center[0])
        self.position.y = position.y + ((self.size.y/2) * center[1])


    def draw(self, color):
        if self.fontsize != 0:
            self.btp.draw_text(self.text, self.position, self.fontsize, color)

class Button:

    def __init__(self, btp) -> None:
        self.btp = btp
        self.text = Text(btp)

        self.margin = Vec()
        self.position = Vec()
        self.size = Vec()

        self.active = False

    def build(self, text, position, margin, fontsize= 20):
        self.position = position
        self.margin = margin
        self.text.build(text, fontsize, position + margin, (0,0))
        self.size = self.text.size + margin*2
        
    def is_hover(self):
        return self.btp.col_rect_point(self.position, self.size, self.btp.mouse)
    
    def draw(self, fg_color, bg_color):
        self.btp.draw_rect(self.position, self.size, bg_color)
        self.btp.draw_rectline(self.position, self.size, fg_color)
        self.text.draw(fg_color)

        if self.active and self.btp.is_mouse_up() and self.is_hover():
            self.active = False
            return True
        
        self.active = self.is_hover() and self.btp.is_mouse_down()
        return False

class Select:

    def __init__(self, btp) -> None:
        self.btp = btp
        self.button = Button(btp)
        self.options = []
        self.toggle = False

    def build(self, text,options, position, margin):
        self.button.build(text + " >", position, margin)
        self.options.clear()

        i = 1.5
        for opt in options:
            btn = Button(self.btp)
            btn.build(opt, self.button.position + Vec(self.button.margin.x, self.button.size.y * i), self.button.margin)
            self.options.append(btn)
            i += 1


    def draw(self, fg_color, bg_color):
        if self.button.draw(fg_color, bg_color):
            self.toggle = not self.toggle

        clicked = None
        if self.toggle:
            for opt in self.options:
                bg = Color(0,0,0,0)
                if opt.is_hover():
                    bg = bg_color

                if opt.draw(fg_color, bg):
                    clicked = opt.text.text
                    self.toggle = False
    
        return clicked
                

class TestGui(Win):

    def __init__(self) -> None:
        super().__init__()
        self.button = Button(self)  
        self.text = Text(self)
        self.input = Input(self)
        self.select = Select(self)
        

    def on_draw(self, arg0: float) -> None:

        btn_colors = Color(255,255,255,255), Color(50,50,50,255)
        if self.button.is_hover():
            btn_colors = Color(200,200,200,255), Color(100,100,100,255)

        if self.button.draw(*btn_colors):
            print("clicked")

        self.text.draw(Color(255,255,255,255))
        text = self.input.draw(Color(255,255,255,255))
        if len(text) >= 2:
            print(text)

        selected = self.select.draw(Color(255,255,255,255), Color(50,50,50,255))
        if selected is not None:
            print(selected)

    def on_draw_ui(self, dt: float) -> None:
        pass

    def on_draw_background(self, dt: float) -> None:
        pass

    def on_draw_loading(self, dt: float) -> None:
        pass

    def on_load(self) -> None:

        self.button.build("button", Vec(100, 50), Vec(20, 10))
        self.text.build("text", 20, Vec(100, 100))
        self.input.build("", Vec(100, 150), Vec(20, 10))
        self.select.build("select", ["options 1", "options 2", "options 3"], Vec(100, 200), Vec(20, 10))

if __name__ == "__main__":
    TestGui().start(500, 500, "BTP - GUI Test", False)