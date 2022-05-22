from window import Ui_MainWindow
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import gd
import os
import pyperclip
import logging

#logging.basicConfig(level=logging.INFO)

class Window(QtWidgets.QMainWindow):
    def convert(self, d):
        return d.split(".")[-1].replace('_', " ").capitalize()

    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(376, 329)

        self.ui.pushButton.clicked.connect(self.copy_path)

        self.connWorker = Worker()
        self.connWorker.start()
        self.connWorker.status.connect(self.update_connection)
        self.connWorker.level_data.connect(self.set_data)
        self.connWorker.finished.connect(self.close)

    def update_connection(self, status):
        if status == "unsuccessful":
            self.ui.label.setText("GeometryDash.exe is not opened")
            self.ui.label.setStyleSheet("color: rgb(0, 0, 0);")

        elif status == "connected":
            self.ui.label.setText("Connected to GeometryDash.exe")
            self.ui.label.setStyleSheet("color: rgb(62, 162, 0);")

            self.write_data(" ")
            self.ui.lineEdit.setText(os.path.abspath("output.txt"))

    def write_data(self, data):
        if not os.path.exists("output.txt"):
            open("output.txt", "a+").close()

        with open("output.txt", "w") as f:
            f.write(data)

    def set_data(self, data):
        out = ""
        if self.ui.name_box.isChecked() and data['name']:
            out += f'Level name: {data["name"]}\n'

        if self.ui.id_box.isChecked() and data['id'] != "None":
            out += f'ID: {data["id"]}\n'
            if self.ui.diff_box.isChecked() and data['difficulty']:
                out += f'Difficulty: {self.convert(str(data["difficulty"]))}\n'

        if self.ui.creator_box.isChecked() and data['creator']:
            out += f'Creator: {data["creator"]}\n'

        if self.ui.atts_box.isChecked() and data['attempts']:
            out += f'Attempts: {data["attempts"]}\n'

        if self.ui.jumps_box.isChecked() and data['jumps']:
            out += f'Jumps: {data["jumps"]}\n'

        self.ui.textEdit.setText(out)
        self.write_data(out)
        logging.info(f"Wrote {len(out)} bytes to output.txt")

    def copy_path(self):
        pyperclip.copy(str(self.ui.lineEdit.text()))

    def closeEvent(self, event):
        open("output.txt", "w")
        event.accept()

class Worker(QThread):
    status = pyqtSignal(str)
    level_data = pyqtSignal(dict)

    def run(self):
        while True:
            try:
                self.memory = gd.memory.State("GeometryDash.exe")
                self.status.emit("connected")

                level = self.memory.game_manager.play_layer.level_settings.level

                id = level.id
                if id == 0:
                    id = None

                self.level_data.emit(
                    {
                        "name": level.name,
                        "id": str(id),
                        "difficulty": level.difficulty,
                        "creator": level.creator_name,
                        "attempts": level.attempts,
                        "jumps": level.jumps
                    }
                )
            except Exception as e:
                logging.info(e)
                self.status.emit("unsuccessful")
                pass


app = QtWidgets.QApplication([])
application = Window()
application.show()
sys.exit(app.exec())
