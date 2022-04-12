import sys
import requests
import base64
import json

from PIL import Image
from PyQt5.QtGui import QPixmap, QImage, QImageReader
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QPushButton, QApplication
from PyQt5.QtWidgets import QInputDialog, QLabel, QLineEdit, QMessageBox

from utils import generate_uuid


class NewCase(QMainWindow):
    def __init__(self, user: str):
        super().__init__()
        self.title = "Register New Case"
        self.name = None
        self.age = None
        self.mob = None
        self.father_name = None
        self.image = None
        self.encoded_image = None
        self.key_points = None
        self.user = user
        self._x_axis = 500
        self.initialize()

    def initialize(self):
        self.setFixedSize(800, 600)
        self.setWindowTitle(self.title)

        upload_image_button = QPushButton("Upload Image", self)
        upload_image_button.resize(150, 50)
        upload_image_button.move(self._x_axis, 20)
        upload_image_button.clicked.connect(self.openFileNameDialog)

        save_button = QPushButton("Save", self)
        save_button.resize(150, 50)
        save_button.move(self._x_axis, 350)
        save_button.clicked.connect(self.save)

        self.get_name()
        self.get_age()
        self.get_fname()
        self.get_mob()
        self.show()

    def get_name(self):
        self.name_label = QLabel(self)
        self.name_label.setText('Name:')
        self.name_label.move(self._x_axis, 100)
        self.name = QLineEdit(self)
        self.name.move(self._x_axis + 50, 100)

    def get_age(self):
        self.age_label = QLabel(self)
        self.age_label.setText('Age:')
        self.age_label.move(self._x_axis, 150)

        self.age = QLineEdit(self)
        self.age.move(self._x_axis + 50, 150)

    def get_fname(self):
        self.fname_label = QLabel(self)
        self.fname_label.setText('Father\'s\n Name:')
        self.fname_label.move(self._x_axis, 200)

        self.father_name = QLineEdit(self)
        self.father_name.move(self._x_axis + 50, 200)

    def get_mob(self):
        self.mob_label = QLabel(self)
        self.mob_label.setText('Mobile:')
        self.mob_label.move(self._x_axis, 250)

        self.mob = QLineEdit(self)
        self.mob.move(self._x_axis + 50, 250)

    def get_facial_points(self, image_url) -> list:
        URL = "http://localhost:8002/image"
        f = [('image', open(image_url, 'rb'))]
        try:
            result = requests.post(URL, files=f)
            if result.status_code == 200:
                return json.loads(result.text)['encoding']
            else:
                QMessageBox.about(self, "Error", "Couldn't find face in Image")
                return None
        except Exception as e:
            QMessageBox.about(self, "Error", "Couldn't connect to face encoding API")
            return None

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        self.fileName, _ = QFileDialog.getOpenFileName(
                    self, "QFileDialog.getOpenFileName()",
                    "", "jpg file (*.jpg)", options=options)

        if self.fileName:
            self.key_points = self.get_facial_points(self.fileName)
            if self.key_points:
                label = QLabel(self)
                pixmap = QPixmap(self.fileName)
                pixmap = pixmap.scaled(320, 350)
                label.setPixmap(pixmap)
                label.resize(310, 350)
                label.move(50, 50)
                label.show()


    def get_entries(self):
        """
        A check to make sure empty fields are not saved.
        A case will be uniquely identified by these fields. 
        """
        entries = {}
        if self.age.text() != "" and self.mob.text() != "" and self.name != ""\
            and self.father_name != "":
            entries['age'] = self.age.text()
            entries['name'] = self.name.text()
            entries['father_name'] = self.father_name.text()
            entries['mobile'] = self.mob.text()
            return entries
        else:
            return None
        
    def save_to_db(self, entries):
        URL = "http://localhost:8000/new_case"
        headers = {'Content-Type': 'application/json',
                   'Accept':'application/json'}

        byte_content = open(self.fileName, 'rb').read()
        base64_bytes = base64.b64encode(byte_content)
        base64_string = base64_bytes.decode("utf-8")

        entries['image'] = base64_string
        try:            
            res = requests.post(URL, json.dumps(entries), headers=headers)
            if res.status_code == 200:
                QMessageBox.about(self, "Success", "Saved successfully")
            else:
                QMessageBox.about(self, "Error", "Something went wrong while saving")
        except Exception as e:
            QMessageBox.about(self, "Error", "Couldn't connect to database")

    def save(self):
        entries = self.get_entries()
        if entries:
            entries['face_encoding'] = self.key_points
            entries['submitted_by'] = self.user
            entries['case_id'] = generate_uuid()
            self.save_to_db(entries)
        else:
            QMessageBox.about(self, "Error", "Please fill all entries")


if __name__ == '__main__':

    app = QApplication(sys.argv)
    w = NewCase('gagan')
    sys.exit(app.exec())