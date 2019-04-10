import cv2
import numpy as np
import csv
import os
from collections import Counter


class SaveData:
    def __init__(self, PhotoData, labelConfig="data/labelConfig.csv", labelList="data/faceLabels.csv", imageDir="data/Images"):
        self.imageDir = imageDir
        self.labels = []
        self.imageIndex = 0
        self.PhotoData = PhotoData
        self.labelListPath = labelList
        self.labelConfigPath = labelConfig
        self.faceImg = None


        with open(labelConfig, 'r+') as csvfile:
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

        if not os.path.isdir(self.imageDir):
            os.mkdir(self.imageDir)

        #print(self.labelCount, self.imageIndex)

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
                self.labelCount[self.currentLabel] += 1
        else:
            print("No Face Image")







class SharedData:
    def __init__(self):
        self.hasPhoto = False
        self.frame = None
        self.FaceImg = None
        self.NoFaceImg = cv2.imread("data/noface.png")
        self.greyscaletoggle = None
        self.facedims = None
        self.hasFaceImg = False


    def __str__(self):
        arrayargs = [self.hasPhoto, self.frame, self.FaceImg, self.NoFaceImg]
        for i in range(len(arrayargs)):
            if type(arrayargs[i]) is np.ndarray:
                arrayargs[i] = arrayargs[i].shape

        datastr = "hasPhoto={}\nphotoshape={}\nfaceimgshape={}\nnofaceimgshape={}".format(*arrayargs)
        return datastr

    def set_photo(self, photo):
        #print("photo set: " + str(photo.shape))
        self.hasPhoto = True
        self.frame = photo

    def get_frame(self):
        return self.frame

    def get_face_image(self):
        #print(self.hasFaceImg, self.FaceImg.shape)
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