import time
from ursina import *
import os

from inv_sys import Inventory
import my_json

enemy = "assets/img/security.png"
player = "assets/img/player.png"
triggers = my_json.read("data/walls")
itms = "assets/img/items/"
ui_icons = "assets/img/ui/"
music = "assets/music.wav"

game_session = None
pause = False

def get_player():
    if game_session:
        if game_session.player is not None:
            return game_session.player
    else:
        return None

def set_player_status(trigger):
    if game_session:
        if game_session.player is not None:
            game_session.player.trigger_status = trigger

def get_player_status():
    if game_session:
        if game_session.player is not None:
            return game_session.player.trigger_status
    else:
        return None

# def setText(txt):
#     msg = dedent(txt).strip()
#     return msg
#
# def show_message(txt, life_time=5):
#     msg.text = setText("")
#     msg.text = setText(txt)
#     invoke(setText, "", delay=life_time)

def show_message(txt, life_time=5):
    get_player().msg.setText("")
    get_player().msg.setText(txt)
    invoke(get_player().msg.setText, "", delay=life_time)

# restart
def loose_menu():
    global pause
    get_player().position = (1, -13)
    get_player().large_msg.setText("")
    get_player().restart_b.disable()
    get_player().ex_b.disable()
    set_player_status("")
    pause = False


class UI(Text):

    def __init__(self, text="", origin=(0, 0), color=color.black, **kwargs):
        super().__init__(parent=camera.ui, origin=origin)
        self.shadow = True

        self.origin_text = Text(text=dedent(text).strip(), parent=self, origin=self.origin, color=color, x=self.x,
                                y=self.y, z=self.z)
        # if shadow True:
        self.shadow_text = Text(text=dedent(text).strip(), parent=self, origin=self.origin, x=self.x + 0.003,
                                y=self.y - 0.003, z=self.z + 0.003, color=rgb(10, 10, 10))

        for key, value in kwargs.items():
            setattr(self, key, value)

    def setText(self, text):
        self.origin_text.text = dedent(text).strip()
        self.shadow_text.text = dedent(text).strip()

    def setColor(self, color):
        self.origin_text.color = color

    # def deleteText(self):
    #     if not pause:
    #         destroy(self)


