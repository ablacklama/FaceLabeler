from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtWidgets import QLabel


class editPictureLabel(QLabel):
    def __init__(self,parent):
        QLabel.__init__(self,parent.editingTab)
        self.move(260,50)
        self.resize(400,400)
        self.startingPoints = []
        self.started = False
        self.ended = False
        self.endingPoints = []
        self.currentPoints = []
        self.parent = parent
        self.painting = False

    def paintEvent(self, QPaintEvent):
        if self.parent.editResizeImageToggle.isChecked() and self.pixmap() is not None:
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.pixmap())
            if len(self.startingPoints ) > 0:
                pen = QPen(Qt.red, 3)
                painter.setPen(pen)

                if self.started and not self.ended:

                    points = (self.startingPoints[-1][0], self.startingPoints[-1][1],
                              self.currentPoints[0] - self.startingPoints[-1][0],
                              self.currentPoints[1] - self.startingPoints[-1][1])
                    painter.drawRect(*points)


                for start, end in zip(self.startingPoints, self.endingPoints):
                    points = (start[0], start[1],
                              end[0] - start[0],
                              end[1] - start[1])
                    painter.drawRect(*points)




        else:
            QLabel.paintEvent(self, QPaintEvent)

    def mousePressEvent(self, QMouseEvent):
        if self.painting:
            self.ended = False
            self.startingPoints.append((QMouseEvent.x(), QMouseEvent.y()))
            self.repaint()
            self.started = True

    def mouseMoveEvent(self, QMouseEvent):
        if self.painting:
            self.currentPoints = (QMouseEvent.x(), QMouseEvent.y())
            self.repaint()


    def mouseReleaseEvent(self, QMouseEvent):
        if self.painting:
            self.ended = True
            self.started = False
            self.endingPoints.append((QMouseEvent.x(), QMouseEvent.y()))
            self.repaint()
            self.currentPoints = []


    def startPainting(self):
        if len(self.parent.editorData.photosAndLabels) > 0:
            if self.painting:
                self.startingPoints = []
                self.endingPoints = []
                self.repaint()
            self.painting = not self.painting


    def test(self):
        print("not fucked")