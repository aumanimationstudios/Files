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
# import pyperclip
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


# main_ui_file = os.path.join(projDir, "files.ui")
main_ui_file = os.path.join(projDir, "files_1.ui")
debug.info(main_ui_file)

imageFormats = ['png','PNG','exr','EXR','jpg','JPG','jpeg','JPEG','svg','SVG']
videoFormats = ['mov','MOV','mp4','MP4','avi','AVI','mkv','MKV']
audioFormats = ['mp3']
textFormats = ['txt','py','sh','text']
supportedFormats = ['mp4','mp3']
# detectedFormats = []
# frameNums = []
# missingFrames = []

parser = argparse.ArgumentParser(description="File conversion utility")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the folder containing image sequence or videos")
args = parser.parse_args()

rootDir = "/"
homeDir = os.path.expanduser("~")

places = {"Home" : homeDir,
          "Root" : rootDir,
          "Crap" : "/blueprod/CRAP/crap",
          "Downloads" : homeDir+os.sep+"Downloads"}

# downloadDir = homeDir+os.sep+"Downloads"
# crapDir = "/blueprod/CRAP/crap"
#
# places["Home"] = homeDir
# places["Root"] = rootDir
# places["Crap"] = crapDir
# places["Downloads"] = downloadDir

app = None
assPath = args.path

if(args.path):
    ROOTDIR = args.path
else:
    ROOTDIR = rootDir

CUR_DIR_SELECTED = None
listIcon = None
iconsIcon = None



# class WorkerSignals(QtCore.QObject):
#     '''
#     Defines the signals available from a running worker thread.
#     Supported signals are:
#     finished
#         No data
#     error
#         `tuple` (exctype, value, traceback.format_exc() )
#     result
#         `object` data returned from processing, anything
#     progress
#         `int` indicating % progress
#     '''
#     finished = pyqtSignal()
#     error = pyqtSignal(tuple)
#     result = pyqtSignal(object)
#     progress = pyqtSignal(int)


# class Worker(QtCore.QRunnable):
#     '''
#     Worker thread
#     Inherits from QRunnable to handler worker thread setup, signals and wrap-up.
#     :param callback: The function callback to run on this worker thread. Supplied args and
#                      kwargs will be passed through to the runner.
#     :type callback: function
#     :param args: Arguments to pass to the callback function
#     :param kwargs: Keywords to pass to the callback function
#     '''
#     def __init__(self, fn, *args, **kwargs):
#         super(Worker, self).__init__()
#
#         # Store constructor arguments (re-used for processing)
#         self.fn = fn
#         self.args = args
#         self.kwargs = kwargs
#         self.signals = WorkerSignals()
#
#         # Add the callback to our kwargs
#         self.kwargs['progress_callback'] = self.signals.progress
#
#     @pyqtSlot()
#     def run(self):
#         '''
#         Initialise the runner function with passed args, kwargs.
#         '''
#         # Retrieve args/kwargs here; and fire processing using them
#         try:
#             result = self.fn(*self.args, **self.kwargs)
#         except:
#             debug.info(str(sys.exc_info()))
#             traceback.print_exc()
#             exctype, value = sys.exc_info()[:2]
#             self.signals.error.emit((exctype, value, traceback.format_exc()))
#         else:
#             self.signals.result.emit(result)  # Return the result of the processing
#         finally:
#             self.signals.finished.emit()  # Done


# class openDirThread(QtCore.QThread):
#     openingDir = QtCore.pyqtSignal(str)
#     openedDir = QtCore.pyqtSignal(str)
#
#     def __init__(self,parent,path):
#         super(openDirThread, self).__init__(parent)
#         self.ui = parent
#         self.path = path
#
#     def run(self):
#         self.openingDir.emit("Opening")
#
#         # openListDir(self.path, self.ui)
#         modelFiles = self.ui.listFiles.model()
#         if not modelFiles:
#             modelFiles = FSM()
#             modelFiles.setIconProvider(IconProvider())
#             self.ui.listFiles.setModel(modelFiles)
#         debug.info(modelFiles)
#
#         self.openedDir.emit("Done")


