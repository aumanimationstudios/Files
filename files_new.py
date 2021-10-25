#!/usr/bin/python2
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
#TODO : TAB OPTION


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
# import pyperclip
import time
import threading
import traceback
import pathlib
import json
from PIL import Image
from multiprocessing import Pool

from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
from PyQt5 import QtCore, uic, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
sys.path.append(projDir)

rootDir = "/"
homeDir = os.path.expanduser("~")

filesThumbsDir = homeDir+"/.cache/thumbnails/files_thumbs/"
if os.path.exists(filesThumbsDir):
    pass
else:
    os.mkdir(filesThumbsDir)

main_ui_file = os.path.join(projDir, "files_2.ui")
debug.info(main_ui_file)

imageFormats = ['png','PNG','exr','EXR','jpg','JPG','jpeg','JPEG','svg','SVG']
videoFormats = ['mov','MOV','mp4','MP4','avi','AVI','mkv','MKV']
audioFormats = ['mp3','aac']
textFormats = ['txt','py','sh','text','json','conf','yml','log']
supportedFormats = ['mp4','mp3']

renamePermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", homeDir]
cutCopyPermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", homeDir]
pastePermittedDirs = ["/blueprod/CRAP/crap", "/crap/crap.server", homeDir] #REMINDER : Do NOT add bluepixels downloads folder
deletePermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", homeDir]
newFolderPermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", homeDir]
prohibitedDirs = ["/blueprod/STOR", "/proj", "/library","/aumbackup"]

parser = argparse.ArgumentParser(description="File viewer utility")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the folder")
args = parser.parse_args()

confFile = homeDir+os.sep+".config"+os.sep+"files.json"

places = {}
places["Home"] = homeDir
# places["Root"] = rootDir
places["Crap"] = "/blueprod/CRAP/crap"
places["Downloads"] = homeDir+os.sep+"Downloads"

rename = os.path.join(projDir, "rename.py")
details = os.path.join(projDir, "details.py")

app = None
assPath = args.path

if(args.path):
    ROOTDIR = args.path
else:
    ROOTDIR = rootDir

CUR_DIR_SELECTED = None
listIcon = None
iconsIcon = None

cutFile = False



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


class IconProvider(QtWidgets.QFileIconProvider):
    def icon(self, fileInfo):
        # if fileInfo.isDir():
        #     return QtGui.QIcon(os.path.join(projDir, "imageFiles", "folder_icon.svg"))
        if fileInfo.isFile():
            if fileInfo.suffix() in videoFormats:
                # filePath = fileInfo.filePath()
                fileName = fileInfo.fileName()
                thumb_image = filesThumbsDir+fileName+".png"
                if os.path.exists(thumb_image):
                    return QtGui.QIcon(thumb_image)
                else:
                    if fileName.startswith("."):
                        pass
                    else:
                        return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_video_icon.svg"))

            if fileInfo.suffix() in audioFormats:
                return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_audio_icon.svg"))

            if fileInfo.suffix() in imageFormats:
                # filePath = fileInfo.filePath()
                fileName = fileInfo.fileName()
                thumb_image = filesThumbsDir + fileName + ".png"
                if os.path.exists(thumb_image):
                    return QtGui.QIcon(thumb_image)
                else:
                    if fileName.startswith("."):
                        pass
                    else:
                        return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_image_icon.svg"))

            if fileInfo.suffix() in textFormats:
                return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_files_icon.svg"))
            return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_icon.svg"))
        return QtWidgets.QFileIconProvider.icon(self, fileInfo)


class FSM4Files(QtWidgets.QFileSystemModel):

    def __init__(self,**kwargs):
        super(FSM4Files, self).__init__(**kwargs)