class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model="cube", collider="box", texture=player, position=(1, -13))
        # ------------ Camera ---------------
        camera.add_script(SmoothFollow(target=self, offset=[0, 1, -40], speed=4))
        # ------------ Player Sprite ---------------
        self.msg = UI("", parent=camera.ui, scale=2, offset=(0.0018, 0.0018), y=-0.35, enabled=True,
                      color=color.white, origin=(0, 0))
        self.large_msg = UI("", scale=5, duration=10, position=(0, 0))
        # ------------ Move ---------------
        self.walk_speed = 8
        self.velocity_x = 0
        self.velocity_y = 0
        self.traverse_target = scene
        # ------------ Other ---------------
        self.inventory = Inventory()
        self.trigger_status = None
        self.t = Trigger()
        # ------------ Buttons ---------------
        self.quest_sprite = Sprite(texture=ui_icons+"", position=(9.88, -9.8), scale=.3, color=color.red)
        Sprite(parent=camera.ui, texture=ui_icons+'inv', position=(-0.58,-0.455), scale=.125)
        Button(icon=ui_icons+'cheese', position=(-0.836,-0.451), scale=.045, on_click=Func(self.drop_itm, "Сыр", "Шкафчик"), tooltip=Tooltip('Сыр'), color=rgb(1,1,1,0))
        Button(icon=ui_icons+'paper', position=(-0.738,-0.455), scale=.045, on_click=Func(self.drop_itm, "Бумага", "Туалет"), tooltip=Tooltip('Бумага'), color=rgb(1,1,1,0))
        Button(icon=ui_icons+'saw', position=(-0.64,-0.455), scale=.05, on_click=Func(self.drop_itm, "Пила", "Стол"), tooltip=Tooltip('Пила'), color=rgb(1,1,1,0))
        Button(icon=ui_icons+'buss', position=(-0.54,-0.455), scale=.05, on_click=Func(self.drop_itm, "Бусы", "Коридор"), tooltip=Tooltip('Бусы'), color=rgb(1,1,1,0))
        Button(icon=ui_icons+'tarakan', position=(-0.445,-0.455), scale=.05, on_click=Func(self.drop_itm, "Таракан", "Тарелки"), tooltip=Tooltip('Таракан'), color=rgb(1,1,1,0))
        Button(icon=ui_icons+'mel', position=(-0.344,-0.455), scale=.05, on_click=Func(self.drop_itm, "Мел", "Пол"), tooltip=Tooltip('Мел'), color=rgb(1,1,1,0))
        # ------------ Loose Buttons ---------------
        self.restart_b = Button(icon=ui_icons+'ZANOVO', position=(0, -0.2), scale=(0.4, 0.1), color=color.rgba(0,0,0,0))
        self.restart_b.on_click = Sequence(Wait(.2), Func(loose_menu), self.restart_b.disable())
        self.ex_b = Button(icon=ui_icons+'VYJTI', position=(0, -0.35), scale=(0.4, 0.1), color=color.rgba(0,0,0,0))
        self.ex_b.on_click = Sequence(Wait(.2), Func(sys.exit), self.ex_b.disable())
        # ------------ Info ---------------
        self.quest = "Подбросить сыр"
        self.info_window = Entity(parent=camera.ui, model=Quad(radius=.03), color=color.rgba(10, 10, 10, 200),
                                  origin=(-.5, .5),
                                  position=Vec2(window.top_left.x + 0.02, window.top_left.y - 0.08),
                                  scale=Vec2(0.43, 0.1))
        self.info = UI(parent=camera.ui, text="null", color=color.orange, origin=(-.5, .5),
                      position=(window.top_left.x + 0.03, window.top_left.y - 0.095, -0.003))

        for key, value in kwargs.items():
            setattr(self, key, value)

    def pickup_itm(self, itm_name, trigger_name):
        if self.trigger_status == trigger_name:
            if not self.inventory.has_item(itm_name):
                self.inventory.add_item(itm_name)
                self.t.get_trigger().disable()

    def drop_itm(self, itm_name, trigger_name):
        if self.trigger_status == trigger_name:
            if self.inventory.has_item(itm_name):
                self.inventory.del_item(itm_name)
                self.t.get_trigger().disable()

    # -------------- Move -----------------
    def update(self):
        global pause

        def setCrosshairTip(tip_text):
            self.msg.setText(tip_text)
            # self.press_e.enabled = True

        def clearCrosshairText():
            get_player().msg.setText("")
            # self.press_e.enabled = False

        if self.trigger_status == "Enemy":
            pause = True
            self.large_msg.setText("Вас поймали")
            self.large_msg.setColor(color.red)
            if pause:
                self.restart_b.enable()
                self.ex_b.enable()

        # начало
        if self.trigger_status == "Шкафчик":
            if self.inventory.has_item("Сыр"):
                setCrosshairTip("Подбросить сыр")
            else:
                self.quest = "Засорить туалет"
                self.quest_sprite.set_position(value=Vec3(-4.55,-11.9,0))

        if self.trigger_status == "Туалет":
            if self.inventory.has_item("Бумага"):
                setCrosshairTip("Засорить туалет")
            else:
                self.quest = "Накидать тараканов в еду"
                Sprite(texture=itms + "toilet", position=(-4.55,-11.9), scale=2)
                self.quest_sprite.set_position(value=Vec3(8.5,3.81,0))

        if self.trigger_status == "Тарелки":
            if self.inventory.has_item("Таракан"):
                setCrosshairTip("Накидать тараканов в еду")
            else:
                self.quest = "Исписать пол"
                Sprite(texture=itms + "tarakans", position=(1.7,1), scale=2)
                self.quest_sprite.set_position(Vec3(1.06,-0.6,0))

        if self.trigger_status == "Пол":
            if self.inventory.has_item("Мел"):
                setCrosshairTip("Исписать пол")
            else:
                self.quest = "Распилить стол"
                Sprite(texture=itms + "mel", position=(1.06,-0.6))
                self.quest_sprite.set_position(Vec3(5.95,0.74,0))

        if self.trigger_status == "Стол":
            if self.inventory.has_item("Пила"):
                setCrosshairTip("Распилить")
            else:
                self.quest = "Рассыпать бусы"
                Sprite(texture=itms + "stol", position=(5.95,0.74))
                self.quest_sprite.set_position(Vec3(-3.87,2.07,0))

        if self.trigger_status == "Коридор":
                if self.inventory.has_item("Бусы"):
                    setCrosshairTip("Рассыпать бусы")
                else:
                    self.quest = "Выбежать из школы"
                    Sprite(texture=itms + "buss", position=(-3.87,2.07))
                    self.quest_sprite.disable()

        if self.inventory.get_items_count() == 0:
            self.inventory.add_item("Кубок")

        if self.trigger_status == "Выход":
            if self.inventory.has_item("Кубок"):
                pause = True
                self.large_msg.setText("ВЫ ПОБЕДИЛИ")
                self.large_msg.setColor(color.yellow)
                self.restart_b.enable()
                self.ex_b.enable()

        elif self.trigger_status == "" or self.trigger_status is None:
            clearCrosshairText()

        if not boxcast(
                # self.position + Vec3(self.velocity_x * time.dt * self.walk_speed, self.scale_y / 2, 0),
                self.position + Vec3(self.velocity_x * time.dt * self.walk_speed,
                                     self.velocity_y * time.dt * self.walk_speed, 0),
                direction=Vec3(self.velocity_x, self.velocity_y, 0),
                distance=abs(self.scale_x / 2),
                ignore=(self,),
                traverse_target=self.traverse_target,
                thickness=(self.scale_x * .9, self.scale_y * .9),
                debug=False
        ).hit:
            self.x += self.velocity_x * time.dt * self.walk_speed
            self.y += self.velocity_y * time.dt * self.walk_speed

        self.info.setText(
            # "POS X: " + str(round(self.x, 2)) + \
            # "\nPOS Y: " + str(round(self.y, 2)) + \
            "\nСделано пакостей: " + str(self.inventory.get_items_count()) + "/6" + \
            "\nЗадание: " + self.quest
        )

    def input(self, key):
        global pause
        if not pause:
            if key == 'd':
                self.velocity_x = 1
                self.rotation_z = 180
            if key == 'd up':
                self.velocity_x = -held_keys['a']
            if key == 'a':
                self.velocity_x = -1
                self.rotation_z = 0
            if key == 'a up':
                self.velocity_x = held_keys['d']
            if key == 'w':
                self.velocity_y = 1
                self.rotation_z = 90
            if key == 'w up':
                self.velocity_y = -held_keys['s']
            if key == 's':
                self.velocity_y = -1
                self.rotation_z = 270
            if key == 's up':
                self.velocity_y = held_keys['w']
            # if key == 'e':
            #     self.drop_itm()
        else:
            self.velocity_x = 0
            self.velocity_y = 0