class IconProvider(QtWidgets.QFileIconProvider):
    def icon(self, fileInfo):
        # if fileInfo.isDir():
        #     return QtGui.QIcon(os.path.join(projDir, "imageFiles", "folder_icon.svg"))
        if fileInfo.isFile():
            if fileInfo.suffix() in videoFormats:
                return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_video_icon.svg"))
            if fileInfo.suffix() in audioFormats:
                return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_audio_icon.svg"))
            if fileInfo.suffix() in imageFormats:
                return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_image_icon.svg"))
            if fileInfo.suffix() in textFormats:
                return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_files_icon.svg"))
            return QtGui.QIcon(os.path.join(projDir, "imageFiles", "file_icon.svg"))
        return QtWidgets.QFileIconProvider.icon(self, fileInfo)

# class CustomIconProvider(QtWidgets.QFileIconProvider):
#     def icon(self, fileInfo):
#         return QtGui.QIcon()

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

    # def createEditor(self, parent, option, index):
    #     dateedit = QDateEdit(parent)
    #     dateedit.setDisplayFormat(self.format)
    #     dateedit.setCalendarPopup(True)
    #     return dateedit
    #
    # def setEditorData(self, editor, index):
    #     value = index.model().data(index, Qt.DisplayRole)
    #     editor.setDate(QDate.fromString(value, "MM/dd/yy hh:mm a"))
    #
    # def setModelData(self, editor, model, index):
    #     date = editor.date()
    #     model.setData(index, date)


def loadSidePane(main_ui):
    model = QtGui.QStandardItemModel()
    main_ui.sidePane.setModel(model)
    for key, value in places.items():
        item = QtGui.QStandardItem(key)
        model.appendRow(item)
        thumb = QtWidgets.QPushButton()
        thumb.setText(key)
        thumb.setFocusPolicy(Qt.NoFocus)
        thumb.clicked.connect(lambda x, path=value, ui=main_ui: openDir(path, ui))
        main_ui.sidePane.setIndexWidget(item.index(), thumb)


def setDir(ROOTDIRNEW, main_ui):
    clearAllSelection(main_ui)
    # debug.info(type(ROOTDIRNEW))
    if "/blueprod/STOR" in ROOTDIRNEW:
        debug.info("Danger zone")
        main_ui.treeDirs.itemsExpandable = False
        main_ui.treeDirs.collapseAll()
    else:
        main_ui.treeDirs.itemsExpandable = True
        modelDirs = FSM(parent=main_ui)
        modelDirs.setIconProvider(IconProvider())
        # modelDirs.setIconProvider(CustomIconProvider())
        modelDirs.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        modelDirs.setRootPath(ROOTDIRNEW)

        main_ui.treeDirs.setModel(modelDirs)

        main_ui.treeDirs.hideColumn(1)
        main_ui.treeDirs.hideColumn(2)
        main_ui.treeDirs.hideColumn(3)

        rootIdx = modelDirs.index(ROOTDIRNEW)
        main_ui.treeDirs.setRootIndex(rootIdx)

        # openDir(ROOTDIRNEW, main_ui)
        return (modelDirs)


# def openDir(dirPath, main_ui):
#     try:
#         threadPool = QtCore.QThreadPool()
#         debug.info("Multithreading with maximum {0} threads".format(threadPool.maxThreadCount()))
#         worker = Worker(fn=openListDir,args=(dirPath, main_ui))  # Any other args, kwargs are passed to the run function
#         threadPool.start(worker)
#     except:
#         debug.info(str(sys.exc_info()))


def openDir(dirPath, main_ui):
    # odT = openDirThread(main_ui,dirPath)
    # # self.msg = messageBox("Place Your Tag")
    # odT.openingDir.connect(startedLoading)
    # odT.openedDir.connect(finishedLoading)
    # odT.start()
    clearAllSelection(main_ui)
    openListDir(dirPath,main_ui)
    openIconDir(dirPath, main_ui)

