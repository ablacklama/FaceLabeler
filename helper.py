from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import os


def handle_error(error):
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Critical)
    error_box.setWindowIcon(QIcon("icon.ico"))
    error_box.setWindowTitle("Fetal Error")
    error_box.setText('A critical error occurred. Select the details to display it.')
    error_box.setInformativeText("If you think this is a bug, please report it to "
                                 "<a href=https://github.com/ablacklama/FaceLabeler/issues/new>the owner's GitHub</a>")
    error_box.setTextFormat(Qt.RichText)
    error_box.setDetailedText(str(error))
    error_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
    error_box.exec()

def showInvalidPaths(patharr, extraText=""):
    # make list of all invalid paths in the list
    invalidPaths = []
    for path in patharr:
        if not os.path.exists(path):
            invalidPaths.append(path)

    # if any invalid paths exist open error window
    if len(invalidPaths) > 0:
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Warning)
        error_box.setWindowIcon(QIcon("data/icon.ico"))
        error_box.setWindowTitle("Path Error")
        error_box.setText('One or more paths are not valid')
        error_box.setInformativeText(extraText + "\n".join(invalidPaths))
        error_box.setTextFormat(Qt.RichText)
        error_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
        error_box.exec()
    return invalidPaths