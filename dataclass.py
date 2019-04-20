import cv2
import numpy as np
import csv
import os
from collections import Counter
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QListWidgetItem
from helper import showInvalidPaths



class SaveData:
    def __init__(self, PhotoData, config):
        self.PhotoData = PhotoData
        self._init(config["CUSTOM"]["imageDir"],
            config["CUSTOM"]["labelListPath"],
            config["CUSTOM"]["labelConfigPath"])

    def _init(self,imageDir, labelListPath, labelConfigPath):
        invalidPaths = showInvalidPaths([imageDir,labelListPath,labelConfigPath],
                                        extraText="configure these in settings the app will crash\n\n")

        self.imageDir = imageDir
        self.labels = []
        self.imageIndex = 0
        self.labelListPath = labelListPath
        self.labelConfigPath = labelConfigPath
        self.faceImg = None
        if len(invalidPaths) < 1:
            with open(self.labelConfigPath, 'r+') as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                for row in reader:
                    self.labels.append(row[1])

            self.labels = np.array(self.labels)
            self.currentLabel = self.labels[0]

            if os.path.isfile(self.labelListPath):
                with open(self.labelListPath, 'r') as file:
                    l = np.array(list(csv.reader(file)))
                    if l.shape[0] > 0:
                        self.labelCount = Counter(l[:, 1])
                        self.imageIndex = int(l[-1, 0][4:-4]) + 1
                    else:
                        self.labelCount = {}
            else:
                self.labelCount = Counter()

            for key in self.labels:
                if key not in self.labelCount:
                    self.labelCount[key] = 0

            if not os.path.isdir(self.imageDir):
                os.mkdir(self.imageDir)

    def get_paths(self):
        return [self.imageDir,
        self.labelListPath,
        self.labelConfigPath]

    def set_face_image(self,image):
        self.faceImg = image
        return

    def change_label(self,index):
        self.currentLabel = self.labels[index]
        return

    def save_current(self):
        if self.faceImg is not None:
            with open(self.labelListPath, 'a+') as csvfile:
                csvFileWriter = csv.writer(csvfile, delimiter=',',
                                                quotechar='|', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                filename = "face" + str(self.imageIndex) + ".png"
                filepath = self.imageDir + "/" + filename
                cv2.imwrite(filepath,self.faceImg)
                csvFileWriter.writerow([filename,self.currentLabel])
                self.imageIndex += 1
                self.faceImg = None
                self.PhotoData.hasFaceImg = False
                self.labelCount[self.currentLabel] += 1

        else:
            #TODO replace with betting error
            print("No Face Image")




class SharedPhotoData:
    def __init__(self, config):
        self.hasPhoto = False
        self.frame = None
        self.FaceImg = None
        self.NoFaceImg = cv2.imread("data/ui/noface.png")
        self.NoFaceImg = cv2.cvtColor(self.NoFaceImg, cv2.COLOR_BGR2RGB)
        self.greyscaletoggle = None
        self.facedims = None
        self.hasFaceImg = False
        self.showFaceBox = False
        self.showVideoStream = True
        self.config = config
        self.detectionDelay = float(config["CUSTOM"]["detectionDelay"])


    def __str__(self):
        arrayargs = [self.hasPhoto, self.frame, self.FaceImg, self.NoFaceImg]
        for i in range(len(arrayargs)):
            if type(arrayargs[i]) is np.ndarray:
                arrayargs[i] = arrayargs[i].shape

        datastr = "hasPhoto={}\nphotoshape={}\nfaceimgshape={}\nnofaceimgshape={}".format(*arrayargs)
        return datastr

    def set_photo(self, photo):
        self.hasPhoto = True
        self.frame = photo

    def get_frame(self):
        return self.frame

    def get_face_image(self):
        if self.hasFaceImg:
            return self.hasFaceImg, np.copy(self.FaceImg)
        else:
            return self.hasFaceImg, self.NoFaceImg

    def set_face_image(self,ret_val, img):
        self.hasFaceImg = ret_val
        self.FaceImg = img

    def set_graytoggle_state(self,state):
        self.greyscaletoggle = state

    def get_graytoggle_state(self):
        return self.greyscaletoggle




class EditorData:
    def __init__(self, parent, config):
        self.photosAndLabels = []
        self.currentIdx = -1
        self.frameWidth = 400
        self.frameHeight = 400
        self.parent = parent
        self.resizeToFullscreen = 0
        self.listLength = 0
        self.config = config

    def _init(self,imageDir, labelListPath, labelConfigPath):
        invalidPaths = showInvalidPaths([imageDir,labelListPath,labelConfigPath],
                                        extraText="configure these in settings the app will crash\n\n")
        self.frameWidth = self.parent.editPicDisplay.frameGeometry().width()
        self.frameHeight = self.parent.editPicDisplay.frameGeometry().height()
        self.parent.pathList.clear()
        self.imageDir = imageDir
        self.labels = []
        self.imageIndex = 0
        self.labelListPath = labelListPath
        self.labelConfigPath = labelConfigPath
        self.faceImg = None
        if len(invalidPaths) < 1:
            with open(self.labelConfigPath, 'r+') as csvfile:
                reader = csv.reader(csvfile, delimiter=",")
                for row in reader:
                    self.labels.append(row[1])

            self.labels = np.array(self.labels)
            self.currentLabel = self.labels[0]

            if os.path.isfile(self.labelListPath):
                with open(self.labelListPath, 'r') as file:
                    self.photosAndLabels = np.array(list(csv.reader(file)))
                    self.listLength = len(self.photosAndLabels)
                    if self.photosAndLabels.shape[0] > 0:
                        self.labelCount = Counter(self.photosAndLabels[:, 1])
                        #self.imageIndex = int(self.photosAndLabels[-1, 0][4:-4]) + 1
                    else:
                        self.labelCount = {}
            else:
                #TODO make this better
                print("nothing to show")

            for key in self.labels:
                if key not in self.labelCount:
                    self.labelCount[key] = 0
        self.changePicture(self.listLength - 1)
        for path,label in self.photosAndLabels:
            self.parent.pathList.addItem(QListWidgetItem("{} : {}".format(path,label)))
        return

    def reloadPicture(self):
        if self.currentIdx < 0 or self.currentIdx >= len(self.photosAndLabels):
            return
        self.picLabel = self.photosAndLabels[self.currentIdx]

        path = os.path.join(self.imageDir, self.picLabel[0])
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if image is not None:
            if image.shape[0] > self.frameHeight or image.shape[1] > self.frameWidth or self.resizeToFullscreen:
                image = cv2.resize(image, (self.frameHeight, self.frameWidth))

            qimg = QImage(image.data, image.shape[1], image.shape[0],
                          image.shape[1], QImage.Format_Grayscale8)
            self.parent.editPicDisplay.setPixmap(QPixmap.fromImage(qimg))
        return

    def changePicture(self,newidx):
        if newidx < 0 or newidx >= len(self.photosAndLabels):
            print('no pictures?')
            return
        self.picLabel = self.photosAndLabels[newidx]
        if not self.currentIdx == newidx:
            path = os.path.join(self.imageDir,self.picLabel[0])
            image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if image is not None:
                if image.shape[0] > self.frameHeight or image.shape[1] > self.frameWidth or self.resizeToFullscreen:
                    image = cv2.resize(image, (self.frameHeight, self.frameWidth))

                qimg = QImage(image.data, image.shape[1], image.shape[0],
                              image.shape[1], QImage.Format_Grayscale8)
                self.parent.editPicDisplay.setPixmap(QPixmap.fromImage(qimg))

        self.parent.picLabelDisplay.setText(self.picLabel[1])
        self.parent.picPathDisplay.setText(self.picLabel[0])
        self.currentIdx = newidx
        return

    def picLeftRight(self, idxAdd):
        self.parent.editorData.changePicture(self.currentIdx + idxAdd)
        self.parent.pathList.setCurrentRow(self.currentIdx)

    def saveCSV(self):
        with open(self.labelListPath, 'w', newline='') as outf:
            writer = csv.writer(outf)
            writer.writerows(self.photosAndLabels)
        return

    def saveLabel(self):
        if self.listLength > 0:
            label = self.parent.editLabelSelector.currentText()
            path = self.photosAndLabels[self.currentIdx][0]
            self.parent.pathList.currentItem().setText("{} : {}".format(path,label))
            self.photosAndLabels[self.currentIdx][1] = label
            self.changePicture(self.currentIdx)
        return

    def changeSelectedLabel(self,addIdx):
        idx = self.parent.editLabelSelector.currentIndex()
        idx = (idx + addIdx)%len(self.labels)
        self.parent.editLabelSelector.setCurrentIndex(idx)
        return

    def deleteCurrent(self):
        pathlabel = self.photosAndLabels[self.currentIdx]
        path = os.path.join(self.imageDir, pathlabel[0])
        if os.path.exists(path):
            os.remove(path)
        self.listLength -= 1
        self.photosAndLabels = np.delete(self.photosAndLabels,[self.currentIdx], 0)
        self.parent.pathList.takeItem(self.currentIdx)
        self.currentIdx = self.parent.pathList.currentRow()