# def startedLoading():
#     debug.info("started loading")
#
#
# def finishedLoading():
#     debug.info("finished loading")


def openListDir(dirPath, main_ui):
    global CUR_DIR_SELECTED

    # pathSelected = modelDirs.filePath(idx)
    # main_ui.labelFile.setText(str(pathSelected).replace(ROOTDIR,"-"))
    CUR_DIR_SELECTED = dirPath.strip()
    debug.info(CUR_DIR_SELECTED)
    if "/blueprod/STOR" in CUR_DIR_SELECTED:
        debug.info("Danger zone")
        main_ui.treeDirs.itemsExpandable = False
        main_ui.treeDirs.collapseAll()
        return
    else:
        main_ui.treeDirs.itemsExpandable = True
        main_ui.currentFolder.clear()
        main_ui.currentFolder.setText(CUR_DIR_SELECTED)

        modelFiles = main_ui.listFiles.model()
        if not modelFiles:
            modelFiles = FSM(parent=main_ui)
            modelFiles.setIconProvider(IconProvider())
            # modelFiles.setIconProvider(CustomIconProvider())
            main_ui.listFiles.setModel(modelFiles)
        modelFiles.setRootPath(CUR_DIR_SELECTED)
        # modelFiles.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        # modelFiles.setFilter(QtCore.QDir.NoDotAndDotDot)
        rootIdx = modelFiles.index(CUR_DIR_SELECTED)

        main_ui.listFiles.setRootIndex(rootIdx)

        main_ui.listFiles.setItemDelegateForColumn(3, DateFormatDelegate())
        # main_ui.listFiles.setItemDelegateForColumn(3,DateFormatDelegate('dd/MM/yyyy'))
        # openIconDir(dirPath,main_ui)


def openIconDir(dirPath, main_ui):
    global CUR_DIR_SELECTED

    CUR_DIR_SELECTED = dirPath.strip()
    debug.info(CUR_DIR_SELECTED)
    if "/blueprod/STOR" in CUR_DIR_SELECTED:
        debug.info("Danger zone")
        main_ui.treeDirs.itemsExpandable = False
        main_ui.treeDirs.collapseAll()
        return
    else:
        main_ui.treeDirs.itemsExpandable = True
        main_ui.currentFolder.clear()
        main_ui.currentFolder.setText(CUR_DIR_SELECTED)

    modelFiles = main_ui.iconFiles.model()
    if not modelFiles:
        modelFiles = FSM4Files(parent=main_ui)
        modelFiles.setIconProvider(IconProvider())
        # modelFiles.setIconProvider(CustomIconProvider())
        main_ui.iconFiles.setModel(modelFiles)
    modelFiles.setRootPath(CUR_DIR_SELECTED)
    # modelFiles.setFilter(QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
    # modelFiles.setFilter(QtCore.QDir.NoDotAndDotDot)
    rootIdx = modelFiles.index(CUR_DIR_SELECTED)

    main_ui.iconFiles.setRootIndex(rootIdx)


def dirSelected(index, model, main_ui):
    dirPath = model.filePath(index)
    openDir(dirPath,main_ui)

# def copyPath(self, main_ui):
#     path = main_ui.currentFolder.text().strip()
#     # main_ui.outputFolder.clear()
#     # main_ui.outputFolder.setText(path)
#     pyperclip.copy(path)
#
#
# def pastePath(self, main_ui):
#     path = pyperclip.paste()
#     if path != None:
#         debug.info(path)
#         main_ui.currentFolder.clear()
#         main_ui.currentFolder.setText(path.strip())
#     else:
#         pass

def clearAllSelection(main_ui):
    main_ui.iconFiles.clearSelection()
    main_ui.listFiles.clearSelection()
    debug.info("Cleared Selection")


