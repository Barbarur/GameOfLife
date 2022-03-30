import csv
import random
import time

from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import NumericProperty, ListProperty, ObjectProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, SlideTransition
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget




############################
# MAIN MENU
############################
class MenuScreen(Screen):
    pass

class WorldType(Screen):
    world_type = ObjectProperty(None)
    prop_test = ObjectProperty(None)

    def size_world(self):
        self.world_type = 'custom'
        self.manager.current = 'size'

    def pre_world(self, type):
        self.world_type = type
        app = App.get_running_app()
        app.sm.current = 'create'

class SettingsScreen(Screen):
    world_shape = 'square'
    life_color = [0, 255, 122]
    dead_color = [60, 0, 0]
    time_speed = 5

    def on_pre_enter(self, *args):
        if self.world_shape == 'square':
            self.square = 'True'
        else:
            self.square = 'False'


    def shape_world(self, shape):
        self.world_shape = shape
        print(self.world_shape)

class CustomSize(Screen):
    x_size = ObjectProperty(None)
    y_size = ObjectProperty(None)
    p_life = ObjectProperty(None)

    def create_world(self):
        # print(self.x_size.text)
        # print(self.y_size.text)
        if self.x_size.text == '' or self.y_size.text == '':
            return
        app = App.get_running_app()
        app.sm.current = 'create'


class CreateWorld(Screen):
    def on_pre_enter(self, *args):
        layout = BoxLayout()
        self.add_widget(layout)
        lbl = Label(text='Creating a new world...')
        layout.add_widget(lbl)

        Clock.schedule_once(self.create, 1)

    def create(self, obj):
        self.world_type = self.manager.get_screen('type').world_type
        if self.world_type == 'custom':
            self.custom()
        else:
            self.predesigned()

    def custom(self):
        x_size = int(self.manager.get_screen('size').x_size.text)
        y_size = int(self.manager.get_screen('size').y_size.text)
        p_life = 100 - int(self.manager.get_screen('size').p_life.text)
        self.day_one = [[0 for i in range(y_size)] for j in range(x_size)]
        for i in range(len(self.day_one)):
            for j in range(len(self.day_one[0])):
                num = random.randint(0, 100)
                if num >= p_life:
                    self.day_one[i][j] = 1
                else:
                    self.day_one[i][j] = 0
        # print(self.x_size)
        # print(self.y_size)
        # print(self.day_one)
        self.go_to_world()

    def predesigned(self):
        data = csv.DictReader(open("worlds.csv"))
        for row in data:
            if row['world'] == self.world_type:
                a = row['array']
                # print(f'a = {a}')
                b = a.split()
                # print(f'b = {b}')
                self.day_one = []
                for i in b:
                    # print(f'i = {i}')
                    c = list(i)
                    # print(f'c = {c}')
                    c = [int(n) for n in c]
                    # print(f'New c = {c}')
                    self.day_one.append(c)
        # print(self.x_size)
        # print(self.y_size)
        # print(self.world)
        self.go_to_world()

    def go_to_world(self):
        app = App.get_running_app()
        app.sm.transition = FadeTransition(duration=2)
        app.sm.current = 'world'


class Cell(Widget):
    color = ListProperty([1, 1, 1, 1])

    def __init__(self, number, **kwargs):
        super(Cell, self).__init__(**kwargs)
        self.number = number
        self.update_color()

    def update_color(self):
        app = App.get_running_app()
        lc = [i/255 for i in app.sm.get_screen('settings').life_color]
        dc = [i / 255 for i in app.sm.get_screen('settings').dead_color]
        if self.number == 1:
            self.color = (lc[0], lc[1], lc[2], 1)
        else:
            self.color = (dc[0], dc[1], dc[2], 1)

    def resize(self, pos, size):
        self.pos = pos
        self.size = size


class WorldScreen(Screen):
    days = ObjectProperty('1')

    def on_pre_enter(self, *args):
        self.world_shape = self.manager.get_screen('settings').world_shape
        self.the_world()

    def the_world(self):
        self.today = self.manager.get_screen('create').day_one
        x_size = len(self.today)
        y_size = len(self.today[0])

        self.world = [[0 for i in range(y_size)] for j in range(x_size)]
        side = min(self.width / x_size, (self.height - dp(30)) / y_size)

        for i in range(len(self.today)):
            for j in range(len(self.today[0])):
                celula = Cell(int(self.today[i][j]))
                celula.resize(pos=(side * i, side * j), size=(side, side))
                celula.update_color()
                self.world[i][j] = celula
                self.add_widget(celula)

        self.start()

    def start(self):
        self.abc = Clock.schedule_interval(self.next_day, 1/self.manager.get_screen('settings').time_speed)

    def stop(self):
        Clock.unschedule(self.next_day)

    def pause(self, widget):
        if widget.state == 'normal':
            widget.text = 'PAUSE'
            self.stop()
        else:
            widget.text = ''
            self.start()

    def next_day(self, obj):
        self.days = str(int(self.days) + 1)
        neighbors = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]


        yesterday = self.today.copy()
        x_size = len(yesterday)
        y_size = len(yesterday[0])
        self.today = [[0 for i in range(y_size)] for j in range(x_size)]
        side = min(self.width / x_size, (self.height - dp(30)) / y_size)
        # print(yesterday)
        # print(self.today)

        for i in range(len(yesterday)):
            for j in range(len(yesterday[0])):
                nn = 0
                # print(f"x={i}, y={j}")
                for x, y in neighbors:
                    a = i + x
                    b = j + y
                    if self.world_shape == 'square':
                        if 0 <= a <= (int(len(yesterday)) - 1) and 0 <= b <= (int(len(yesterday[0]) - 1)) and yesterday[a][b] == 1:
                            # print(f"a={a}, b={b}")
                            nn += 1
                    elif self.world_shape == 'round':
                        if a < 0:
                            a = a + int(len(yesterday))
                        if (int(len(yesterday)) - 1) < a:
                            a = a - int(len(yesterday))
                        if b < 0:
                            b = b + int(len(yesterday[0]))
                        if (int(len(yesterday[0]) - 1)) < b:
                            b = b - int(len(yesterday[0]))
                        if yesterday[a][b] == 1:
                            nn += 1
                # print(f"neighbours = {nn}")
                if yesterday[i][j] == 1 and (nn < 2 or 3 < nn):
                    self.world[i][j].number = 0
                    # print('die')
                elif yesterday[i][j] == 1 and (2 <= nn <= 3):
                    self.world[i][j].number = 1
                    self.today[i][j] = 1
                elif yesterday[i][j] == 0 and nn == 3:
                    self.world[i][j].number = 1
                    self.today[i][j] = 1
                    # print('new live')
                self.world[i][j].resize(pos=(side * i, side * j), size=(side, side))
                self.world[i][j].update_color()

    def clear(self):
        for i in range(len(self.world)):
            for j in range(len(self.world[0])):
                self.remove_widget(self.world[i][j])


Builder.load_file("kivydesign.kv")


class GameOfLifeApp(App):
    sm = None

    def build(self):
        self.sm = ScreenManager()
        self.sm.add_widget(MenuScreen(name="menu"))
        self.sm.add_widget(SettingsScreen(name="settings"))
        self.sm.add_widget(WorldType(name="type"))
        self.sm.add_widget(CustomSize(name="size"))
        self.sm.add_widget(CreateWorld(name="create"))
        self.sm.add_widget(WorldScreen(name="world"))
        self.sm.current = "menu"
        return self.sm


GameOfLifeApp().run()
