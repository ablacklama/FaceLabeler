import sys
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage,QKeySequence, QIcon
from PyQt5.uic import loadUi
from video import VideoThread
from dataclass import SharedPhotoData, SaveData
from facedetection import FaceDetectionThread
import cv2
import os
import signal
from helper import handle_error, showInvalidPaths
import configparser




class EmotionLabeler(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.PhotoData = SharedPhotoData(config)
            self.saver = SaveData(self.PhotoData, config)
            self.initUI()
            self.setupSettings()
        except Exception as e:
            handle_error(e)
            raise(e)

    def setImage(self, image):
        self.videoFeed.setPixmap(QPixmap.fromImage(image))
        return

    def setFaceImg(self):
        ret_val, img = self.PhotoData.get_face_image()

        if ret_val:
            self.saver.set_face_image(img)

        if not ret_val or not self.GrayScaleBox.isChecked():
            resized = cv2.resize(img, (200, 200))
            qimg = QImage(resized.data, resized.shape[1], resized.shape[0],
                          resized.shape[1] * 3, QImage.Format_RGB888)
        else:
            resized = cv2.resize(img,(200,200))
            qimg = QImage(resized.data, resized.shape[1], resized.shape[0],
                       resized.shape[1], QImage.Format_Grayscale8)

        p = QPixmap.fromImage(qimg)
        self.faceImg.setPixmap(p)

    def greyScaleToggle(self):
        self.PhotoData.set_graytoggle_state(self.GrayScaleBox.isChecked())
        config["CUSTOM"]["grayscalebox"] = str(int(self.GrayScaleBox.isChecked()))

    def createMenu(self):
        self.mainMenu = self.menuBar()
        action = QAction("settings",self)
        action.triggered.connect(self.openSettings)
        self.mainMenu.addAction(action)

    def saveLabeledFace(self):
        self.saver.save_current()
        self.updateLabelTracker()

    def labelChange(self):
        self.saver.change_label(self.LabelMenu.currentIndex())

    def updateLabelTracker(self):
        keys = self.saver.labels

        string = ""
        numLines = 1
        for key in keys:
            string += str(key) + ":" + str(self.saver.labelCount[key]) + "   "
            if len(string) > 100 * numLines:
                string += "\n"
                numLines += 1
        self.LabelTracker.setText(string)

    def captureAndSave(self):
        self.setFaceImg()
        self.saveLabeledFace()

    def capShortcutToggle(self):
        config["CUSTOM"]["capshortcutbox"] = str(int(self.CapShortcutBox.isChecked()))
        if self.CapShortcutBox.isChecked():
            self.CapAndSaveShortcut.activated.connect(self.captureAndSave)
        else:
            self.CapAndSaveShortcut.activated.disconnect()

    def showFaceDetectionBoxToggle(self):
        self.PhotoData.showFaceBox = self.ShowFaceDetectionBox.isChecked()
        config["CUSTOM"]["showdetectionbox"] = str(int(self.ShowFaceDetectionBox.isChecked()))

    def openSettings(self):
        self.setWin.show()

    def setupSettings(self):
        self.setWin = settingsWindow(self)
        self.setWin.reloadsignal.connect(self.reloadSaver)

    def reloadSaver(self, defaults, fromSetWin=False):
        #change files in saver
        #defaults: bool, true if we are reseting to default paths
        if defaults:
            patharr = [config["DEFAULT"]["imageDir"],
                       config["DEFAULT"]["labelListPath"],
                       config["DEFAULT"]["labelConfigPath"]]
            delay = float(config["DEFAULT"]["detectionDelay"])
        else:
            #get the paths the user has set in the settings window
            patharr = [self.setWin.imageDir.text(),
                             self.setWin.labelListPath.text(),
                             self.setWin.labelConfigPath.text()]
            delay = self.setWin.detectionDelay.value()

        config["CUSTOM"]["detectionDelay"] = str(delay)
        self.PhotoData.detectionDelay = delay
        #make list of all invalid paths in the list
        invalidPaths = showInvalidPaths(patharr)
        if len(invalidPaths) < 1:
            #update saver, main window UI, and settings window ui
            self.saver._init(*patharr)
            self.LabelMenu.clear()
            self.LabelMenu.addItems(self.saver.labels)
            self.updateLabelTracker()

            config["CUSTOM"]["imageDir"] = patharr[0]
            config["CUSTOM"]["labelListPath"] = patharr[1]
            config["CUSTOM"]["labelConfigPath"] = patharr[2]

            if fromSetWin:
                self.setWin.loadText()

    def initUI(self):
        loadUi('data/ui/mainwindow.ui', self)

        qtRectangle = self.frameGeometry()
        self.createMenu()

        centerpoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerpoint)

        #WINDOW TITLE
        self.setWindowTitle("FaceLabeler")
        self.setWindowIcon(QIcon("data/ui/icon.ico"))

        #FACE DETECTION
        faceth = FaceDetectionThread(self.PhotoData)
        faceth.start()

        #GET IMAGE BUTTON
        self.FaceButton.clicked.connect(self.setFaceImg)

        #VIDEO STREAM
        vidth = VideoThread(self.PhotoData)
        vidth.changePixmap.connect(self.setImage)
        vidth.start()

        #GREYSCALE TOGGLE
        self.GrayScaleBox.stateChanged.connect(self.greyScaleToggle)
        self.GrayScaleBox.setChecked(bool(int(config["CUSTOM"]["grayscalebox"])))

        #SAVE BUTTON
        self.SaveButton.clicked.connect(self.saveLabeledFace)

        #LABEL SELECTION
        self.LabelMenu.addItems(self.saver.labels)
        self.LabelMenu.currentIndexChanged.connect(self.labelChange)

        #LABEL COUNT TRACKER
        self.updateLabelTracker()
        self.LabelTracker.setAlignment(Qt.AlignHCenter)

        #CAPTURE AND SAVE BUTTON
        self.CapAndSaveButton.clicked.connect(self.captureAndSave)

        #CAP AND SAVE SHORTCUT TOGGLE
        self.CapAndSaveShortcut = QShortcut(QKeySequence("Space"),self)
        self.CapShortcutBox.stateChanged.connect(self.capShortcutToggle)
        self.CapShortcutBox.setChecked(bool(int(config["CUSTOM"]["capshortcutbox"])))

        #SHOW FACE DETECTION TOGGLE
        self.ShowFaceDetectionBox.stateChanged.connect(self.showFaceDetectionBoxToggle)
        self.ShowFaceDetectionBox.setChecked(bool(int(config["CUSTOM"]["showdetectionbox"])))


        self.show()



