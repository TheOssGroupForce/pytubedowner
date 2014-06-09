__author__ = 'hemanth'
from PySide.QtCore import *
from PySide.QtGui import *
from new_gui import Ui_MainWindow
import sys
import pafy
import urllib2
import os
import pickle


class DownloadWorker(QThread):
    """
    Threading to  show a fancy progressbar
    """
    #This is the signal that will be emitted during the processing.
    #By including int as an argument, it lets the signal know to expect
    #an integer argument when emitting.
    updateProgress = Signal(float)

    #You can do any extra things in this init you need, but for this example
    #nothing else needs to be done expect call the super's init
    def __init__(self, url, download_dir, file_name):
        QThread.__init__(self)
        self.url = url
        self.download_dir = download_dir
        self.file_name = file_name

    #A QThread is run by calling it's start() function, which calls this run()
    #function in it's own "thread".
    def run(self):
        #Notice this is the same thing you were doing in your progress() function
        u = urllib2.urlopen(self.url)
        meta = u.info()
        file_size = int(meta.getheaders('Content-Length')[0])
        #print file_size

        f = open(os.path.join(self.download_dir, self.file_name), 'wb')

        downloaded_bytes = 0
        block_size = 1024*8
        while True:
            byte_buffer = u.read(block_size)
            if not byte_buffer:
                break
            f.write(byte_buffer)
            downloaded_bytes += block_size
            #print downloaded_bytes
            self.updateProgress.emit(float(downloaded_bytes)/file_size*100)
        f.close()
        return


class MainWin(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setupUi(self)
        self.connect(self.pushButton, SIGNAL("clicked()"), self.download_file)
        self.connect(self.get_button, SIGNAL("clicked()"), self.get_video_details)
        self.connect(self.dir_button, SIGNAL("clicked()"), self.set_download_folder)

        #Disable the download directory lineEdit. Only use button to select folder
        self.dir_edit.setEnabled(False)
        
        # Try to load user options. If it fails, use working directory
        try:
            self.options = pickle.load(open("user.p","rb"))
            self.dw_directory = self.options["download_dir"]
        except Exception, e:
            self.dw_directory = os.getcwd()
        # And set the download directory LineEdit to the obtained value
        self.dir_edit.setText(self.dw_directory)

        self.video = None
        self.downloader = None
        self.streams = None

        # Option to set a default download directory
        self.options = {"download_dir":""}

    def set_progress(self, progress, style="update"):
        if style == "indeterminate":
            self.progressBar.setRange(0, 0)
            self.progressBar.setValue(0)
        elif style == "reset":
            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(0)
        else:
            #Normal progress bar with updated value
            self.progressBar.setValue(progress)

    # Set download folder of user's choice
    def set_download_folder(self):
        dir_name = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.dw_directory = dir_name
        self.dir_edit.setText(self.dw_directory)
        self.options["download_dir"] = self.dw_directory
        pickle.dump( self.options, open( "user.p", "wb" ) )


    def get_video_details(self):
        try:
            video = pafy.new(self.lineEdit.text())
            self.streams = video.allstreams
            self.comboBox.clear()
            for s in self.streams:
                self.comboBox.addItem(str(s).replace(":", " ").replace("video", "video only").replace(
                    "audio", "audio only").replace("normal", ""))
            self.video = video

            data = urllib2.urlopen(self.video.thumb).read()
            image = QImage()
            image.loadFromData(data)
            scene = QGraphicsScene()
            scene.addPixmap(QPixmap(image))
            self.graphicsView.setScene(scene)
        except Exception, e:
            QMessageBox.warning(self, "Warning!", str(e))

    def download_file(self):
        media = self.streams[self.comboBox.currentIndex()]
        #file_name = self.video.title.replace(" ", "_")[:20]+media.resolution+"."+media.extension
        valid_filename = "".join(x for x in self.video.title if x.isalnum())
        file_name = QFileDialog.getSaveFileName(self, "Save File",self.dw_directory+os.sep+valid_filename+"."+media.extension,
                                                "(*."+media.extension+")")
        if not file_name[0] :
            pass
        else:
            file_name = file_name[0]
            self.progressBar.setRange(0, 100)
            self.downloader = DownloadWorker(media.url, self.dw_directory, file_name)
            self.downloader.updateProgress.connect(self.set_progress)
            self.downloader.start()

    def populate_gui(self):
        video = None
        self.streams = video.allstreams
        for s in self.streams:
            self.comboBox.addItem(str(s), s.url)
        self.video = video

        data = urllib2.urlopen(self.video.thumb).read()
        image = QImage()
        image.loadFromData(data)
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(image))
        self.graphicsView.setScene(scene)


    #QMessageBox.information(self, "Hello!", "Hello there, "+video.title)

#https://www.youtube.com/watch?v=j_UzlOEviL4&list=PLC413CFE45E5D304D&index=2
#https://www.youtube.com/watch?v=zx1IvvLuuEI

app = QApplication(sys.argv)
form = MainWin()
form.show()
app.exec_()