def changeView(self, main_ui):
    clearAllSelection(main_ui)
    if main_ui.iconFiles.isHidden():
        main_ui.changeViewButt.setIcon(QtGui.QIcon(listIcon))
        main_ui.iconFiles.show()
        main_ui.listFiles.hide()
    else:
        main_ui.changeViewButt.setIcon(QtGui.QIcon(iconsIcon))
        main_ui.iconFiles.hide()
        main_ui.listFiles.show()


def previousDir(self, main_ui):
    # debug.info("previous directory")
    ROOTDIR = main_ui.currentFolder.text().strip().encode('utf-8')
    if ROOTDIR != "":
        if os.path.exists(ROOTDIR):
            ROOTDIRNEW = os.sep.join(ROOTDIR.split(os.sep)[:-1])
            debug.info(ROOTDIRNEW)
            if os.path.exists(ROOTDIRNEW):
                openDir(ROOTDIRNEW, main_ui)
                messages(main_ui, "white", "")
        else:
            debug.info("No such folder!")


def changeDir(self, main_ui):
    ROOTDIR = main_ui.currentFolder.text().strip().encode('utf-8')
    if ROOTDIR != "":
        ROOTDIRNEW = os.path.abspath(os.path.expanduser(ROOTDIR))
        # home = os.path.expanduser(ROOTDIR)
        # debug.info(home)
        if os.path.exists(ROOTDIRNEW):
            debug.info (ROOTDIRNEW)
            openDir(ROOTDIRNEW, main_ui)
            messages(main_ui, "white", "")
        else:
            messages(main_ui,"red","No such folder!")


def clearPath(self, main_ui):
    main_ui.currentFolder.clear()


def getSelectedFiles(main_ui):
    model = None
    selectedIndexes = None
    files =[]

    if main_ui.iconFiles.isVisible():
        model = main_ui.iconFiles.model()
        selectedIndexes = main_ui.iconFiles.selectedIndexes()
    elif main_ui.listFiles.isVisible():
        model = main_ui.listFiles.model()
        selectedIndexes = main_ui.listFiles.selectedIndexes()

    for selectedIndex in selectedIndexes:
        try:
            # filePath = os.path.abspath(str(model.filePath(selectedIndex)))
            filePath = os.path.abspath(str(model.filePath(selectedIndex).encode('utf-8')))
            debug.info(filePath)
            files.append(filePath)
        except:
            debug.info(str(sys.exc_info()))

    files = list(OrderedDict.fromkeys(files))
    return (model,selectedIndexes,files)


def openFile(self, main_ui):
    debug.info("double clicked!!!")
    # selectedFiles = getSelectedFiles(main_ui)

    # files = []
    # model = None
    # selectedIndexes = None
    # if main_ui.iconFiles.isVisible():
    #     model = main_ui.iconFiles.model()
    #     selectedIndexes = main_ui.iconFiles.selectedIndexes()
    # elif main_ui.listFiles.isVisible():
    #     model = main_ui.listFiles.model()
    #     selectedIndexes = main_ui.listFiles.selectedIndexes()
    # selectedItems = main_ui.listFiles.selectionModel().selectedIndexes()
    # debug.info(selectedItems)

    model, selectedIndexes, selectedFiles = getSelectedFiles(main_ui)
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
                openDir(filePath, main_ui)

            if fileInfo.isFile():
                debug.info("This is a file!")
                try:
                    # suffix = fileName.split(".")[-1]
                    suffix = pathlib.Path(fileName).suffix.split('.')[-1]
                    debug.info(suffix)
                    openCmd = ""
                    if suffix in videoFormats+audioFormats:
                        openCmd = "mpv --screenshot-directory=/tmp/ --input-conf={0} '{1}' ".format(os.path.join(projDir,"video-input.conf"),filePath)
                    elif (suffix in imageFormats):
                        # openCmd = projDir+os.sep+"mediaPlayer.py --path '{0}' ".format(filePath)
                        openCmd = "mpv --geometry=1920x1080 --image-display-duration=inf --loop-file=inf --input-conf={0} '{1}' "\
                                   .format(os.path.join(projDir,"image-input.conf"),filePath)
                    elif suffix in textFormats:
                        openCmd = "leafpad '{0}' ".format(filePath)
                    # else:
                    #     messages(main_ui, "red", "no matches found")
                    # elif formatOfSelected in videoFormats:
                    #     # openCmd = "mpv " + selectedFilePath
                    #     openCmd = "mpv '{0}' ".format(filePath)
                    # elif formatOfSelected in musicFormats:
                    #     openCmd = "qmmp '{0}' ".format(filePath)
                    # else:
                    #     openCmd = "xdg-open "+selectedFilePath
                    # openCmd = "xdg-open "+selectedFilePath
                    debug.info(shlex.split(openCmd))
                    # p = subprocess.Popen(shlex.split(openCmd),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1, universal_newlines=True)
                    # subprocess.Popen(openCmd, shell=True)
                    if openCmd:
                        subprocess.Popen(shlex.split(openCmd))
                except:
                    debug.info(str(sys.exc_info()))
        except:
            debug.info(str(sys.exc_info()))


