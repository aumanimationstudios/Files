#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"

import debug
import argparse
import glob
import os
import sys
import re
import pexpect
import setproctitle
import subprocess
import shlex
from collections import OrderedDict
# import pipes
# from six.moves import shlex_quote
# import pyperclip
import time
import threading

try:
    from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
    from PyQt5 import QtCore, uic, QtGui, QtWidgets, QtWebEngineWidgets
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from PyQt5.QtGui import *
except:
    debug.info("Error importing modules(PyQt5)")

projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
sys.path.append(projDir)


main_ui_file = os.path.join(projDir, "mediaPlayer.ui")
debug.info(main_ui_file)

imageFormats = ['png','PNG','exr','EXR','jpg','JPG','jpeg','JPEG']
videoFormats = ['mov','MOV','mp4','MP4','avi','AVI','mkv','MKV']
musicFormats = ['mp3']

parser = argparse.ArgumentParser(description="File conversion utility")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the folder containing image sequence or videos")
args = parser.parse_args()

app = None
assPath = args.path


def mainGui(main_ui):
    main_ui.setWindowTitle("MEDIA PLAYER")

    pathUrl = QtCore.QUrl().fromLocalFile(assPath)
    main_ui.mediaPlayer.setUrl(pathUrl)

    main_ui.showMaximized()
    main_ui.update()


    qtRectangle = main_ui.frameGeometry()
    centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    main_ui.move(qtRectangle.topLeft())


def mainfunc():
    global app
    app = QApplication(sys.argv)
    main_ui = uic.loadUi(main_ui_file)
    mainGui(main_ui)
    # ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    setproctitle.setproctitle("MEDIA_PLAYER")
    mainfunc()