class FSM(QtWidgets.QFileSystemModel):

    def __init__(self,**kwargs):
        super(FSM, self).__init__(**kwargs)


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
        global listIcon
        global iconsIcon

        self.threadpool = QtCore.QThreadPool()

        self.main_ui = uic.loadUi(main_ui_file)
        self.main_ui.setWindowTitle("FILES")

        sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
        self.main_ui.setStyleSheet(sS.read())
        sS.close()

        self.main_ui.currentFolderBox.clear()
        self.main_ui.currentFolderBox.setText(ROOTDIR)

        self.main_ui.treeDirs.sortByColumn(0, QtCore.Qt.AscendingOrder)
        self.main_ui.listFiles.sortByColumn(0, QtCore.Qt.AscendingOrder)

        ROOTDIRNEW = os.path.abspath(self.main_ui.currentFolderBox.text().strip()).encode('utf-8')
        debug.info(ROOTDIRNEW)

        modelDirs = self.setDir(ROOTDIRNEW)

        self.openDir(homeDir)

        self.initConfig()
        self.loadFavourites()

        listIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "view_list.png"))
        iconsIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "view_icons.png"))
        prevDirIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-up-1.png"))
        goIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-down-1.png"))
        searchIcon = os.path.join(projDir, "imageFiles", "search_icon.svg")

        self.main_ui.changeViewButt.setIcon(QtGui.QIcon(iconsIcon))
        self.main_ui.previousDirButt.setIcon(QtGui.QIcon(prevDirIcon))
        self.main_ui.changeDirButt.setIcon(QtGui.QIcon(goIcon))
        self.main_ui.searchButt.setIcon(QtGui.QIcon(searchIcon))

        self.main_ui.currentFolderBox.findChild(QtWidgets.QToolButton).setIcon(
            QtGui.QIcon(os.path.join(projDir, "imageFiles", "clear_icon.svg")))
        self.main_ui.searchBox.findChild(QtWidgets.QToolButton).setIcon(
            QtGui.QIcon(os.path.join(projDir, "imageFiles", "clear_icon.svg")))

        self.main_ui.changeViewButt.setShortcut(QtGui.QKeySequence("V"))
        self.main_ui.previousDirButt.setShortcut(QtGui.QKeySequence("Backspace"))
        self.main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))

        self.main_ui.changeViewButt.setToolTip("Change View (V)")
        self.main_ui.previousDirButt.setToolTip("Previous Directory (Backspace)")
        self.main_ui.changeDirButt.setToolTip("Change Directory (Enter)")

        self.main_ui.treeDirs.clicked.connect(lambda x, modelDirs=modelDirs: self.dirSelected(x, modelDirs))
        self.main_ui.searchBox.textChanged.connect(lambda x : self.search())
        self.main_ui.changeViewButt.clicked.connect(lambda x : self.changeView())
        self.main_ui.previousDirButt.clicked.connect(lambda x: self.previousDir())
        self.main_ui.changeDirButt.clicked.connect(lambda x: self.changeDir())
        self.main_ui.searchButt.clicked.connect(lambda x: self.search())

        self.main_ui.iconFiles.customContextMenuRequested.connect(lambda x, context=self.main_ui.iconFiles.viewport(): self.popUpFiles(context, x))
        self.main_ui.iconFiles.doubleClicked.connect(lambda x : self.openFile())
        self.main_ui.listFiles.customContextMenuRequested.connect(lambda x, context=self.main_ui.listFiles.viewport() : self.popUpFiles(context, x))
        self.main_ui.listFiles.doubleClicked.connect(lambda x : self.openFile())

        self.main_ui.progressBar.hide()
        self.messages("white", "")

        self.main_ui.v_splitter.setSizes([100, 2000])
        self.main_ui.h_splitter.setSizes([250, 1000])
        self.main_ui.listFiles.setColumnWidth(0, 400)

        self.main_ui.iconFiles.hide()

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
            thumb.setFocusPolicy(Qt.NoFocus)

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
        rename = menu.addAction("Rename")
        remove = menu.addAction("Remove")
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
            self.main_ui.treeDirs.itemsExpandable = False
            self.main_ui.treeDirs.collapseAll()
        else:
            self.messages("green","Generating thumbnails")
            self.main_ui.treeDirs.itemsExpandable = True
            modelDirs = FSM(parent=self.main_ui)
            modelDirs.setIconProvider(IconProvider())
            # modelDirs.setIconProvider(CustomIconProvider())
            modelDirs.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
            modelDirs.setRootPath(ROOTDIRNEW)

            self.main_ui.treeDirs.setModel(modelDirs)

            self.main_ui.treeDirs.hideColumn(1)
            self.main_ui.treeDirs.hideColumn(2)
            self.main_ui.treeDirs.hideColumn(3)

            rootIdx = modelDirs.index(ROOTDIRNEW)
            self.main_ui.treeDirs.setRootIndex(rootIdx)

            # openDir(ROOTDIRNEW, self.main_ui)
            return (modelDirs)


    def openDir(self, dirPath):
        self.clearAllSelection()
        self.openListDir(dirPath)
        self.openIconDir(dirPath)

        # self.threadpool = QtCore.QThreadPool()
        # debug.info("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        worker = Worker(self.genThumb,dirPath)
        # worker.signals.finished.connect(lambda dir_path=dirPath: self.refreshDir(dir_path))
        self.threadpool.start(worker)


    # def refreshDir(self, dirPath):
    #     self.clearAllSelection()
    #     self.openListDir(dirPath)
    #     self.openIconDir(dirPath)


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

                if ext in videoFormats:
                    thumb_image = filesThumbsDir + f + ".png"
                    if os.path.exists(thumb_image):
                        pass
                    else:
                        try:
                            genThumbCmd = "ffmpeg -ss 00:00:01.000 -i \"{0}\" -vf 'scale=128:128:force_original_aspect_ratio=decrease' -vframes 1 \"{1}\" -y ".format(
                                          file_path, thumb_image)
                            subprocess.call(shlex.split(genThumbCmd))
                        except:
                            debug.info(str(sys.exc_info()))

                if ext in imageFormats:
                    thumb_image = filesThumbsDir + f + ".png"
                    if os.path.exists(thumb_image):
                        pass
                    else:
                        try:
                            im = Image.open(file_path)
                            im.thumbnail((128,128))
                            im.save(thumb_image)
                        except:
                            debug.info(str(sys.exc_info()))


    def openListDir(self, dirPath):
        global CUR_DIR_SELECTED

        CUR_DIR_SELECTED = dirPath.strip()
        debug.info(CUR_DIR_SELECTED)

        searchTerm = self.main_ui.searchBox.text().strip()
        # debug.info(searchTerm)

        permitted = True
        for x in prohibitedDirs:
            if x in CUR_DIR_SELECTED:
                permitted = False
        if permitted:
            self.messages("green", "Generating thumbnails")
            self.main_ui.treeDirs.itemsExpandable = True
            self.main_ui.currentFolderBox.clear()
            self.main_ui.currentFolderBox.setText(CUR_DIR_SELECTED)

            # modelFiles = self.main_ui.listFiles.model()
            # if not modelFiles:
            modelFiles = FSM(parent=self.main_ui)
            modelFiles.setIconProvider(IconProvider())
            # modelFiles.setIconProvider(CustomIconProvider())
            self.main_ui.listFiles.setModel(modelFiles)
            modelFiles.setRootPath(CUR_DIR_SELECTED)

            modelFiles.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
            modelFiles.setNameFilters([searchTerm+"*"])
            modelFiles.setNameFilterDisables(False)
            debug.info(modelFiles.nameFilters())

            rootIdx = modelFiles.index(CUR_DIR_SELECTED)

            self.main_ui.listFiles.setRootIndex(rootIdx)

            self.main_ui.listFiles.setItemDelegateForColumn(3, DateFormatDelegate())
            # self.main_ui.listFiles.setItemDelegateForColumn(3,DateFormatDelegate('dd/MM/yyyy'))
            # openIconDir(dirPath,self.main_ui)
            return
        else:
            debug.info("Danger zone")
            debug.info("Error! No permission to open.")
            self.messages("red", "Error! No permission to open.")
            self.main_ui.treeDirs.itemsExpandable = False
            self.main_ui.treeDirs.collapseAll()
            return


    def openIconDir(self, dirPath):
        global CUR_DIR_SELECTED

        CUR_DIR_SELECTED = dirPath.strip()
        debug.info(CUR_DIR_SELECTED)

        searchTerm = self.main_ui.searchBox.text().strip()
        # debug.info(searchTerm)

        permitted = True
        for x in prohibitedDirs:
            if x in CUR_DIR_SELECTED:
                permitted = False
        if permitted:
            self.messages("green", "Generating thumbnails")
            self.main_ui.treeDirs.itemsExpandable = True
            self.main_ui.currentFolderBox.clear()
            self.main_ui.currentFolderBox.setText(CUR_DIR_SELECTED)

            # modelFiles = self.main_ui.iconFiles.model()
            # if not modelFiles:
            modelFiles = FSM4Files(parent=self.main_ui)
            modelFiles.setIconProvider(IconProvider())
            # modelFiles.setIconProvider(CustomIconProvider())
            self.main_ui.iconFiles.setModel(modelFiles)
            modelFiles.setRootPath(CUR_DIR_SELECTED)

            modelFiles.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
            modelFiles.setNameFilters([searchTerm + "*"])
            modelFiles.setNameFilterDisables(False)
            debug.info(modelFiles.nameFilters())

            rootIdx = modelFiles.index(CUR_DIR_SELECTED)

            self.main_ui.iconFiles.setRootIndex(rootIdx)
            return
        else:
            debug.info("Danger zone")
            debug.info("Error! No permission to open.")
            self.messages("red", "Error! No permission to open.")
            self.main_ui.treeDirs.itemsExpandable = False
            self.main_ui.treeDirs.collapseAll()
            return


    def dirSelected(self, index, model):
        dirPath = model.filePath(index)
        self.openDir(dirPath)

    # def copyPath(self, self.main_ui):
    #     path = self.main_ui.currentFolderBox.text().strip()
    #     # self.main_ui.outputFolder.clear()
    #     # self.main_ui.outputFolder.setText(path)
    #     pyperclip.copy(path)
    #
    #
    # def pastePath(self, self.main_ui):
    #     path = pyperclip.paste()
    #     if path != None:
    #         debug.info(path)
    #         self.main_ui.currentFolderBox.clear()
    #         self.main_ui.currentFolderBox.setText(path.strip())
    #     else:
    #         pass

    def clearAllSelection(self):
        self.main_ui.iconFiles.clearSelection()
        self.main_ui.listFiles.clearSelection()
        debug.info("Cleared Selection")


    def changeView(self):
        self.clearAllSelection()
        if self.main_ui.iconFiles.isHidden():
            self.main_ui.changeViewButt.setIcon(QtGui.QIcon(listIcon))
            self.main_ui.iconFiles.show()
            self.main_ui.listFiles.hide()
        else:
            self.main_ui.changeViewButt.setIcon(QtGui.QIcon(iconsIcon))
            self.main_ui.iconFiles.hide()
            self.main_ui.listFiles.show()


    def previousDir(self):
        # debug.info("previous directory")
        ROOTDIR = self.main_ui.currentFolderBox.text().strip().encode('utf-8')
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
        ROOTDIR = self.main_ui.currentFolderBox.text().strip().encode('utf-8')
        if ROOTDIR != "":
            ROOTDIRNEW = os.path.abspath(os.path.expanduser(ROOTDIR))
            # home = os.path.expanduser(ROOTDIR)
            # debug.info(home)
            if os.path.exists(ROOTDIRNEW):
                debug.info (ROOTDIRNEW)
                self.openDir(ROOTDIRNEW)
                self.messages("white", "")
            else:
                self.messages("red","No such folder!")


    def search(self):
        ROOTDIR = self.main_ui.currentFolderBox.text().strip().encode('utf-8')
        self.openDir(ROOTDIR)


    def clearPath(self):
        self.main_ui.currentFolderBox.clear()


    def getSelectedFiles(self):
        model = None
        selectedIndexes = None
        files =[]

        if self.main_ui.iconFiles.isVisible():
            model = self.main_ui.iconFiles.model()
            selectedIndexes = self.main_ui.iconFiles.selectedIndexes()
        elif self.main_ui.listFiles.isVisible():
            model = self.main_ui.listFiles.model()
            selectedIndexes = self.main_ui.listFiles.selectedIndexes()

        for selectedIndex in selectedIndexes:
            try:
                # filePath = os.path.abspath(str(model.filePath(selectedIndex)))
                filePath = os.path.abspath(str(model.filePath(selectedIndex).encode('utf-8')))
                # debug.info(filePath)
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
                filePath = os.path.abspath(str(model.filePath(index).encode('utf-8')))
                fileName = str(model.fileName(index).encode('utf-8'))
                debug.info(filePath)
                debug.info(fileName)

                if fileInfo.isDir():
                    debug.info("This is a directory!")
                    self.main_ui.searchBox.clear()
                    self.openDir(filePath)

                if fileInfo.isFile():
                    debug.info("This is a file!")
                    try:
                        # suffix = fileName.split(".")[-1]
                        suffix = pathlib.Path(fileName).suffix.split('.')[-1]
                        debug.info(suffix)
                        openCmd = ""
                        if suffix in videoFormats+audioFormats:
                            openCmd = "mpv --screenshot-directory=/tmp/ --input-conf={0} \"{1}\" ".format(os.path.join(projDir,"video-input.conf"),filePath)
                        elif (suffix in imageFormats):
                            # openCmd = projDir+os.sep+"mediaPlayer.py --path '{0}' ".format(filePath)
                            openCmd = "mpv --geometry=1920x1080 --image-display-duration=inf --loop-file=inf --input-conf={0} \"{1}\" "\
                                       .format(os.path.join(projDir,"image-input.conf"),filePath)
                        elif suffix in textFormats:
                            openCmd = "leafpad \"{0}\" ".format(filePath)
                        elif suffix == "pdf":
                            openCmd = "pdfReader \"{0}\" ".format(filePath)

                        debug.info(shlex.split(openCmd))
                        if openCmd:
                            subprocess.Popen(shlex.split(openCmd))
                    except:
                        debug.info(str(sys.exc_info()))
            except:
                debug.info(str(sys.exc_info()))


    # def popupTabs(self.main_ui,pos):
    #     debug.info("Tab Popup")
    #     menu = QtWidgets.QMenu()
    #     newTabAction = menu.addAction("New Tab")
    #     action = menu.exec_(self.main_ui.tabWidget.mapToGlobal(pos))
    #
    #     if(action==newTabAction):
    #         debug.info("New Tab")
    #         tab1 = QtWidgets.QWidget()
    #         tab1.setLayout(self.main_ui.verticalLayout)
    #         self.main_ui.tabWidget.addTab(tab1, "new")


    def popUpFiles(self,context,pos):
        clip = QtWidgets.QApplication.clipboard()
        pasteUrls = clip.mimeData().urls()
        # debug.info(pasteUrls)

        menu = QtWidgets.QMenu()
        self.setStyle(menu)

        # REMINDER : DO NOT ADD OPEN WITH ACTION

        copyAction = menu.addAction("Copy")
        cutAction = menu.addAction("Cut")
        pasteAction = menu.addAction("Paste")
        newFolderAction = menu.addAction("New Folder")
        addToFavAction = menu.addAction("Add To Favourites")
        renameAction = menu.addAction("Rename")
        deleteAction = menu.addAction("Delete")
        detailsAction = menu.addAction("Details")

        model,selectedIndexes,selectedFiles = self.getSelectedFiles()
        # debug.info(selectedFiles)
        action = menu.exec_(context.mapToGlobal(pos))
        # path = os.path.abspath(self.main_ui.currentFolderBox.text().strip())
        # debug.info(path)

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
        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())).encode('utf-8'))

        permitted = False
        for x in cutCopyPermittedDirs:
            if x in currDir:
                permitted = True
        if permitted:
        # sourcePath = os.path.abspath(self.main_ui.currentFolderBox.text().strip())
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
                sourceFile = url.toLocalFile().encode('utf-8')
                destFolder = self.main_ui.currentFolderBox.text().strip().encode('utf-8')
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
                                    pasteCmd = ""
                                    rmDirCmd = ""
                                    if cutFile:
                                        pasteCmd = "rsync --remove-source-files -azHXW --info=progress2 \"{0}\" \"{1}\" ".format(sourceFile,destPath)
                                        rmDirCmd = "rmdir \"{0}\" ".format(sourceFile)
                                    else:
                                        pasteCmd = "rsync -azHXW --info=progress2 \"{0}\" \"{1}\" ".format(sourceFile,destPath)
                                    debug.info(pasteCmd)
                                    self.messages("green", "Copying "+sourceFile)
                                    p = subprocess.Popen(shlex.split(pasteCmd),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1, universal_newlines=True)
                                    for line in iter(p.stdout.readline, b''):
                                        synData = (tuple(filter(None, line.strip().split(' '))))
                                        if synData:
                                            prctg = synData[1].split("%")[0]
                                            # debug.info(prctg)
                                            self.main_ui.progressBar.show()
                                            self.main_ui.progressBar.setValue(int(prctg))
                                    subprocess.Popen(shlex.split("sync"))
                                    if rmDirCmd:
                                        try:
                                            subprocess.Popen(shlex.split(rmDirCmd))
                                        except:
                                            debug.info(str(sys.exc_info()))
                        else:
                            debug.info("Danger Zone: Can not paste")
                            debug.info("Error! No permission to paste.")
                            self.messages("red", "Error! No permission to paste.")
                self.main_ui.progressBar.hide()
                # messages(self.main_ui, "white", "")
            except:
                debug.info(str(sys.exc_info()))


    def createNewFolder(self):
        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())).encode('utf-8'))
        debug.info(currDir)

        permitted = False
        for x in newFolderPermittedDirs:
            if x in currDir:
                permitted = True
        if permitted:
            newFolder = currDir+os.sep+"New_Folder"
            newFolderCmd = "mkdir \"{0}\" ".format(newFolder)
            debug.info(newFolderCmd)
            subprocess.Popen(shlex.split(newFolderCmd))
        else:
            debug.info("Danger Zone: Can not create new folder")
            debug.info("Error! No permission to create new folder.")
            self.messages("red", "Error! No permission to create new folder.")


    def addToFavourites(self):
        global places
        # currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())).encode('utf-8'))
        model, selectedIndexes, selectedFiles = self.getSelectedFiles()

        indexes = [i for i in selectedIndexes if i.column() == 0]
        for index in indexes:
            try:
                fileInfo = model.fileInfo(index)
                fileName = (str(model.fileName(index).encode('utf-8')).capitalize())
                filePath = os.path.abspath(str(model.filePath(index).encode('utf-8')))
                if fileInfo.isDir():
                    places[fileName] = filePath
                    with open(confFile, 'w') as conf_file:
                        json.dump(places, conf_file, sort_keys=True, indent=4)
                    self.initConfig()
                    self.loadFavourites()
            except:
                debug.info(str(sys.exc_info()))


    def renameUi(self):
        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())).encode('utf-8'))
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
                    fileName = (str(model.fileName(index).encode('utf-8')))
                    filePath = os.path.abspath(str(model.filePath(index).encode('utf-8')))
                    fileDets[fileName] = filePath
                except:
                    debug.info(str(sys.exc_info()))
            debug.info(fileDets)

            if (len(fileDets)) == 1:
                for key, value in fileDets.items():
                    cmd = sys.executable+" "+rename+" --name \"{0}\" --path \"{1}\" ".format(key,currDir)
                    debug.info(cmd)
                    subprocess.Popen(shlex.split(cmd))
        else:
            debug.info("Error! No permission to rename.")
            self.messages("red","Error! No permission to rename.")


    def deleteFiles(self):
        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())).encode('utf-8'))
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
                    fileName = (str(model.fileName(index).encode('utf-8')))
                    fileNames.append(fileName)
                except:
                    debug.info(str(sys.exc_info()))
            debug.info(fileNames)
            confirm = QtWidgets.QMessageBox()
            self.setStyle(confirm)
            # confirm.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png"))))
            confirm.setWindowTitle("Warning!")
            # confirm.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png"))))
            confirm.setIconPixmap(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png")))
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
                        subprocess.Popen(shlex.split(removeCmd))
                        debug.info("Deleted "+x)
        else:
            debug.info("Error! No permission to delete.")
            self.messages("red","Error! No permission to delete.")


    def showDetails(self):
        currDir = str(os.path.abspath(os.path.expanduser(self.main_ui.currentFolderBox.text().strip())).encode('utf-8'))
        debug.info(currDir)
        model, selectedIndexes, selectedFiles = self.getSelectedFiles()
        debug.info(selectedFiles)

        # detsCmd = ['du', '-ch', '--max-depth=1'] + selectedFiles
        detsCmd = ['du', '-sch'] + selectedFiles
        debug.info(detsCmd)

        cmd = sys.executable + " " + details + " --command \"{0}\" ".format(detsCmd)
        debug.info(cmd)
        subprocess.Popen(shlex.split(cmd))


    def messages(self,color,msg):
        self.main_ui.messages.setStyleSheet("color: %s" %color)
        self.main_ui.messages.setText("%s"%msg)


    def setStyle(self,ui):
        sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
        ui.setStyleSheet(sS.read())
        sS.close()


if __name__ == '__main__':
    setproctitle.setproctitle("FILES")
    app = QtWidgets.QApplication(sys.argv)
    window = filesWidget()
    sys.exit(app.exec_())
