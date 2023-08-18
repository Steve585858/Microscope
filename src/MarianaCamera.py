
import os, sys, time
from pathlib import Path
import sys
#import cv2
#from PIL import Image

from PyQt5.QtWidgets import QErrorMessage, QPushButton, QStyle
from PyQt5.QtMultimedia import QCameraInfo, QCamera, QCameraImageCapture, QMultimedia
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtCore import Qt, QUrl, QIODevice, QObject
from PyQt5.QtGui import QImageWriter, QImage
from PyQt5.QtMultimedia import QMediaRecorder, QCamera, QCameraInfo, QAudioEncoderSettings, \
    QVideoEncoderSettings

class RecordButton(QPushButton):
    def __init__(self, parent= None):
        super(RecordButton,self).__init__(parent)
        self.parent = parent
        self.isRecording = False
        self.setIcon(self.style().standardIcon(QStyle.SP_DialogNoButton))
        self.setStyleSheet('QPushButton {background-color: #26c6da}')
        # self.setDisabled(False)

    def mousePressEvent(self, event):
        print(f'isRecording={self.isRecording}')
        self.toggleRecording()
        self.updateStyle(self.isRecording)

    def updateStyle(self, isRecording):
        if (isRecording):
            self.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
            # recording color: red
            self.setStyleSheet('QPushButton {background-color: #e57373}')
        else:
            self.setIcon(self.style().standardIcon(QStyle.SP_DialogNoButton))
            # non-recording color: cyan
            self.setStyleSheet('QPushButton {background-color: #26c6da}')        

    def toggleRecording(self):
        if self.isRecording:
            self.stopRecording()
            self.isRecording = False
            self.updateStyle(self.isRecording)
        else:
            self.startRecording()
            self.isRecording = True
            self.updateStyle(self.isRecording)

    def startRecording(self):
        cam = self.parent.marianaCamera
        cam.initVideo()
        cam.startRecording("output.mp4")

    def stopRecording(self):
        cam = self.parent.marianaCamera
        cam.stopRecording()

class MarianaCamera(QObject):
    def __init__(self, parent=QObject(), selectedCameraIndex=1):
        self.parent = parent
        self.selectedCameraIndex = selectedCameraIndex
        self.camera = None
        self.recorder = None
        self.photo_seq = 0
        print(f'self.selectedCameraIndex={self.selectedCameraIndex}')

        self.available_cameras = QCameraInfo.availableCameras() 
        if self.available_cameras: 
            for c in self.available_cameras:
                print(f'available camera: {c.deviceName} description={c.description}')
        else:
            print('no camera is available camera')

    def cameraWidget(self):
        self.viewfinder = QCameraViewfinder()
        self.viewfinder.show() 
        #self.initCamera()
        self.select_camera(self.selectedCameraIndex)
        return self.viewfinder
    
    def nextImageName(self):
        self.photo_seq += 1
        if self.photo_seq>=10000:
            self.photo_seq = 0
        return "img_%04d.jpg" % self.photo_seq
    
    def select_first_external_camera(self):
        cameras = QCameraInfo.availableCameras()
        for camera in cameras:
            if camera.position() == QCameraInfo.BackFace and not camera.isNull():
                # Found an external camera
                return camera

    def select_camera(self, i):
        c = self.available_cameras[self.selectedCameraIndex]
        if i==1:
            for camera in self.available_cameras:
                if not camera.isNull():
                    c = camera

        self.camera = QCamera(c)
        self.camera.setViewfinder(self.viewfinder)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        #self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
        self.camera.start()
        
        self.capture = QCameraImageCapture(self.camera)
        #self.capture.error.connect(lambda error_msg, error, msg: self.alert(msg))
        #self.capture.imageCaptured.connect(self.image_captured) 

    def initCamera(self):
        if self.camera:
            self.camera.load()
        else:
            self.camera = QCamera(self.available_cameras[self.selectedCameraIndex])
        self.camera.setViewfinder(self.viewfinder)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.recorder = QMediaRecorder(self.camera)
        self.camera.start()

        self.capture = QCameraImageCapture(self.camera)
        #self.capture.error.connect(lambda error_msg, error, msg: self.alert(msg))
        #self.capture.imageCaptured.connect(self.image_captured) 
    
    def image_captured(self, image_path, image):
        print(f'image_path={image_path}')
        #clipboard = QApplication.clipboard()
        #clipboard.setImage(image)

    def alert(self, msg):
        error = QErrorMessage(self)
        error.showMessage(msg)

    def generate_gif(self, gif_name, image_files):
        pass
        '''
        images = [Image.open(f) for f in image_files]
        images[0].save(gif_name, save_all=True, append_images=images[1:], duration=200, loop=0)
        '''

    def generate_video(self, video_name, image_files):    
        pass
        '''
        fourcc = cv2.VideoWriter_fourcc(*'DIVX') 

        print(f'file={image_files[0]}')

        frame = cv2.imread(image_files[0])
        height, width, channels = frame.shape

        fps = 20
        video = cv2.VideoWriter(video_name, fourcc, fps, (width, height))

        for image_file in image_files:
            video.write(cv2.imread(image_file))
            
        cv2.destroyAllWindows()
        video.release() 
        '''

    def generate_video2(self, file_name, image_files):
        writer = QImageWriter(file_name)
        writer.setFormat(b"mp4")
        writer.setQuality(90)
        writer.device().open(QIODevice.WriteOnly)

        # Write the images to the video file
        for image_file in image_files:
            image = QImage(image_file)
            writer.write(image)

        # Close the video file
        writer.device().close()

    def initVideo(self):
        if self.camera:
            self.camera.load()
        else:
            self.camera = QCamera(self.available_cameras[self.selectedCameraIndex])
        self.camera.setViewfinder(self.viewfinder)
        self.camera.setCaptureMode(QCamera.CaptureVideo)
        self.recorder = QMediaRecorder(self.camera)
        self.camera.start()

        audio = QAudioEncoderSettings()
        audio.setCodec("audio/amr")
        audio.setQuality(QMultimedia.NormalQuality)
        video = QVideoEncoderSettings()
        # video.setCodec("video/mp4")
        video.setQuality(QMultimedia.NormalQuality) #(Qt.HighQuality)
        video.setResolution(640, 480) #(1920, 1080)
        video.setFrameRate(30.0)
        # self.recorder.setAudioSettings(audio)
        self.recorder.setVideoSettings(video)
        self.recorder.setContainerFormat("mp4")

    def startRecording(self, filename):
        directory = os.path.abspath(str(os.getcwd()))
        abs_path = os.path.join(directory, filename)
        print(f'path={abs_path}')
        #self.recorder.setOutputLocation(QUrl(abs_path))
        self.recorder.setOutputLocation(QUrl.fromLocalFile(abs_path))
        self.recorder.record()

    def stopRecording(self):
        self.recorder.stop()