def popUpFiles(main_ui,context,pos):
    clip = QtWidgets.QApplication.clipboard()
    pasteUrls = clip.mimeData().urls()
    # debug.info(pasteUrls)

    menu = QtWidgets.QMenu()
    setStyle(menu)

    #REMINDER : DO NOT ADD OPEN WITH ACTION
    #DONE : CHANGE DATE FORMAT
    #DONE : DELETE OPTION
    #TODO : CUT OPTION
    #TODO : RENAME OPTION
    #TODO : NEW FOLDER OPTION
    #TODO : SEARCH

    # openWithMenu = QtWidgets.QMenu("Open With")
    # setStyle(openWithMenu)
    # mpv = openWithMenu.addAction("mpv player")
    # menu.addMenu(openWithMenu)

    copyAction = menu.addAction("Copy")
    pasteAction = menu.addAction("Paste")
    deleteAction = menu.addAction("Delete")

    model,selectedIndexes,selectedFiles = getSelectedFiles(main_ui)
    # debug.info(selectedFiles)
    action = menu.exec_(context.mapToGlobal(pos))
    # path = os.path.abspath(main_ui.currentFolder.text().strip())
    # debug.info(path)


    if (action == copyAction):
        if (selectedFiles):
            copyToClipboard(main_ui)
    if (action == pasteAction):
        pasteFilesFromClipboard(main_ui,pasteUrls)
    if (action == deleteAction):
        if (selectedFiles):
            deleteFiles(main_ui)


def copyToClipboard(main_ui):
    # sourcePath = os.path.abspath(main_ui.currentFolder.text().strip())
    model,selectedIndexes,selectedFiles = getSelectedFiles(main_ui)
    urlList = []
    mimeData = QtCore.QMimeData()
    for x in selectedFiles:
        debug.info("Copied "+x)
        urlList.append(QtCore.QUrl().fromLocalFile(x))
    mimeData.setUrls(urlList)
    QtWidgets.QApplication.clipboard().setMimeData(mimeData)


def pasteFilesFromClipboard(main_ui,urls):
    for url in urls:
        try:
            sourceFile = url.toLocalFile().encode('utf-8')
            destFolder = main_ui.currentFolder.text().strip().encode('utf-8')
            # debug.info(destFolder)
            if destFolder:
                destPath = os.path.abspath(destFolder)+"/"
                # debug.info(destPath)
                if destPath and os.path.exists(destPath):
                    # if "/opt/home/bluepixels" in destPath:
                    #     debug.info("Danger Zone: Can not paste")
                    # else:
                    pasteCmd = "rsync -azHXW --info=progress2 '{0}' '{1}' ".format(sourceFile,destPath)
                    debug.info(pasteCmd)
                    messages(main_ui, "green", "Copying "+sourceFile)
                    p = subprocess.Popen(shlex.split(pasteCmd),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1, universal_newlines=True)
                    for line in iter(p.stdout.readline, b''):
                        synData = (tuple(filter(None, line.strip().split(' '))))
                        if synData:
                            prctg = synData[1].split("%")[0]
                            # debug.info(prctg)
                            main_ui.progressBar.show()
                            main_ui.progressBar.setValue(int(prctg))
            main_ui.progressBar.hide()
            messages(main_ui, "white", "")
        except:
            debug.info(str(sys.exc_info()))


