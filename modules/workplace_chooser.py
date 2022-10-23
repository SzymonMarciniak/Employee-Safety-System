from kivy.app import App
from kivy.core.window import Window
from iconfonts.iconfonts import icon
from kivy.metrics import sp
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, FadeTransition

from modules import global_vars
from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules.global_vars import MAIN_COLOR, SECONDARY_COLOR


class ChooseWorkplaceScreen(Screen):
    workplace_chooser_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_pre_enter(self):
        Window.set_system_cursor('arrow')
        global_vars.hoverEventObjects = []
        size = Window.size
        Window.size = (100, 100)
        Window.size = size
        self.workplace_chooser_layout.clear_widgets()
        self.workplace_chooser_layout.build_layout()


class NewWorkplace(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = .3
        self.color = MAIN_COLOR
        self.text = "+ SETUP NEW WORKPLACE"
        self.background_down = ''
        self.background_normal = ''
        self.background_color = [0, 0, 0, 0]

    def on_press(self):
        app = App.get_running_app()
        app.root.transition = FadeTransition()
        app.root.current = 'new_workplace_screen'


class ExistingWorkplace(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = .3
        self.orientation = 'vertical'
        self.padding = 20, 25


class EwTitle(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_x = .9
        self.valign = 'top'
        self.color = SECONDARY_COLOR
        self.font_name = 'Lato'
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = self.size


class EwNumber(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.valign = 'top'
        self.halign = 'right'
        self.color = SECONDARY_COLOR
        self.font_name = 'Lato'


class EwStatus(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.font_name = 'Lato'
        self.color = [0, 0, 0, 1]
        self.bind(size=self.update)

    def update(self, *args):
        self.text_size = self.size


class WorkplaceChooserLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = .73

    def build_layout(self):
        db, cursor = connectToDatabase()
        cursor.execute("SELECT name, position, state_activation, state_notifications, ID FROM workplaces"
                       " WHERE userID=%s ORDER BY position ASC;", (global_vars.userID,))
        results = cursor.fetchall()
        row_count = cursor.rowcount
        closeDatabaseConnection(db, cursor)
        if results is not None:
            for row in results:
                self.buildExistingWorkplace(
                    row[0], row[1], row[2], row[3], row[4])
        for i in range(row_count, 3):
            self.buildNewWorkplace()

    def buildExistingWorkplace(self, title, pos, s_activation, s_notifications, workplaceID):
        db, cursor = connectToDatabase()
        cursor.execute(
            "SELECT COUNT(ID) FROM logs WHERE workplaceID=%s AND seen=0", (workplaceID,))
        results = cursor.fetchone()
        alertsCount = results[0]
        ew = ExistingWorkplace()
        ew.workplaceID = workplaceID
        boxlayout = BoxLayout()
        boxlayout.add_widget(EwTitle(text=title))
        boxlayout.add_widget(EwNumber(text='#' + str(pos)))
        ew.add_widget(boxlayout)
        division = DivisionLayout(spacing=10)
        boxlayout = StatusGridLayout()
        label_text = "[color=%s]%s[/color] " \
                     "Status: %s" % ("#08c48c" if s_activation > 0 else "#c92a1e",
                                     icon('zmdi-circle'), "Active" if s_activation > 0 else "Disabled")
        boxlayout.add_widget(EwStatus(text=label_text))
        label_text = "[color=%s]%s[/color] " \
                     "Notifications: %s" % ("#08c48c" if s_notifications > 0 else "#c92a1e",
                                            icon('zmdi-notifications-active') if s_notifications > 0 else
                                            icon(
                                                'zmdi-notifications-off'), "Active"
                                            if s_notifications > 0 else "Disabled")
        boxlayout.add_widget(EwStatus(text=label_text))
        # label_text = "[color=%s]%s[/color] " \
        #              "%s" % ("#08c48c" if s_notifications > 0 else "#c92a1e",
        #                      icon('zmdi-') if s_notifications > 0 else
        #                      icon('zmdi-notifications-active'), "No actions to be taken"
        #                      if self.s_activation > 0 else "X alerts active")
        boxlayout.add_widget(EwStatus(text="[color=%s]%s[/color] %s" % ("08c48c" if alertsCount <= 0 else "#eaa700",
                                                                        icon('zmdi-check') if alertsCount <= 0 else
                                                                        icon(
                                                                            'zmdi-alert-octagon'),
                                                                        "No new alerts" if alertsCount <= 0 else
                                                                        "%d alerts registered!" % alertsCount)))
        division.add_widget(boxlayout)
        boxlayout = ActionButtonsLayout(orientation='vertical')
        chooseBtn = ChooseButton(markup=True, text="%s" %
                                 icon('zmdi-chevron-right'))
        chooseBtn.workplaceID = ew.workplaceID
        boxlayout.add_widget(chooseBtn)
        boxlayout.add_widget(EditButton())
        division.add_widget(boxlayout)
        ew.add_widget(division)
        self.add_widget(ew)

    def buildNewWorkplace(self):
        self.add_widget(NewWorkplace())


class ActionButtonsLayout(BoxLayout):
    pass


class StatusGridLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class DivisionLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ChooseButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]
        self.font_size = sp(32)
        global_vars.hoverEventObjects.append(self)

    def on_press(self):
        global_vars.choosenWorkplace = self.workplaceID
        app = App.get_running_app()
        app.root.transition = FadeTransition()
        app.root.current = 'main_workplace_screen'


class EditButton(Button):
    def __init__(self, **kwargs):
        super(EditButton, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]
        global_vars.hoverEventObjects.append(self)


class LogoutButton(Button):
    workplace_chooser_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.rectColor = self.color
        self.rectColor = "#0fafff"

    def on_pressed(self):
        self.rectColor = "#0f87ff"

    def on_released(self):
        self.rectColor = "#0fafff"
        LogoutClient()


def LogoutClient():
    global_vars.userID = None
    app = App.get_running_app()
    app.root.transition = FadeTransition()
    app.root.current = "login_screen"