class Trigger(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.trigger_id = None
        self.trigger_targets = (self,)
        self.radius = None
        self.scale = self.radius
        self.color = color.rgba(10, 10, 10, 50)

        self.triggerers = []

        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_trigger_id(self):
        return self.trigger_id

    def get_trigger(self):
        return self

    def update(self):

        for other in self.trigger_targets:
            if other == self:
                continue
            dist = distance(other, self)

            # Вошел
            if other not in self.triggerers and dist <= self.radius:
                print("Вошел в: " + self.get_trigger_id())
                self.triggerers.append(other)
                # print("Статус: " + self.get_trigger_id())
                set_player_status(self.get_trigger_id())

                continue

            # Вышел
            if other in self.triggerers and dist > self.radius:
                print("Вышел из: " + self.get_trigger_id())
                self.triggerers.remove(other)
                # print("Убран Статус: " + get_player_status())
                set_player_status("")
                continue


class Gameplay(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        global game_session
        self.player = Player()
        game_session = self

        for trigger in triggers["triggers"]:
            Trigger(trigger_targets=(self.player,), position=trigger["pos"], invisible=False, radius=1, sacle=1,
                    trigger_id=trigger["id"])

        Enemy_Sprite = Sprite(position=(-5,-9.85), texture=enemy, scale=1.3)
        Enemy = Trigger(collider="sphere", position=(-5,-9.85), invisible=False, radius=1, scale=1,
                        trigger_targets=(self.player,), trigger_id="Enemy")

        Enemy.animate_x(8, duration=10, loop=True, curve=curve.linear_boomerang)
        Enemy_Sprite.animate_x(8, duration=10, loop=True, curve=curve.linear_boomerang)

        # Audio(music, pitch=random.uniform(.5, 1), loop=True, autoplay=True)

        for key, value in kwargs.items():
            setattr(self, key, value)
