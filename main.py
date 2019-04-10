import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage,QKeySequence, QIcon
from video import VideoThread
from dataclass import SharedData, SaveData
from facedetection import FaceDetectionThread
import cv2
import os
import signal




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
        self.fileMenu = self.mainMenu.addMenu('File')

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



    def initUI(self):

        self.resize(*self.MainWindowSize)
        qtRectangle = self.frameGeometry()
        #self.createMenu()
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
        vidth = VideoThread(self.PhotoData)#, camera="http://192.168.1.9:4747/video")
        vidth.changePixmap.connect(self.setImage)
        vidth.start()

        #GREYSCALE TOGGLE
        self.GrayScaleBox = QCheckBox("GrayScale", self)
        self.GrayScaleBox.stateChanged.connect(self.greyScaleToggle)
        self.GrayScaleBox.move(700,260)
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
        self.LabelMenu.move(700,300)

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



        #CAP AND SAVE SHORTCUT
        self.CapShortcutBox = QCheckBox("Space to Cap/Save", self)
        self.CapShortcutBox.stateChanged.connect(self.capShortcutToggle)
        self.CapShortcutBox.move(700, 240)
        self.CapShortcutBox.resize(120,15)
        self.CapAndSaveShortcut = QShortcut(QKeySequence("Space"),self)




        self.show()

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