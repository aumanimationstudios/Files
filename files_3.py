#!/usr/bin/python3
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


#DONE : CHANGE DATE FORMAT
#DONE : DELETE OPTION
#DONE : RENAME OPTION
#DONE : ADD FAVOURITES TO SIDEPANE
#DONE : CUT OPTION
#DONE : NEW FOLDER OPTION
#DONE : DETAILS
#DONE : SEARCH
#DONE : REPLACE WARNING
#DONE : TAB OPTION
#DONE : FIX CHANGE VIEW
#TODO : RSYNC IN THREAD
#TODO : THUMBS IN THREAD

import debug
import constants
from constants import mimeTypes
from constants import mimeConvertCmds
from constants import mimeTypesOpenCmds
import widgetProvider
import argparse
import glob
import os
import sys
import stat
from datetime import datetime, timedelta
import re
# import pexpect
import setproctitle
import signal
import subprocess
import shlex
from collections import OrderedDict
# import pyperclip
import time
import threading
import traceback
import pathlib
import json
from PIL import Image
from multiprocessing import Pool

from PyQt5 import QtCore, uic, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem, QWidget, QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
sys.path.append(projDir)

rootDir = "/"
homeDir = os.path.expanduser("~")
externalToolsDir = "/proj/standard/share/"

filesThumbsDir = homeDir+"/.cache/thumbnails/files_thumbs/"
if os.path.exists(filesThumbsDir):
    files = [f for f in os.listdir(filesThumbsDir) if os.path.isfile(os.path.join(filesThumbsDir, f))]
    for f in files:
        file_path = os.path.join(filesThumbsDir, f)
        file_mod_time = datetime.fromtimestamp(os.stat(file_path).st_mtime)  # This is a datetime.datetime object
        now = datetime.today()
        max_delay = timedelta(minutes=21600)
        if now - file_mod_time > max_delay:
            os.remove(file_path)
        else:
            pass
else:
    os.mkdir(filesThumbsDir)

main_ui_file = os.path.join(projDir, "files_3.ui")
debug.info(main_ui_file)


renamePermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", homeDir]
cutCopyPermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", homeDir]
pastePermittedDirs = ["/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", homeDir] #REMINDER : Do NOT add bluepixels downloads folder
deletePermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", homeDir]
newFolderPermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", homeDir]
prohibitedDirs = ["/blueprod/STOR", "/proj", "/library","/aumbackup"]

parser = argparse.ArgumentParser(description="File viewer utility")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the folder")
args = parser.parse_args()

confFile = homeDir+os.sep+".config"+os.sep+"files.json"

places = {}
places["Home"] = homeDir
places["Crap"] = "/blueprod/CRAP/crap"
places["Downloads"] = homeDir+os.sep+"Downloads"

openTabs = {}

rename = os.path.join(projDir, "rename.py")
details = os.path.join(projDir, "details.py")

app = None
assPath = args.path

if(args.path):
    ROOTDIR = args.path
else:
    ROOTDIR = rootDir

CUR_DIR_SELECTED = None

cutFile = False

currDownloads = []

currIconFiles = None
currListFiles = None
currView = "LIST"


