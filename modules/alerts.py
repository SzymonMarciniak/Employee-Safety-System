from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from mysql.connector.cursor_cext import CMySQLCursor

from modules.dbactions import connectToDatabase, closeDatabaseConnection
from modules import global_vars


class AlertsScreen(Screen):
    alerts_count_label = ObjectProperty()

    def __init__(self, **kwargs):
        super(AlertsScreen, self).__init__(**kwargs)
        self.logs_layout = None
        self.last_id = 0

    def on_kv_post(self, base_widget):
        self.logs_layout = self.ids.logs_layout

    def on_pre_enter(self):
        self.logs_layout.clear_widgets()
        self.last_id = 0
        self.build_logs()

    def build_logs(self):
        """
        Builds alerts log container and changes 'seen' indicator to 1
        """
        self.alerts_count_label.unseen_alerts = 0
        db, cursor = connectToDatabase()
        cursor.execute("SELECT cameraID, alertReason, alertAction, date, seen FROM logs WHERE workplaceID=%s"
                       " ORDER BY date DESC;", (global_vars.choosenWorkplace,))
        results = cursor.fetchall()
        if results is not None:
            for row in results:
                self.generateLog(row)
        cursor.execute("UPDATE logs SET seen=1 WHERE workplaceID=%s;",
                       (global_vars.choosenWorkplace,))
        db.commit()
        closeDatabaseConnection(db, cursor)

    def generateLog(self, row):
        """
        Generates alert log object and adds it to the container. Provides whole information such as reason,
        taken action, date etc.

        Params
        ------------------
        row: List
            Row from the results containing needed information
        """
        self.last_id += 1
        logObject = Log()
        logLabel = [LogLabel(text=str(self.last_id), size_hint_x=.6), LogLabel(text=global_vars.cameras_dict[row[0]]),
                    LogLabel(text=str(row[1])), LogLabel(text=str(row[2]))]
        string = str(row[3]).split(' ')
        logLabel.append(LogLabel(text=string[0] + '\n' + string[1]))
        if row[4] != 1:
            self.alerts_count_label.unseen_alerts += 1
            logObject.unseen = 1
        for label in logLabel:
            logObject.add_widget(label)
        self.logs_layout.add_widget(logObject)


class LogLabel(Label):
    def __init__(self, **kwargs):
        super(LogLabel, self).__init__(**kwargs)


class Log(BoxLayout):
    unseen = NumericProperty()

    def __init__(self, **kwargs):
        super(Log, self).__init__(**kwargs)
