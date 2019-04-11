from PyQt5.QtCore import QThread, pyqtSignal
import cv2
from PyQt5.QtGui import QImage
import numpy as np

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

    def run(self):

        while self.isRunning:
            ret, frame = self.cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.PhotoData.set_photo(rgb_image)
                p = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
                self.changePixmap.emit(p)

    def __del__(self):
        self.cap.release()


    def display(self, img, faces, numImages, lastlabel, saving):
        disp_img = np.copy(img)
        if len(faces) == 1:
            x, y, w, h = faces[0]
            savestr = ""
            if saving:
                savestr = "SAVED"
            cv2.rectangle(disp_img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(disp_img, lastlabel + "  {}".format(str(numImages)) + savestr,
                        (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0))

        return disp_img

