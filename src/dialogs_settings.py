import sys
from PyQt5.QtGui import QColor, QFont, QPen, QPainter
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtWidgets import QFrame, QScrollArea, QTabWidget, QGridLayout, QVBoxLayout, QFormLayout, QWidget, QDialog, \
   QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QRadioButton, QDialogButtonBox

class ContentWidget(QWidget):
    def __init__(self, parent, section: dict):
        super().__init__(parent)
        layout = QFormLayout(self)

        for key, value in section.items():
            layout.addRow(QLabel(key), value)
    
class ScrollWidget(QWidget):
    def __init__(self, parent, section: dict):
        super().__init__(parent)
        self.contentWidget = ContentWidget(parent, section)
        scroll = QScrollArea(self)
        scroll.setWidget(self.contentWidget)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

    def sizeHint(self) -> QSize:
        return self.contentWidget.sizeHint() + QSize(50, 0)
    
class SettingsDialog(QDialog):
    def __init__(self, parent=None, title="Custom Dialog"):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(title)

        parser = self.parent.config
        self.lineEdit_dict = {}
        
        for section in parser.sections():
            temp_dict = {}
            for key, value in parser.items(section):
                lineEdit = QLineEdit(self)
                lineEdit.setText(value)
                temp_dict[key] = lineEdit
            self.lineEdit_dict[section] = temp_dict

        tabWidget = QTabWidget(self)
        for section in parser.sections():
            tabWidget.addTab(ScrollWidget(self.parent, self.lineEdit_dict[section]), section)

        mainVerticalLayout = QVBoxLayout(self)

        mainVerticalLayout.addWidget(tabWidget)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        mainVerticalLayout.addWidget(button_box)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
             
        self.setLayout(mainVerticalLayout)
    
    def accept(self):
        self.apply_changes()
        super().accept()

    def reject(self):
        super().reject()

    def apply_changes(self):
        parser = self.parent.config

        for section in self.lineEdit_dict:
            for key, value in self.lineEdit_dict[section].items():
                parser.set(section, key, value.text())
        parser.save()

class LabelEditLineWidget(QWidget):
    def __init__(self, parent=None, labelText="text", lineEdit=None):
        super().__init__(parent)
        self.parent = parent
        self.labelText = labelText

        vBoxLayout = QHBoxLayout(self)
        label = QLabel(labelText)
        vBoxLayout.addWidget(label)
        if lineEdit:
            vBoxLayout.addWidget(lineEdit)

class CustomFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.parent = parent
        self.title = "title"

    def paintEvent(self, event):
        # Perform custom painting here
        painter = QPainter(self)
        painter.setPen(QColor(255, 0, 0))
        painter.setBrush(QColor(255, 255, 0))
        painter.drawRect(self.rect())
        super().paintEvent(event)

    def paintEvent2(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.color)
        pen.setWidth(5)  
        painter.setPen(pen)
        painter.drawRect(QRect(5, 5, self.width() - 7, self.height() - 7))
        text_color = QColor(0, 0, 0)  # Black color
        painter.setPen(text_color)
        #painter.drawText(5, 15, self.title)
        #painter.drawText(self.rect(),  Qt.AlignTop | Qt.AlignHCenter, self.title)

class MicrostepResolutionDialog(QDialog):
    def __init__(self, parent=None, title="Custom Dialog"):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle(title)
        
        qVBoxLayout = QVBoxLayout(self)
        self.qLineEditDict = {'motor1': '1', 'motor2': '2', 'motor3': '3'}
        self.resolutions = ["Full Step", "Half Step", "Quater Step", "Eighth Step", "Sixteenth Step"]
        self.motorSpeed = ["step", "speed", "maxSpeed", "acceleration"]
        #MS1	MS2	MS3	Microstep resolution
        #Low	Low	Low	Full step
        #High	Low	Low	1/2 step
        #Low	High	Low	1/4 step
        #High	High	Low	1/8 step
        #High	High	High	1/16 step
        self.resolutionDict = {
            0: [0,0,0],
            1: [1,0,0], 
            2: [0,1,0], 
            3: [1,1,0],
            4: [1,1,1]
        }

        motorNames = []
        for key in self.qLineEditDict.keys():
            motorNames.append(key)
        qVBoxLayout.addWidget(self.createFrame("X Axis: ", QColor('red'), motorNames[0]))
        qVBoxLayout.addWidget(self.createFrame("Y Axis: ", QColor('green'), motorNames[1]))
        qVBoxLayout.addWidget(self.createFrame("Z Axis: ", QColor('blue'), motorNames[2]))

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        qVBoxLayout.addWidget(button_box)

    def createFrame(self, labelText, color, motorName):
        #frame = QFrame(self, labelText, color)
        frame = QFrame(self)
        frame.setObjectName(u"Microstep Resolution")
        #self.frame.setMinimumSize(QSize(0, 48))
        frame.setStyleSheet(u"background-color: rgb(255, 255, 255);")
        #frame.setStyleSheet("border: 2px solid blue;")
        frame.setFrameShape(QFrame.StyledPanel)

        gridLayout = QGridLayout(frame)
        iRow = 0
        iCol = 0
        label = QLabel(labelText)
        label.setAlignment(Qt.AlignCenter) 
        label.setStyleSheet("font-weight: bold;")   
        label.setStyleSheet(f'color: {color.name()};')  
        font = QFont("Arial", 16)
        label.setFont(font)
        gridLayout.addWidget(label, iRow, iCol,1,1)

        qLineEdits = []
        for index, itemName in enumerate(self.motorSpeed):
            iCol = index+1
            qLineEdit = QLineEdit(self.parent.preference.get(motorName, itemName))
            labelEditLineWidget = LabelEditLineWidget(self, itemName, qLineEdit)
            gridLayout.addWidget(labelEditLineWidget, iRow, iCol,1,1)
            qLineEdits.append(qLineEdit)
        self.qLineEditDict.update({motorName: qLineEdits})

        iRow += 1
        for index, value in enumerate(self.resolutions):
            iCol = index
            gridLayout.addWidget(self.createQRadioButton(value, motorName, iCol), iRow, iCol,1,1, Qt.AlignCenter)
            gridLayout.setColumnStretch(iCol, 1)

        return frame

    def createQRadioButton(self, labelText, motorName, stepId):
        qRadioButton = QRadioButton(labelText)
        if stepId==0:
            qRadioButton.setChecked(True)
        qRadioButton.toggled.connect(lambda: self.radio_button_clicked(qRadioButton, motorName, stepId))
        return qRadioButton
    
    def radio_button_clicked(self, b, motorName, stepId):
        if b.isChecked():
            print(f'{motorName} and {stepId} is checked ')
            pinValues = self.resolutionDict[stepId]
            start_index = 2
            index = 0
            for p in self.parent.pinNames[start_index:]:
                self.parent.preference.set(motorName, p, pinValues[index])
                index += 1
            
            self.parent.backgroundActions(3, motorName)

    def accept(self):
        self.apply_changes()
        super().accept()

    def reject(self):
        super().reject()

    def apply_changes(self):
        for motorName, qLineEdits in self.qLineEditDict.items():
            for index, itemName in enumerate(self.motorSpeed):
                self.parent.preference.set(motorName, itemName, qLineEdits[index].text())
        self.parent.preference.save()
        


