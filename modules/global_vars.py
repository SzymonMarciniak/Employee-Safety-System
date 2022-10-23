from kivy.uix.stacklayout import StackLayout
from kivy.utils import rgba

hoverEventObjects = []
userID = None
choosenWorkplace = None
BG_COLOR = rgba('#ececec')
MAIN_COLOR = rgba('#0fafff')
SECONDARY_COLOR = rgba('#0f87ff')
DECORATION_COLOR = [0.031, 0.768, 0.549, 0.2]
DECORATION_COLOR_NOALPHA = rgba('#08c48c')
ERROR_COLOR = rgba("#c92a1e")

cameras_dict = {}
cameras_layout: StackLayout
detection_dict = {1: 'No mask', 2: 'No helmet',
                  3: 'No cap', 4: 'No vest', 7: 'Person falls'}
actions_dict = {1: 'Flash lights', 2: 'Start alarm', 3: 'Notificate'}

AI_run = False