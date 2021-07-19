#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


#REMINDER : DO NOT ADD OPEN WITH ACTION
#DONE : CHANGE DATE FORMAT
#DONE : DELETE OPTION
#DONE : RENAME OPTION
#DONE : ADD FAVOURITES TO SIDEPANE
#TODO : CUT OPTION
#TODO : TAB OPTION
#TODO : NEW FOLDER OPTION
#TODO : SEARCH
#TODO : DETAILS


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

from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
from PyQt5 import QtCore, uic, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


projDir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
sys.path.append(projDir)


# main_ui_file = os.path.join(projDir, "files.ui")
main_ui_file = os.path.join(projDir, "files_2.ui")
debug.info(main_ui_file)

imageFormats = ['png','PNG','exr','EXR','jpg','JPG','jpeg','JPEG','svg','SVG']
videoFormats = ['mov','MOV','mp4','MP4','avi','AVI','mkv','MKV']
audioFormats = ['mp3']
textFormats = ['txt','py','sh','text','json']
supportedFormats = ['mp4','mp3']

renamePermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server"]
prohibitedDirs = ["/blueprod/STOR", "/proj"]

parser = argparse.ArgumentParser(description="File viewer utility")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the folder")
args = parser.parse_args()

rootDir = "/"
homeDir = os.path.expanduser("~")

confFile = homeDir+os.sep+".config"+os.sep+"files.json"

places = {}
places["Home"] = homeDir
# places["Root"] = rootDir
places["Crap"] = "/blueprod/CRAP/crap"
places["Downloads"] = homeDir+os.sep+"Downloads"

rename = os.path.join(projDir, "rename.py")

app = None
assPath = args.path

if(args.path):
    ROOTDIR = args.path
else:
    ROOTDIR = rootDir

CUR_DIR_SELECTED = None
listIcon = None
iconsIcon = None


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


def initConfig():
    global places
    global confFile

    if os.path.exists(confFile):
        f = open(confFile)
        data = json.load(f)
        places = data
    else:
        with open(confFile, 'w') as conf_file:
            json.dump(places, conf_file, sort_keys=True, indent=4)


def loadFavourites(main_ui):
    global places
    model = QtGui.QStandardItemModel()
    main_ui.favourites.setModel(model)

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

        thumb.clicked.connect(lambda x, path=value, ui=main_ui: openDir(path, ui))
        entButt.clicked.connect(lambda x,button=thumb,editor=line,entButt=entButt,main_ui=main_ui: changeFavName(main_ui,button,editor,entButt))

        thumb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        thumb.customContextMenuRequested.connect(lambda pos,button=thumb,editor=line,entButt=entButt,main_ui=main_ui: favouritesPopup(main_ui,button,editor,entButt,pos))

        hLay.addWidget(thumb)
        hLay.addWidget(line)
        hLay.addWidget(entButt)
        frame.setLayout(hLay)

        main_ui.favourites.setIndexWidget(item.index(), frame)


def favouritesPopup(main_ui,button,editor,entButt,pos):
    global places
    currName = button.text()
    # editorName = editor.text()
    debug.info(currName)
    # debug.info(editorName)

    menu = QtWidgets.QMenu()
    setStyle(menu)
    rename = menu.addAction("Rename")
    remove = menu.addAction("Remove")
    # action = menu.exec_(context.mapToGlobal(pos))
    action = menu.exec_(button.mapToGlobal(pos))

    if action == rename:
        main_ui.changeDirButt.setShortcut(QtGui.QKeySequence(""))
        entButt.setShortcut(QtGui.QKeySequence("Return"))
        button.hide()
        editor.show()
        entButt.show()
        editor.setFocus()

    if action == remove:
        places.pop(currName)
        with open(confFile, 'w') as conf_file:
            json.dump(places, conf_file, sort_keys=True, indent=4)
        initConfig()
        loadFavourites(main_ui)


def changeFavName(main_ui,button,editor,entButt):
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
                initConfig()
                loadFavourites(main_ui)

    button.show()
    editor.hide()
    entButt.hide()
    editor.clearFocus()
    main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))
    entButt.setShortcut(QtGui.QKeySequence(""))


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


def openDir(dirPath, main_ui):
    clearAllSelection(main_ui)
    openListDir(dirPath,main_ui)
    openIconDir(dirPath, main_ui)


def openListDir(dirPath, main_ui):
    global CUR_DIR_SELECTED

    CUR_DIR_SELECTED = dirPath.strip()
    debug.info(CUR_DIR_SELECTED)

    permitted = True
    for x in prohibitedDirs:
        if x in CUR_DIR_SELECTED:
            permitted = False
    if permitted:
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
    else:
        debug.info("Danger zone")
        main_ui.treeDirs.itemsExpandable = False
        main_ui.treeDirs.collapseAll()
        return


def openIconDir(dirPath, main_ui):
    global CUR_DIR_SELECTED

    CUR_DIR_SELECTED = dirPath.strip()
    debug.info(CUR_DIR_SELECTED)
    permitted = True
    for x in prohibitedDirs:
        if x in CUR_DIR_SELECTED:
            permitted = False
    if permitted:
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
    else:
        debug.info("Danger zone")
        main_ui.treeDirs.itemsExpandable = False
        main_ui.treeDirs.collapseAll()
        return


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
            # debug.info(filePath)
            files.append(filePath)
        except:
            debug.info(str(sys.exc_info()))

    files = list(OrderedDict.fromkeys(files))
    return (model,selectedIndexes,files)


def openFile(self, main_ui):
    debug.info("double clicked!!!")

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

                    debug.info(shlex.split(openCmd))
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

    copyAction = menu.addAction("Copy")
    pasteAction = menu.addAction("Paste")
    addToFavAction = menu.addAction("Add To Favourites")
    renameAction = menu.addAction("Rename")
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
    if (action == addToFavAction):
        if (selectedFiles):
            addToFavourites(main_ui)
    if (action == renameAction):
        if (selectedFiles):
            renameUi(main_ui)
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
                    if "/opt/home/bluepixels" in destPath:
                        debug.info("Danger Zone: Can not paste")
                    else:
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


def addToFavourites(main_ui):
    global places
    # currDir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolder.text().strip())).encode('utf-8'))
    model, selectedIndexes, selectedFiles = getSelectedFiles(main_ui)

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
                initConfig()
                loadFavourites(main_ui)
        except:
            debug.info(str(sys.exc_info()))


def renameUi(main_ui):
    currDir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolder.text().strip())).encode('utf-8'))
    model, selectedIndexes, selectedFiles = getSelectedFiles(main_ui)

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
                cmd = sys.executable+" "+rename+" --name '{0}' --path '{1}' ".format(key,currDir)
                debug.info(cmd)
                subprocess.Popen(shlex.split(cmd))
    else:
        debug.info("Error! No permission to rename.")
        messages(main_ui,"red","Error! No permission to rename.")


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

    openDir(homeDir,main_ui)

    initConfig()
    loadFavourites(main_ui)

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
    main_ui.clearPathButt.setShortcut(QtGui.QKeySequence("Delete"))

    main_ui.changeViewButt.setToolTip("Change View (V)")
    main_ui.previousDirButt.setToolTip("Previous Directory (Backspace)")
    main_ui.changeDirButt.setToolTip("Change Directory (Enter)")
    main_ui.clearPathButt.setToolTip("Clear Path (Delete)")

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
