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
import ast

from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
from PyQt5 import QtCore, uic, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
sys.path.append(projDir)

main_ui_file = os.path.join(projDir, "details.ui")
debug.info(main_ui_file)

parser = argparse.ArgumentParser(description="File details utility")
parser.add_argument("-c","--command",dest="command",help="command")
# parser.add_argument("-c", "--command", nargs="+", default=["a", "b"], help="command")
args = parser.parse_args()


def mainGui(main_ui):
    main_ui.setWindowTitle("DETAILS")

    sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
    main_ui.setStyleSheet(sS.read())
    sS.close()

    if (args.command):
        # debug.info(args.command)
        # detsCmd = args.command.strip('][').split(', ')
        detsCmd = ast.literal_eval(args.command)
        debug.info(detsCmd)
        p = subprocess.Popen(detsCmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
        for line in iter(p.stdout.readline, b''):
            debug.info(line)
            main_ui.textEdit.append(line)

    # main_ui.cancelButton.clicked.connect((lambda self, main_ui = main_ui : closeEvent(self, main_ui)))
    # main_ui.renameButton.clicked.connect((lambda self, main_ui = main_ui : rename(self, main_ui)))

    main_ui.show()
    main_ui.update()

    qtRectangle = main_ui.frameGeometry()
    centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    main_ui.move(qtRectangle.topLeft())


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
    setproctitle.setproctitle("DETAILS")
    mainFunc()
