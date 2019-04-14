import sys
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage,QKeySequence, QIcon
from PyQt5.uic import loadUi
from video import VideoThread
from dataclass import SharedData, SaveData
from facedetection import FaceDetectionThread
import cv2
import os
import signal
from helper import handle_error, showInvalidPaths




class EmotionLabeler(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.MainWindowSize = [900,580]
            self.LabelTrackerSize = [640,200]
            self.videoRunning = None
            self.PhotoData = SharedData()
            self.saver = SaveData(self.PhotoData)
            self.initUI()
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

    def greyScaleToggle(self, state):
        self.PhotoData.set_graytoggle_state(self.GrayScaleBox.isChecked())

    def createMenu(self):
        self.mainMenu = self.menuBar()
        action = QAction("settings",self)
        action.triggered.connect(self.settingsMenu)
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
        if self.CapShortcutBox.isChecked():
            self.CapAndSaveShortcut.activated.connect(self.captureAndSave)
        else:
            self.CapAndSaveShortcut.activated.disconnect()

    def settingsMenu(self):
        #open settings window
        self.setWin = settingsWindow(self)
        self.setWin.reloadsignal.connect(self.reloadSaver)
        self.setWin.show()

    def reloadSaver(self, defaults, fromSetWin=False):
        #change files in saver
        #defaults: bool, true if we are reseting to default paths
        if defaults:
            patharr = ["data/Images","data/faceLabels.csv","data/labelConfig.csv"]
        else:
            #get the paths the user has set in the settings window
            patharr = [self.setWin.imageDir.text(),
                             self.setWin.labelListPath.text(),
                             self.setWin.labelConfigPath.text()]

        #make list of all invalid paths in the list
        invalidPaths = showInvalidPaths(patharr)
        if len(invalidPaths) < 1:
            #update saver, main window UI, and settings window ui
            self.saver._init(*patharr)
            self.LabelMenu.clear()
            self.LabelMenu.addItems(self.saver.labels)
            self.updateLabelTracker()
            if fromSetWin:
                self.setWin.loadText()

    def initUI(self):

        self.resize(*self.MainWindowSize)
        qtRectangle = self.frameGeometry()
        self.createMenu()
        centerpoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerpoint)

        #WINDOW TITLE
        self.setWindowTitle("FaceLabeler")
        self.setWindowIcon(QIcon("data/icon.ico"))


        #FACE DETECTION
        faceth = FaceDetectionThread(self.PhotoData)
        faceth.start()
        self.faceImg = QLabel(self)
        self.faceImg.move(650, 40)
        self.faceImg.resize(200, 200)

        #GET IMAGE BUTTON
        self.FaceButton = QPushButton("Get Image", self)
        self.FaceButton.move(650, 490)
        self.FaceButton.clicked.connect(self.setFaceImg)


        #VIDEO STREAM
        self.videoFeed = QLabel(self)
        self.videoFeed.move(0, 40)
        self.videoFeed.resize(640, 480)
        vidth = VideoThread(self.PhotoData)
        vidth.changePixmap.connect(self.setImage)
        vidth.start()

        #GREYSCALE TOGGLE
        self.GrayScaleBox = QCheckBox("GrayScale", self)
        self.GrayScaleBox.stateChanged.connect(self.greyScaleToggle)
        self.GrayScaleBox.move(650,260)
        self.GrayScaleBox.toggle()

        #SAVE BUTTON
        self.SaveButton = QPushButton("Save", self)
        self.SaveButton.move(750,490)
        self.SaveButton.resize(self.FaceButton.size())
        self.SaveButton.clicked.connect(self.saveLabeledFace)

        #LABEL SELECTION
        self.LabelMenu = QComboBox(self)
        self.LabelMenu.addItems(self.saver.labels)
        self.LabelMenu.currentIndexChanged.connect(self.labelChange)
        self.LabelMenu.move(650,300)

        #LABEL COUNT TRACKER
        self.LabelTracker = QLabel(self)
        self.updateLabelTracker()
        self.LabelTracker.move(0,530)
        self.LabelTracker.resize(*self.LabelTrackerSize)
        self.LabelTracker.setAlignment(Qt.AlignHCenter)


        #CAPTURE AND SAVE BUTTON
        self.CapAndSaveButton = QPushButton("Capture and Save \n (shortcut: space)", self)
        self.CapAndSaveButton.move(650, 520)
        self.CapAndSaveButton.resize(200,40)
        self.CapAndSaveButton.clicked.connect(self.captureAndSave)



        #CAP AND SAVE SHORTCUT TOGGLE
        self.CapShortcutBox = QCheckBox("Enable Cap/Save Shortcut", self)
        self.CapShortcutBox.stateChanged.connect(self.capShortcutToggle)
        self.CapShortcutBox.move(650, 240)
        self.CapShortcutBox.resize(180,16)
        self.CapAndSaveShortcut = QShortcut(QKeySequence("Space"),self)


        self.show()



class settingsWindow(QDialog):
    reloadsignal = pyqtSignal(bool, bool)
    def __init__(self, parent,):
        super(settingsWindow, self).__init__(parent)
        loadUi('settings.ui',self)
        self.parent = parent
        self.loadText()
        self.buttonArray.button(QDialogButtonBox.Discard).clicked.connect(self.loadText)
        self.buttonArray.button(QDialogButtonBox.Save).clicked.connect(lambda: self.reload(False))
        self.buttonArray.button(QDialogButtonBox.RestoreDefaults).clicked.connect(lambda: self.reload(True))

    def loadText(self):
        self.imageDir.setText(self.parent.saver.imageDir)
        self.labelListPath.setText(self.parent.saver.labelListPath)
        self.labelConfigPath.setText(self.parent.saver.labelConfigPath)

    def reload(self, defaults):
        self.reloadsignal.emit(defaults, True)








if __name__ == '__main__':
    PID = os.getpid()

    try:
        app = QApplication(sys.argv)
        ex = EmotionLabeler()
        signal.signal(signal.SIGTERM, app.exec_())
        os.kill(PID, signal.SIGTERM)
    except Exception as e:
        raise (e)
        os.kill(PID, signal.SIGTERM)

    sys.exit()