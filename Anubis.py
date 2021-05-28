#############      author => Anubis Graduation Team        ############
#############      this project is part of my graduation project and it intends to make a fully functioned IDE from scratch    ########
#############      I've borrowed a function (serial_ports()) from a guy in stack overflow whome I can't remember his name, so I gave hime the copyrights of this function, thank you  ########


import sys
import glob
import serial

import Python_Coloring
import CSharp_Coloring
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pathlib import Path
global languageMode 
languageMode = "" #by default no language

def serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
         
   
    return result


#
#
#
#
############ Signal Class ############
#
#
#
#
class Signal(QObject):

    # initializing a Signal which will take (string) as an input
    readingSignal = pyqtSignal(str)

    # init Function for the Signal class
    def __init__(self):
        QObject.__init__(self)

#
#
############ end of Class ############
#
#

# Making text editor as A global variable (to solve the issue of being local to (self) in widget class)
codeText = QTextEdit
previewText = QTextEdit

#
#
#
#
############ Text Widget Class ############
#
#
#
#

# this class is made to connect the QTab with the necessary layouts
class text_widget(QWidget):
    def __init__(self):
        super().__init__()
        self.itUI()
    def itUI(self):
        global codeText
        codeText = QTextEdit()
        hbox = QHBoxLayout()
        hbox.addWidget(codeText)
        self.setLayout(hbox)



#
#
############ end of Class ############
#
#



