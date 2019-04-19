from PyQt5.QtCore import QThread
import cv2
import numpy as np
import time


class FaceDetectionThread(QThread):

    #changePixmap = pyqtSignal(QImage)

    def __init__(self, PhotoData, parent=None):
        QThread.__init__(self, parent=parent)
        self.PhotoData = PhotoData
        self.haar_cascade = cv2.CascadeClassifier(
            'data/haarcascade/haarcascade_frontalface_default.xml')


    def biggerFace(self,faces):
        faces = np.array(faces)

        if faces.shape[0] < 2:
            return faces
        else:

            biggestFace = None
            biggestSize = 0
            for face in faces:
                size = face[2] * face[3]
                if size > biggestSize:
                    biggestFace = face
                    biggestSize = size
            return [biggestFace]

    def getFaceImg(self):
        if self.PhotoData.hasPhoto:
            img = self.PhotoData.get_frame()

            #img = cv2.flip(img, 1)
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

            faces = self.haar_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
            faces = self.biggerFace(faces)

            if len(faces) == 1:
                x, y, w, h = faces[0]
                self.PhotoData.facedims = faces[0]
                if self.PhotoData.get_graytoggle_state():
                    faceimg = gray[y:y + h, x:x + w]
                else:
                    faceimg = img[y:y + h, x:x + w]
                return True, np.copy(faceimg)
            else:
                self.PhotoData.facedims = None

        return False, None



    def run(self):
        while True:
            if self.PhotoData.showVideoStream:
                self.PhotoData.set_face_image(*self.getFaceImg())
                time.sleep(self.PhotoData.detectionDelay)
            else:
                time.sleep(.5)