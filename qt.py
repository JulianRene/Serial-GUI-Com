__author__ = 'Mehmet Cagri Aksoy - github.com/mcagriaksoy'

import sys, os, serial, serial.tools.list_ports, warnings
from PyQt5.QtCore import *
import time
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

# Port Detection START
ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'USB' in p.description
]

if not ports:
    raise IOError("There is no device exist on serial port!")

if len(ports) > 1:
    warnings.warn('Connected....')

ser = serial.Serial('COM2', 115200, timeout=1) #(ports[0], 115200)    #('COM1', 115200, timeout=1)
# Port Detection END
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
        #ser = None
        self.label_11.setText(ports[0])
        self.pushBtnClicked = False

    def loop_finished(self):
        print('Loop Finished')

    def start_loop(self):

        self.label_11.setText(ports[0])

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
        if i != '':
            self.textEdit_3.append("{}".format(i))
            print(i)

    # TXT Save
    def on_pushButton_5_clicked(self):
        with open('Log.txt', 'w') as f:
            my_text = self.textEdit_3.toPlainText()
            f.write(my_text)

        #Put confirmation button
        #TODO Put a clear screen button and try to be always at the end of the screen

    def on_pushButton_2_clicked(self):
        self.textEdit.setText('Stopped! Please click CONNECT...')

    def on_pushButton_clicked(self):
        #Start the connection
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

        if self.txtIQfile.toPlainText() == "" or self.txt_Dir.toPlainText() == "":
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No IQ File Name!")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("There is not an IQ File Name or Directory. Please specify the File Name and Directory first.")
            msgBox.exec()
            self.pushBtnClicked = True
            return

        # go across files and rename those
        folder = self.txt_Dir.toPlainText()
        for count, filename in enumerate(os.listdir(folder)):
            if count < 10:
                numb = '0' + str(count)
            else:
                numb = str(count)

            dst = self.txtIQfile.toPlainText() + numb + ".mov"
            src = folder + '/' + filename
            dst = folder + '/' + dst

            os.rename(src, dst)

        self.pushBtnClicked = True

    def on_pb_StCo_clicked(self):
        if self.pushBtnClicked:
            self.pushBtnClicked = False
            return

        if self.txtIQfile.toPlainText() == "":
            msgBox = QMessageBox()
            msgBox.setWindowTitle("No IQ File Name!")
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setText("There is not an IQ File Name. Please specify the File Name first.")
            msgBox.exec()
            self.pushBtnClicked = True
            return

        count = self.sb_Num.value()
        if count < 10:
            numb = '0' + str(count)
        else:
            numb = str(count)

        #check for store command
        if self.ch_Store.isChecked():
            mytext = "cine store j:" + self.txtIQfile.toPlainText() + numb + ".iq 2363 2442 2 1\n"
            ser.write(mytext.encode())

        # check for copy command
        if self.ch_Copy.isChecked():
            mytext = "io copy j:" + self.txtIQfile.toPlainText() + numb + ".iq " + self.cb_Drive.currentText() + "\n"
            ser.write(mytext.encode())

        #Check if auto-increment index
        if self.ck_Auto.isChecked():
            self.sb_Num.setValue(count+1)

        self.pushBtnClicked = True


def run():
    app = QApplication(sys.argv)
    widget = qt()           #TOFIX: There is this line that maybe is calling twice objects
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()