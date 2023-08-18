

import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QAction, QFileDialog, QDesktopWidget, QMessageBox, QSizePolicy, QToolBar, QStatusBar, QDockWidget, QVBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon, QPixmap, QTransform, QPainter
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from actions_file import FileActions, TestAction
from actions_edit import EditActions
from actions_operation import OperationActions

class MarianaMenu():

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def createMenu(self, menu_bar):
        menu_bar.setNativeMenuBar(False)

        # Create file menu and add actions 
        file_menu = menu_bar.addMenu('File')
        self.fileOpen = FileActions(self.parent, "Open")
        #file_menu.addAction(self.fileOpen)
        self.fileSave = FileActions(self.parent, "Save")
        #file_menu.addAction(self.fileSave)
        file_menu.addSeparator()
        
        self.fileSettings = FileActions(self.parent, "Settings")
        file_menu.addAction(self.fileSettings)
        file_menu.addSeparator()

        self.filePrint = FileActions(self.parent, "Print")
        #file_menu.addAction(self.filePrint)
        file_menu.addSeparator()
        self.fileExit = FileActions(self.parent, "Exit")
        file_menu.addAction(self.fileExit)

        #edit_menu = menu_bar.addMenu('Edit')
        #self.editRotate90 = EditActions(self.parent, "Rotate 90")
        #edit_menu.addAction(self.editRotate90)
        #self.editRotate180 = EditActions(self.parent, "Rotate 180")
        #edit_menu.addAction(self.editRotate180)

        #Operation
        operation_menu = menu_bar.addMenu('Operation')
        self.opInfo = OperationActions(self.parent, "Board Info")
        self.opInfo.setEnabled(False)
        operation_menu.addAction(self.opInfo)
        self.opTemperature = OperationActions(self.parent, "Motor Info")
        self.opTemperature.setEnabled(False)
        operation_menu.addAction(self.opTemperature)
        operation_menu.addSeparator()

        self.opMicrostepResolution = OperationActions(self.parent, "Microstep Resolution")
        operation_menu.addAction(self.opMicrostepResolution)

        self.opStepMotor = OperationActions(self.parent, "Control Step Motor")
        #operation_menu.addAction(self.opStepMotor)
        operation_menu.addSeparator()

        self.opScan = OperationActions(self.parent, "Scan")
        self.opScan.setEnabled(False)
        #operation_menu.addAction(self.opScan)
        #operation_menu.addSeparator()
        self.opTakePhoto = OperationActions(self.parent, "Take Photo")
        operation_menu.addAction(self.opTakePhoto)

        self.opTakePhotoToClipboard = OperationActions(self.parent, "Take Photo To Clipboard")
        operation_menu.addAction(self.opTakePhotoToClipboard)

        self.opToVideo = OperationActions(self.parent, "To Video")
        #operation_menu.addAction(self.opToVideo)
        
        #self.opStartToRecordMovie = OperationActions(self.parent, "Start to Record Movie")
        #operation_menu.addAction(self.opStartToRecordMovie)

        #self.opStopToRecordMovie = OperationActions(self.parent, "Stop Recording Movie")
        #operation_menu.addAction(self.opStopToRecordMovie)


        navigation_menu = menu_bar.addMenu('Navigation')

        self.opLeft = OperationActions(self.parent, "Set to Left")
        navigation_menu.addAction(self.opLeft)
        self.opXMiddle = OperationActions(self.parent, "Set to X Middle")
        navigation_menu.addAction(self.opXMiddle)
        self.opRight = OperationActions(self.parent, "Set to Right")
        navigation_menu.addAction(self.opRight)

        self.opFront = OperationActions(self.parent, "Set to Front")
        navigation_menu.addAction(self.opFront)
        self.opYMiddle = OperationActions(self.parent, "Set to Y Middle")
        navigation_menu.addAction(self.opYMiddle)
        self.opBack = OperationActions(self.parent, "Set to Back")
        navigation_menu.addAction(self.opBack)

        self.opTop = OperationActions(self.parent, "Set to Top")
        navigation_menu.addAction(self.opTop)
        self.opZMiddle = OperationActions(self.parent, "Set to Z Middle")
        navigation_menu.addAction(self.opZMiddle)
        self.opBottom = OperationActions(self.parent, "Set to Bottom")
        navigation_menu.addAction(self.opBottom)

        navigation_menu.addSeparator()
        self.opCenter = OperationActions(self.parent, "Set to Center")
        navigation_menu.addAction(self.opCenter)
        self.opBottomLeft = OperationActions(self.parent, "Set to Bottom Left")
        navigation_menu.addAction(self.opBottomLeft)
        self.opBottomRight = OperationActions(self.parent, "Set to Bottom Right")
        navigation_menu.addAction(self.opBottomRight)
        self.opTopLeft = OperationActions(self.parent, "Set to Top Left")
        navigation_menu.addAction(self.opTopLeft)
        self.opTopRight = OperationActions(self.parent, "Set to Top Right")
        navigation_menu.addAction(self.opTopRight)



    