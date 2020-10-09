from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from json import load as jsonread
from math import ceil

class WordList(QScrollArea):
    def __init__(self, window, centralWidget):
        QScrollArea.__init__(self,window)
        self.setWidgetResizable(True)
        self.widget = QWidget(self)
        self.setWidget(self.widget)
        self.layout = QVBoxLayout(self.widget)
        self.centralWidget = centralWidget
        self.reload(0)

    def reload(self,page):
        for child in (self.layout.itemAt(i) for i in range(self.layout.count())):
            self.layout.removeItem(child)
        if page == 53:
            for word in self.centralWidget.window.defaultWords[53*64:]:
                checkbox = QCheckBox(word)
                self.layout.addWidget(checkbox)
        else:
            for word in self.centralWidget.window.defaultWords[page*64:(page+1)*64]:
                checkbox = QCheckBox(word)
                self.layout.addWidget(checkbox)

class WordListTabs(QTabBar):
    def __init__(self, window, centralWidget):
        QTabBar.__init__(self,window)
        self.centralWidget = centralWidget
        self.currentChanged.connect(self.tabChanged)
    
    def tabChanged(self, index):
        self.centralWidget.wordList.reload(index)

class CentralWidget(QWidget):
    def __init__(self, window):
        QWidget.__init__(self,window)
        self.window = window
        
        self.bottomHalfWidget = QWidget()
        self.bottomHalfLayout = QVBoxLayout(self.bottomHalfWidget)
        self.bottomHalfTabs = WordListTabs(self.bottomHalfWidget,self)
        self.wordList = WordList(self.bottomHalfWidget,self)
        self.bottomHalfLayout.addWidget(self.bottomHalfTabs)
        self.bottomHalfLayout.addWidget(self.wordList)
        tabLength = ceil(len(window.defaultWords)/64)
        for i in range(tabLength)[:53]:
            self.bottomHalfTabs.addTab(str(i+1))
        if tabLength >= 53:
            self.bottomHalfTabs.addTab("...")
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.bottomHalfWidget,"Filtered")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QWidget())
        self.layout.addWidget(self.tabWidget)
        self.setLayout(self.layout)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        with open("dictionary.json","r") as jsonfile:
            self.defaultWords = sorted([word[0] for word in jsonread(jsonfile) if not "-" in word[0]])
        
        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.setMinimumSize(210,250)
        self.show()

    def resizeEvent(self, event):
        self.centralWidget.tabWidget.setFixedSize(self.frameGeometry().width()-18,int(self.frameGeometry().height()/2))

app = QApplication([])
app.setWindowIcon(QIcon('favicon.png'))
app.setApplicationName("Word filter")
window = MainWindow()
app.exec_()
