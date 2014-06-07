__author__ = 'hemanth'
from PySide.QtCore import *
from PySide.QtGui import *
import gui_a
import sys
import pafy
import urllib2
import os






class MainWin(QDialog, gui_a.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWin, self).__init__(parent)
        self.setupUi(self)
        self.connect(self.pushButton, SIGNAL("clicked()"), self.download_file)
        self.connect(self.get_button, SIGNAL("clicked()"), self.get_video_details)
        self.thumb_url = ""
        self.video_url = ""
        self.video_suffix = ""
        self.progressBar.setRange(0, 100)


    def setProgress(self, progress):
        self.progressBar.setValue(progress)

    def get_video_details(self):
        self.comboBox.clear()
        try:
            video = pafy.new(self.lineEdit.text())
            streams = video.allstreams
            for s in streams:
                self.comboBox.addItem(str(s), s.url)
            self.video_title = video.title
        except Exception, e:
            QMessageBox.warning(self, "Warning!", str(e))
        self.video_url = self.comboBox.itemData(self.comboBox.currentIndex())
        data = urllib2.urlopen(video.thumb).read()
        image = QImage()
        image.loadFromData(data)
        scene = QGraphicsScene()
        scene.addPixmap(QPixmap(image))
        self.graphicsView.setScene(scene)

    def download_file(self):
        url = self.video_url
        download_dir = "./"
        file_name = self.video_title.replace(" ", "_")[:10]

        u = urllib2.urlopen(url)
        meta = u.info()
        file_size = int(meta.getheaders('Content-Length')[0])
        print file_size

        f = open(os.path.join(download_dir, file_name), 'wb')

        downloaded_bytes = 0
        block_size = 1024*8
        while True:
            byte_buffer = u.read(block_size)
            if not byte_buffer:
                break
            f.write(byte_buffer)
            downloaded_bytes += block_size
            print downloaded_bytes



#https://www.youtube.com/watch?v=j_UzlOEviL4&list=PLC413CFE45E5D304D&index=2

app = QApplication(sys.argv)
form = MainWin()
form.show()
app.exec_()