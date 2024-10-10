from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QMainWindow, QLabel, QPushButton
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtCore import QSize, QThread,  QTimer, Qt, QRectF
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter, QBrush, QColor
import sys
import cv2
import datetime
import os
import getpass

from maw import *

class VideoPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout(self)
        self.video_label = QLabel("Wait... Video will be here")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.video_label)
        self.aiflag = 0

        self.video = cv2.VideoCapture(0, cv2.CAP_ANY)
        self.timer = QTimer()

        self.timer.timeout.connect(self.update_frame)
        self.timer.start(40)

    def highlight_face(self, net, frame, conf_threshold=0.7):
        frameOpencvDnn = frame.copy()
        frameHeight = frameOpencvDnn.shape[0]
        frameWidth = frameOpencvDnn.shape[1]
        blob = cv2.dnn.blobFromImage(frameOpencvDnn, 1.0, (300, 300), [104, 117, 123], True, False)
        net.setInput(blob)
        detections = net.forward()
        faceBoxes = []

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > conf_threshold:
                x1 = int(detections[0, 0, i, 3] * frameWidth)
                y1 = int(detections[0, 0, i, 4] * frameHeight)
                x2 = int(detections[0, 0, i, 5] * frameWidth)
                y2 = int(detections[0, 0, i, 6] * frameHeight)
                faceBoxes.append([x1, y1, x2, y2])
                cv2.rectangle(frameOpencvDnn, (x1, y1), (x2, y2), (0, 255, 0), int(round(frameHeight / 150)), 8)

        return frameOpencvDnn, faceBoxes

    def update_frame(self):
        hasFrame, frame = self.video.read()
        if hasFrame:
            if self.aiflag == 0:
                resultImg = frame
            else:
                resultImg, faceBoxes = self.highlight_face(faceNet, frame)

                if not faceBoxes:
                    resultImg = frame

                for faceBox in faceBoxes:
                    face = frame[max(0, faceBox[1]):
                                 min(faceBox[3], frame.shape[0] - 1), max(0, faceBox[0])
                                                                      :min(faceBox[2], frame.shape[1] - 1)]
                    blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False)
                    genderNet.setInput(blob)
                    genderPreds = genderNet.forward()
                    gender = genderList[genderPreds[0].argmax()]

                    ageNet.setInput(blob)
                    agePreds = ageNet.forward()
                    age = ageList[agePreds[0].argmax()]

                    cv2.putText(resultImg, f'{gender}, {age}', (faceBox[0], faceBox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                                (0, 255, 255), 2, cv2.LINE_AA)

            show_v = resultImg
            image = cv2.cvtColor(show_v, cv2.COLOR_BGR2RGB)
            h, w, ch = image.shape
            bytes_per_line = ch * w
            qimage = QImage(image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap(qimage)
            rounded_pixmap = self.get_rounded_pixmap(pixmap, radius=30)
            self.video_label.setPixmap(rounded_pixmap)

    def get_rounded_pixmap(self, pixmap, radius):
        size = pixmap.size()
        rounded = QPixmap(size)
        rounded.fill(Qt.GlobalColor.transparent)

        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        brush = QBrush(pixmap)

        rect = QRectF(0, 0, size.width(), size.height())
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        painter.end()
        return rounded

    def capture_image(self):
        ret, frame = self.video.read()

        if not os.path.exists(download_path):
            os.makedirs(download_path)

        if ret:
            time = datetime.datetime.now()
            time = str(time)
            time = time.replace('.', '_').replace(':', '_').replace(' ', '_')
            cv2.imwrite(f'{download_path}/{time}.png', frame)


class ControlPanel(QWidget):
    def __init__(self, video_widget):
        super().__init__()

        self.video_widget = video_widget

        self.border_style = "border-width: 2px; border-radius: 10px; border-style: inset"

        self.capture_btn = QPushButton('Make photo')
        self.capture_btn.setStyleSheet(f"background-color: #2372e8; color: #ffffff; {self.border_style}; border-color: #2372e8")#border-width: 0.5px; border-color: #ffffff; border-radius: 20px; border-style: outset;")
        self.capture_btn.clicked.connect(self.video_widget.capture_image)

        self.useai_btn_base_style = f"background-color: #14db71; color: #ffffff; {self.border_style}; border-color: #14db71"
        self.useai_btn_base_text = "Use AI (off)"

        self.useai_btn = QPushButton(self.useai_btn_base_text)
        self.useai_btn.setCheckable(True)
        self.useai_btn.setStyleSheet(self.useai_btn_base_style)
        self.useai_btn.clicked.connect(self.second_btn_usage)

        layout = QHBoxLayout(self)
        layout.addWidget(self.capture_btn)
        layout.addWidget(self.useai_btn)

    def second_btn_usage(self):
        self.change_btn_style_2()

    def change_btn_style_2(self):
        if self.useai_btn.isChecked():
            self.useai_btn.setText("Use AI (on)")
            self.useai_btn.setStyleSheet(f"background-color: #dbb014; color: #ffffff; {self.border_style}; border-color: #dbb014")
            self.video_widget.aiflag = 1
        else:
            self.useai_btn.setText(self.useai_btn_base_text)
            self.useai_btn.setStyleSheet(self.useai_btn_base_style)
            self.video_widget.aiflag = 0

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        background_image_path = os.path.join(basedir, 'media', 'back.png')
        background_image_path_str = str(background_image_path).replace("\\", "/")

        self.setStyleSheet( 'MainWindow {background-image: url(' + background_image_path_str + ');}' )
        self.setWindowTitle("Camera Streaming")
        self.setFixedSize(QSize(800, 600))

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.video_widget = VideoPanel()
        layout.addWidget(self.video_widget)

        self.control_panel = ControlPanel(self.video_widget)
        layout.addWidget(self.control_panel)


if __name__ == "__main__":
    user_name = getpass.getuser()
    download_path = f"C:/Users/{user_name}/Pictures/CameraStreamingApp"
    basedir = os.path.dirname(__file__)

    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(os.path.join(basedir, 'media', 'logo2.ico')))

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())