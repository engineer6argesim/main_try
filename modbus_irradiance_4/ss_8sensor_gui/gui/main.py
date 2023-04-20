'''
Created on 25 Dec 2021

@author: sy 
'''
from automatic_soiling_gui import Ui_MainWindow_ss
#from gui.automatic_soiling_gui import Ui_MainWindow_ss
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import *
from PyQt5 import Qt
from PyQt5.Qt import *

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

################################################################################close event deneme   ##############################################################################

class MainWin(QMainWindow):

    

    def __init__(self):
        super().__init__()


    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Tab and event.modifiers() & Qt.ControlModifier:
                # Ctrl+Tab tuş kombinasyonu algılandı, olayı ele alma
                return True
            if event.key() in [Qt.Key_Right]:
            # Sadece ok tuşlarına basıldığında hiçbir şey yapmayın
                return True
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Tab and event.modifiers() & Qt.ControlModifier:
                # Ctrl+Tab tuş kombinasyonu algılandı, olayı ele alma
                return True
            if event.key() in [Qt.Key_Right]:
            # Sadece ok tuşlarına basıldığında hiçbir şey yapmayın
                return True
        return False


    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.       #FURKAN

        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        
        reply = QMessageBox.question(
        self, "Message",
        "Are you sure you want to quit?",
        QMessageBox.Close | QMessageBox.Cancel)

        if reply == QMessageBox.Close:
            if(ui.isTimerCreated==True):
                ui.kill_timer=True
                ui.timer.join()
                ui.timer.cancel()
                ui.ser.close()
            if(ui.status_logfile==False):
                    ui.LogFileThread_ins.terminate()
            ui.tab_bar.removeEventFilter(ui.event_filter)
            for widget in self.findChildren(QWidget):
                    widget.removeEventFilter(self)
                    #check if widget has an event filter
            app.quit()
            event.accept()

            #    ui.timer.quit()
            #ui.ser.close()
            ##event.accept()
            ##self.close()

            
            ## cleanup()
        else:
            event.ignore()

    def showInputDialog(self)-> bool:
        text, ok = QInputDialog.getText(None, 'Password Dialog', 'Enter password:', QLineEdit.Password)
        if ok:
                if text == '1919':
                    QMessageBox.warning(None, 'Correct', 'Password is correct')
                    #Created for a object eventFilter which 
                    #it can not do any event before password message box
                    self.main_eventSignal.emit()
                    return False
                else:
                   QMessageBox.warning(None, 'Incorrect', 'Password is not correct')
                   return True
        else:
            return True


############################################################################################################################################################


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWin()
    ui = Ui_MainWindow_ss()
    ui.setupUi(MainWindow)
    for widget in MainWindow.findChildren(QWidget):
        widget.installEventFilter(MainWindow)
    ui.module_init()
    MainWindow.show()
    sys.exit(app.exec_())