def deleteFiles(main_ui):
    currDir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolder.text().strip())).encode('utf-8'))
    debug.info(currDir)
    # if currDir == "/opt/home/bluepixels/Downloads":
    if "/opt/home/bluepixels/Downloads" in currDir:
        model,selectedIndexes,selectedFiles = getSelectedFiles(main_ui)
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
        setStyle(confirm)
        # confirm.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png"))))
        confirm.setWindowTitle("Warning!")
        confirm.setText("<b>Permanently Delete these item(s)?</b>"+"\n")
        confirm.setInformativeText(",\n".join(i for i in fileNames))
        confirm.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        selection = confirm.exec_()
        if (selection == QtWidgets.QMessageBox.Yes):
            for x in selectedFiles:
                if "/opt/home/bluepixels/Downloads/" in x:
                    removeCmd = "rm -frv '{0}' ".format(x)
                    debug.info(shlex.split(removeCmd))
                    if removeCmd:
                        subprocess.Popen(shlex.split(removeCmd))
                        debug.info("Deleted "+x)
    else:
        debug.info("Error! No permission to delete.")
        messages(main_ui,"red","Error! No permission to delete.")


def messages(main_ui,color,msg):
    main_ui.messages.setStyleSheet("color: %s" %color)
    main_ui.messages.setText("%s"%msg)


def setStyle(ui):
    sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
    ui.setStyleSheet(sS.read())
    sS.close()


# def messageBox(msg1, msg2="", icon=""):
#     msg = QtWidgets.QMessageBox()
#     msg.setWindowTitle("Message")
#     msg.setText(msg1+"\n"+msg2)
#     okBut = msg.addButton("OK", QtWidgets.QMessageBox.NoRole)
#     msg.setDefaultButton(okBut)
#     if icon:
#         msg.setIconPixmap(QtGui.QPixmap(icon))
#     else:
#         msg.setIcon(QtWidgets.QMessageBox.Information)
#     qssFile = os.path.join(projDir, "styleSheet", "stylesheetTest.qss")
#     with open(qssFile, "r") as sty:
#         msg.setStyleSheet(sty.read())
#     msg.exec_()


