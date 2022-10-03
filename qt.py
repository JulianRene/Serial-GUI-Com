__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

import sys, os, serial, serial.tools.list_ports, warnings
from PyQt5.QtCore import * #QSize, QRect, QObject, pyqtSignal, QThread, pyqtSignal, pyqtSlot
import time
from PyQt5.QtWidgets import * #QApplication, QComboBox, QDialog, QMainWindow, QWidget, QLabel, QTextEdit, QListWidget, \
    #QListView
#from PyQt5.QtGui import *
from PyQt5.uic import loadUi

#TODO Line to update GUI: pyuic5 -o Tools_Main.py Tools_Main.ui

#Port Detection START
ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'USB' in p.description
]

if not ports:
    raise IOError("There is no device exist on serial port!")

if len(ports) > 1:
    warnings.warn('Connected....')

ser = serial.Serial(ports[0],115200)
#Port Detection END

# MULTI-THREADING

class Worker(QObject):
    finished = pyqtSignal()
    intReady = pyqtSignal(str)

    @pyqtSlot()
    def __init__(self):
        super(Worker, self).__init__()
        self.working = True

    def work(self):
        while self.working:
            line = ser.readline().decode('utf-8')
            print(line)
            time.sleep(0.1)
            self.intReady.emit(line)

        self.finished.emit()

class qt(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)
        loadUi('qt.ui', self)

        self.thread = None
        self.worker = None
        self.pushButton.clicked.connect(self.start_loop)
        self.label_11.setText(ports[0])
        self.pushBtnClicked = False

    def loop_finished(self):
        print('Loop Finished')

    def start_loop(self):

        self.worker = Worker()   # a new worker to perform those tasks
        self.thread = QThread()  # a new thread to run our background tasks in
        self.worker.moveToThread(self.thread)  # move the worker into the thread, do this first before connecting the signals

        self.thread.started.connect(self.worker.work) # begin our worker object's loop when the thread starts running

        self.worker.intReady.connect(self.onIntReady)

        self.pushButton_2.clicked.connect(self.stop_loop)      # stop the loop on the stop button click

        self.worker.finished.connect(self.loop_finished)       # do something in the gui when the worker loop ends
        self.worker.finished.connect(self.thread.quit)         # tell the thread it's time to stop running
        self.worker.finished.connect(self.worker.deleteLater)  # have worker mark itself for deletion
        self.thread.finished.connect(self.thread.deleteLater)  # have thread mark itself for deletion
        self.thread.start()

    def stop_loop(self):
        self.worker.working = False

    def onIntReady(self, i):
        self.textEdit_3.append("{}".format(i))
        print(i)

    # Save the settings
    def on_pushButton_4_clicked(self):
        if self.x != 0:
            self.textEdit.setText('Settings Saved!')
        else:
            self.textEdit.setText('Please enter port and speed!')

    # TXT Save
    def on_pushButton_5_clicked(self):
        with open('Sonuc.txt', 'w') as f:
            my_text = self.textEdit_3.toPlainText()
            f.write(my_text)

    def on_pushButton_2_clicked(self):
        self.textEdit.setText('Stopped! Please click CONNECT...')

    def on_pushButton_clicked(self):

        self.completed = 0
        while self.completed < 100:
            self.completed += 0.001
            self.progressBar.setValue(self.completed)
        self.textEdit.setText('Data Gathering...')
        self.label_5.setText("CONNECTED!")
        self.label_5.setStyleSheet('color: green')
        x = 1
        self.textEdit_3.setText(":")
        mytext = "\n"      #Send first enter
        ser.write(mytext.encode())

    def on_pushButton_3_clicked(self):
        # Send data from serial port:
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return
        mytext = self.textEdit_2.toPlainText() + "\n"
        print(mytext.encode())
        ser.write(mytext.encode())
        self.pushBtnClicked = True

    def on_pb_Free_clicked(self):
        # Send Freeze command from serial port:
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return
        mytext = "cine freeze\n"
        print(mytext.encode())
        ser.write(mytext.encode())
        self.pushBtnClicked = True

    def on_pb_Unfre_clicked(self):
        # Send Unfreeze command from serial port:
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return
        mytext = "cine unfreeze\n"
        print(mytext.encode())
        ser.write(mytext.encode())
        self.pushBtnClicked = True

    def on_pb_List_clicked(self):
        # Send List dir command from serial port:
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return
        mytext = "io dir " + self.cb_Drive.currentText() + "\n"
        print(mytext.encode())
        ser.write(mytext.encode())
        self.pushBtnClicked = True

    def on_pb_Brow_clicked(self):
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return
        # select folder with files to rename
        folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if not folder:
            return

        self.txt_Dir.setText(folder)
        self.pushBtnClicked = True

    def on_pb_Rena_clicked(self):
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return

        # go across files and rename those
        folder = self.txt_Dir.toPlainText()
        for count, filename in enumerate(os.listdir(folder)):
            if count < 10:
                numb = '0' + str(count)
            else:
                numb = str(count)

            dst = self.txtFileName.text() + numb + ".mov"
            src = folder + '/' + filename
            dst = folder + '/' + dst

            os.rename(src, dst)

        self.pushBtnClicked = True

    def on_pb_Rena_clicked(self):
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return

        count = self.sb_Num.Value
        if count < 10:
            numb = '0' + str(count)
        else:
            numb = str(count)

        mytext = "cine store j:" + self.txtIQfile.toPlainText() + numb + ".iq 2363 2442 2 1\n"
        print(mytext.encode())
        ser.write(mytext.encode())
        self.pushBtnClicked = True


def run():
    app = QApplication(sys.argv)
    widget = qt()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()