class WorkerSignals(QtCore.QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()



class FSM(QtWidgets.QFileSystemModel):

    def __init__(self,**kwargs):
        super(FSM, self).__init__(**kwargs)

    def data(self, index, role):
        if role == Qt.DecorationRole and index.column() == 0:
            fileInfo = self.fileInfo(index)

            if fileInfo.isDir():
                # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "folder.svg"))
                # return QtGui.QIcon("/usr/share/icons/elementary-xfce/places/symbolic/folder-symbolic.svg")
                return QtGui.QIcon.fromTheme("folder")
            if fileInfo.isFile():
                if fileInfo.suffix() in mimeTypes["video"]:
                    fileName = fileInfo.fileName()
                    thumb_image = filesThumbsDir+fileName+".jpeg"
                    if os.path.exists(thumb_image):
                        return QtGui.QIcon(thumb_image)
                    else:
                        if fileName.startswith("."):
                            pass
                        else:
                            # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "file-video.svg"))
                            # return QtGui.QIcon("/usr/share/icons/elementary-xfce/places/symbolic/folder-videos-symbolic.svg")
                            return QtGui.QIcon.fromTheme("video-x-generic")
                    return QtGui.QIcon.fromTheme("video-x-generic")
                    # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "file-video.svg"))
                    # return QtGui.QIcon("/usr/share/icons/elementary-xfce/places/symbolic/folder-videos-symbolic.svg")

                if fileInfo.suffix() in mimeTypes["audio"]:
                    return QtGui.QIcon.fromTheme("audio-x-generic")
                    # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "file-audio.svg"))
                    # return QtGui.QIcon("/usr/share/icons/elementary-xfce/places/symbolic/folder-music-symbolic.svg")

                if fileInfo.suffix() in mimeTypes["image"]:
                    fileName = fileInfo.fileName()
                    thumb_image = filesThumbsDir + fileName + ".jpeg"
                    if os.path.exists(thumb_image):
                        return QtGui.QIcon(thumb_image)
                    else:
                        if fileName.startswith("."):
                            pass
                        else:
                            # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "file-image.svg"))
                            # return QtGui.QIcon("/usr/share/icons/elementary-xfce/places/symbolic/folder-pictures-symbolic.svg")
                            return QtGui.QIcon.fromTheme("image-x-generic")
                    return QtGui.QIcon.fromTheme("image-x-generic")
                    # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "file-image.svg"))
                    # return QtGui.QIcon("/usr/share/icons/elementary-xfce/places/symbolic/folder-pictures-symbolic.svg")

                if fileInfo.suffix() in mimeTypes["text"]:
                    # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "file-text.svg"))
                    # return QtGui.QIcon("/usr/share/icons/elementary-xfce/mimes/symbolic/text-x-generic-symbolic.svg")
                    return QtGui.QIcon.fromTheme("text-x-generic")

                # return QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "file.svg"))
                # return QtGui.QIcon("/usr/share/icons/elementary-xfce/places/symbolic/folder-documents-symbolic.svg")
                return QtGui.QIcon.fromTheme("text-x-generic")

        return QFileSystemModel.data(self, index, role)



class DateFormatDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(DateFormatDelegate, self).__init__(parent)
        self.format = "dd-MMM-yy"

    def displayText(self, value, locale):
        # return value.toDate().toString(self.date_format)
        # return QDate.fromString(value, "yyyy-MM-dd").toString(self.format)
        return QDateTime.fromString(value, "MM/dd/yy hh:mm a").toString(self.format)


class filesWidget():
    def __init__(self):
        # global listIcon
        # global iconsIcon
        global currIconFiles
        global currListFiles

        self.threadpool = QtCore.QThreadPool()

        self.main_ui = uic.loadUi(main_ui_file)
        self.main_ui.setWindowTitle("FILES")
        self.main_ui.setWindowIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons" , "folder-main.svg")))

        sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
        self.main_ui.setStyleSheet(sS.read())
        sS.close()
        os.environ['FILES_THEME'] = "dark"

        # currIconFiles = self.main_ui.iconFiles
        # currListFiles = self.main_ui.listFiles

        self.main_ui.currentFolderBox.clear()
        self.main_ui.currentFolderBox.setText(ROOTDIR)

        # self.main_ui.treeDirs.sortByColumn(0, QtCore.Qt.AscendingOrder)
        # currListFiles.sortByColumn(0, QtCore.Qt.AscendingOrder)

        ROOTDIRNEW = os.path.abspath(self.main_ui.currentFolderBox.text().strip())
        debug.info(ROOTDIRNEW)

        modelDirs = self.setDir(ROOTDIRNEW)

        # ICONS
        self.homeIcon = os.path.join(projDir, "imageFiles", "icons", "home.svg")
        self.darkIcon = os.path.join(projDir, "imageFiles", "icons", "moon.svg")
        self.lightIcon = os.path.join(projDir, "imageFiles", "icons", "sun.svg")
        self.listIcon = os.path.join(projDir, "imageFiles", "icons", "layout-list.svg")
        self.iconsIcon = os.path.join(projDir, "imageFiles", "icons", "layout-grid.svg")
        self.prevDirIcon = os.path.join(projDir, "imageFiles", "icons", "arrow-up.svg")
        self.goIcon = os.path.join(projDir, "imageFiles", "icons", "rotate-cw.svg")
        self.searchIcon = os.path.join(projDir, "imageFiles", "icons", "search.svg")
        self.clearIcon = os.path.join(projDir, "imageFiles", "icons", "clear.svg")
        self.closeIcon = os.path.join(projDir, "imageFiles", "icons", "close.svg")
        self.addIcon = os.path.join(projDir, "imageFiles", "icons", "plus.svg")
        self.removeIcon = os.path.join(projDir, "imageFiles", "icons", "minus.svg")
        self.renameIcon = os.path.join(projDir, "imageFiles", "icons", "edit.svg")
        self.copyIcon = os.path.join(projDir, "imageFiles", "icons", "copy.svg")
        self.cutIcon = os.path.join(projDir, "imageFiles", "icons", "cut.svg")
        self.pasteIcon = os.path.join(projDir, "imageFiles", "icons", "paste.svg")
        self.deleteIcon = os.path.join(projDir, "imageFiles", "icons", "delete.svg")
        self.newFolderIcon = os.path.join(projDir, "imageFiles", "icons", "new-folder.svg")
        self.addFavouritesIcon = os.path.join(projDir, "imageFiles", "icons", "add-favourites.svg")
        self.detailsIcon = os.path.join(projDir, "imageFiles", "icons", "info.svg")
        self.helpIcon = os.path.join(projDir, "imageFiles", "icons", "help.svg")

        self.homeGIcon = os.path.join(projDir, "imageFiles", "icons", "home-green.svg")
        self.folderIcon = os.path.join(projDir, "imageFiles", "icons", "folder-other.svg")
        self.serverIcon = os.path.join(projDir, "imageFiles", "icons", "server-green.svg")
        self.downloadIcon = os.path.join(projDir, "imageFiles", "icons", "download-green.svg")
        self.tempIcon = os.path.join(projDir, "imageFiles", "icons", "folder-temp-green.svg")

        # listIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "view_list.png"))
        # self.listIcon = os.path.join(projDir, "imageFiles", "new_icons", "view_list.svg")
        # self.iconsIcon = os.path.join(projDir, "imageFiles", "new_icons", "view_icons.svg")
        # self.prevDirIcon = os.path.join(projDir, "imageFiles", "new_icons", "go-up.svg")
        # self.goIcon = os.path.join(projDir, "imageFiles", "new_icons", "reload.svg")
        # self.searchIcon = os.path.join(projDir, "imageFiles", "search_icon.svg")
        # self.closeIcon = os.path.join(projDir, "imageFiles", "new_icons", "close.svg")
        # self.addIcon = os.path.join(projDir, "imageFiles", "new_icons", "add.svg")
        # self.removeIcon = os.path.join(projDir, "imageFiles", "new_icons", "remove.svg")
        # self.helpIcon = os.path.join(projDir, "imageFiles", "help-icon-1.png")
        # self.copyIcon = os.path.join(projDir, "imageFiles", "new_icons", "copy.svg")
        # self.cutIcon = os.path.join(projDir, "imageFiles", "new_icons", "cut.svg")
        # self.pasteIcon = os.path.join(projDir, "imageFiles", "new_icons", "paste.svg")
        # self.newFolderIcon = os.path.join(projDir, "imageFiles", "new_icons", "new_folder.svg")
        # self.addFavouritesIcon = os.path.join(projDir, "imageFiles", "new_icons", "add_favourites.svg")
        # self.renameIcon = os.path.join(projDir, "imageFiles", "new_icons", "rename.svg")
        # self.deleteIcon = os.path.join(projDir, "imageFiles", "new_icons", "delete.svg")
        # self.detailsIcon = os.path.join(projDir, "imageFiles", "new_icons", "details.svg")

        self.openDir(homeDir)
        self.initConfig()
        self.loadFavourites()

        # self.main_ui.tabWidget.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        # self.main_ui.tabWidget.customContextMenuRequested.connect(lambda x, context=self.main_ui.tabWidget.currentWidget().viewport(): self.popUpTabs(context, x))
        self.main_ui.tabWidget.customContextMenuRequested.connect(self.popUpTabs)
        # self.main_ui.connect(self.main_ui.tabWidget, SIGNAL('customContextMenuRequested(const QPoint &)'), self.popUpTabs)
        self.main_ui.tabWidget.currentChanged.connect(self.current_tab_changed)
        self.main_ui.tabWidget.tabCloseRequested.connect(self.close_current_tab)

        self.main_ui.changeViewButt.setIcon(QtGui.QIcon(self.iconsIcon))
        self.main_ui.previousDirButt.setIcon(QtGui.QIcon(self.prevDirIcon))
        self.main_ui.changeDirButt.setIcon(QtGui.QIcon(self.goIcon))
        self.main_ui.searchButt.setIcon(QtGui.QIcon(self.searchIcon))
        self.main_ui.homeButt.setIcon(QtGui.QIcon(self.homeIcon))
        self.main_ui.themeButt.setIcon(QtGui.QIcon(self.lightIcon))

        self.main_ui.currentFolderBox.findChild(QtWidgets.QToolButton).setIcon(QtGui.QIcon(self.clearIcon))
        self.main_ui.searchBox.findChild(QtWidgets.QToolButton).setIcon(QtGui.QIcon(self.clearIcon))

        # self.changeViewSc = QShortcut(QKeySequence("Ctrl+V"), self)
        # self.changeViewSc.activated.connect(self.changeView)
        QShortcut(QKeySequence("Ctrl+T"),self.main_ui).activated.connect(self.tab_open_doubleclick)
        # QShortcut(QKeySequence("Ctrl+W"),self.main_ui).activated.connect(lambda currTabIndex = self.main_ui.tabWidget.currentIndex() :self.close_current_tab(currTabIndex))
        QShortcut(QKeySequence("Ctrl+F"),self.main_ui).activated.connect(self.main_ui.searchBox.setFocus)

        self.main_ui.changeViewButt.setShortcut(QtGui.QKeySequence("V"))
        self.main_ui.previousDirButt.setShortcut(QtGui.QKeySequence("Backspace"))
        self.main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))

        self.main_ui.changeViewButt.setToolTip("Change View (V)")
        self.main_ui.previousDirButt.setToolTip("Previous Directory (Backspace)")
        self.main_ui.changeDirButt.setToolTip("Change Directory (Enter)")

        self.main_ui.themeButt.clicked.connect(self.changeTheme)
        self.main_ui.homeButt.clicked.connect(self.goHome)
        self.main_ui.searchBox.textChanged.connect(lambda x : self.search())
        self.main_ui.changeViewButt.clicked.connect(lambda x : self.changeView())
        self.main_ui.previousDirButt.clicked.connect(lambda x: self.previousDir())
        self.main_ui.changeDirButt.clicked.connect(lambda x: self.changeDir())
        self.main_ui.searchButt.clicked.connect(lambda x: self.search())

        self.main_ui.audioRestartButt.clicked.connect(lambda x: self.audioRestart())
        self.main_ui.fixPenDisplayButt.clicked.connect(lambda x: self.fixPenDisplay())
        self.main_ui.blenderMediaViewerButt.clicked.connect(lambda x: self.blenderMediaViewer())
        self.main_ui.downloadButt.clicked.connect(lambda x: self.downloadVideo())
        self.main_ui.cancelButt.clicked.connect(lambda x: self.cancelVideoDownload())

        try:
            currIconFiles.customContextMenuRequested.connect(lambda x, context=currIconFiles.viewport(): self.popUpFiles(context, x))
            currIconFiles.doubleClicked.connect(lambda x : self.openFile())
            currListFiles.customContextMenuRequested.connect(lambda x, context=currListFiles.viewport() : self.popUpFiles(context, x))
            currListFiles.doubleClicked.connect(lambda x : self.openFile())
        except:
            debug.info(str(sys.exc_info()))

        self.main_ui.progressBar.hide()
        self.main_ui.downloadProgressBar.hide()
        self.main_ui.cancelButt.setEnabled(False)
        self.main_ui.cancelButt.hide()
        self.messages("white", "")

        self.main_ui.splitter01.setSizes([100, 140])
        # self.main_ui.searchButt.hide()

        try:
            currListFiles.setColumnWidth(0, 660)
            currIconFiles.hide()
        except:
            debug.info(str(sys.exc_info()))

        # self.main_ui.places_label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
        # self.main_ui.places_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.main_ui.places_label.setText("<b>Places</b>")

        self.main_ui.tools_label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
        self.main_ui.tools_label.setAlignment(QtCore.Qt.AlignCenter)
        self.main_ui.tools_label.setText("<b>Tools</b>")

        # self.main_ui.search_label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
        # self.main_ui.search_label.setAlignment(QtCore.Qt.AlignCenter)
        # self.main_ui.search_label.setText("<b>Search</b>")

        self.main_ui.searchBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.main_ui.searchBox.setFocus()

        self.tab_open_doubleclick()

        self.main_ui.showMaximized()
        self.main_ui.update()

        qtRectangle = self.main_ui.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.main_ui.move(qtRectangle.topLeft())


    def initConfig(self):
        global places
        global confFile

        if os.path.exists(confFile):
            f = open(confFile)
            data = json.load(f)
            places = data
        else:
            with open(confFile, 'w') as conf_file:
                json.dump(places, conf_file, sort_keys=True, indent=4)


    def popUpTabs(self, pos):
        menu = QtWidgets.QMenu()
        self.setStyle(menu)
        newAction = menu.addAction(QtGui.QIcon(self.addIcon),"New Tab")
        closeAction = menu.addAction(QtGui.QIcon(self.closeIcon), "Close Tab")

        # action = menu.exec_(context.mapToGlobal(pos))
        action = menu.exec_(self.main_ui.tabWidget.mapToGlobal(pos))

        if (action == newAction):
            self.tab_open_doubleclick()
        if (action == closeAction):
            currTabIndex = self.main_ui.tabWidget.currentIndex()
            self.close_current_tab(currTabIndex)


    def tab_open_doubleclick(self):
        global currIconFiles
        global currListFiles
        global currView

        debug.info("Tab Opened")
        content = QFrame()

        layV = QtWidgets.QVBoxLayout()
        content.setLayout(layV)
        iconFiles1 = widgetProvider.iconFiles()
        listFiles1 = widgetProvider.listFiles()
        layV.addWidget(iconFiles1)
        layV.addWidget(listFiles1)

        currIconFiles = iconFiles1
        currListFiles = listFiles1

        if currView == "LIST":
            currIconFiles.hide()
            currListFiles.show()
        elif currView == "ICON":
            currIconFiles.show()
            currListFiles.hide()
        # currIconFiles.hide()
        currListFiles.setColumnWidth(0, 660)

        currIconFiles.customContextMenuRequested.connect(lambda x, context=currIconFiles.viewport(): self.popUpFiles(context, x))
        currIconFiles.doubleClicked.connect(lambda x: self.openFile())
        currListFiles.customContextMenuRequested.connect(lambda x, context=currListFiles.viewport(): self.popUpFiles(context, x))
        currListFiles.doubleClicked.connect(lambda x: self.openFile())

        currDirPath = str(os.path.abspath(self.main_ui.currentFolderBox.text().strip()))
        currDirName = str(os.path.abspath(self.main_ui.currentFolderBox.text().strip())).split(os.sep)[-1]


        i = self.main_ui.tabWidget.addTab(content, currDirName)
        self.main_ui.tabWidget.setCurrentIndex(i)

        self.openDir(currDirPath)
        # self.main_ui.tabWidget.currentWidget().customContextMenuRequested.connect(self.popUpTabs)

        # self.main_ui.currentFolderBox.clear()
        # self.main_ui.currentFolderBox.setText(self.main_ui.tabWidget.tabToolTip(i))


    def current_tab_changed(self, i):
        global currIconFiles
        global currListFiles
        global currView

        currIconFiles = self.main_ui.tabWidget.currentWidget().findChild(QtWidgets.QListView)
        currListFiles = self.main_ui.tabWidget.currentWidget().findChild(QtWidgets.QTreeView)

        try:
            currTabIndex = self.main_ui.tabWidget.currentIndex()
            # currTabName = self.main_ui.tabWidget.tabText(currTabIndex)
            currDirPath = self.main_ui.tabWidget.tabToolTip(currTabIndex)
            # debug.info(currDirPath)
            self.main_ui.currentFolderBox.clear()
            self.main_ui.currentFolderBox.setText(currDirPath)
            self.main_ui.pathBox.clear()
            self.main_ui.pathBox.setText(currDirPath)
        except:
            debug.info(str(sys.exc_info()))
        # currTabIndex = self.main_ui.tabWidget.currentIndex()
        # debug.info(openTabs)
        if currListFiles.isVisible() and currIconFiles.isHidden():
            currView = "LIST"
            self.main_ui.changeViewButt.setIcon(QtGui.QIcon(self.iconsIcon))
        elif currIconFiles.isVisible() and currListFiles.isHidden():
            currView = "ICON"
            self.main_ui.changeViewButt.setIcon(QtGui.QIcon(self.listIcon))

    def close_current_tab(self, i):
        # global currIconFiles
        # global currListFiles
        #
        # currIconFiles = self.main_ui.tabWidget.currentWidget().findChild(QtWidgets.QListView)
        # currListFiles = self.main_ui.tabWidget.currentWidget().findChild(QtWidgets.QTreeView)
        debug.info(i)
        if self.main_ui.tabWidget.count() < 2:
            return

        self.main_ui.tabWidget.removeTab(i)
        # try:
        #     openTabs.pop(list(openTabs.keys())[i])
        # except:
        #     debug.info(str(sys.exc_info()))


    def loadFavourites(self):
        global places
        model = QtGui.QStandardItemModel()
        self.main_ui.favourites.setModel(model)

        sortedPlaces = OrderedDict(sorted(places.items()))
        for key, value in sortedPlaces.items():
            item = QtGui.QStandardItem(key)
            model.appendRow(item)

            frame = QtWidgets.QFrame()
            hLay = QtWidgets.QHBoxLayout()
            hLay.setContentsMargins(0, 0, 0, 0)

            line = QtWidgets.QLineEdit()
            line.setText(key)
            line.hide()

            thumb = QtWidgets.QPushButton()

            thumb.setText(key)

            if key == "Home":
                # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "home.svg")))
                thumb.setIcon(QtGui.QIcon(self.homeGIcon))
            elif key == "Downloads":
                # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "downloads.svg")))
                thumb.setIcon(QtGui.QIcon(self.downloadIcon))
            elif key == "Tmp":
                # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "temp.svg")))
                thumb.setIcon(QtGui.QIcon(self.tempIcon))
            elif key == "Crap":
                # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "crap.svg")))
                thumb.setIcon(QtGui.QIcon(self.serverIcon))
            else:
                # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "folder-other.svg")))
                thumb.setIcon(QtGui.QIcon(self.folderIcon))

            thumb.setFocusPolicy(Qt.NoFocus)

            thumb.setStyleSheet(''' QPushButton { text-align: left; border-style: transparent; padding-left: 8px; }
                                                QPushButton:hover { border: 1px solid #3daee9; } ''')

            entButt = QtWidgets.QPushButton()
            entButt.setFocusPolicy(Qt.NoFocus)
            entButt.hide()

            thumb.clicked.connect(lambda x, path=value : self.openDir(path))
            entButt.clicked.connect(lambda x, button=thumb,editor=line,entButt=entButt : self.changeFavName(button,editor,entButt))

            thumb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            thumb.customContextMenuRequested.connect(lambda x,button=thumb,editor=line,entButt=entButt : self.favouritesPopup(button,editor,entButt,x))

            hLay.addWidget(thumb)
            hLay.addWidget(line)
            hLay.addWidget(entButt)
            frame.setLayout(hLay)

            self.main_ui.favourites.setIndexWidget(item.index(), frame)

    def favouritesPopup(self,button,editor,entButt,pos):
        global places
        currName = button.text()
        # editorName = editor.text()
        debug.info(currName)
        # debug.info(editorName)

        menu = QtWidgets.QMenu()
        self.setStyle(menu)
        rename = menu.addAction(QtGui.QIcon(self.renameIcon),"Rename")
        remove = menu.addAction(QtGui.QIcon(self.removeIcon),"Remove")
        # action = menu.exec_(context.mapToGlobal(pos))
        action = menu.exec_(button.mapToGlobal(pos))

        if action == rename:
            self.main_ui.changeDirButt.setShortcut(QtGui.QKeySequence(""))
            entButt.setShortcut(QtGui.QKeySequence("Return"))
            button.hide()
            editor.show()
            entButt.show()
            editor.setFocus()

        if action == remove:
            places.pop(currName)
            with open(confFile, 'w') as conf_file:
                json.dump(places, conf_file, sort_keys=True, indent=4)
            self.initConfig()
            self.loadFavourites()


    def changeFavName(self,button,editor,entButt):
        currName = button.text()
        newName = editor.text()
        debug.info(currName)
        debug.info(newName)

        if newName == currName:
            debug.info("no changes found in name")
        else:
            for key,value in places.items():
                if key == currName:
                    places[newName] = value
                    places.pop(key)
                    with open(confFile, 'w') as conf_file:
                        json.dump(places, conf_file, sort_keys=True, indent=4)
                    self.initConfig()
                    self.loadFavourites()

        button.show()
        editor.hide()
        entButt.hide()
        editor.clearFocus()
        self.main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))
        entButt.setShortcut(QtGui.QKeySequence(""))


    def setDir(self, ROOTDIRNEW):
        self.clearAllSelection()
        # debug.info(type(ROOTDIRNEW))
        if "/blueprod/STOR" in ROOTDIRNEW:
            debug.info("Danger zone")
            # self.main_ui.treeDirs.itemsExpandable = False
            # self.main_ui.treeDirs.collapseAll()
        else:
            # self.messages("green","Generating thumbnails")
            # self.main_ui.treeDirs.itemsExpandable = True
            modelDirs = FSM(parent=self.main_ui)
            # modelDirs.setIconProvider(IconProvider())
            # modelDirs.setIconProvider(CustomIconProvider())
            modelDirs.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
            modelDirs.setRootPath(ROOTDIRNEW)

            # self.main_ui.treeDirs.setModel(modelDirs)

            # self.main_ui.treeDirs.hideColumn(1)
            # self.main_ui.treeDirs.hideColumn(2)
            # self.main_ui.treeDirs.hideColumn(3)

            rootIdx = modelDirs.index(ROOTDIRNEW)
            # self.main_ui.treeDirs.setRootIndex(rootIdx)

            # openDir(ROOTDIRNEW, self.main_ui)
            return (modelDirs)


    def openDir(self, dirPath):
        global currListFiles

        if not os.path.exists(dirPath):
            self.messages("red", "Error! Path not found.")
            return

        self.clearAllSelection()
        self.openListDir(dirPath)
        self.openIconDir(dirPath)

        self.main_ui.pathBox.setText(dirPath)

        currDirPath = str(dirPath)
        currDirName = str(currDirPath.split(os.sep)[-1])
        currTabIndex = self.main_ui.tabWidget.currentIndex()
        # debug.info(currTabIndex)
        # openTabs[currTabIndex] = {currDirName:currDirPath}

        self.main_ui.tabWidget.setTabText(currTabIndex, currDirName)
        self.main_ui.tabWidget.setTabToolTip(currTabIndex, currDirPath)
        try:
            currListFiles.setColumnWidth(0, 660)
            # self.main_ui.currentFolderBox.clear()
            # self.main_ui.currentFolderBox.setText(currDirPath)
        except:
            debug.info(str(sys.exc_info()))

        worker = Worker(self.genThumb,dirPath)
        self.threadpool.start(worker)


    def genThumb(self, dirPath, progress_callback):
        files = [f for f in os.listdir(dirPath) if os.path.isfile(os.path.join(dirPath, f))]
        for f in files:
            # debug.info(f)
            if f.startswith("."):
                pass
            else:
                file_path = os.path.join(dirPath, f)
                file_extension = os.path.splitext(file_path)[1]
                # debug.info(file_extension)

                # ext = file_extension.split(".")[1]
                ext = file_extension.replace(".", "").strip()
                # debug.info(ext)

                if ext in mimeTypes["video"]:
                    thumb_image = filesThumbsDir + f + ".jpeg"
                    if os.path.exists(thumb_image):
                        pass
                    else:
                        try:
                            # genThumbCmd = "ffmpeg -ss 00:00:01.000 -i \"{0}\" -vf 'scale=128:128:force_original_aspect_ratio=decrease' -vframes 1 \"{1}\" -y ".format(
                            #               file_path, thumb_image)
                            genThumbCmd = mimeConvertCmds["video"].format(file_path, thumb_image)
                            subprocess.call(shlex.split(genThumbCmd))
                        except:
                            debug.info(str(sys.exc_info()))

                if ext in mimeTypes["image"]:
                    thumb_image = filesThumbsDir + f + ".jpeg"
                    if os.path.exists(thumb_image):
                        pass
                    else:
                        try:
                            # im = Image.open(file_path)
                            # im.thumbnail((128,128))
                            # im.save(thumb_image)
                            genThumbCmd = mimeConvertCmds["image"].format(file_path, thumb_image)
                            subprocess.call(shlex.split(genThumbCmd))
                        except:
                            debug.info(str(sys.exc_info()))


    def openListDir(self, dirPath):
        global CUR_DIR_SELECTED
        global currIconFiles
        global currListFiles

        CUR_DIR_SELECTED = dirPath.strip()
        debug.info(CUR_DIR_SELECTED)

        searchTerm = self.main_ui.searchBox.text().strip()
        # debug.info(searchTerm)

        permitted = True
        for x in prohibitedDirs:
            if x in CUR_DIR_SELECTED:
                permitted = False
        if permitted:
            # self.messages("green", "Generating thumbnails")
            # self.main_ui.treeDirs.itemsExpandable = True
            self.main_ui.currentFolderBox.clear()
            self.main_ui.currentFolderBox.setText(CUR_DIR_SELECTED)

            modelFiles = FSM(parent=self.main_ui)
            # modelFiles.setIconProvider(IconProvider())
            try:
                currListFiles.setModel(modelFiles)
            except:
                debug.info(str(sys.exc_info()))
            modelFiles.setRootPath(CUR_DIR_SELECTED)

            modelFiles.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
            modelFiles.setNameFilters([searchTerm+"*"])
            modelFiles.setNameFilterDisables(False)
            debug.info(modelFiles.nameFilters())

            rootIdx = modelFiles.index(CUR_DIR_SELECTED)
            try:
                currListFiles.setRootIndex(rootIdx)
                currListFiles.setItemDelegateForColumn(3, DateFormatDelegate())
            except:
                debug.info(str(sys.exc_info()))
            return
        else:
            debug.info("Danger zone")
            debug.info("Error! No permission to open.")
            self.messages("red", "Error! No permission to open.")
            # self.main_ui.treeDirs.itemsExpandable = False
            # self.main_ui.treeDirs.collapseAll()
            return


    def openIconDir(self, dirPath):
        global CUR_DIR_SELECTED
        global currIconFiles
        global currListFiles

        CUR_DIR_SELECTED = dirPath.strip()
        debug.info(CUR_DIR_SELECTED)

        searchTerm = self.main_ui.searchBox.text().strip()
        # debug.info(searchTerm)

        permitted = True
        for x in prohibitedDirs:
            if x in CUR_DIR_SELECTED:
                permitted = False
        if permitted:
            # self.messages("green", "Generating thumbnails")
            # self.main_ui.treeDirs.itemsExpandable = True
            self.main_ui.currentFolderBox.clear()
            self.main_ui.currentFolderBox.setText(CUR_DIR_SELECTED)

            modelFiles = FSM(parent=self.main_ui)
            # modelFiles.setIconProvider(IconProvider())
            try:
                currIconFiles.setModel(modelFiles)
            except:
                debug.info(str(sys.exc_info()))
            modelFiles.setRootPath(CUR_DIR_SELECTED)

            modelFiles.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
            modelFiles.setNameFilters([searchTerm + "*"])
            modelFiles.setNameFilterDisables(False)
            debug.info(modelFiles.nameFilters())

            rootIdx = modelFiles.index(CUR_DIR_SELECTED)
            try:
                currIconFiles.setRootIndex(rootIdx)
            except:
                debug.info(str(sys.exc_info()))
            return
        else:
            debug.info("Danger zone")
            debug.info("Error! No permission to open.")
            self.messages("red", "Error! No permission to open.")
            # self.main_ui.treeDirs.itemsExpandable = False
            # self.main_ui.treeDirs.collapseAll()
            return


    def dirSelected(self, index, model):
        dirPath = model.filePath(index)
        self.openDir(dirPath)


    def clearAllSelection(self):
        global currIconFiles
        global currListFiles

        try:
            currIconFiles.clearSelection()
            currListFiles.clearSelection()
        except:
            debug.info(str(sys.exc_info()))
        debug.info("Cleared Selection")


    def changeView(self):
        global currIconFiles
        global currListFiles
        global currView

        self.clearAllSelection()
        if currView == "LIST":
            self.main_ui.changeViewButt.setIcon(QtGui.QIcon(self.listIcon))
            currView = "ICON"
            currIconFiles.show()
            currListFiles.hide()
        elif currView == "ICON":
            self.main_ui.changeViewButt.setIcon(QtGui.QIcon(self.iconsIcon))
            currView = "LIST"
            currIconFiles.hide()
            currListFiles.show()

        # if currIconFiles.isHidden():
        #     self.main_ui.changeViewButt.setIcon(QtGui.QIcon(self.listIcon))
        #     currIconFiles.show()
        #     currListFiles.hide()
        # else:
        #     self.main_ui.changeViewButt.setIcon(QtGui.QIcon(self.iconsIcon))
        #     currIconFiles.hide()
        #     currListFiles.show()


    def previousDir(self):
        # debug.info("previous directory")
        ROOTDIR = self.main_ui.currentFolderBox.text().strip()
        if ROOTDIR != "":
            if os.path.exists(ROOTDIR):
                ROOTDIRNEW = os.sep.join(ROOTDIR.split(os.sep)[:-1])
                debug.info(ROOTDIRNEW)
                if os.path.exists(ROOTDIRNEW):
                    self.openDir(ROOTDIRNEW)
                    self.messages("white", "")
            else:
                debug.info("No such folder!")


    def changeDir(self):
        ROOTDIR = self.main_ui.currentFolderBox.text().strip()
        if ROOTDIR != "":
            ROOTDIRNEW = os.path.abspath(os.path.expanduser(ROOTDIR))
            if os.path.exists(ROOTDIRNEW):
                debug.info (ROOTDIRNEW)
                self.openDir(ROOTDIRNEW)
                self.messages("white", "")
            else:
                self.messages("red","No such folder!")


    def search(self):
        ROOTDIR = self.main_ui.currentFolderBox.text().strip()
        self.openDir(ROOTDIR)


    def clearPath(self):
        self.main_ui.currentFolderBox.clear()


    def getSelectedFiles(self):
        global currIconFiles
        global currListFiles

        model = None
        selectedIndexes = None
        files =[]

        if currIconFiles.isVisible():
            model = currIconFiles.model()
            selectedIndexes = currIconFiles.selectedIndexes()
        elif currListFiles.isVisible():
            model = currListFiles.model()
            selectedIndexes = currListFiles.selectedIndexes()

        for selectedIndex in selectedIndexes:
            try:
                filePath = os.path.abspath(str(model.filePath(selectedIndex)))
                files.append(filePath)
            except:
                debug.info(str(sys.exc_info()))

        files = list(OrderedDict.fromkeys(files))
        return (model,selectedIndexes,files)


    def openFile(self):
        debug.info("double clicked!!!")

        model, selectedIndexes, selectedFiles = self.getSelectedFiles()
        indexes = [i for i in selectedIndexes if i.column() == 0]
        # debug.info(indexes)
        for index in indexes:
            try:
                fileInfo = model.fileInfo(index)
                filePath = os.path.abspath(str(model.filePath(index)))
                fileName = str(model.fileName(index))
                debug.info(filePath)
                debug.info(fileName)

                if fileInfo.isDir():
                    debug.info("This is a directory!")
                    self.main_ui.searchBox.clear()
                    self.openDir(filePath)

                if fileInfo.isFile():
                    debug.info("This is a file!")
                    try:
                        suffix = pathlib.Path(fileName).suffix.split('.')[-1]
                        debug.info(suffix)
                        openCmd = ""
                        if suffix in mimeTypes["video"]:
                            openCmd = mimeTypesOpenCmds["video"].format(os.path.join(projDir,"video-input.conf"),filePath)
                        elif suffix in mimeTypes["audio"]:
                            openCmd = mimeTypesOpenCmds["audio"].format(filePath)
                        elif (suffix in mimeTypes["image"]):
                            # openCmd = projDir+os.sep+"mediaPlayer.py --path '{0}' ".format(filePath)
                            openCmd = mimeTypesOpenCmds["image"].format(os.path.join(projDir,"image-input.conf"),filePath)
                            # openCmd = "pureref \"{0}\" ".format(filePath)
                        elif suffix in mimeTypes["text"]:
                            openCmd = mimeTypesOpenCmds["text"].format(filePath)
                        elif suffix == "pdf":
                            openCmd = mimeTypesOpenCmds["pdf"].format(filePath)
                        elif suffix == "pur":
                            openCmd = mimeTypesOpenCmds["pureref"].format(filePath)

                        debug.info(shlex.split(openCmd))
                        if openCmd:
                            subprocess.Popen(shlex.split(openCmd))
                    except:
                        debug.info(str(sys.exc_info()))
            except:
                debug.info(str(sys.exc_info()))


    def popUpFiles(self,context,pos):
        clip = QtWidgets.QApplication.clipboard()
        pasteUrls = clip.mimeData().urls()

        menu = QtWidgets.QMenu()
        self.setStyle(menu)

        # REMINDER : DO NOT ADD OPEN WITH ACTION

        copyAction = menu.addAction(QtGui.QIcon(self.copyIcon),"Copy")
        cutAction = menu.addAction(QtGui.QIcon(self.cutIcon),"Cut")
        pasteAction = menu.addAction(QtGui.QIcon(self.pasteIcon),"Paste")
        newFolderAction = menu.addAction(QtGui.QIcon(self.newFolderIcon),"New Folder")
        addToFavAction = menu.addAction(QtGui.QIcon(self.addFavouritesIcon),"Add To Favourites")
        renameAction = menu.addAction(QtGui.QIcon(self.renameIcon),"Rename")
        deleteAction = menu.addAction(QtGui.QIcon(self.deleteIcon),"Delete")
        detailsAction = menu.addAction(QtGui.QIcon(self.detailsIcon),"Details")

        model,selectedIndexes,selectedFiles = self.getSelectedFiles()
        action = menu.exec_(context.mapToGlobal(pos))


        if (action == copyAction):
            if (selectedFiles):
                self.copyFiles()
        if (action == cutAction):
            if (selectedFiles):
                self.cutFiles()
        if (action == pasteAction):
            self.pasteFiles(pasteUrls)
        if (action == newFolderAction):
            self.createNewFolder()
        if (action == addToFavAction):
            if (selectedFiles):
                self.addToFavourites()
        if (action == renameAction):
            if (selectedFiles):
                self.renameUi()
        if (action == deleteAction):
            if (selectedFiles):
                self.deleteFiles()
        if (action == detailsAction):
            if (selectedFiles):
                self.showDetails()


    def copyFiles(self):
        global cutFile
        cutFile = False
        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())))

        permitted = False
        for x in cutCopyPermittedDirs:
            if x in currDir:
                permitted = True
        if permitted:
            model,selectedIndexes,selectedFiles = self.getSelectedFiles()
            urlList = []
            mimeData = QtCore.QMimeData()
            for x in selectedFiles:
                debug.info("Copied "+x)
                urlList.append(QtCore.QUrl().fromLocalFile(x))
            mimeData.setUrls(urlList)
            QtWidgets.QApplication.clipboard().setMimeData(mimeData)
        else:
            debug.info("Error! No permission to copy.")
            self.messages("red", "Error! No permission to copy.")


    def cutFiles(self):
        global cutFile
        self.copyFiles()
        cutFile = True


    def pasteFiles(self,urls):
        global cutFile
        for url in urls:
            try:
                sourceFile = url.toLocalFile()
                destFolder = self.main_ui.currentFolderBox.text().strip()
                sourceFileName = os.path.basename(sourceFile)
                debug.info(sourceFile)
                debug.info(sourceFileName)
                # debug.info(destFolder)
                if destFolder:
                    destPath = os.path.abspath(destFolder)+"/"
                    # debug.info(destPath)
                    if destPath and os.path.exists(destPath):
                        permitted = False
                        for x in pastePermittedDirs:
                            if x in destPath:
                                permitted = True
                        if permitted:
                            if "/opt/home/bluepixels" in destPath: #REMINDER : Do NOT remove this code.
                                debug.info("Danger Zone: Can not paste")
                                return
                            else:
                                if os.path.exists(destPath+sourceFileName):
                                    debug.info("File already exists")
                                    self.messages("red", "File already exists")
                                else:
                                    remove_source_files=False
                                    if cutFile:
                                        remove_source_files=True
                                    self.messages("green", "Copying "+sourceFile)
                                    self.main_ui.progressBar.show()
                                    self.main_ui.progressBar.setValue(0)
                                    file_copy_thread = rsyncThread(sourceFile, destPath, app, remove_source_files=remove_source_files)
                                    file_copy_thread.progress_updated.connect(lambda x, source=sourceFile: self.update_progress(x, source))
                                    # file_copy_thread.finished.connect(self.copy_finished)
                                    file_copy_thread.finished.connect(lambda source=sourceFile, cutFile=cutFile: self.copy_finished(source,cutFile=cutFile))
                                    file_copy_thread.start()

                                    if cutFile:
                                        rmDirCmd = "rmdir \"{0}\" ".format(sourceFile)
                                        try:
                                            subprocess.Popen(shlex.split(rmDirCmd))
                                        except:
                                            debug.info(str(sys.exc_info()))

                                    # pasteCmd = ""
                                    # rmDirCmd = ""
                                    # if cutFile:
                                    #     pasteCmd = "rsync --remove-source-files -azHXW --info=progress2 \"{0}\" \"{1}\" ".format(sourceFile,destPath)
                                    #     rmDirCmd = "rmdir \"{0}\" ".format(sourceFile)
                                    # else:
                                    #     pasteCmd = "rsync -azHXW --info=progress2 \"{0}\" \"{1}\" ".format(sourceFile,destPath)
                                    # debug.info(pasteCmd)
                                    # self.messages("green", "Copying "+sourceFile)
                                    # p = subprocess.Popen(shlex.split(pasteCmd),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1, universal_newlines=True)
                                    # # for line in iter(p.stdout.readline, b''):
                                    # for line in p.stdout:
                                    #     synData = (tuple(filter(None, line.strip().split(' '))))
                                    #     if synData:
                                    #         prctg = synData[1].split("%")[0]
                                    #         debug.info(prctg)
                                    #         self.main_ui.progressBar.show()
                                    #         self.main_ui.progressBar.setValue(int(prctg))
                                    # subprocess.Popen(shlex.split("sync"))
                                    # if rmDirCmd:
                                    #     try:
                                    #         subprocess.Popen(shlex.split(rmDirCmd))
                                    #     except:
                                    #         debug.info(str(sys.exc_info()))
                        else:
                            debug.info("Danger Zone: Can not paste")
                            debug.info("Error! No permission to paste.")
                            self.messages("red", "Error! No permission to paste.")
                # self.main_ui.progressBar.hide()
                # messages(self.main_ui, "white", "")
            except:
                debug.info(str(sys.exc_info()))


    def update_progress(self, progress, source):
        debug.info(progress)
        self.main_ui.progressBar.show()
        self.messages("green", "Copying "+source)
        self.main_ui.progressBar.setValue(int(progress))


    def copy_finished(self, source, cutFile=False):
        self.main_ui.progressBar.hide()
        subprocess.Popen(shlex.split("sync"))
        self.messages("green", "Finished copying")

        if cutFile:
            rmDirCmd = "rmdir \"{0}\" ".format(source)
            try:
                subprocess.Popen(shlex.split(rmDirCmd))
            except:
                debug.info(str(sys.exc_info()))


    def createNewFolder(self):
        self.clearInfoFrame()
        self.main_ui.splitter01.setSizes([100, 140])
        layOut = self.main_ui.infoFrame.layout()

        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())))
        debug.info(currDir)

        permitted = False
        for x in newFolderPermittedDirs:
            if x in currDir:
                permitted = True
        if permitted:
            label = QtWidgets.QLabel()
            nameLine = QtWidgets.QLineEdit()
            createButton = QtWidgets.QPushButton()
            cancelButton = QtWidgets.QPushButton()
            vSpacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            layOut.addWidget(label, 1, 0, 1, 2)
            layOut.addWidget(nameLine, 2, 0, 1, 2)
            layOut.addWidget(cancelButton, 3, 0)
            layOut.addWidget(createButton, 3, 1)
            layOut.addItem(vSpacer)
            self.main_ui.searchBox.setFocusPolicy(QtCore.Qt.ClickFocus)
            self.main_ui.searchBox.setFocus()
            nameLine.setFocusPolicy(QtCore.Qt.StrongFocus)
            nameLine.setFocus()
            label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setText("<b>Create New Folder</b>")
            nameLine.setText("New_Folder")
            cancelButton.setText("Cancel")
            createButton.setText("Create")
            self.main_ui.changeDirButt.setShortcut(QtGui.QKeySequence(""))
            createButton.setShortcut(QtGui.QKeySequence("Return"))
            cancelButton.setShortcut(QtGui.QKeySequence("Escape"))
            createButton.clicked.connect(lambda x, line=nameLine: self.addFolder(line))
            cancelButton.clicked.connect(self.clearInfoFrame)
        else:
            debug.info("Danger Zone: Can not create new folder")
            debug.info("Error! No permission to create new folder.")
            self.messages("red", "Error! No permission to create new folder.")
            self.clearInfoFrame()
            return


    def addFolder(self, line):
        debug.info(line.text())

        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())))
        debug.info(currDir)

        newFolderName = str(line.text()).strip()
        dirs = [x for x in os.listdir(currDir) if not x.startswith(".") and os.path.isdir(os.path.join(currDir, x))]
        debug.info(dirs)
        for i in range(1,100):
            if newFolderName in dirs:
                newFolderName += "_"+str(i)
            else:
                break

        newFolder = currDir + os.sep + newFolderName
        newFolderCmd = "mkdir \"{0}\" ".format(newFolder)
        debug.info(newFolderCmd)
        try:
            subprocess.Popen(shlex.split(newFolderCmd))
        except:
            debug.info(str(sys.exc_info()))
        self.clearInfoFrame()


    def clearInfoFrame(self):
        self.main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))
        self.main_ui.searchBox.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.main_ui.searchBox.setFocus()
        # self.main_ui.v_splitter1.setSizes([100, 140])
        layOut = self.main_ui.infoFrame.layout()
        if layOut:
            try:
                for i in reversed(range(layOut.count())):
                    widget = layOut.takeAt(i).widget()
                    if widget is not None:
                        widget.setParent(None)
            except:
                debug.info(str(sys.exc_info()))


    def addToFavourites(self):
        global places
        # currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())))
        model, selectedIndexes, selectedFiles = self.getSelectedFiles()

        indexes = [i for i in selectedIndexes if i.column() == 0]
        for index in indexes:
            try:
                fileInfo = model.fileInfo(index)
                fileName = (str(model.fileName(index)).capitalize())
                filePath = os.path.abspath(str(model.filePath(index)))
                if fileInfo.isDir():
                    places[fileName] = filePath
                    with open(confFile, 'w') as conf_file:
                        json.dump(places, conf_file, sort_keys=True, indent=4)
                    self.initConfig()
                    self.loadFavourites()
            except:
                debug.info(str(sys.exc_info()))


    def renameUi(self):
        self.clearInfoFrame()
        self.main_ui.splitter01.setSizes([100, 140])
        layOut = self.main_ui.infoFrame.layout()

        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())))
        model, selectedIndexes, selectedFiles = self.getSelectedFiles()

        fileDets = {}
        permitted = False
        for x in renamePermittedDirs:
            if x in currDir:
                permitted = True
        if permitted:
            indexes = [i for i in selectedIndexes if i.column() == 0]
            for index in indexes:
                try:
                    fileName = (str(model.fileName(index)))
                    filePath = os.path.abspath(str(model.filePath(index)))
                    fileDets[fileName] = filePath
                except:
                    debug.info(str(sys.exc_info()))
            debug.info(fileDets)
        else:
            debug.info("Error! No permission to rename.")
            self.messages("red", "Error! No permission to rename.")
            self.clearInfoFrame()
            return
        debug.info(fileDets)
        if (len(fileDets)) == 1:
            for key, value in fileDets.items():
                label = QtWidgets.QLabel()
                nameLine = QtWidgets.QLineEdit()
                renameButton = QtWidgets.QPushButton()
                cancelButton = QtWidgets.QPushButton()
                vSpacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
                layOut.addWidget(label, 1, 0, 1, 2)
                layOut.addWidget(nameLine, 2, 0, 1, 2)
                layOut.addWidget(cancelButton, 3, 0)
                layOut.addWidget(renameButton, 3, 1)
                layOut.addItem(vSpacer)
                self.main_ui.searchBox.setFocusPolicy(QtCore.Qt.ClickFocus)
                self.main_ui.searchBox.setFocus()
                nameLine.setFocusPolicy(QtCore.Qt.StrongFocus)
                nameLine.setFocus()
                label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setText("<b>Rename</b>")
                nameLine.setText(key)
                nameLine.setCursorPosition(0)
                cancelButton.setText("Cancel")
                renameButton.setText("Rename")
                self.main_ui.changeDirButt.setShortcut(QtGui.QKeySequence(""))
                renameButton.setShortcut(QtGui.QKeySequence("Return"))
                cancelButton.setShortcut(QtGui.QKeySequence("Escape"))
                renameButton.clicked.connect(lambda x, line=nameLine, path=currDir, name=key: self.renameNew(line, path, name))
                cancelButton.clicked.connect(self.clearInfoFrame)


    def renameNew(self, line, path, name):
        # newName = str(line.text()).strip()
        newName = line.text().strip()
        if os.path.exists(path+os.sep+newName):
            debug.info("Error! File Exists.")
            self.messages("red", "Error! File Exists.")
            self.clearInfoFrame()
            return
        cmd = "mv \"{0}\" \"{1}\" ".format(path + os.sep + name, path + os.sep + newName)
        debug.info(cmd)
        subprocess.Popen(shlex.split(cmd))
        self.clearInfoFrame()


    def deleteFiles(self):
        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())))
        debug.info(currDir)
        permitted = False
        for x in deletePermittedDirs:
            if x in currDir:
                permitted = True
        if permitted:
        # if "/opt/home/bluepixels/Downloads" in currDir:
            model,selectedIndexes,selectedFiles = self.getSelectedFiles()
            fileNames = []
            indexes = [i for i in selectedIndexes if i.column() == 0]
            for index in indexes:
                try:
                    fileName = (str(model.fileName(index)))
                    fileNames.append(fileName)
                except:
                    debug.info(str(sys.exc_info()))
            debug.info(fileNames)
            confirm = QtWidgets.QMessageBox()
            self.setStyle(confirm)
            # confirm.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png"))))
            confirm.setWindowTitle("Warning!")
            # confirm.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png"))))
            confirm.setIconPixmap(QtGui.QPixmap(self.helpIcon))
            confirm.setText("<b>Permanently Delete these item(s)?</b>"+"\n")
            confirm.setInformativeText(",\n".join(i for i in fileNames))
            confirm.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
            selection = confirm.exec_()
            if (selection == QtWidgets.QMessageBox.Yes):
                for x in selectedFiles:
                    # if "/opt/home/bluepixels/Downloads/" in x:
                    removeCmd = "rm -frv \"{0}\" ".format(x)
                    debug.info(shlex.split(removeCmd))
                    if removeCmd:
                        p = subprocess.Popen(shlex.split(removeCmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        output, error = p.communicate()
                        if p.returncode == 0:
                            debug.info("Deleted "+x)
                            self.changeDir()
                        else:
                            debug.info(f"Command failed with return code: {p.returncode}")
                        # debug.info("Deleted "+x)
                        # self.changeDir()
        else:
            debug.info("Error! No permission to delete.")
            self.messages("red","Error! No permission to delete.")


    def showDetails(self):
        self.clearInfoFrame()
        self.main_ui.splitter01.setSizes([100, 140])
        layOut = self.main_ui.infoFrame.layout()

        label = QtWidgets.QLabel()
        detsField = QtWidgets.QTextEdit()
        detsField.setReadOnly(True)
        # detsField.setStyleSheet(''' border: 1px solid #76797C; ''')
        detsField.setStyleSheet(''' QTextEdit { border: 1px solid #76797C; } ''')

        layOut.addWidget(label, 1, 0, 1, 2)
        layOut.addWidget(detsField, 2, 0, 1, 2)

        label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setText("<b>Properties</b>")

        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())))
        debug.info(currDir)
        model, selectedIndexes, selectedFiles = self.getSelectedFiles()
        debug.info(selectedFiles)

        fileNames = []
        indexes = [i for i in selectedIndexes if i.column() == 0]
        for index in indexes:
            fileName = (str(model.fileName(index)))
            fileNames.append(fileName)

        # detsField.append("\n")
        detsField.append("<b>Name : </b>"+", ".join(fileNames))
        detsField.append("<b>Location : </b>" + currDir)

        # allSelectedFiles = [file+"/*" for file in selectedFiles]

        detsCmd = ['du', '-sch']
        for file in selectedFiles:
            detsCmd = detsCmd + [file]
        debug.info(detsCmd)

        detsField.append("<b>Items : </b>" + str(len(selectedFiles)+len(detsCmd)-2))

        sT = getSizeThread(detsCmd, app)
        sT.result.connect(lambda x, textEdit=detsField: self.setSize(textEdit,x))
        sT.start()


    def setSize(self,textEdit,size):
        textEdit.append("<b>Size : </b>"+size+"B")


    def messages(self,color,msg):
        self.main_ui.messages.setStyleSheet("color: %s" %color)
        self.main_ui.messages.setText("%s"%msg)


    def setStyle(self,ui):
        light = os.path.join(projDir, "styleSheets", "light.qss")
        dark = os.path.join(projDir, "styleSheets", "dark.qss")
        theme = os.environ['FILES_THEME']
        if theme == "light":
            theme = light
            # os.environ['FILES_THEME'] = "light"
        else:
            theme = dark
            # os.environ['FILES_THEME'] = "dark"
        sS = open(theme, "r")
        ui.setStyleSheet(sS.read())
        sS.close()


    def changeTheme(self):
        light = os.path.join(projDir, "styleSheets", "light.qss")
        dark = os.path.join(projDir, "styleSheets", "dark.qss")

        theme = os.environ['FILES_THEME']
        if theme == "light":
            theme = dark
            os.environ['FILES_THEME'] = "dark"
            self.main_ui.themeButt.setIcon(QtGui.QIcon(self.lightIcon))
        else:
            theme = light
            os.environ['FILES_THEME'] = "light"
            self.main_ui.themeButt.setIcon(QtGui.QIcon(self.darkIcon))

        sS = open(theme, "r")
        self.main_ui.setStyleSheet(sS.read())
        sS.close()


    def goHome(self):
        self.openDir(homeDir)


    def audioRestart(self):
        arCmd = "/usr/local/bin/audio-restart"
        debug.info(arCmd)
        subprocess.Popen(arCmd)


    def fixPenDisplay(self):
        pdcmd = "/proj/standard/share/penDisplay.py"
        debug.info(pdcmd)
        subprocess.Popen(pdcmd)


    def blenderMediaViewer(self):
        bmvcmd = "/proj/standard/share/blender-3.0/blender --app-template blender_media_viewer -w"
        debug.info(bmvcmd)
        subprocess.Popen(shlex.split(bmvcmd))


    def updateDownloadProgress(self, prctg):
        self.main_ui.downloadProgressBar.setValue(int(prctg))


    def afterVideoDownload(self, msg):
        self.main_ui.downloadProgressBar.hide()
        self.main_ui.urlBox.setReadOnly(False)
        self.main_ui.pathBox.setReadOnly(False)
        self.main_ui.cancelButt.setEnabled(False)
        self.main_ui.downloadButt.setEnabled(True)
        self.main_ui.downloadButt.show()
        self.main_ui.cancelButt.hide()
        self.messages("green", msg)


    def downloadVideo(self):
        link = str(self.main_ui.urlBox.text().strip())
        downDir = str(os.path.abspath(os.path.expanduser(self.main_ui.pathBox.text().strip())))
        path = str(os.path.abspath(os.path.expanduser(self.main_ui.pathBox.text().strip())))+os.sep+"%(title)s.%(ext)s"
        if link:
            if os.path.exists(downDir):
                permitted = False
                for x in pastePermittedDirs:
                    if x in downDir:
                        permitted = True
                if permitted:
                    self.main_ui.downloadProgressBar.show()
                    self.main_ui.urlBox.setReadOnly(True)
                    self.main_ui.pathBox.setReadOnly(True)
                    self.main_ui.cancelButt.setEnabled(True)
                    self.main_ui.downloadButt.setEnabled(False)
                    self.main_ui.downloadButt.hide()
                    self.main_ui.cancelButt.show()

                    dT = downloadVideoThread(path,link, app)
                    dT.result.connect(lambda x : self.afterVideoDownload(x))
                    dT.progress.connect(lambda x : self.updateDownloadProgress(x))
                    # dT.finished.connect(lambda x : self.afterVideoDownload(x))
                    dT.start()
                else:
                    debug.info("No permission to write")
                    self.messages("red", "Not permitted!")
            else:
                debug.info("No such directory")
                self.messages("red", "Folder does not exists!")
        else:
            debug.info("URL field is empty")
            self.messages("red", "URL field is empty")


    def cancelVideoDownload(self):
        debug.info(currDownloads)
        for proc in currDownloads:
            try:
                debug.info(proc.pid)
                # os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                os.kill(proc.pid, signal.SIGTERM)
                subprocess.run("killall aria2c", shell=True)
                # TODO: Remove residuals from cancelled downloads
            except:
                debug.info(str(sys.exc_info()))
        self.afterVideoDownload("Cancelled")



class rsyncThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, source_path, destination_path, parent, remove_source_files=False):
        super(rsyncThread, self).__init__(parent)
        self.source_path = source_path
        self.destination_path = destination_path
        self.remove_source_files = remove_source_files

    def run(self):
        rsyncCommand = ""
        if self.remove_source_files:
            rsyncCommand = ["rsync", "--remove-source-files", "-azHXW", "--info=progress2", self.source_path, self.destination_path]
        else:
            rsyncCommand = ["rsync", "-azHXW", "--info=progress2", self.source_path, self.destination_path]
        
        process = subprocess.Popen(rsyncCommand,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1, universal_newlines=True)
        
        for line in process.stdout:
            synData = (tuple(filter(None, line.strip().split(' '))))
            # print (synData)
            if synData:
                try:
                    prctg = int(synData[1].split("%")[0])
                    # print (prctg)
                    self.progress_updated.emit(prctg)
                except:
                    debug.info(str(sys.exc_info()))
        process.wait()

        # Emit the finished signal
        self.finished.emit()



class downloadVideoThread(QThread):
    progress = pyqtSignal(int)
    result = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, path, link, parent):
        super(downloadVideoThread, self).__init__(parent)
        self.path = path
        self.link = link

    def run(self):
        downCmd = os.path.join(externalToolsDir,"yt-dlp_linux")+" --external-downloader aria2c --external-downloader-args " \
                  "'--summary-interval 1 --download-result=hide -c -s 10 -x 10 -k 1M' " \
                  "-o \"{0}\" \"{1}\" ".format(self.path,self.link)
        debug.info(downCmd)
        try:
            # p = subprocess.Popen(shlex.split(downCmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            #                      bufsize=1,universal_newlines=True, preexec_fn=os.setsid)
            # currDownloads.append(p)
            # msg = ""

            p = subprocess.Popen(shlex.split(downCmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            currDownloads.append(p)
            msg = ""
            for line in p.stdout:
                if line:
                    debug.info(line)
                    if "Unable to download webpage" in line:
                        msg = "Unable to download video"
                    elif "already been downloaded and merged" in line:
                        msg = "Already been downloaded and merged"
                    elif "100%" in line:
                        msg = "Video Downloaded"
                    elif "Unsupported URL" in line:
                        msg = "Unsupported URL"
                    elif "looks truncated" in line:
                        msg = "Url looks truncated"
                    elif "Unable to extract video data" in line:
                        msg = "Unable to extract video data"
                    elif "Download aborted" in line:
                        msg = "Download aborted"
                    elif "Redirecting to" in line:
                        msg = "Aborted"
                    elif "%" in line:
                        synData = (tuple(filter(None, line.strip().split('('))))
                        if synData:
                            prctg = synData[1].split("%")[0].strip()
                            self.progress.emit(int(prctg))
                    
                    elif "Deleting original file" in line:
                        self.result.emit("Download finished")
                        self.finished.emit()
                        
            if p.returncode == 0:
                self.result.emit("Download finished")
                self.finished.emit()
            else:
                debug.info(f"Command failed with return code: {p.returncode}")
        except:
            debug.info(str(sys.exc_info()))
        else:
            self.result.emit(msg)
        finally:
            self.finished.emit()
            return


class getSizeThread(QThread):
    finished = pyqtSignal()
    result = pyqtSignal(str)

    def __init__(self,cmd,parent):
        super(getSizeThread, self).__init__(parent)
        self.cmd = cmd

    def run(self):
        try:
            p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
                                 universal_newlines=True)
            out, err = p.communicate()
            size = out.split("\t")[-2].split("\n")[1]
        except:
            debug.info(str(sys.exc_info()))
        else:
            self.result.emit(size)
        finally:
            self.finished.emit()



if __name__ == '__main__':
    setproctitle.setproctitle("FILES")
    app = QtWidgets.QApplication(sys.argv)
    # QtGui.QIcon.setThemeName("elementary")
    # QtGui.QIcon.setThemeSearchPaths(["/usr/share/icons"])
    window = filesWidget()
    sys.exit(app.exec_())
