import sys, os, inspect, importlib
from BTP.BTP import *
import BTP.BTP

class Game(Win):

    def __init__(self) -> None:
        super().__init__()

    def on_draw(self, dt: float) -> None:
        Game.draw_game(self, dt)
    
    def on_draw_background(self, dt: float) -> None:
        Game.draw_background(self, dt)
    
    def on_draw_loading(self, dt: float) -> None:
        Game.draw_loading(self, dt)
    
    def on_draw_ui(self, dt: float) -> None:
        Game.draw_ui(self, dt)
    
    def on_load(self) -> None:
        Game.loading_game(self)
    
    @staticmethod
    def draw_game(game, dt: float):
        pass
    
    @staticmethod
    def draw_ui(game, dt: float):
        pass
    
    @staticmethod
    def draw_background(game, dt: float):
        pass
    
    @staticmethod
    def draw_loading(game, dt: float):
        pass

    @staticmethod
    def loading_game(game):
        pass

def set_function(func, mod2, name, check):
    mod_func = getattr(mod2, name, None)
    if mod_func is not None and callable(mod_func) and check(mod_func):
        return mod_func
    return func

def get_constante(module, name, els):
    return  getattr(module, name, els)

def main(args):
    if len(args) <= 0:
        print("[ERROR] No Module provided")
        return 1
    
    module_path = os.path.abspath(args[0])
    if not os.path.exists(module_path) or not module_path.endswith('.py'):
        print("[ERROR] Module not found")
        return 1
    module = None
    try:
        module_name = os.path.basename(module_path).replace('.py', "")
        module = importlib.import_module(module_name)
    except Exception as e:
        print("[ERROR] {}".format(e.with_traceback(e.__traceback__)))
        return 1
    
    if module is None:
        print("[ERROR] Can't load module")
        return 1
    
    has_2_args = lambda x: len(inspect.getfullargspec(x)[0]) == 2
    has_1_arg = lambda x: len(inspect.getfullargspec(x)[0]) == 1

    game = Game()
    
    Game.draw_game = set_function(Game.draw_game, module, 'draw', has_2_args)
    Game.draw_background = set_function(Game.draw_background, module, 'draw_background', has_2_args)
    Game.draw_ui = set_function(Game.draw_ui, module, 'draw_ui', has_2_args)
    Game.draw_loading = set_function(Game.draw_loading, module, 'draw_loading', has_2_args)
    Game.loading_game = set_function(Game.loading_game, module, 'loading_game', has_1_arg)

    title = get_constante(module, 'WIN_TITLE', "BTP v{}- Game".format(BTP.__version__))
    width = get_constante(module, 'WIN_WIDTH', 0)
    height = get_constante(module, 'WIN_HEIGHT', 0)
    full = get_constante(module, 'WIN_FULLSCREEN', True)

    game.start(width, height, title, full)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
