from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from PyQt5.QtGui import QImage
import numpy as np
import time

class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, PhotoData, parent=None, camera=0):
        QThread.__init__(self, parent=parent)
        self.isRunning = True
        self.PhotoData = PhotoData
        self.cap = None
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(camera)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)

    def run(self):

        while self.isRunning:
            if self.PhotoData.showVideoStream:
                ret, frame = self.cap.read()
                if ret:
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.PhotoData.set_photo(rgb_image)
                    if self.PhotoData.showFaceBox:
                        rgb_image = self.display(rgb_image,self.PhotoData.facedims)
                    p = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
                    self.changePixmap.emit(p)
            else:
                time.sleep(.25)

    def __del__(self):
        self.cap.release()


    def display(self, img, faces):
        disp_img = np.copy(img)
        if faces is not None and len(faces) == 4:
            x, y, w, h = faces
            cv2.rectangle(disp_img, (x, y), (x + w, y + h), (255, 127, 0), 2)
        return disp_img

