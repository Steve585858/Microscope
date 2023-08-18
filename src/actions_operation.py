from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon, QPixmap, QTransform, QPainter
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QAction, QDialog, QFileDialog)
from PyQt5.QtGui import QIcon, QImage, QPixmap, QTransform, QPainter
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QRunnable, QTimer
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from moviepy.editor import VideoFileClip
import numpy as np


from PIL import Image

import os
import time
import traceback, sys
from pathlib import Path

from PyQt5.QtCore import Qt, QThread, pyqtSignal

from dialogs_info import InfoDialog
from dialogs_led import LedDialog
from dialogs_motor import MotorDialog
from MarianaActions import MarianaActions
from dialogs_settings import MicrostepResolutionDialog


from qasync import asyncSlot

#https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/

class OperationActions(MarianaActions):
    def __init__(self, parent, actionName):
        super().__init__(parent, actionName)
        self.parent = parent
        if(self.actionName=="Board Info"):
            self.createSubMenu(actionName, 100, 'Retrieve Arduino board information')
        elif(self.actionName=="Motor Info"):
            self.createSubMenu(actionName, 200, 'Retrieve motor information')
        elif(self.actionName=="Control Step Motor"):
            self.createSubMenu(actionName, 101, 'Control Step Motor')
        elif(self.actionName=="Microstep Resolution"):
            self.createSubMenu(actionName, 102, 'Microstep Resolution')
        elif(self.actionName=="Scan"):
            self.createSubMenu(actionName, 103, 'Scan stage')
        elif(self.actionName=="Take Photo"):
            self.createSubMenu(actionName, 110, 'Save the current view as an image', None, 'screenshot.png')
        elif(self.actionName=="Take Photo To Clipboard"):
            self.createSubMenu(actionName, 111, 'Save the current view as an image to clipboard', None, 'screenshotToClipBoard.png')
        elif(self.actionName=="To Video"):
            self.createSubMenu(actionName, 112, 'To Video', None, 'movie.png')
        elif(self.actionName=="Stop Recording Movie"):
            self.createSubMenu(actionName, 120, 'Stop Recording Movie', None, 'movie.png')
        elif(self.actionName=="Start to Record Movie"):
            self.createSubMenu(actionName, 120, 'Start to Record Movie', None, 'movie.png')
        elif(self.actionName=="Set to Center"):
            self.createSubMenu(actionName, 201, 'Set to Center', None, 'goto-0.png')
        elif(self.actionName=="Set to Bottom Left"):
            self.createSubMenu(actionName, 202, 'Set to Bottom Left', None, 'goto-4.png')
        elif(self.actionName=="Set to Bottom Right"):
            self.createSubMenu(actionName, 203, 'Set to Bottom Right', None, 'goto-3.png')
        elif(self.actionName=="Set to Top Left"):
            self.createSubMenu(actionName, 204, 'Set to Top Left', None, 'goto-1.png')
        elif(self.actionName=="Set to Top Right"):
            self.createSubMenu(actionName, 205, 'Set to Top Right', None, 'goto-2.png')
        elif(self.actionName=="Set to Left"):
            self.createSubMenu(actionName, 210, 'Set to Left', None, 'arrows_left_edge.png')
        elif(self.actionName=="Set to X Middle"):
            self.createSubMenu(actionName, 211, 'Set to X Middle', None, 'goto-5.png')
        elif(self.actionName=="Set to Right"):
            self.createSubMenu(actionName, 212, 'Set to Right', None, 'arrows_right_edge.png')
        elif(self.actionName=="Set to Front"):
            self.createSubMenu(actionName, 220, 'Set to Front', None, 'arrows_up_edge.png')
        elif(self.actionName=="Set to Y Middle"):
            self.createSubMenu(actionName, 221, 'Set to Y Middle', None, 'goto-6.png')
        elif(self.actionName=="Set to Back"):
            self.createSubMenu(actionName, 222, 'Set to Back', None, 'arrows_down_edge.png')
        elif(self.actionName=="Set to Top"):
            self.createSubMenu(actionName, 230, 'Set to Top', None, 'arrows_z_up_edge.png')
        elif(self.actionName=="Set to Z Middle"):
            self.createSubMenu(actionName, 231, 'Set to Z Middle', None, 'goto-7.png')
        elif(self.actionName=="Set to Bottom"):
            self.createSubMenu(actionName, 232, 'Set to Bottom', None, 'arrows_z_down_edge.png')

    def handle_action(self, actionId):
        if actionId==100:
            self.boardInfo(self.parent)
        elif actionId==101:
            self.controlStepMotor(self.parent)
        elif actionId==102:
            self.setMicrostepResolution(self.parent)
        elif actionId==103:
            pass
        elif actionId==110:
            self.take_photo()
        elif actionId==111:
            self.take_photo_to_clipboard()
        elif actionId==112:
            self.generate_video_gif(False)
        elif actionId==120:
            self.record_movie()
        elif actionId==201: #Zero
            self.navigation([1, 1, 0], [True, True, False])
        elif actionId==202: #Bottom Left
            self.navigation([0, 0, 0], [True, True, False])
        elif actionId==203: #Bottom Right
            self.navigation([2, 0, 0], [True, True, False])
        elif actionId==204: #Top Left
            self.navigation([0, 2, 0], [True, True, False])
        elif actionId==205: #Top Right
            self.navigation([2, 2, 0], [True, True, False])
        elif actionId==210:
            self.navigation([0, 0, 0], [True, False, False])
        elif actionId==211:
            self.navigation([1, 1, 1], [True, False, False])
        elif actionId==212:
            self.navigation([2, 2, 2], [True, False, False])
        elif actionId==220:
            self.navigation([0, 0, 0], [False, True, False])
        elif actionId==221:
            self.navigation([1, 1, 1], [False, True, False])
        elif actionId==222:
            self.navigation([2, 2, 2], [False, True, False])
        elif actionId==230:
            self.navigation([0, 0, 0], [False, False, True])
        elif actionId==231:
            self.navigation([0, 0, 1], [False, False, True])
        elif actionId==232:
            self.navigation([2, 2, 2], [False, False, True])
    
    def generate_video_gif(self, isVideo): 
        parent_dir = os.path.abspath(str(os.getcwd()))
        directory = os.path.join(parent_dir, "test11")
        files = os.listdir(directory)
        files.sort()
        # Create a list of absolute file paths
        filesWithPath = [os.path.join(directory, f) for f in files]   
        if isVideo: 
            video_filename = os.path.join(parent_dir, "test1.avi")
            self.parent.marianaCamera.generate_video(video_filename, filesWithPath)
        else:
            gif_filename = os.path.join(parent_dir, "test11.gif")
            self.parent.marianaCamera.generate_gif(gif_filename, filesWithPath)

    def take_photo3(self):
        self.timer = QTimer()
        self.timer.setInterval(100)  
        self.timer.timeout.connect(self.save_photo)
        self.timer.start()

    def save_photo(self): 
        directory = os.path.join(os.path.abspath(str(os.getcwd())), "test1")
        filename = self.parent.marianaCamera.nextImageName()
        abs_filename = os.path.join(directory, filename)
        print(f'file={abs_filename}')
        self.parent.marianaCamera.capture.capture(abs_filename)
        if self.parent.marianaCamera.photo_seq>=500:
            self.timer.stop()
            self.timer.deleteLater()

            
    @asyncSlot()
    async def navigation(self, positionIdList, enableMotorList):
        board = self.parent.board
        if board is None:
            return
        for index, motorName in enumerate(self.parent.motorNames):
            if not enableMotorList[index]:
                continue

            position = 0
            positionId = positionIdList[index]
            if positionId==1:
                position = int(self.parent.config.get(motorName, 'edge'))//2
            elif positionId==2:
                position = int(self.parent.config.get(motorName, 'edge')) 
            
            motor = self.parent.motors[motorName]

            await board.stepper_move_to(motor, position)

            speed = int(self.parent.preference.get(motorName, "speed"))
            await board.stepper_set_speed(motor, speed)

            await board.stepper_run_speed_to_position(motor, completion_callback=self.the_callback)


    async def the_callback(self, data):
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
        print(f'Motor {data[1]}  motion completed at: {date}.')

    
    def take_photo(self): 
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        path = self.parent.preference.get("Photo", "path")
        name = os.path.join(path,"%s.jpg" % (timestamp))
        #image_capture.capture(QUrl.fromLocalFile("path/to/save/image.jpg"))
       #self.parent.capture.capture(name)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.parent, "Save As", name, 
                                                  "All Files (*);;Image Files (*.jpg)", options=options)
        
        if fileName:
            self.parent.marianaCamera.capture.capture(fileName)

    def take_photo_to_clipboard1(self):
        path = self.parent.preference.get("Photo", "path")
        name = os.path.join(path,".tmp.jpg")
        os.remove(name)        
        time.sleep(5)
        self.parent.marianaCamera.capture.capture(name)
        image = QImage(name)
        pixmap = QPixmap.fromImage(image)
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        #self.parent.marianaCamera.capture.deleteLater()
    def take_photo_to_clipboard(self):
        self.parent.marianaCamera.capture.capture()

    def record_movie(self): 
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        path = self.parent.preference.get("Photo", "path")
        name = os.path.join(path,"%s.jpg" % (timestamp))
        #image_capture.capture(QUrl.fromLocalFile("path/to/save/image.jpg"))
       #self.parent.capture.capture(name)
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.parent, "Save As", name, 
                                                  "All Files (*);;Image Files (*.jpg)", options=options)
        
        if fileName:
            self.parent.marianaCamera.capture.capture(fileName)
                
    def boardInfo(self, parent):
        print("Board")
        dialog = InfoDialog(parent, "Board Info")
        dialog.setFixedSize(800, 600)
        dialog.show()

    def controlLed(self, parent):
        print("Control LED")
        dialog = LedDialog(parent, "LED Control")
        dialog.setFixedSize(300, 200)
        dialog.show()

    def setMicrostepResolution(self, parent):
        print("Microstep Resolution")
        if self.parent.board:
            dialog = MicrostepResolutionDialog(parent, "Microstep Resolution")
            dialog.setFixedSize(800, 550)
            dialog.show()
    
    def controlStepMotor(self, parent):
        print("Control Step Motor")
        dialog = MotorDialog(parent, "Step Motor Control")
        dialog.setFixedSize(1000, 700)
        dialog.show()
        
    def scanStage(self, parent):
        print("scan")
        worker = Worker(self.movieClipToImage) # Any other args, kwargs are passed to the run function
        worker.signals.result.connect(self.display_scan_results)
        worker.signals.finished.connect(self.thread_complete)
        worker.signals.progress.connect(self.progress_fn)
        parent.threadpool.start(worker)

    def moveToLeft(self, parent):
        print("moveToLeft")
    
    def moveToRight(self, parent):
        print("moveToRight")
    
    def progress_fn(self, n):
        count = n[0]
        array = n[1]
        #print("%d%% done" % count)
        self.update_pixmap(array, self.parent)

    def display_scan_results(self, n):
        count = n[0]
        array = n[1]
        print("Total count: %d" % (count))
        self.update_pixmap(array, self.parent)

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def movieClipToImage(self, progress_callback):
        inputFileName = os.path.join(self.data_path, 'spidermanTrailer.mp4')
        clip = VideoFileClip(inputFileName)
        print('%s is %i fps, for %i seconds at %s' % (inputFileName, clip.fps, clip.duration, clip.size))
        #clip = clip.subclip(20, 30)
        #print('subclip is %i fps, for %i seconds at %s' % (clip.fps, clip.duration, clip.size))

        # np.zeros is how we generate an empty ndarray
        img = np.zeros((clip.size[1], clip.size[0], 3), dtype='uint8')

        currentX = 0
        slitwidth = 1

        slitpoint = clip.size[0] // 2

        # generate our target fps with width / duration
        target_fps = clip.size[0] / clip.duration

        for i in clip.iter_frames(fps=target_fps, dtype='uint8'):
            if currentX < (clip.size[0] - slitwidth):
                img[:,currentX:currentX + slitwidth,:] = i[:,slitpoint:slitpoint+slitwidth,:]
            currentX += slitwidth
            #progress_callback.emit((currentX, img))
            if currentX%10==0:
                progress_callback.emit((currentX, img))
            #self.update_pixmap(img, parent)
        return (currentX, img)

    def update_pixmap(self, array, parent):
        parent = self.parent
        '''
        converts a NumPy array to a QPixmap object and update display
        '''
        height, width = array.shape[:2]
        bytes_per_line = 3 * width
        q_image = QImage(array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        parent.image = QPixmap.fromImage(q_image)

        parent.image_label.setPixmap(parent.image.scaled(parent.image_label.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
    

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(tuple)
    progress = pyqtSignal(tuple)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done
