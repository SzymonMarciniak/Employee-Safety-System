from kivy.animation import Animation
from threading import Thread
from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import FadeTransition, Screen
from modules.cameras import RLayout

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules import global_vars
from modules.cameras import CamerasLayout
from modules.global_vars import cameras_dict

choices = {
    1: 'cameras_screen',
    2: 'alerts_screen',
    4: 'rules_screen',
    5: 'SetupScreen',
    6: 'settings_screen',
    7: 'login_screen'
}

t1 = Thread(target=RLayout.set_interval)


class MainWorkplaceScreen(Screen):
    upper_menu = ObjectProperty()
    bottom_menu = ObjectProperty()
    hello_text = StringProperty()

    def __init__(self, **kwargs):
        super(MainWorkplaceScreen, self).__init__(**kwargs)
        userName = global_vars.userID
        self.hello_text = f"Hello {userName}"

    def on_enter(self, *args):
        # Window.fullscreen = 'auto'
        pass

    def on_pre_enter(self):
        """
        Reset mouseover effect and apply it to newly loaded objects.
        Also add cameras to global list and show user's name on the main screen.
        """
        global_vars.hoverEventObjects = []
        for children in self.upper_menu.children:
            global_vars.hoverEventObjects.append(children)
        for children in self.bottom_menu.children:
            global_vars.hoverEventObjects.append(children)

        userid = global_vars.userID
        db, cursor = connectToDatabase()
        cursor.execute("SELECT name FROM accounts WHERE id=%s", (userid,))
        userData = cursor.fetchone()
        cursor.execute(
            f"SELECT generated_id, name FROM cameras WHERE workspace_id={global_vars.choosenWorkplace}")
        results = cursor.fetchall()

        global_vars.cameras_dict = {}
        for row in results:
            global_vars.cameras_dict[row[0]] = row[1]

        closeDatabaseConnection(db, cursor)

        userName = ""
        for l in userData[0]:
            if l == " ":
                break
            userName += l
        self.hello_text = f"Hello, {userName}"

        # db, cursor = connectToDatabase()
        # cursor.execute(f"SELECT state_activation FROM workplaces WHERE id = {global_vars.choosenWorkplace}")
        # AI_enabled = cursor.fetchall()[0][0]
        # cursor.execute(f"SELECT state_notifications FROM workplaces WHERE id = {global_vars.choosenWorkplace}")
        # notification_enabled = cursor.fetchall()[0][0]
        # closeDatabaseConnection(db, cursor)

        # if not AI_enabled:
        #     self.settingsID.ids.toog1.state = "normal"
        #     self.on_toggled(self.ids.toog1, "", True)
        # if not notification_enabled:
        #     self.settingsID.ids.toog2.state = "normal"
        #     self.on_toggled(self.ids.toog2, "", True)


class CamerasGrid(GridLayout):

    def __init__(self, **kwargs):
        super(CamerasGrid, self).__init__(**kwargs)


first = True


class MenuButton(Button):
    main_screen_sm = ObjectProperty()
    bottom_menu = ObjectProperty()
    upper_menu = ObjectProperty()
    canva_s1 = NumericProperty()
    active = False
    sID = NumericProperty()

    def on_press(self):
        if self.sID != 7:
            anim = Animation(canva_s1=1, duration=.3, transition='in_out_quad')
            anim.start(self)
        for children in self.upper_menu.children:
            if children == self:
                continue
            if children.active is True:
                anim = Animation(canva_s1=0, duration=.3,
                                 transition='in_out_quad')
                anim.start(children)
        for children in self.bottom_menu.children:
            if children == self:
                continue
            if children.active is True:
                anim = Animation(canva_s1=0, duration=.3,
                                 transition='in_out_quad')
                anim.start(children)
        self.active = True
        if self.sID == 1:
            if not global_vars.AI_run:
                global first
                if first:
                    t1.run()
                    first = False
                global_vars.AI_run = True
        else:
            global_vars.AI_run = False
        if self.sID == 7:
            global_vars.userID = None
            app = App.get_running_app()
            app.root.transition = FadeTransition()
            app.root.current = choices.get(self.sID)
            self.main_screen_sm.current = 'default'
            self.active = False
            return
        self.main_screen_sm.transition = FadeTransition()
        self.main_screen_sm.current = choices.get(self.sID)
