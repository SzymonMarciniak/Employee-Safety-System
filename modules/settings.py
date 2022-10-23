from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import FadeTransition

from modules import global_vars
from modules.dbactions import connectToDatabase


class DeleteWorkspacePopupContent(BoxLayout):
    def __init__(self, **kwargs):
        super(DeleteWorkspacePopupContent, self).__init__(**kwargs)
        self.add_widget(Label(markup=True, font_name='Lato', text='Are you sure you want to delete this '
                                                                  'workplace?\nThis process is irreversible!',
                              font_size=40))
        boxlayout = BoxLayout(spacing=30, padding=[15, 0])
        btn = Button(text="YES, DELETE", size_hint_y=.25, size_hint_x=.3)
        boxlayout.add_widget(btn)
        btn.bind(on_release=self.delete_workspace)
        btn = Button(text="NO, CANCEL PROCESS",
                     size_hint_y=.25, size_hint_x=.7)
        boxlayout.add_widget(btn)
        self.add_widget(boxlayout)

    def delete_workspace(self, dt):
        db, cursor = connectToDatabase()
        cursor.execute("DELETE FROM workplaces WHERE ID=%s",
                       (global_vars.choosenWorkplace,))
        db.commit()
        app = App.get_running_app()
        app.root.transition = FadeTransition()
        app.root.current = 'choose_workplace_screen'

        global_vars.choosenWorkplace = None  # CLEAR WORKSPACE ID


class DeleteWorkspaceButton(Button):
    def __init__(self, **kwargs):
        super(DeleteWorkspaceButton, self).__init__(**kwargs)

    def on_press(self):
        content = DeleteWorkspacePopupContent(orientation='vertical')
        popup = Popup(title="Warning", auto_dismiss=False,
                      content=content, size_hint=[.7, .7])
        for child in content.children:
            if type(child) is BoxLayout:
                for btn in child.children:
                    btn.bind(on_press=popup.dismiss)
        popup.open()
