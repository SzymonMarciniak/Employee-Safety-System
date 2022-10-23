import platform

from kivy.animation import Animation
from kivy.core.window import Window

if platform.system() == 'Windows':
    import win32api
    import win32con
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, ColorProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import FadeTransition, Screen
from kivy.uix.textinput import TextInput

from modules import global_vars
from modules.checkers import checkDataCorrectness


class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    loginBox = ObjectProperty()
    passwordBox = ObjectProperty()
    registerBtn = ObjectProperty()
    loginBtn = ObjectProperty()
    resetPswdBtn = ObjectProperty()

    def on_enter(self, *args):
        Window.fullscreen = False

    def on_pre_enter(self):
        Clock.schedule_once(self.callback)
        # It is necessary to call function one frame later.
        # Calling it right away is causing an error because
        # the IDs are not yet initalized

    def callback(self, dt):
        """
        Resets whole screen right before user can see it. Also provides login screen's mouseover effect on certain
        objects
        """
        global_vars.hoverEventObjects = [self.loginBox, self.passwordBox, self.loginBtn,
                                         self.registerBtn, self.resetPswdBtn]
        self.loginBox.text = ''
        self.passwordBox.text = ''


class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    loginBox = ObjectProperty()
    newPasswordBox = ObjectProperty()
    repeatPasswordBox = ObjectProperty()
    nameBox = ObjectProperty()
    registerBtn = ObjectProperty()
    loginBtn = ObjectProperty()
    resetPswdBtn = ObjectProperty()

    def on_pre_enter(self):
        """
        Resets whole screen right before user can see it. Also provides register screen's mouseover effect on certain
        objects
        """
        global_vars.hoverEventObjects = [
            self.registerBtn, self.loginBtn, self.resetPswdBtn]
        self.loginBox.text = ''
        self.newPasswordBox.text = ''
        self.repeatPasswordBox.text = ''
        self.nameBox.text = ''


class LoginScreenLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(LoginScreenLayout, self).__init__(**kwargs)


class RegisterScreenLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(RegisterScreenLayout, self).__init__(**kwargs)


class SimpleInput(TextInput):
    canva_s1 = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform.system() == 'Windows':
            self.bind(text=self.on_entered)

    def on_focus(self, instance, value):
        """
        Creates smooth animation of text inputs all over the application.
        """
        if value:
            self.canva_s1 = 0
            anim = Animation(canva_s1=1, duration=.5, transition="in_quart")
            anim.start(self)

    activated = False

    def on_entered(self, instance, value):
        """
        Changes caps lock indicator state when text is entered in any text input.
        Works only on Windows.
        """
        caps_status = win32api.GetKeyState(win32con.VK_CAPITAL)
        if caps_status == 0 and self.activated:
            current_app = App.get_running_app()
            current_app.root.get_screen(
                'login_screen').ids.capsLockLabel.text = ''
            current_app.root.get_screen(
                'register_screen').ids.capsLockLabel_newPasswordBox.text = ''
            current_app.root.get_screen(
                'register_screen').ids.capsLockLabel_repeatPasswordBox.text = ''
            current_app.root.get_screen(
                'new_password_screen').ids.capsLockLabel_forgotNewPasswordBox.text = ''
            current_app.root.get_screen(
                'new_password_screen').ids.capsLockLabel_forgotRepeatNewPasswordBox.text = ''
            self.activated = False
        elif caps_status == 1 and not self.activated:
            current_app = App.get_running_app()
            current_app.root.get_screen(
                'login_screen').ids.capsLockLabel.text = 'Caps ON'
            current_app.root.get_screen(
                'register_screen').ids.capsLockLabel_newPasswordBox.text = 'Caps ON'
            current_app.root.get_screen(
                'register_screen').ids.capsLockLabel_repeatPasswordBox.text = 'Caps ON'
            current_app.root.get_screen(
                'new_password_screen').ids.capsLockLabel_forgotNewPasswordBox.text = 'Caps ON'
            current_app.root.get_screen('new_password_screen').ids.capsLockLabel_forgotRepeatNewPasswordBox.text = \
                'Caps ON '
            self.activated = True


class LoginButton(Button):
    rectColor = StringProperty('')
    loginBox = ObjectProperty()
    passwordBox = ObjectProperty()
    errorBox = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.rectColor = self.color
        self.rectColor = "#0fafff"

    def on_pressed(self):
        self.rectColor = "#0f87ff"
        checkDataCorrectness(self.loginBox.text,
                             self.passwordBox.text, self.errorBox)

    def on_released(self):
        self.rectColor = "#0fafff"


class RegisterButton(Button):
    rectColor = StringProperty('')
    loginBox = ObjectProperty()
    newPasswordBox = ObjectProperty()
    repeatPasswordBox = ObjectProperty()
    nameBox = ObjectProperty()
    errorBox = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.rectColor = self.color
        self.rectColor = "#0fafff"

    def on_pressed(self):
        self.rectColor = "#0f87ff"
        checkDataCorrectness(self.loginBox.text, self.newPasswordBox.text, self.errorBox, self.repeatPasswordBox.text,
                             self.nameBox.text)

    def on_released(self):
        self.rectColor = "#0fafff"


class ResetPasswordButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        """
        Go to password reseting screen whether clicked
        """
        App.get_running_app().root.transition = FadeTransition()
        App.get_running_app().root.current = 'forgot_password_screen'


class SwitchRegisterButton(Button):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_press(self):
        self.color = "#0f87ff"

    def on_release(self):
        self.color = "#0fafff"


class ChangeLanguage(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.english = True

    def on_press(self):
        if self.english:
            self.background_down = 'img/pl.png'
            self.background_normal = 'img/pl.png'
            self.english = False
        else:
            self.background_down = 'img/gb.png'
            self.background_normal = 'img/gb.png'
            self.english = True