#
#
#
#
############ Widget Class ############
#
#
#
#
class Widget(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        # This widget is responsible of making Tab in IDE which makes the Text editor looks nice
        tab = QTabWidget()
        textWidget = text_widget()
        tab.addTab(textWidget, "Tab"+"1")

        # second editor in which the error messeges and succeeded connections will be shown
        global previewText
        previewText = QTextEdit()
        previewText.setReadOnly(True)
        # defining a Treeview variable to use it in showing the directory included files
        self.treeview = QTreeView()

        # making a variable (path) and setting it to the root path (surely I can set it to whatever the root I want, not the default)
        #path = QDir.rootPath()

        path = QDir.currentPath()

        # making a Filesystem variable, setting its root path and applying somefilters (which I need) on it
        self.dirModel = QFileSystemModel()
        self.dirModel.setRootPath(QDir.rootPath())

        # NoDotAndDotDot => Do not list the special entries "." and "..".
        # AllDirs =>List all directories; i.e. don't apply the filters to directory names.
        # Files => List files.
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.treeview.setModel(self.dirModel)
        self.treeview.setRootIndex(self.dirModel.index(path))
        self.treeview.clicked.connect(self.onClicked)

        vbox = QVBoxLayout()
        Left_hbox = QHBoxLayout()
        Right_hbox = QHBoxLayout()

        # after defining variables of type QVBox and QHBox
        # I will Assign treevies variable to the left one and the first text editor in which the code will be written to the right one
        Left_hbox.addWidget(self.treeview)
        Right_hbox.addWidget(tab)

        # defining another variable of type Qwidget to set its layout as an QHBoxLayout
        # I will do the same with the right one
        Left_hbox_Layout = QWidget()
        Left_hbox_Layout.setLayout(Left_hbox)

        Right_hbox_Layout = QWidget()
        Right_hbox_Layout.setLayout(Right_hbox)

        # I defined a splitter to seperate the two variables (left, right) and make it more easily to change the space between them
        H_splitter = QSplitter(Qt.Horizontal)
        H_splitter.addWidget(Left_hbox_Layout)
        H_splitter.addWidget(Right_hbox_Layout)
        H_splitter.setStretchFactor(1, 1)

        # I defined a new splitter to seperate between the upper and lower sides of the window
        V_splitter = QSplitter(Qt.Vertical)
        V_splitter.addWidget(H_splitter)
        V_splitter.addWidget(previewText)

        Final_Layout = QHBoxLayout(self)
        Final_Layout.addWidget(V_splitter)

        self.setLayout(Final_Layout)

    # defining a new Slot (takes string) to save the text inside the first text editor
    @pyqtSlot(str)
    def saving(s):
        if languageMode == "python":
           with open('main.py', 'w') as f:
               textToSave = codeText.toPlainText()
               f.write(textToSave)
        elif languageMode == "C#":
           with open('main.cs', 'w') as f:
               textToSave = codeText.toPlainText()
               f.write(textToSave)
        else:
           previewText.append("Please, Choose language first.")
           

    # defining a new Slot (takes string) to set the string to the text editor
    @pyqtSlot(str)
    def Open(s):
        global codeText
        codeText.setText(s)

    def onClicked(self, index):

        readData = self.sender().model().filePath(index)
        readData = tuple([readData])

        if readData[0]:
            f = open(readData[0],'r')
            with f:
                data = f.read()
                codeText.setText(data)

#
#
############ end of Class ############
#
#

# defining a new Slot (takes string)
# Actually I could connect the (mainwindow) class directly to the (widget class) but I've made this function in between for futuer use
# All what it do is to take the (input string) and establish a connection with the widget class, send the string to it
@pyqtSlot(str)
def reading(s):
    inputSignal = Signal()
    inputSignal.readingSignal.connect(Widget.saving)
    inputSignal.readingSignal.emit(s)

# same as reading Function
@pyqtSlot(str)
def Openning(s):
    inputSignal = Signal()
    inputSignal.readingSignal.connect(Widget.Open)
    inputSignal.readingSignal.emit(s)
#
#
#
#
############ MainWindow Class ############
#
#
#
#
class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.intUI()

    def intUI(self):
        global languageMode
        self.port_flag = 1
        self.inputSignal = Signal()

        self.Open_Signal = Signal()

        # connecting (self.Open_Signal) with Openning function
        self.Open_Signal.readingSignal.connect(Openning)

        # connecting (self.b) with reading function
        self.inputSignal.readingSignal.connect(reading)

        # creating menu items
        menu = self.menuBar()

        # I have three menu items
        filemenu = menu.addMenu('File')
        Port = menu.addMenu('Port')
        Run = menu.addMenu('Run')
        
        language = menu.addMenu('Language') 

        # As any PC or laptop have many ports, so I need to list them to the User
        # so I made (Port_Action) to add the Ports got from (serial_ports()) function
        # copyrights of serial_ports() function goes back to a guy from stackoverflow(whome I can't remember his name), so thank you (unknown)
        Port_Action = QMenu('port', self)

        res = serial_ports()

        for i in range(len(res)):
            s = res[i]
            Port_Action.addAction(s, self.PortClicked)

        # adding the menu which I made to the original (Port menu)
        Port.addMenu(Port_Action)

#        Port_Action.triggered.connect(self.Port)
#        Port.addAction(Port_Action)

        # Making and adding Run Actions
        RunAction = QAction("Run", self)
        RunAction.triggered.connect(self.Run)
        Run.addAction(RunAction)

        # Making and adding File Features
        Save_Action = QAction("Save", self)
        Save_Action.triggered.connect(self.save)
        Save_Action.setShortcut("Ctrl+S")
        Close_Action = QAction("Close", self)
        Close_Action.setShortcut("Alt+c")
        Close_Action.triggered.connect(self.close)
        Open_Action = QAction("Open", self)
        Open_Action.setShortcut("Ctrl+O")
        Open_Action.triggered.connect(self.Open)


        filemenu.addAction(Save_Action)
        filemenu.addAction(Close_Action)
        filemenu.addAction(Open_Action)

        # Languages handeling
        pythonLanguage = QAction("Python", self)
        cSharp = QAction("C#", self)
        pythonLanguage.triggered.connect(self.PythonModeSet)
        cSharp.triggered.connect(self.CSharpModeSet)
        language.addAction(pythonLanguage)
        language.addAction(cSharp)

        # Seting the window Geometry
        self.setGeometry(200, 150, 800, 650)
        self.setWindowTitle('Anubis IDE')
        self.setWindowIcon(QtGui.QIcon('Anubis.png'))
        

        widget = Widget()

        self.setCentralWidget(widget)
        self.show()

    ###########################        Start OF the Functions          ##################
    def PythonModeSet(self):
       global languageMode
       languageMode = "python"
       Python_Coloring.PythonHighlighter(codeText)
       
    def CSharpModeSet(self):
       global languageMode
       languageMode = "C#"
       CSharp_Coloring.CSharpHighlighter(codeText)


    def Run(self):
        #print(languageMode)
        
        if languageMode == "":
            previewText.append("Sorry, Choose language first.")
            
        if self.port_flag == 0:
            mytext = codeText.toPlainText()
        #
        ##### Compiler Part
        #
#            ide.create_file(mytext)
#            ide.upload_file(self.portNo)
            previewText.append("Sorry, there is no attached compiler.")

        else:
            previewText.append("Please Select Your Port Number First")


    # this function is made to get which port was selected by the user
    @QtCore.pyqtSlot()
    def PortClicked(self):
        action = self.sender()
        self.portNo = action.text()
        self.port_flag = 0



    # I made this function to save the code into a file
    def save(self):
        self.inputSignal.readingSignal.emit("name")


    # I made this function to open a file and exhibits it to the user in a text editor
    def Open(self):
        global languageMode
        file_name = QFileDialog.getOpenFileName(self,'Open File','/home')
        extension = file_name[0].split(".")[1]
        if file_name[0]:
            f = open(file_name[0],'r')
            with f:
               if extension == "py":
                  data = f.read()
                  self.Open_Signal.readingSignal.emit(data)
                  languageMode = "python"
                  Python_Coloring.PythonHighlighter(codeText)
                  
               if extension == "cs":
                  data = f.read()
                  self.Open_Signal.readingSignal.emit(data)
                  languageMode = "C#"
                  CSharp_Coloring.CSharpHighlighter(codeText)


#
#
############ end of Class ############
#
#

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = UI()
    # ex = Widget()
    sys.exit(app.exec_())
