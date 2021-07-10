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
import time
import threading
import traceback
import pathlib

from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
from PyQt5 import QtCore, uic, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
sys.path.append(projDir)

main_ui_file = os.path.join(projDir, "rename.ui")
debug.info(main_ui_file)

parser = argparse.ArgumentParser(description="File rename utility")
parser.add_argument("-n","--name",dest="name",help="Name of the file or folder")
parser.add_argument("-p","--path",dest="path",help="Absolute path to the file or folder")
args = parser.parse_args()


def mainGui(main_ui):
    main_ui.setWindowTitle("RENAME")

    sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
    main_ui.setStyleSheet(sS.read())
    sS.close()

    if (args.name):
        debug.info(args.name)
        try:
            main_ui.nameBox.setText(args.name)
        except:
            debug.info(str(sys.exc_info()))

    main_ui.cancelButton.clicked.connect((lambda self, main_ui = main_ui : closeEvent(self, main_ui)))
    main_ui.renameButton.clicked.connect((lambda self, main_ui = main_ui : rename(self, main_ui)))

    main_ui.show()
    main_ui.update()

    qtRectangle = main_ui.frameGeometry()
    centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    main_ui.move(qtRectangle.topLeft())


def rename(self,main_ui):
    newName = str(main_ui.nameBox.text().encode('utf-8')).strip()
    if args.name and args.path:
        debug.info(args.name)
        debug.info(newName)
        debug.info(args.path)
        cmd = "mv '{0}' '{1}' ".format(args.path+os.sep+args.name, args.path+os.sep+newName)
        debug.info(cmd)
        subprocess.Popen(shlex.split(cmd))
        main_ui.close()
        sys.exit()
    else:
        main_ui.close()
        sys.exit()


def closeEvent(self, main_ui):
    main_ui.close()
    sys.exit()


def mainFunc():
    global app
    app = QApplication(sys.argv)
    main_ui = uic.loadUi(main_ui_file)
    mainGui(main_ui)
    sys.exit(app.exec_())


if __name__ == '__main__':
    setproctitle.setproctitle("RENAME")
    mainFunc()
