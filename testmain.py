import sys
import threading
from PyQt5 import QtCore, QtGui, QtWidgets


from OpencvQt import Capture, Converter


config = {
    "DURATION_INT": 5
}



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        lay = QtWidgets.QVBoxLayout(central_widget)
        self.view = QtWidgets.QLabel()
        self.btn_start = QtWidgets.QPushButton("Start")
        self.btn_stop = QtWidgets.QPushButton("Stop")
        self.label_time = QtWidgets.QLabel()
        lay.addWidget(self.view, alignment=QtCore.Qt.AlignCenter)
        lay.addWidget(self.btn_start)
        lay.addWidget(self.btn_stop)

        lay.addWidget(self.label_time, alignment=QtCore.Qt.AlignCenter)
        self.view.setFixedSize(640, 400)
        self.show()
        self.init_camera()


    def init_camera(self):
        self.capture = Capture()
        self.converter = Converter()
        captureThread = QtCore.QThread(self)
        converterThread = QtCore.QThread(self)
        self.converter.setProcessAll(False)
        captureThread.start()
        converterThread.start()
        self.capture.moveToThread(captureThread)
        self.converter.moveToThread(converterThread)
        self.capture.frameReady.connect(self.converter.processFrame)
        self.converter.imageReady.connect(self.setImage)
        self.capture.started.connect(lambda: print("started"))
        self.btn_start.clicked.connect(self.capture.start)
        self.btn_stop.clicked.connect(self.capture.stop)

    @QtCore.pyqtSlot(QtGui.QImage)
    def setImage(self, image):
        self.view.setPixmap(QtGui.QPixmap.fromImage(image))





    def onFrameChanged(self, frame):
        if frame !=0:
            self.label_time.setNum(frame)
        else:
            self.label_time.setText("Smile...!")
            QtWidgets.QApplication.beep()
            image = QtGui.QImage(self.converter.image)
            ba = QtCore.QByteArray()
            buff = QtCore.QBuffer(ba)
            image.save(buff, "PNG")
            th = threading.Thread(target=send_email, args=(*self._info, ba))
            th.start()

    def closeEvent(self, event):
        self.capture.stop()
        super(MainWindow, self).closeEvent(event)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    sys.exit(app.exec_())