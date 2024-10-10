import os
import sys
import cv2

# Определение базовой директории, в зависимости от того, выполняется ли программа из EXE
if getattr(sys, 'frozen', False):
    basedir = sys._MEIPASS  # Используем временную директорию, созданную PyInstaller
else:
    basedir = os.path.dirname(__file__)  # Используем исходную директорию скрипта

# Загружаем файлы моделей, используя базовую директорию
faceProto = os.path.join(basedir, "modelsAndWeights", "opencv_face_detector.pbtxt")
faceModel = os.path.join(basedir, "modelsAndWeights", "opencv_face_detector_uint8.pb")
genderProto = os.path.join(basedir, "modelsAndWeights", "gender_deploy.prototxt")
genderModel = os.path.join(basedir, "modelsAndWeights", "gender_net.caffemodel")
ageProto = os.path.join(basedir, "modelsAndWeights", "age_deploy.prototxt")
ageModel = os.path.join(basedir, "modelsAndWeights", "age_net.caffemodel")

# Настраиваем нейросети
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
genderList = ['Male', 'Female']
ageList = ['(0-2)', '(4-6)', '(8-12)', '(15-20)', '(25-32)', '(38-43)', '(48-53)', '(60-100)']

# Загружаем модели
faceNet = cv2.dnn.readNet(faceModel, faceProto)
genderNet = cv2.dnn.readNet(genderModel, genderProto)
ageNet = cv2.dnn.readNet(ageModel, ageProto)
