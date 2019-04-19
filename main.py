import sys
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import QAction, QDesktopWidget, QShortcut, QDialog, QDialogButtonBox, QApplication, QMainWindow
from PyQt5.QtGui import QPixmap, QImage,QKeySequence, QIcon
from PyQt5.uic import loadUi
from video import VideoThread
from dataclass import SharedPhotoData, SaveData, EditorData
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
            self.editorData = EditorData(self)
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

    def changeTabs(self, idx, initializing=False):

        currentIdx = self.mainTabs.currentIndex()
        if currentIdx == idx:
            return

        if currentIdx == 0:
            self.PhotoData.showVideoStream = False
        elif idx == 0:
            self.PhotoData.showVideoStream = True

        if idx == 1:
            self.editorData._init(config["CUSTOM"]["imageDir"],
            config["CUSTOM"]["labelListPath"],
            config["CUSTOM"]["labelConfigPath"])
            self.editDownShortcut.activated.connect(lambda: self.editorData.changeSelectedLabel(1))
            self.editUpShortcut.activated.connect(lambda: self.editorData.changeSelectedLabel(-1))
            self.editRightShortcut.activated.connect(self.picForward)
            self.editLeftShortcut.activated.connect(self.picBack)
        elif currentIdx == 1 and not initializing:
            self.editDownShortcut.disconnect()
            self.editUpShortcut.disconnect()
            self.editRightShortcut.disconnect()
            self.editLeftShortcut.disconnect()
            self.editorData.saveCSV()

        self.mainTabs.setCurrentIndex(idx)
        return

    def createMenu(self):
        settingsAction = QAction("settings",self)
        settingsAction.triggered.connect(self.openSettings)
        editorTabAction = QAction("edit", self)
        editorTabAction.triggered.connect(lambda: self.changeTabs(1))
        captureTabAction = QAction("capture", self)
        captureTabAction.triggered.connect(lambda: self.changeTabs(0))


        self.mainMenu.addAction(settingsAction)
        self.mainMenu.addAction(captureTabAction)
        self.mainMenu.addAction(editorTabAction)

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
        self.changeTabs(0, initializing=True)

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

        #EDITOR LABEL SELECTION
        self.editLabelSelector.addItems(self.saver.labels)
        #self.editLabelSelector.currentIndexChanged.connect(self.EditLabelChange)

        #EDITOR PICTURE NAVIGATION
        self.picForward = lambda: self.editorData.picLeftRight(1)
        self.picBack = lambda: self.editorData.picLeftRight(-1)
        self.editPicNav.button(QDialogButtonBox.Yes).setText("<--")
        self.editPicNav.button(QDialogButtonBox.No).setText("-->")
        self.editPicNav.button(QDialogButtonBox.Yes).clicked.connect(self.picBack)
        self.editPicNav.button(QDialogButtonBox.No).clicked.connect(self.picForward)
        self.editRightShortcut = QShortcut(QKeySequence("Right"), self)
        self.editLeftShortcut = QShortcut(QKeySequence("Left"), self)
        self.editUpShortcut = QShortcut(QKeySequence("Up"), self)
        self.editDownShortcut = QShortcut(QKeySequence("Down"), self)

        #EDITOR LABEL SAVE BUTTON
        self.editSaveButton.clicked.connect(self.editorData.saveLabel)

        #PATH LIST
        self.pathList.currentItemChanged.connect(lambda:self.editorData.changePicture(
                                                    self.pathList.currentRow()))

        #EDITOR DELETE KEY
        self.editDelete.clicked.connect(self.editorData.deleteCurrent)


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
        with open("data/ui/settings.ini", "w") as configFile:
            config.write(configFile)
        raise(e)

    sys.exit()