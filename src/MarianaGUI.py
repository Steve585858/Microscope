
import os, sys, time
from pathlib import Path
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QStyleFactory, QFileDialog, QDesktopWidget, QErrorMessage, QMessageBox, QSizePolicy, QToolBar, QStatusBar, QDockWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QPushButton)
from PyQt5.QtGui import QIcon, QPixmap, QTransform, QPainter
from PyQt5.QtCore import Qt, QSize, QRect, QThreadPool
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog


from MarianaMenu import MarianaMenu
from MarianaCamera import MarianaCamera, RecordButton
from telemetrix_aio import telemetrix_aio

from config import Config, UserPreference
from MarianaThreadPool import Worker

from MotorControlWidget import MotorControlWidget

import asyncio
from qasync import QEventLoop, asyncSlot

class WiderSeparator(QLabel):
    def __init__(self, width):
        super().__init__()
        self.setFrameShape(QLabel.VLine)
        self.setFrameShadow(QLabel.Sunken)
        self.setFixedWidth(width)
        #self.setFixedHeight(20)

class MarianaGUI(QMainWindow):

    def __init__(self):
        super().__init__()
        self.version = '0.0.1'
        self.path_root = Path(os.path.abspath(__file__)).parents[0]
        self.path_parent = Path(os.path.abspath(__file__)).parents[1]
        self.path_images = os.path.join(self.path_root, 'images')
        self.path_examples = os.path.join(self.path_parent, 'examples')
        self.path_resources = os.path.join(self.path_parent, 'resources')
        self.config = Config(self.path_root, 'config.ini')
        user_root = os.path.join(os.path.expanduser("~"), '.mariana')
        self.preference = UserPreference(user_root, "user_preference.ini")

        self.motors = {}
        self.motorNames = ["motor1", "motor2", "motor3"]
        self.pinNames = ["steppin", "dirpin", "ms1pin", "ms2pin", "ms3pin"]
        self.joystickName = "joystick"
        self.joystickPinNames = ["sw", "vrx", "vry"]

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        try:
            #self.board = telemetrix.Telemetrix()
            self.board = telemetrix_aio.TelemetrixAIO()
            self.backgroundActions(1)
        except Exception as e:
            self.board = None
            print(e)
        
        self.initializeAndShow()

        if self.board:
            self.backgroundActions(2)

    def backgroundActions(self, actionId, motorName=None):
        print(f'Starting Thread with actionId={actionId}')
        worker = Worker(self.start_background_loop, self.board, actionId=actionId, motorName=motorName)
        worker.signals.finished.connect(lambda: self.thread_complete(actionId))
        self.threadpool.start(worker)

    def thread_complete(self, actionId):
        print(f'Thread with actionId={actionId} finished')
        
    def start_background_loop(self, *args, **kwargs) -> None:
        board = args[0]
        actionId = kwargs['actionId']
        motorName = kwargs['motorName']
        print(f'start_back_ground = {actionId}')
        asyncio.run(self.runInAnotherQThread(board, actionId, motorName))

    async def runInAnotherQThread(self, board, actionId, motorName):
        task = None
        if actionId==1:
            task = asyncio.create_task(self.initPins(board))
        elif actionId==2:
            task = asyncio.create_task(self.initMotors(board))
            #lambda board, actionId: (await self.initMotors(board, actionId) for _ in '_').__anext__()
            #asyncio.run(lambda: self.initMotors(board, actionId))
        elif actionId==3:
            task = asyncio.create_task(self.setPinValues(board, motorName))
        elif actionId==4:
            task = asyncio.create_task(self.updateSpeedMaxSpeedAccelerations(board))
        tasks = []
        #task.set_name(str(actionId))
        #task.add_done_callback(self.check_task_status)
        tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    async def initPins(self, board) -> None:
        tasks = []
        print("starting to Init Pin")
        for m in self.motorNames:
            for p in self.pinNames:
                pin_number = int(self.config.get(m, p))
                task = asyncio.create_task(self.digital_out(board, pin_number))
                task.set_name(f'set pin {pin_number} as digital output')
                task.add_done_callback(self.check_task_status)
                tasks.append(task)       
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def setPinValues(self, board, motorName) -> None:
        tasks = []
        print(f'starting to set pin for {motorName}')
        start_index = 2
        for m in self.motorNames:
            if motorName and motorName!=m:
                continue
            for p in self.pinNames[start_index:]:
                pin_number = int(self.config.get(m, p))
                pin_value = int(self.preference.get(m, p))
                task = asyncio.create_task(self.digital_write(board, pin_number, pin_value))
                task.set_name(f'set pin {pin_number} value as {pin_value}')
                task.add_done_callback(self.check_task_status)
                tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def digital_out(self, board, pin):
        await board.set_pin_mode_digital_output(pin)
    async def digital_write(self, board, pin, value):
        await board.digital_write(pin, value)
        
    def check_task_status(self, task: asyncio.Task):
        if task.done():
            if task.exception() is not None:
                print(f'Task {task.get_name()} failed')
                return
            print(f'Task {task.get_name()} complete, result - {task.result()}')

    def set_motor_task(self, task: asyncio.Task):
        if task.done():
            if task.exception() is not None:
                print(f'Task #{task.get_name()} failed')
                return
            print(f'set Motor Task {task.get_name()} complete, result - {task.result()}')
            self.motors[task.get_name()]=task.result()

    async def createMotor(self, board, name, stepPin, dirPin):
        motor = await board.set_pin_mode_stepper(interface=1, pin1=stepPin, pin2=dirPin)
        speed = int(self.preference.get(name, "speed"))
        await self.board.stepper_set_speed(motor, speed)
        maxSpeed = int(self.preference.get(name, "maxSpeed"))
        await self.board.stepper_set_max_speed(motor, maxSpeed)
        acceleration = int(self.preference.get(name, "acceleration"))
        await self.board.stepper_set_acceleration(motor, acceleration)

        await self.board.stepper_set_current_position(motor, 0)

        return motor

    async def initMotors(self, board) -> None:
        tasks = []
        for name in self.motorNames:
            stepPin = int(self.config.get(name, "stepPin"))
            dirPin = int(self.config.get(name, "dirPin"))
            #print(f'name={name} steppin={stepPin} dirPin={dirPin}')
            task = asyncio.create_task(self.createMotor(board, name, stepPin, dirPin))
            task.set_name(f'{name}')
            task.add_done_callback(self.set_motor_task)
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def updateSpeedMaxSpeedAccelerations(self, board):
        tasks = []
        for name in self.motorNames:
            task = asyncio.create_task(self.updateSpeedMaxSpeedAcceleration(board, name))
            task.set_name(f'{name}')
            task.add_done_callback(self.set_motor_task)
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)

    async def updateSpeedMaxSpeedAcceleration(self, board, name):
        motor = self.motors[name]
        speed = int(self.preference.get(name, "speed"))
        await self.board.stepper_set_speed(motor, speed)
        maxSpeed = int(self.preference.get(name, "maxSpeed"))
        await self.board.stepper_set_max_speed(motor, maxSpeed)
        acceleration = int(self.preference.get(name, "acceleration"))
        await self.board.stepper_set_acceleration(motor, acceleration)
    
    def closeEvent(self, event):
        print('Window closed')
        if self.board:
            self.board.shutdown()
        self.config.save()
        self.preference.save()
        sys.exit(0)

    async def the_callback(self, data):
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
        print(f'Motor {data[1]} relative  motion completed at: {date}.')
    
    async def current_position_callback1(self, data):
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data[2]))
        print(f'Motor {data[1]} relative  motion completed at: {date}.')
    
    async def current_position_callback(self, data):
        print(f'current_position_callback returns {data[2]}\n')
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_size = event.size()
        #print("Widget resized to:", new_size)

    def initializeAndShow(self):
        #self.setFixedSize(650, 650)
        self.setWindowIcon(QIcon(os.path.join(self.path_images, 'marianaLogo_greenCircle.png')))
        self.setWindowTitle('MARIANA')
        self.centerMainWindow()
        #self.createToolsDockWidget()

        menu_bar = self.menuBar()
        self.maMenu = MarianaMenu(self)
        self.maMenu.createMenu(menu_bar)
        self.createToolBar(self.maMenu)
        self.statusBar = QStatusBar(self)
        self.statusBar.setStyleSheet("background : white;")
        self.setStatusBar(self.statusBar)

        widget = QWidget()
        gridLayout = QGridLayout(widget)

        iRow = 0
        iCol = 0
        self.marianaCamera = MarianaCamera(self, 0)
        if self.marianaCamera.available_cameras: 
            gridLayout.addWidget(self.marianaCamera.cameraWidget(), iRow, iCol,1,3)
        else:
            gridLayout.addWidget(self.photoEditorWidgets(), iRow, iCol,1,3)

        iCol +=3
        motorControlWidget = MotorControlWidget(self, 0)
        #motorControlWidget.setFixedWidth(500)
        #motorControlWidget.setFixedHeight(500)
        motorControlWidget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        gridLayout.addWidget(motorControlWidget, iRow, iCol,1,1)

        self.setCentralWidget(widget)
        self.show()

    def createToolBar(self, menu):
        tool_bar = QToolBar("Toolbar")
        tool_bar.setIconSize(QSize(36,36))
        self.addToolBar(tool_bar)

        #tool_bar.addAction(menu.fileOpen)
        tool_bar.addSeparator()
        #tool_bar.addAction(menu.fileSave)
        tool_bar.addSeparator()
        tool_bar.addAction(menu.opTakePhoto)
        tool_bar.addSeparator()
        tool_bar.addAction(menu.opTakePhotoToClipboard)
        tool_bar.addWidget(WiderSeparator(50))
        tool_bar.addAction(menu.opLeft)
        tool_bar.addAction(menu.opXMiddle)
        tool_bar.addAction(menu.opRight)
        tool_bar.addWidget(WiderSeparator(30))
        tool_bar.addAction(menu.opFront)
        tool_bar.addAction(menu.opYMiddle)
        tool_bar.addAction(menu.opBack)
        tool_bar.addWidget(WiderSeparator(30))
        tool_bar.addAction(menu.opTop)
        tool_bar.addAction(menu.opZMiddle)
        tool_bar.addAction(menu.opBottom)
        
        tool_bar.addWidget(WiderSeparator(50))
        tool_bar.addAction(menu.opCenter)
        tool_bar.addAction(menu.opBottomLeft)
        tool_bar.addAction(menu.opBottomRight)
        tool_bar.addAction(menu.opTopLeft)
        tool_bar.addAction(menu.opTopRight)

        #tool_bar.addAction(menu.opToVideo)
        #tool_bar.addSeparator()
        #button = RecordButton(self)
        #tool_bar.addWidget(button)

    def createToolsDockWidget(self):
        self.dock_tools_view = QDockWidget()
        self.dock_tools_view.setWindowTitle("Edit Image Tools")
        self.dock_tools_view.setAllowedAreas(Qt.LeftDockWidgetArea |
            Qt.RightDockWidgetArea)

        # create container QWidget to hold all widgets inside dock widget
        self.tools_contents = QWidget()

        # create tool push buttons 
        self.rotate90 = QPushButton("Rotate 90º")
        self.rotate90.setMinimumSize(QSize(130, 40))
        self.rotate90.setStatusTip('Rotate image 90º clockwise')
        self.rotate90.clicked.connect(self.rotateImage90)

        self.rotate180 = QPushButton("Rotate 180º")
        self.rotate180.setMinimumSize(QSize(130, 40))
        self.rotate180.setStatusTip('Rotate image 180º clockwise')
        self.rotate180.clicked.connect(self.rotateImage180)

        self.flip_horizontal = QPushButton("Flip Horizontal")
        self.flip_horizontal.setMinimumSize(QSize(130, 40))
        self.flip_horizontal.setStatusTip('Flip image across horizontal axis')
        self.flip_horizontal.clicked.connect(self.flipImageHorizontal)

        self.flip_vertical = QPushButton("Flip Vertical")
        self.flip_vertical.setMinimumSize(QSize(130, 40))
        self.flip_vertical.setStatusTip('Flip image across vertical axis')
        self.flip_vertical.clicked.connect(self.flipImageVertical)

        self.resize_half = QPushButton("Resize Half")
        self.resize_half.setMinimumSize(QSize(130, 40))
        self.resize_half.setStatusTip('Resize image to half the original size')
        self.resize_half.clicked.connect(self.resizeImageHalf)

        # set up vertical layout to contain all the push buttons 
        dock_v_box = QVBoxLayout()
        dock_v_box.addWidget(self.rotate90)
        dock_v_box.addWidget(self.rotate180)
        dock_v_box.addStretch(1)
        dock_v_box.addWidget(self.flip_horizontal)
        dock_v_box.addWidget(self.flip_vertical)
        dock_v_box.addStretch(1)
        dock_v_box.addWidget(self.resize_half)
        dock_v_box.addStretch(6)

        # set the main layout for the QWidget, tools_contents,
        # then set the main widget of the dock widget
        self.tools_contents.setLayout(dock_v_box)
        self.dock_tools_view.setWidget(self.tools_contents)
        
        # set initial location of dock widget
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_tools_view)

        # handles the visibility of the dock widget
        self.toggle_dock_tools_act = self.dock_tools_view.toggleViewAction()

    def photoEditorWidgets(self):
        self.image = QPixmap()
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
        #self.setCentralWidget(self.image_label)
        return self.image_label
                
    def rotateImage90(self):
        """
        Rotate image 90º clockwise
        """
        if self.image.isNull() == False:
            transform90 = QTransform().rotate(90)
            pixmap = QPixmap(self.image)

            rotated = pixmap.transformed(transform90, mode=Qt.SmoothTransformation)

            self.image_label.setPixmap(rotated.scaled(self.image_label.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image = QPixmap(rotated) 
            self.image_label.repaint() # repaint the child widget
        else:
            # No image to rotate
            pass

    def rotateImage180(self):
        """
        Rotate image 180º clockwise
        """
        if self.image.isNull() == False:
            transform180 = QTransform().rotate(180)
            pixmap = QPixmap(self.image)

            rotated = pixmap.transformed(transform180, mode=Qt.SmoothTransformation)

            self.image_label.setPixmap(rotated.scaled(self.image_label.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # .......... To keep being allowed to rotate the image
            self.image = QPixmap(rotated) 
            self.image_label.repaint() # repaint the child widget
        else:
            # No image to rotate
            pass

    def flipImageHorizontal(self):
        """
        Mirror the image across the horizontal axis
        """
        if self.image.isNull() == False:
            flip_h = QTransform().scale(-1, 1)
            pixmap = QPixmap(self.image)

            flipped = pixmap.transformed(flip_h)

            self.image_label.setPixmap(flipped.scaled(self.image_label.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image = QPixmap(flipped)
            self.image_label.repaint()
        else:
            # No image to flip
            pass

    def flipImageVertical(self):
        """
        Mirror the image across the vertical axis
        """
        if self.image.isNull() == False:
            flip_v = QTransform().scale(1, -1)
            pixmap = QPixmap(self.image)

            flipped = pixmap.transformed(flip_v)

            self.image_label.setPixmap(flipped.scaled(self.image_label.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image = QPixmap(flipped)
            self.image_label.repaint()
        else:
            # No image to flip
            pass

    def resizeImageHalf(self):
        if self.image.isNull() == False:
            resize = QTransform().scale(0.5, 0.5)
            pixmap = QPixmap(self.image)

            resized = pixmap.transformed(resize)

            self.image_label.setPixmap(resized.scaled(self.image_label.size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image = QPixmap(resized)
            self.image_label.repaint()
        else:
            # No image to resize
            pass

    

    def centerMainWindow(self):
        app = QApplication.instance()
        screen = app.screenAt(self.pos())
        geometry = screen.availableGeometry()
        screen_width = geometry.width()
        screen_height = geometry.height()
        self.resize(int(screen_width * 0.8), int(screen_height * 0.8))
        self.setMinimumSize(int(screen_width * 0.5), int(screen_height * 0.5))
        #desktop = QDesktopWidget().screenGeometry()
        self.move(int((screen_width - self.width()) / 2), int((screen_height - self.height()) / 2))

    def on_about_to_quit(self):
        print("Application is about to quit")
    
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def screen_resolutions(self):
        for displayNr in range(QDesktopWidget().screenCount()):
            sizeObject = QDesktopWidget().screenGeometry(displayNr)
            print("Display: " + str(displayNr) + " Screen size : " + str(sizeObject.height()) + "x" + str(sizeObject.width()))

   
# Run program
if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    #print(QStyleFactory.keys())
    #app.setStyle("Windows")
    #QCoreApplication.aboutToQuit.connect(on_about_to_quit)
    #app.setAttribute(Qt.AA_DontShowIconsInMenus, True)
    ex = MarianaGUI()
    #sys.exit(app.exec_())

    with loop:
        sys.exit(loop.run_forever())