class settingsWindow(QDialog):
    reloadsignal = pyqtSignal(bool, bool)
    def __init__(self, parent):
        super(settingsWindow, self).__init__(parent)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        loadUi('data/ui/settings.ui',self)
        self.setWindowIcon(QIcon("data/ui/icon.ico"))
        self.parent = parent
        self.loadText()
        self.buttonArray.button(QDialogButtonBox.Discard).clicked.connect(self.loadText)
        self.buttonArray.button(QDialogButtonBox.Save).clicked.connect(lambda: self.reload(False))
        self.buttonArray.button(QDialogButtonBox.RestoreDefaults).clicked.connect(lambda: self.reload(True))

    def loadText(self):
        self.detectionDelay.setValue(self.parent.PhotoData.detectionDelay)
        self.imageDir.setText(self.parent.saver.imageDir)
        self.labelListPath.setText(self.parent.saver.labelListPath)
        self.labelConfigPath.setText(self.parent.saver.labelConfigPath)

    def reload(self, defaults):
        self.reloadsignal.emit(defaults, True)








if __name__ == '__main__':
    PID = os.getpid()

    try:
        config = configparser.ConfigParser()
        config.read("data/ui/settings.ini")
        app = QApplication(sys.argv)
        ex = EmotionLabeler()
        signal.signal(signal.SIGTERM, app.exec_())
        with open("data/ui/settings.ini", "w") as configFile:
            config.write(configFile)
        os.kill(PID, signal.SIGTERM)
    except Exception as e:
        with open("settings.ini", "w") as configFile:
            config.write(configFile)
        raise(e)

    sys.exit()