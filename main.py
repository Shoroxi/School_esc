from ursina import *
from game import Gameplay
import my_json

fon = "assets/img/fon.png"
game_font = "assets/soft_sa.ttf"
icon = "assets/img/icon.png"

if __name__ == '__main__':
    app = Ursina()

    background = Entity(model='quad', texture=fon, scale=30, position=(0, 0, -1), ignore=True, render_queue=10,
                        world_position=(0,0,10))

    walls = my_json.read("data/walls")
    for wall in walls["walls"]:
        Entity(model='quad', scale=wall["scale"], position=wall["pos"], ignore=True, collider="box", color=color.red,
               visible=False)

    Text.default_font = game_font
    text.default_resolution = 720 * Text.size
    window.icon = icon
    window.fullscreen = True
    window.borderless = False
    camera.orthographic = True
    camera.fov = 20

    # Cursor(texture='cursor', scale=.1)
    # mouse.visible = False

    scene = Gameplay()

    app.run()