def mainGui(main_ui):
    global listIcon
    global iconsIcon

    main_ui.setWindowTitle("FILES")

    sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
    main_ui.setStyleSheet(sS.read())
    sS.close()

    main_ui.currentFolder.clear()
    main_ui.currentFolder.setText(ROOTDIR)

    main_ui.treeDirs.sortByColumn(0, QtCore.Qt.AscendingOrder)
    main_ui.listFiles.sortByColumn(0, QtCore.Qt.AscendingOrder)

    ROOTDIRNEW = os.path.abspath(main_ui.currentFolder.text().strip()).encode('utf-8')
    debug.info(ROOTDIRNEW)

    modelDirs = setDir(ROOTDIRNEW, main_ui)

    # threadPool = QtCore.QThreadPool()
    # debug.info("Multithreading with maximum %d threads" % threadPool.maxThreadCount())
    # openDirWorker = Worker(openDir(homeDir,main_ui))  # Any other args, kwargs are passed to the run function
    # threadPool.start(openDirWorker)

    openDir(homeDir,main_ui)

    loadSidePane(main_ui)

    listIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "view_list.png"))
    iconsIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "view_icons.png"))
    prevDirIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-up-1.png"))
    goIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "arrow-right-1.png"))
    clearIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "clear-icon-1.png"))

    # copyIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "copy-icon-1.png"))
    # pasteIcon = QtGui.QPixmap(os.path.join(projDir, "imageFiles", "paste-icon-1.png"))

    # main_ui.copyButton.setIcon(QtGui.QIcon(copyIcon))
    # main_ui.pasteButton.setIcon(QtGui.QIcon(pasteIcon))
    main_ui.changeViewButt.setIcon(QtGui.QIcon(iconsIcon))
    main_ui.previousDirButt.setIcon(QtGui.QIcon(prevDirIcon))
    main_ui.changeDirButt.setIcon(QtGui.QIcon(goIcon))
    main_ui.clearPathButt.setIcon(QtGui.QIcon(clearIcon))

    main_ui.changeViewButt.setShortcut(QtGui.QKeySequence("V"))
    main_ui.previousDirButt.setShortcut(QtGui.QKeySequence("Backspace"))
    main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))

    # main_ui.copyButton.setToolTip("Copy to Clipboard")
    # main_ui.pasteButton.setToolTip("Paste from Clipboard")
    # main_ui.upButton.setToolTip("Previous Folder")
    # main_ui.goButton.setToolTip("Go to Folder")

    # main_ui.copyButton.hide()
    # main_ui.pasteButton.hide()

    main_ui.treeDirs.clicked.connect(lambda index, modelDirs=modelDirs, main_ui = main_ui : dirSelected(index, modelDirs, main_ui))
    # main_ui.copyButton.clicked.connect(lambda self, main_ui = main_ui : copyPath(self, main_ui))
    # main_ui.pasteButton.clicked.connect(lambda self, main_ui = main_ui : pastePath(self, main_ui))
    main_ui.changeViewButt.clicked.connect(lambda self, main_ui = main_ui : changeView(self, main_ui))
    main_ui.previousDirButt.clicked.connect(lambda self, main_ui = main_ui : previousDir(self, main_ui))
    main_ui.changeDirButt.clicked.connect(lambda self, main_ui = main_ui : changeDir(self, main_ui))
    main_ui.clearPathButt.clicked.connect(lambda self, main_ui = main_ui : clearPath(self, main_ui))
    # main_ui.convertButton.clicked.connect(lambda self, main_ui = main_ui : startConvert(self, main_ui))
    # main_ui.outputFormat.currentIndexChanged.connect(lambda self, main_ui=main_ui: changeFormat(self, main_ui))


    main_ui.iconFiles.customContextMenuRequested.connect(lambda pos, context = main_ui.iconFiles.viewport(), main_ui = main_ui: popUpFiles(main_ui, context, pos))
    main_ui.iconFiles.doubleClicked.connect(lambda self, main_ui = main_ui : openFile(self, main_ui))
    main_ui.listFiles.customContextMenuRequested.connect(lambda pos, context = main_ui.listFiles.viewport(), main_ui = main_ui: popUpFiles(main_ui, context, pos))
    main_ui.listFiles.doubleClicked.connect(lambda self, main_ui = main_ui : openFile(self, main_ui))

    main_ui.progressBar.hide()
    messages(main_ui, "white", "")

    main_ui.v_splitter.setSizes([100, 2000])
    main_ui.h_splitter.setSizes([250, 1000])
    # main_ui.v_splitter.setHandleWidth(0)
    main_ui.listFiles.setColumnWidth(0, 400)

    main_ui.iconFiles.hide()

    main_ui.showMaximized()
    main_ui.update()


    qtRectangle = main_ui.frameGeometry()
    centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
    qtRectangle.moveCenter(centerPoint)
    main_ui.move(qtRectangle.topLeft())


def mainFunc():
    global app
    app = QApplication(sys.argv)
    main_ui = uic.loadUi(main_ui_file)
    mainGui(main_ui)
    # ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    setproctitle.setproctitle("FILES")
    mainFunc()

