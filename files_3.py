#!/usr/bin/python3
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"

# TODO: Separate threads and utility to different files.
# TODO: Quit and delete threads properly
# TODO: Handle errors properly
# TODO: Documentation


import debug
import constants
from constants import mimeTypes
from constants import mimeConvertCmds
from constants import mimeTypesOpenCmds
from constants import mimeTypesOpenWithCmds
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
from subprocess import Popen, PIPE, STDOUT
import shlex
from shlex import split
from collections import OrderedDict
# import pyperclip
import time
import threading
import traceback
import pathlib
import json
# from PIL import Image
from multiprocessing import Pool
import binascii
import hashlib

from PySide6 import QtCore, QtUiTools, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem, QWidget
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


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
    os.system("mkdir -p {0}".format(filesThumbsDir))

main_ui_file = os.path.join(projDir, "files_3.ui")
debug.info(main_ui_file)

style_sheet_path = os.path.join(projDir, "styleSheets", "style.qss")

renamePermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", '/TEMP_STOR2/temp_stor2', homeDir]
cutCopyPermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", '/TEMP_STOR2/temp_stor2', homeDir]
pastePermittedDirs = ["/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", '/TEMP_STOR2/temp_stor2', homeDir] #REMINDER : Do NOT add bluepixels downloads folder
deletePermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", '/TEMP_STOR2/temp_stor2', homeDir]
newFolderPermittedDirs = ["/opt/home/bluepixels/Downloads", "/blueprod/CRAP/crap", "/crap/crap.server", "/UNREAL_SHARE/unreal", '/TEMP_STOR2/temp_stor2', homeDir]
prohibitedDirs = ["/blueprod/STOR", "/proj", "/library","/aumbackup"]

parser = argparse.ArgumentParser(description="File viewer utility")
parser.add_argument("-p","--path",dest="path",help="Absolute path of the folder")
args = parser.parse_args()

favourites_conf_file = homeDir+os.sep+".config"+os.sep+"files_favourites.json"
thumbs_conf_file = homeDir+os.sep+".config"+os.sep+"files_thumbs.json"

places = {"Home": homeDir, "Crap": "/blueprod/CRAP/crap", "Downloads": homeDir + os.sep + "Downloads"}

thumbs = {}

openTabs = {}

rename = os.path.join(projDir, "rename.py")
details = os.path.join(projDir, "details.py")

# app = None
assPath = args.path

if(args.path):
    ROOTDIR = args.path
else:
    ROOTDIR = rootDir

CUR_DIR_SELECTED = None

cutFile = False

currDownloads = {}

current_icon_files = None
current_list_files = None
current_view = "LIST"

# ICONS
home_icon = os.path.join(projDir, "imageFiles", "icons", "home.svg")
dark_icon = os.path.join(projDir, "imageFiles", "icons", "moon.svg")
light_icon = os.path.join(projDir, "imageFiles", "icons", "sun.svg")
list_icon = os.path.join(projDir, "imageFiles", "icons", "layout-list.svg")
icons_icon = os.path.join(projDir, "imageFiles", "icons", "layout-grid.svg")
prev_dir_icon = os.path.join(projDir, "imageFiles", "icons", "arrow-up.svg")
go_icon = os.path.join(projDir, "imageFiles", "icons", "rotate-cw.svg")
search_icon = os.path.join(projDir, "imageFiles", "icons", "search.svg")
clear_icon = os.path.join(projDir, "imageFiles", "icons", "clear.svg")
close_icon = os.path.join(projDir, "imageFiles", "icons", "close.svg")
add_icon = os.path.join(projDir, "imageFiles", "icons", "plus.svg")
remove_icon = os.path.join(projDir, "imageFiles", "icons", "minus.svg")
rename_icon = os.path.join(projDir, "imageFiles", "icons", "edit.svg")
copy_icon = os.path.join(projDir, "imageFiles", "icons", "copy.svg")
cut_icon = os.path.join(projDir, "imageFiles", "icons", "cut.svg")
paste_icon = os.path.join(projDir, "imageFiles", "icons", "paste.svg")
delete_icon = os.path.join(projDir, "imageFiles", "icons", "delete.svg")
new_folder_icon = os.path.join(projDir, "imageFiles", "icons", "new-folder.svg")
add_favourites_icon = os.path.join(projDir, "imageFiles", "icons", "add-favourites.svg")
details_icon = os.path.join(projDir, "imageFiles", "icons", "info.svg")
help_icon = os.path.join(projDir, "imageFiles", "icons", "help.svg")

home_g_icon = os.path.join(projDir, "imageFiles", "icons", "home-green.svg")
folder_icon = os.path.join(projDir, "imageFiles", "icons", "folder-other.svg")
server_icon = os.path.join(projDir, "imageFiles", "icons", "server-green.svg")
download_icon = os.path.join(projDir, "imageFiles", "icons", "download-green.svg")
temp_icon = os.path.join(projDir, "imageFiles", "icons", "folder-temp-green.svg")


# class WorkerSignals(QObject):
#     finished = Signal()
#     error = Signal(tuple)
#     result = Signal(object)
#     progress = Signal(int)
#
#
# class Worker(QThread):
#     def __init__(self, fn, *args, **kwargs):
#         super().__init__()
#         self.fn = fn
#         self.args = args
#         self.kwargs = kwargs
#         self.signals = WorkerSignals()
#         self.kwargs['progress_callback'] = self.signals.progress.emit
#
#     @Slot()
#     def run(self):
#         try:
#             result = self.fn(*self.args, **self.kwargs)
#         except Exception as e:
#             self.signals.error.emit((type(e), e, traceback.format_exc()))
#             # traceback.print_exc()
#             # exctype, value = sys.exc_info()[:2]
#             # self.signals.error.emit((exctype, value, traceback.format_exc()))
#         else:
#             self.signals.result.emit(result)
#         finally:
#             self.signals.finished.emit()


class FSM(QtWidgets.QFileSystemModel):
    icon_theme = ""
    try:
        icon_theme = subprocess.check_output(shlex.split("xfconf-query -lvc xsettings -p /Net/IconThemeName")).decode().split(" ")[-1].strip()
        debug.info(icon_theme)
    except Exception as e:
        # icon_theme = subprocess.check_output(shlex.split("gsettings get org.gnome.desktop.interface icon-theme")).decode().strip()
        debug.info(f"Icon theme detection failed: {str(e)}")
        # debug.info(str(sys.exc_info()))

    def __init__(self,**kwargs):
        super(FSM, self).__init__(**kwargs)
        if self.icon_theme:
            QtGui.QIcon.setThemeName(self.icon_theme)
        self.icon_cache = {
            "folder": QtGui.QIcon.fromTheme("folder"),
            "video": QtGui.QIcon.fromTheme("video-x-generic"),
            "audio": QtGui.QIcon.fromTheme("audio-x-generic"),
            "image": QtGui.QIcon.fromTheme("image-x-generic"),
            "text": QtGui.QIcon.fromTheme("text-x-generic"),
            "default": QtGui.QIcon.fromTheme("text-x-generic")
        }

    def data(self, index, role):

        # QtGui.QIcon.setThemeName(self.icon_theme)

        if role == QtCore.Qt.DecorationRole and index.column() == 0:
            file_info = self.fileInfo(index)

            if file_info.isDir():
                return self.icon_cache["folder"]

            if file_info.isFile():
                suffix = file_info.suffix()
                file_name = file_info.fileName()
                file_abs_path = file_info.filePath()

                if suffix in mimeTypes["video"]:
                    return self.get_icon(file_abs_path, "video", file_name)
                elif suffix in mimeTypes["audio"]:
                    return self.icon_cache["audio"]
                elif suffix in mimeTypes["image"]:
                    return self.get_icon(file_abs_path, "image", file_name)
                elif suffix in mimeTypes["text"]:
                    return self.icon_cache["text"]

                return self.icon_cache["default"]

        return super(FSM, self).data(index, role)

    def get_icon(self, file_abs_path, file_type, file_name):
        try:
            thumb_image = os.path.join(filesThumbsDir, thumbs[file_abs_path] + ".jpeg")
            if os.path.exists(thumb_image):
                return QtGui.QIcon(thumb_image)
            elif not file_name.startswith("."):
                return self.icon_cache[file_type]
        except Exception as e:
            debug.info(f"Error generating thumbnail for {file_abs_path}: {str(e)}")

        return self.icon_cache[file_type]


class DateFormatDelegate(QtWidgets.QStyledItemDelegate):
    def __init__(self, parent=None):
        super(DateFormatDelegate, self).__init__(parent)
        self.format = "dd-MMM-yy"

    def displayText(self, value, locale):
        # return value.toDate().toString(self.date_format)
        # return QDate.fromString(value, "yyyy-MM-dd").toString(self.format)
        return QDateTime.fromString(value, "MM/dd/yy hh:mm a").toString(self.format)


def init_config():
    global places
    global thumbs
    global favourites_conf_file
    global thumbs_conf_file

    if os.path.exists(favourites_conf_file):
        f = open(favourites_conf_file)
        data = json.load(f)
        places = data
    else:
        with open(favourites_conf_file, 'w') as conf_file:
            json.dump(places, conf_file, sort_keys=True, indent=4)

    if os.path.exists(thumbs_conf_file):
        f = open(thumbs_conf_file)
        data = json.load(f)
        thumbs = data
    else:
        with open(thumbs_conf_file, 'w') as conf_file:
            json.dump(thumbs, conf_file, sort_keys=True, indent=4)


def tabs_popup(main_ui, pos):
    menu = QtWidgets.QMenu()
    # self.setStyle(menu)
    new_action = menu.addAction(QtGui.QIcon(add_icon), "New Tab")
    close_action = menu.addAction(QtGui.QIcon(close_icon), "Close Tab")

    # action = menu.exec_(context.mapToGlobal(pos))
    action = menu.exec(main_ui.tabWidget.mapToGlobal(pos))

    if action == new_action:
        tab_open_doubleclick(main_ui)
    if action == close_action:
        curr_tab_index = main_ui.tabWidget.currentIndex()
        close_current_tab(main_ui, curr_tab_index)


def tab_open_doubleclick(main_ui):
    global current_icon_files
    global current_list_files
    global current_view

    debug.info("Tab Opened")
    content = QFrame()

    v_layout = QtWidgets.QVBoxLayout()
    content.setLayout(v_layout)
    icon_files_1 = widgetProvider.icon_files_widget()
    list_files_1 = widgetProvider.list_files_widget()
    v_layout.addWidget(icon_files_1)
    v_layout.addWidget(list_files_1)

    current_icon_files = icon_files_1
    current_list_files = list_files_1

    if current_view == "LIST":
        current_icon_files.hide()
        current_list_files.show()
    elif current_view == "ICON":
        current_icon_files.show()
        current_list_files.hide()
    # currIconFiles.hide()
    current_list_files.setColumnWidth(0, 660)

    current_icon_files.customContextMenuRequested.connect(lambda x, mu=main_ui, context=current_icon_files.viewport(): files_popup(mu, context, x))
    current_icon_files.doubleClicked.connect(lambda x, mu=main_ui: open_file(main_ui))
    current_list_files.customContextMenuRequested.connect(lambda x, mu=main_ui, context=current_list_files.viewport(): files_popup(mu, context, x))
    current_list_files.doubleClicked.connect(lambda x, mu=main_ui: open_file(main_ui))

    curr_dir_path = str(os.path.abspath(main_ui.currentFolderBox.text().strip()))
    curr_dir_name = str(os.path.abspath(main_ui.currentFolderBox.text().strip())).split(os.sep)[-1]

    i = main_ui.tabWidget.addTab(content, curr_dir_name)
    main_ui.tabWidget.setCurrentIndex(i)

    open_dir(main_ui, dir_path=curr_dir_path)
    # main_ui.tabWidget.currentWidget().customContextMenuRequested.connect(self.popUpTabs)

    # main_ui.currentFolderBox.clear()
    # main_ui.currentFolderBox.setText(main_ui.tabWidget.tabToolTip(i))


def current_tab_changed(main_ui, i):
    global current_icon_files
    global current_list_files
    global current_view

    current_icon_files = main_ui.tabWidget.currentWidget().findChild(QtWidgets.QListView)
    current_list_files = main_ui.tabWidget.currentWidget().findChild(QtWidgets.QTreeView)

    try:
        curr_tab_index = main_ui.tabWidget.currentIndex()
        # currTabName = main_ui.tabWidget.tabText(curr_tab_index)
        curr_dir_path = main_ui.tabWidget.tabToolTip(curr_tab_index)
        # debug.info(currDirPath)
        main_ui.currentFolderBox.clear()
        main_ui.currentFolderBox.setText(curr_dir_path)
        main_ui.pathBox.clear()
        main_ui.pathBox.setText(curr_dir_path)
    except:
        debug.info(str(sys.exc_info()))
    # currTabIndex = main_ui.tabWidget.currentIndex()
    # debug.info(openTabs)
    if current_list_files.isVisible() and current_icon_files.isHidden():
        current_view = "LIST"
        main_ui.changeViewButt.setIcon(QtGui.QIcon(icons_icon))
    elif current_icon_files.isVisible() and current_list_files.isHidden():
        current_view = "ICON"
        main_ui.changeViewButt.setIcon(QtGui.QIcon(list_icon))


def close_current_tab(main_ui, i):
    # global currIconFiles
    # global currListFiles
    #
    # currIconFiles = main_ui.tabWidget.currentWidget().findChild(QtWidgets.QListView)
    # currListFiles = main_ui.tabWidget.currentWidget().findChild(QtWidgets.QTreeView)
    debug.info(i)
    if main_ui.tabWidget.count() < 2:
        return

    main_ui.tabWidget.removeTab(i)
    # try:
    #     openTabs.pop(list(openTabs.keys())[i])
    # except:
    #     debug.info(str(sys.exc_info()))


def load_favourites(main_ui):
    global places
    model = QtGui.QStandardItemModel()
    main_ui.favourites.setModel(model)

    sorted_places = OrderedDict(sorted(places.items()))
    for key, value in sorted_places.items():
        item = QtGui.QStandardItem(key)
        model.appendRow(item)

        frame = QtWidgets.QFrame()
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)

        line = QtWidgets.QLineEdit()
        line.setText(key)
        line.hide()

        thumb = QtWidgets.QPushButton()

        thumb.setText(key)

        if key == "Home":
            # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "home.svg")))
            thumb.setIcon(QtGui.QIcon(home_g_icon))
        elif key == "Downloads":
            # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "downloads.svg")))
            thumb.setIcon(QtGui.QIcon(download_icon))
        elif key == "Tmp":
            # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "temp.svg")))
            thumb.setIcon(QtGui.QIcon(temp_icon))
        elif key == "Crap":
            # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "crap.svg")))
            thumb.setIcon(QtGui.QIcon(server_icon))
        else:
            # thumb.setIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "new_icons", "folder-other.svg")))
            thumb.setIcon(QtGui.QIcon(folder_icon))

        thumb.setFocusPolicy(Qt.NoFocus)
        thumb.setStyleSheet(''' QPushButton { text-align: left; } ''')
        # thumb.setStyleSheet(''' QPushButton { text-align: left; border-style: transparent; padding-left: 8px; }
        #                                     QPushButton:hover { border: 1px solid #3daee9; } ''')

        enter_button = QtWidgets.QPushButton()
        enter_button.setFocusPolicy(Qt.NoFocus)
        enter_button.hide()

        thumb.clicked.connect(lambda x, mu=main_ui, dir_path=value: open_dir(mu, dir_path=dir_path))
        enter_button.clicked.connect(lambda x, mu=main_ui, button=thumb, editor=line, eb=enter_button: change_fav_name(mu, button, editor, eb))

        thumb.setContextMenuPolicy(Qt.CustomContextMenu)
        thumb.customContextMenuRequested.connect(lambda x, mu=main_ui, button=thumb, editor=line, eb=enter_button: favourites_popup(mu, button, editor, eb, x))

        h_layout.addWidget(thumb)
        h_layout.addWidget(line)
        h_layout.addWidget(enter_button)
        frame.setLayout(h_layout)

        main_ui.favourites.setIndexWidget(item.index(), frame)


def favourites_popup(main_ui, button, editor, enter_button, pos):
    global places
    curr_name = button.text()
    # editorName = editor.text()
    debug.info(curr_name)
    # debug.info(editorName)

    menu = QMenu()
    # self.setStyle(menu)
    rename_action = menu.addAction(QtGui.QIcon(rename_icon), "Rename")
    remove_action = menu.addAction(QtGui.QIcon(remove_icon), "Remove")
    # action = menu.exec_(context.mapToGlobal(pos))
    action = menu.exec(button.mapToGlobal(pos))

    if action == rename_action:
        main_ui.changeDirButt.setShortcut(QtGui.QKeySequence(""))
        enter_button.setShortcut(QtGui.QKeySequence("Return"))
        button.hide()
        editor.show()
        enter_button.show()
        editor.setFocus()

    if action == remove_action:
        places.pop(curr_name)
        with open(favourites_conf_file, 'w') as conf_file:
            json.dump(places, conf_file, sort_keys=True, indent=4)
        init_config()
        load_favourites(main_ui)


def change_fav_name(main_ui, button, editor, enter_button):
    curr_name = button.text()
    new_name = editor.text()
    debug.info(curr_name)
    debug.info(new_name)

    if new_name == curr_name:
        debug.info("no changes found in name")
    else:
        for key, value in places.items():
            if key == curr_name:
                places[new_name] = value
                places.pop(key)
                with open(favourites_conf_file, 'w') as conf_file:
                    json.dump(places, conf_file, sort_keys=True, indent=4)
                init_config()
                load_favourites(main_ui)

    button.show()
    editor.hide()
    enter_button.hide()
    editor.clearFocus()
    main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))
    enter_button.setShortcut(QtGui.QKeySequence(""))


def set_dir(main_ui, root_dir_new):
    clear_all_selection()
    # debug.info(type(ROOTDIRNEW))
    if "/blueprod/STOR" in root_dir_new:
        debug.info("Danger zone")
        # main_ui.treeDirs.itemsExpandable = False
        # main_ui.treeDirs.collapseAll()
    else:
        # self.messages("green","Generating thumbnails")
        # main_ui.treeDirs.itemsExpandable = True
        model_dirs = FSM(parent=main_ui)
        # modelDirs.setIconProvider(IconProvider())
        # modelDirs.setIconProvider(CustomIconProvider())
        model_dirs.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        model_dirs.setRootPath(root_dir_new)

        # main_ui.treeDirs.setModel(modelDirs)

        # main_ui.treeDirs.hideColumn(1)
        # main_ui.treeDirs.hideColumn(2)
        # main_ui.treeDirs.hideColumn(3)

        # rootIdx = modelDirs.index(ROOTDIRNEW)
        # main_ui.treeDirs.setRootIndex(rootIdx)

        # openDir(ROOTDIRNEW, main_ui)
        return model_dirs


def open_dir(main_ui, dir_path=""):
    global current_list_files

    if not os.path.exists(dir_path):
        messages(main_ui, "red", "Error! Path not found.")
        return

    clear_all_selection()
    open_list_dir(main_ui, dir_path)
    open_icon_dir(main_ui, dir_path)

    main_ui.pathBox.setText(dir_path)

    curr_dir_path = str(dir_path)
    curr_dir_name = str(curr_dir_path.split(os.sep)[-1])
    curr_tab_index = main_ui.tabWidget.currentIndex()
    # debug.info(currTabIndex)
    # openTabs[currTabIndex] = {currDirName:currDirPath}

    main_ui.tabWidget.setTabText(curr_tab_index, curr_dir_name)
    main_ui.tabWidget.setTabToolTip(curr_tab_index, curr_dir_path)
    try:
        current_list_files.setColumnWidth(0, 660)
        # main_ui.currentFolderBox.clear()
        # main_ui.currentFolderBox.setText(currDirPath)
    except:
        debug.info(str(sys.exc_info()))

    # worker = Worker(gen_thumb, dir_path=dir_path)
    # # self.threadpool.start(worker)
    # worker.start()
    # worker.wait()

    gen_thumb_thread = GenThumbThread(dir_path=dir_path, parent=app)
    # gen_thumb_thread.result.connect(lambda d, mu=main_ui: after_video_download(mu, d))
    # gen_thumb_thread.progress.connect(lambda u, mu=main_ui: update_download_progress(mu, u))
    # dT.finished.connect(lambda x : self.afterVideoDownload(x))
    gen_thumb_thread.start()


def gen_thumb(dir_path=""):
    global thumbs
    all_files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    for f in all_files:
        # debug.info(f)
        if f.startswith("."):
            pass
        else:
            file_abs_path = os.path.join(dir_path, f)
            file_extension = os.path.splitext(file_abs_path)[1]
            # debug.info(file_extension)

            # ext = file_extension.split(".")[1]
            ext = file_extension.replace(".", "").strip()
            # debug.info(ext)

            if ext in mimeTypes["video"]:

                debug.info(file_abs_path)
                # hex_file_path = binascii.hexlify(file_abs_path.encode()).decode()
                hex_file_path = hashlib.sha256(file_abs_path.encode()).hexdigest()
                debug.info(hex_file_path)
                thumbs[file_abs_path] = hex_file_path
                # with open(thumbs_conf_file, 'w') as conf_file:
                #     json.dump(thumbs, conf_file, sort_keys=True, indent=4)

                thumb_image = filesThumbsDir + hex_file_path + ".jpeg"
                if os.path.exists(thumb_image):
                    pass
                else:
                    try:
                        # genThumbCmd = "ffmpeg -ss 00:00:01.000 -i \"{0}\" -vf 'scale=128:128:force_original_aspect_ratio=decrease' -vframes 1 \"{1}\" -y ".format(
                        #               file_abs_path, thumb_image)
                        gen_thumb_cmd = mimeConvertCmds["video"].format(file_abs_path, thumb_image)
                        subprocess.call(shlex.split(gen_thumb_cmd))
                    except:
                        debug.info(str(sys.exc_info()))

            if ext in mimeTypes["image"]:

                debug.info(file_abs_path)
                # hex_file_path = binascii.hexlify(file_abs_path.encode()).decode()
                hex_file_path = hashlib.sha256(file_abs_path.encode()).hexdigest()
                debug.info(hex_file_path)
                thumbs[file_abs_path] = hex_file_path
                # with open(thumbs_conf_file, 'w') as conf_file:
                #     json.dump(thumbs, conf_file, sort_keys=True, indent=4)

                thumb_image = filesThumbsDir + hex_file_path + ".jpeg"
                if os.path.exists(thumb_image):
                    pass
                else:
                    try:
                        # im = Image.open(file_abs_path)
                        # im.thumbnail((128,128))
                        # im.save(thumb_image)
                        gen_thumb_cmd = mimeConvertCmds["image"].format(file_abs_path, thumb_image)
                        subprocess.call(shlex.split(gen_thumb_cmd))
                    except:
                        debug.info(str(sys.exc_info()))

    with open(thumbs_conf_file, 'w') as conf_file:
        json.dump(thumbs, conf_file, sort_keys=True, indent=4)


def open_list_dir(main_ui, dir_path=""):
    global CUR_DIR_SELECTED
    global current_icon_files
    global current_list_files

    CUR_DIR_SELECTED = dir_path.strip()
    debug.info(CUR_DIR_SELECTED)

    search_term = main_ui.searchBox.text().strip()
    # debug.info(search_term)

    permitted = True
    for x in prohibitedDirs:
        if x in CUR_DIR_SELECTED:
            permitted = False
    if permitted:
        # self.messages("green", "Generating thumbnails")
        # main_ui.treeDirs.itemsExpandable = True
        main_ui.currentFolderBox.clear()
        main_ui.currentFolderBox.setText(CUR_DIR_SELECTED)

        model_files = FSM(parent=main_ui)
        # model_files.setIconProvider(IconProvider())
        try:
            current_list_files.setModel(model_files)
        except:
            debug.info(str(sys.exc_info()))
        model_files.setRootPath(CUR_DIR_SELECTED)

        model_files.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        model_files.setNameFilters([search_term+"*"])
        model_files.setNameFilterDisables(False)
        debug.info(model_files.nameFilters())

        root_index = model_files.index(CUR_DIR_SELECTED)
        try:
            current_list_files.setRootIndex(root_index)
            current_list_files.setItemDelegateForColumn(3, DateFormatDelegate())
        except:
            debug.info(str(sys.exc_info()))
        return
    else:
        debug.info("Danger zone")
        debug.info("Error! No permission to open.")
        messages(main_ui, "red", "Error! No permission to open.")
        # main_ui.treeDirs.itemsExpandable = False
        # main_ui.treeDirs.collapseAll()
        return


def open_icon_dir(main_ui, dir_path=""):
    global CUR_DIR_SELECTED
    global current_icon_files
    global current_list_files

    CUR_DIR_SELECTED = dir_path.strip()
    debug.info(CUR_DIR_SELECTED)

    search_term = main_ui.searchBox.text().strip()
    # debug.info(search_term)

    permitted = True
    for x in prohibitedDirs:
        if x in CUR_DIR_SELECTED:
            permitted = False
    if permitted:
        # self.messages("green", "Generating thumbnails")
        # main_ui.treeDirs.itemsExpandable = True
        main_ui.currentFolderBox.clear()
        main_ui.currentFolderBox.setText(CUR_DIR_SELECTED)

        model_files = FSM(parent=main_ui)
        # model_files.setIconProvider(IconProvider())
        try:
            current_icon_files.setModel(model_files)
        except:
            debug.info(str(sys.exc_info()))
        model_files.setRootPath(CUR_DIR_SELECTED)

        model_files.setFilter(QtCore.QDir.Dirs | QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot)
        model_files.setNameFilters([search_term + "*"])
        model_files.setNameFilterDisables(False)
        debug.info(model_files.nameFilters())

        root_index = model_files.index(CUR_DIR_SELECTED)
        try:
            current_icon_files.setRootIndex(root_index)
        except:
            debug.info(str(sys.exc_info()))
        return
    else:
        debug.info("Danger zone")
        debug.info("Error! No permission to open.")
        messages("red", "Error! No permission to open.")
        # main_ui.treeDirs.itemsExpandable = False
        # main_ui.treeDirs.collapseAll()
        return


# def dirSelected(self, index, model):
#     dir_path = model.filePath(index)
#     open_dir(dir_path)


def clear_all_selection():
    global current_icon_files
    global current_list_files

    try:
        current_icon_files.clearSelection()
        current_list_files.clearSelection()
    except:
        debug.info(str(sys.exc_info()))
    debug.info("Cleared Selection")


def change_view(main_ui):
    global current_icon_files
    global current_list_files
    global current_view

    clear_all_selection()
    if current_view == "LIST":
        main_ui.changeViewButt.setIcon(QtGui.QIcon(list_icon))
        current_view = "ICON"
        current_icon_files.show()
        current_list_files.hide()
    elif current_view == "ICON":
        main_ui.changeViewButt.setIcon(QtGui.QIcon(icons_icon))
        current_view = "LIST"
        current_icon_files.hide()
        current_list_files.show()

    # if currIconFiles.isHidden():
    #     main_ui.changeViewButt.setIcon(QtGui.QIcon(self.listIcon))
    #     currIconFiles.show()
    #     currListFiles.hide()
    # else:
    #     main_ui.changeViewButt.setIcon(QtGui.QIcon(self.iconsIcon))
    #     currIconFiles.hide()
    #     currListFiles.show()


def previous_dir(main_ui):
    # debug.info("previous directory")
    ROOTDIR = main_ui.currentFolderBox.text().strip()
    if ROOTDIR != "":
        if os.path.exists(ROOTDIR):
            ROOTDIRNEW = os.sep.join(ROOTDIR.split(os.sep)[:-1])
            debug.info(ROOTDIRNEW)
            if os.path.exists(ROOTDIRNEW):
                open_dir(main_ui, dir_path=ROOTDIRNEW)
                messages(main_ui, "white", "")
        else:
            debug.info("No such folder!")


def change_dir(main_ui):
    ROOTDIR = main_ui.currentFolderBox.text().strip()
    if ROOTDIR != "":
        ROOTDIRNEW = os.path.abspath(os.path.expanduser(ROOTDIR))
        if os.path.exists(ROOTDIRNEW):
            debug.info (ROOTDIRNEW)
            open_dir(main_ui, dir_path=ROOTDIRNEW)
            messages(main_ui, "white", "")
        else:
            messages(main_ui, "red", "Folder not found!")


def search(main_ui):
    ROOTDIR = main_ui.currentFolderBox.text().strip()
    open_dir(main_ui, dir_path=ROOTDIR)


def clearPath(self):
    main_ui.currentFolderBox.clear()


def get_selected_files():
    global current_icon_files
    global current_list_files

    model = None
    selected_indexes = None
    all_files = []

    if current_icon_files.isVisible():
        model = current_icon_files.model()
        selected_indexes = current_icon_files.selectedIndexes()
    elif current_list_files.isVisible():
        model = current_list_files.model()
        selected_indexes = current_list_files.selectedIndexes()

    for selected_index in selected_indexes:
        try:
            file_abs_path = os.path.abspath(str(model.filePath(selected_index)))
            all_files.append(file_abs_path)
        except:
            debug.info(str(sys.exc_info()))

    all_files = list(OrderedDict.fromkeys(all_files))
    return model, selected_indexes, all_files


def open_file(main_ui):
    debug.info("double clicked!!!")

    model, selected_indexes, selected_files = get_selected_files()
    indexes = [i for i in selected_indexes if i.column() == 0]
    # debug.info(indexes)
    for index in indexes:
        try:
            file_info = model.fileInfo(index)
            file_abs_path = os.path.abspath(str(model.filePath(index)))
            file_name = str(model.fileName(index))
            debug.info(file_abs_path)
            debug.info(file_name)

            if file_info.isDir():
                debug.info("This is a directory!")
                main_ui.searchBox.clear()
                open_dir(main_ui, dir_path=file_abs_path)

            if file_info.isFile():
                debug.info("This is a file!")
                try:
                    suffix = pathlib.Path(file_name).suffix.split('.')[-1]
                    debug.info(suffix)
                    open_command = ""
                    if suffix in mimeTypes["video"]:
                        open_command = mimeTypesOpenCmds["video"].format(os.path.join(projDir,"video-input.conf"), file_abs_path)
                    elif suffix in mimeTypes["audio"]:
                        open_command = mimeTypesOpenCmds["audio"].format(file_abs_path)
                    elif suffix in mimeTypes["image"]:
                        # openCmd = projDir+os.sep+"mediaPlayer.py --path '{0}' ".format(filePath)
                        open_command = mimeTypesOpenCmds["image"].format(os.path.join(projDir,"image-input.conf"), file_abs_path)
                        # openCmd = "pureref \"{0}\" ".format(filePath)
                    elif suffix in mimeTypes["text"]:
                        open_command = mimeTypesOpenCmds["text"].format(file_abs_path)
                    elif suffix == "pdf":
                        open_command = mimeTypesOpenCmds["pdf"].format(file_abs_path)
                    elif suffix == "pur":
                        open_command = mimeTypesOpenCmds["pureref"].format(file_abs_path)

                    debug.info(shlex.split(open_command))
                    if open_command:
                        subprocess.Popen(shlex.split(open_command))
                except:
                    debug.info(str(sys.exc_info()))
        except:
            debug.info(str(sys.exc_info()))


def files_popup(main_ui, context, pos):
    clip = QtWidgets.QApplication.clipboard()
    paste_urls = clip.mimeData().urls()

    menu = QtWidgets.QMenu()
    # self.setStyle(menu)

    model, selected_indexes, selected_files = get_selected_files()

    open_with_cmd_actions = {}

    if len(selected_files) == 1:
        if os.path.isfile(selected_files[0]):
            debug.info("Eligible for open with")
            open_action = menu.addAction("Open")
            open_with_menu = QtWidgets.QMenu("Open With")
            # self.setStyle(openWithMenu)

            file_name = str(model.fileName(selected_indexes[0]))
            suffix = pathlib.Path(file_name).suffix.split('.')[-1]
            debug.info(suffix)
            for fileType in mimeTypes.keys():
                if suffix in mimeTypes[fileType]:
                    if fileType in mimeTypesOpenWithCmds.keys():
                        mime_softs = [i for i in mimeTypesOpenWithCmds[fileType].keys()]
                        debug.info(mime_softs)
                        for soft in mime_softs:
                            open_with_cmd_actions[open_with_menu.addAction(soft)] = mimeTypesOpenWithCmds[fileType][soft].format(selected_files[0])

            debug.info(open_with_cmd_actions)

            menu.addMenu(open_with_menu)

    copy_action = menu.addAction(QtGui.QIcon(copy_icon), "Copy")
    cut_action = menu.addAction(QtGui.QIcon(cut_icon), "Cut")
    paste_action = menu.addAction(QtGui.QIcon(paste_icon), "Paste")
    new_folder_action = menu.addAction(QtGui.QIcon(new_folder_icon), "New Folder")
    add_to_fav_action = menu.addAction(QtGui.QIcon(add_favourites_icon), "Add To Favourites")
    rename_action = menu.addAction(QtGui.QIcon(rename_icon), "Rename")
    delete_action = menu.addAction(QtGui.QIcon(delete_icon), "Delete")
    details_action = menu.addAction(QtGui.QIcon(details_icon), "Details")

    action = menu.exec(context.mapToGlobal(pos))

    try:
        if action == open_action:
            if selected_files:
                open_file(main_ui)
    except:
        debug.info(str(sys.exc_info()))

    try:
        if action in open_with_cmd_actions.keys():
            if selected_files:
                run_command = open_with_cmd_actions[action]
                debug.info(run_command)
                subprocess.Popen(shlex.split(run_command))
    except:
        debug.info(str(sys.exc_info()))

    if action == copy_action:
        if selected_files:
            copy_files(main_ui)
    if action == cut_action:
        if selected_files:
            cut_files(main_ui)
    if action == paste_action:
        paste_files(main_ui, paste_urls)
    if action == new_folder_action:
        create_new_folder(main_ui)
    if action == add_to_fav_action:
        if selected_files:
            add_to_favourites(main_ui)
    if action == rename_action:
        if selected_files:
            rename_ui(main_ui)
    if action == delete_action:
        if selected_files:
            delete_files(main_ui)
    if action == details_action:
        if selected_files:
            show_details(main_ui)


def copy_files(main_ui):
    global cutFile
    cutFile = False
    current_dir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolderBox.text().strip())))

    permitted = False
    for x in cutCopyPermittedDirs:
        if x in current_dir:
            permitted = True
    if permitted:
        model, selected_indexes, selected_files = get_selected_files()
        url_list = []
        mime_data = QtCore.QMimeData()
        for x in selected_files:
            debug.info("Copied "+x)
            url_list.append(QtCore.QUrl().fromLocalFile(x))
        mime_data.setUrls(url_list)
        QtWidgets.QApplication.clipboard().setMimeData(mime_data)
    else:
        debug.info("Error! No permission to copy.")
        messages(main_ui, "red", "Error! No permission to copy.")


def cut_files(main_ui):
    global cutFile
    copy_files(main_ui)
    cutFile = True


def paste_files(main_ui, urls):
    global cutFile
    for url in urls:
        try:
            source_file = url.toLocalFile()
            dest_folder = main_ui.currentFolderBox.text().strip()
            source_file_name = os.path.basename(source_file)
            debug.info(source_file)
            debug.info(source_file_name)
            # debug.info(destFolder)
            if dest_folder:
                dest_path = os.path.abspath(dest_folder)+"/"
                # debug.info(destPath)
                if dest_path and os.path.exists(dest_path):
                    debug.info(dest_path)
                    permitted = False
                    for x in pastePermittedDirs:
                        if x in dest_path:
                            permitted = True
                    if permitted:
                        if "/opt/home/bluepixels" in dest_path: #REMINDER : Do NOT remove this code.
                            debug.info("Danger Zone: Can not paste")
                            return
                        else:
                            if os.path.exists(dest_path+source_file_name):
                                debug.info("File already exists")
                                messages(main_ui, "red", "File already exists")
                            else:
                                remove_source_files=False
                                if cutFile:
                                    remove_source_files=True
                                messages(main_ui, "green", "Copying " + source_file)
                                main_ui.progressBar.show()
                                main_ui.progressBar.setValue(0)
                                file_copy_thread = RsyncThread(source_file, dest_path, parent=app, remove_source_files=remove_source_files)
                                file_copy_thread.progress_updated.connect(lambda progress, mu=main_ui, source=source_file: update_progress(mu, progress, source))
                                # file_copy_thread.finished.connect(self.copy_finished)
                                file_copy_thread.finished.connect(lambda mu=main_ui, source=source_file, cut_file=cutFile: copy_finished(mu, source, cut_file=cut_file))
                                file_copy_thread.start()

                                if cutFile:
                                    rm_dir_cmd = "rmdir \"{0}\" ".format(source_file)
                                    try:
                                        subprocess.Popen(shlex.split(rm_dir_cmd))
                                    except:
                                        debug.info(str(sys.exc_info()))

                    else:
                        debug.info("Danger Zone: Can not paste")
                        debug.info("Error! No permission to paste.")
                        messages(main_ui, "red", "Error! No permission to paste.")
        except:
            debug.info(str(sys.exc_info()))


def update_progress(main_ui, progress, source):
    debug.info(progress)
    main_ui.progressBar.show()
    messages(main_ui, "green", "Copying " + source)
    main_ui.progressBar.setValue(int(progress))


def copy_finished(main_ui, source, cut_file=False):
    main_ui.progressBar.hide()
    subprocess.Popen(shlex.split("sync"))
    messages(main_ui, "green", "Finished copying")

    if cut_file:
        rm_dir_cmd = "rmdir \"{0}\" ".format(source)
        try:
            subprocess.Popen(shlex.split(rm_dir_cmd))
        except:
            debug.info(str(sys.exc_info()))


def create_new_folder(main_ui):
    clear_info_frame(main_ui)
    main_ui.splitter01.setSizes([100, 140])
    layout = main_ui.infoFrame.layout()

    current_dir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolderBox.text().strip())))
    debug.info(current_dir)

    permitted = False
    for x in newFolderPermittedDirs:
        if x in current_dir:
            permitted = True
    if permitted:
        label = QtWidgets.QLabel()
        name_line = QtWidgets.QLineEdit()
        create_button = QtWidgets.QPushButton()
        cancel_button = QtWidgets.QPushButton()
        v_spacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addWidget(label, 1, 0, 1, 2)
        layout.addWidget(name_line, 2, 0, 1, 2)
        layout.addWidget(cancel_button, 3, 0)
        layout.addWidget(create_button, 3, 1)
        layout.addItem(v_spacer)
        main_ui.searchBox.setFocusPolicy(QtCore.Qt.ClickFocus)
        main_ui.searchBox.setFocus()
        name_line.setFocusPolicy(QtCore.Qt.StrongFocus)
        name_line.setFocus()
        # label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setText("<b>Create New Folder</b>")
        name_line.setText("New_Folder")
        cancel_button.setText("Cancel")
        create_button.setText("Create")
        main_ui.changeDirButt.setShortcut(QtGui.QKeySequence(""))
        create_button.setShortcut(QtGui.QKeySequence("Return"))
        cancel_button.setShortcut(QtGui.QKeySequence("Escape"))
        create_button.clicked.connect(lambda f, mu=main_ui, line=name_line: add_folder(mu, line))
        cancel_button.clicked.connect(lambda c, mu=main_ui: clear_info_frame(mu))
    else:
        debug.info("Danger Zone: Can not create new folder")
        debug.info("Error! No permission to create new folder.")
        messages(main_ui, "red", "Error! No permission to create new folder.")
        clear_info_frame(main_ui)
        return


def add_folder(main_ui, line):
    debug.info(line.text())

    current_dir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolderBox.text().strip())))
    debug.info(current_dir)

    new_folder_name = str(line.text()).strip()
    dirs = [x for x in os.listdir(current_dir) if not x.startswith(".") and os.path.isdir(os.path.join(current_dir, x))]
    debug.info(dirs)
    for i in range(1,100):
        if new_folder_name in dirs:
            new_folder_name += "_"+str(i)
        else:
            break

    new_folder = current_dir + os.sep + new_folder_name
    new_folder_cmd = "mkdir \"{0}\" ".format(new_folder)
    debug.info(new_folder_cmd)
    try:
        subprocess.Popen(shlex.split(new_folder_cmd))
    except:
        debug.info(str(sys.exc_info()))
    clear_info_frame(main_ui)


def clear_info_frame(main_ui):
    main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))
    main_ui.searchBox.setFocusPolicy(QtCore.Qt.StrongFocus)
    main_ui.searchBox.setFocus()
    # main_ui.v_splitter1.setSizes([100, 140])
    layout = main_ui.infoFrame.layout()
    if layout:
        try:
            for i in reversed(range(layout.count())):
                widget = layout.takeAt(i).widget()
                if widget is not None:
                    widget.setParent(None)
        except:
            debug.info(str(sys.exc_info()))


def add_to_favourites(main_ui):
    global places
    # currDir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolderBox.text().strip())))
    model, selected_indexes, selected_files = get_selected_files()

    indexes = [i for i in selected_indexes if i.column() == 0]
    for index in indexes:
        try:
            file_info = model.fileInfo(index)
            file_name = (str(model.fileName(index)).capitalize())
            file_abs_path = os.path.abspath(str(model.filePath(index)))
            if file_info.isDir():
                places[file_name] = file_abs_path
                with open(favourites_conf_file, 'w') as conf_file:
                    json.dump(places, conf_file, sort_keys=True, indent=4)
                init_config()
                load_favourites(main_ui)
        except:
            debug.info(str(sys.exc_info()))


def rename_ui(main_ui):
    clear_info_frame(main_ui)
    main_ui.splitter01.setSizes([100, 140])
    layout = main_ui.infoFrame.layout()

    current_dir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolderBox.text().strip())))
    model, selected_indexes, selected_files = get_selected_files()

    file_dets = {}
    permitted = False
    for x in renamePermittedDirs:
        if x in current_dir:
            permitted = True
    if permitted:
        indexes = [i for i in selected_indexes if i.column() == 0]
        for index in indexes:
            try:
                file_name = (str(model.fileName(index)))
                file_abs_path = os.path.abspath(str(model.filePath(index)))
                file_dets[file_name] = file_abs_path
            except:
                debug.info(str(sys.exc_info()))
        debug.info(file_dets)
    else:
        debug.info("Error! No permission to rename.")
        messages(main_ui, "red", "Error! No permission to rename.")
        clear_info_frame(main_ui)
        return
    debug.info(file_dets)
    if (len(file_dets)) == 1:
        for key, value in file_dets.items():
            label = QtWidgets.QLabel()
            name_line = QtWidgets.QLineEdit()
            rename_button = QtWidgets.QPushButton()
            cancel_button = QtWidgets.QPushButton()
            v_spacer = QtWidgets.QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
            layout.addWidget(label, 1, 0, 1, 2)
            layout.addWidget(name_line, 2, 0, 1, 2)
            layout.addWidget(cancel_button, 3, 0)
            layout.addWidget(rename_button, 3, 1)
            layout.addItem(v_spacer)
            main_ui.searchBox.setFocusPolicy(QtCore.Qt.ClickFocus)
            main_ui.searchBox.setFocus()
            name_line.setFocusPolicy(QtCore.Qt.StrongFocus)
            name_line.setFocus()
            # label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
            label.setAlignment(QtCore.Qt.AlignCenter)
            label.setText("<b>Rename</b>")
            name_line.setText(key)
            name_line.setCursorPosition(0)
            cancel_button.setText("Cancel")
            rename_button.setText("Rename")
            main_ui.changeDirButt.setShortcut(QtGui.QKeySequence(""))
            rename_button.setShortcut(QtGui.QKeySequence("Return"))
            cancel_button.setShortcut(QtGui.QKeySequence("Escape"))
            rename_button.clicked.connect(lambda r, mu=main_ui, line=name_line, path=current_dir, name=key: rename_new(mu, line, path, name))
            cancel_button.clicked.connect(lambda c, mu=main_ui: clear_info_frame(mu))


def rename_new(main_ui, line, path, name):
    try:
        new_name = line.text().strip()
        if os.path.exists(path+os.sep+new_name):
            debug.info("Error! File Exists.")
            messages(main_ui, "red", "Error! File Exists.")
            clear_info_frame(main_ui)
            return
        cmd = "mv \"{0}\" \"{1}\" ".format(path + os.sep + name, path + os.sep + new_name)
        debug.info(cmd)
        subprocess.Popen(shlex.split(cmd))
        clear_info_frame(main_ui)
    except:
        debug.info(str(sys.exc_info()))


def delete_files(main_ui):
    current_dir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolderBox.text().strip())))
    debug.info(current_dir)
    permitted = False
    for x in deletePermittedDirs:
        if x in current_dir:
            permitted = True
    if permitted:
    # if "/opt/home/bluepixels/Downloads" in currDir:
        model, selected_indexes, selected_files = get_selected_files()
        file_names = []
        indexes = [i for i in selected_indexes if i.column() == 0]
        for index in indexes:
            try:
                file_name = (str(model.fileName(index)))
                file_names.append(file_name)
            except:
                debug.info(str(sys.exc_info()))
        debug.info(file_names)
        confirm = QtWidgets.QMessageBox()
        # self.setStyle(confirm)
        # confirm.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png"))))
        confirm.setWindowTitle("Warning!")
        # confirm.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join(projDir, "imageFiles", "help-icon-1.png"))))
        confirm.setIconPixmap(QtGui.QPixmap(help_icon))
        confirm.setText("<b>Permanently Delete these item(s)?</b>"+"\n")
        confirm.setInformativeText(",\n".join(i for i in file_names))
        confirm.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        selection = confirm.exec()
        if selection == QtWidgets.QMessageBox.Yes:
            for x in selected_files:
                # if "/opt/home/bluepixels/Downloads/" in x:
                remove_cmd = "rm -frv \"{0}\" ".format(x)
                debug.info(shlex.split(remove_cmd))
                if remove_cmd:
                    p = subprocess.Popen(shlex.split(remove_cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    output, error = p.communicate()
                    if p.returncode == 0:
                        debug.info("Deleted "+x)
                        change_dir(main_ui)
                    else:
                        debug.info(f"Command failed with return code: {p.returncode}")
                    # debug.info("Deleted "+x)
                    # self.change_dir()
    else:
        debug.info("Error! No permission to delete.")
        messages(main_ui, "red", "Error! No permission to delete.")


def show_details(main_ui):
    clear_info_frame(main_ui)
    main_ui.splitter01.setSizes([100, 140])
    layout = main_ui.infoFrame.layout()

    label = QtWidgets.QLabel()
    dets_field = QtWidgets.QTextEdit()
    dets_field.setReadOnly(True)
    # detsField.setStyleSheet(''' border: 1px solid #76797C; ''')
    # dets_field.setStyleSheet(''' QTextEdit { border: 1px solid #76797C; } ''')

    layout.addWidget(label, 1, 0, 1, 2)
    layout.addWidget(dets_field, 2, 0, 1, 2)

    # label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
    label.setAlignment(QtCore.Qt.AlignCenter)
    label.setText("<b>Properties</b>")

    current_dir = str(os.path.abspath(os.path.expanduser(main_ui.currentFolderBox.text().strip())))
    debug.info(current_dir)
    model, selected_indexes, selected_files = get_selected_files()
    debug.info(selected_files)

    file_names = []
    indexes = [i for i in selected_indexes if i.column() == 0]
    for index in indexes:
        file_name = (str(model.fileName(index)))
        file_names.append(file_name)

    # detsField.append("\n")
    dets_field.append("<b>Name : </b>"+", ".join(file_names))
    dets_field.append("<b>Location : </b>" + current_dir)

    # allSelectedFiles = [file+"/*" for file in selectedFiles]

    dets_cmd = ['du', '-sch']
    for file in selected_files:
        dets_cmd = dets_cmd + ["\""+file+"\""]
    debug.info(dets_cmd)

    dets_field.append("<b>Items : </b>" + str(len(selected_files)+len(dets_cmd)-2))

    s_t = GetSizeThread(dets_cmd, app)
    s_t.result.connect(lambda x, text_edit=dets_field: set_size(text_edit, x))
    s_t.start()


def set_size(text_edit, size):
    text_edit.append("<b>Size : </b>"+size+"B")


def messages(main_ui, color, msg):
    # main_ui.messages.setStyleSheet("color: %s" %color)
    main_ui.messages.setText(f"{msg}")


# def setStyle(self,ui):
#     light = os.path.join(projDir, "styleSheets", "light.qss")
#     dark = os.path.join(projDir, "styleSheets", "dark.qss")
#     theme = os.environ['FILES_THEME']
#     if theme == "light":
#         theme = light
#         # os.environ['FILES_THEME'] = "light"
#     else:
#         theme = dark
#         # os.environ['FILES_THEME'] = "dark"
#     sS = open(theme, "r")
#     ui.setStyleSheet(sS.read())
#     sS.close()


# def changeTheme(self):
#     light = os.path.join(projDir, "styleSheets", "light.qss")
#     dark = os.path.join(projDir, "styleSheets", "dark.qss")
#
#     theme = os.environ['FILES_THEME']
#     if theme == "light":
#         theme = dark
#         os.environ['FILES_THEME'] = "dark"
#         main_ui.themeButt.setIcon(QtGui.QIcon(self.lightIcon))
#     else:
#         theme = light
#         os.environ['FILES_THEME'] = "light"
#         main_ui.themeButt.setIcon(QtGui.QIcon(self.darkIcon))
#
#     sS = open(theme, "r")
#     main_ui.setStyleSheet(sS.read())
#     sS.close()


def go_home(main_ui):
    open_dir(main_ui, dir_path=homeDir)


def show_video_downloader(mu):
    if not mu.videoDownloaderFrame.isVisible():
        mu.videoDownloaderFrame.show()
    else:
        mu.videoDownloaderFrame.hide()


def audio_restart():
    ar_cmd = "/usr/local/bin/audio-restart"
    debug.info(ar_cmd)
    subprocess.Popen(ar_cmd)


def fix_pen_display():
    pd_cmd = "/proj/standard/share/penDisplay.py"
    debug.info(pd_cmd)
    subprocess.Popen(pd_cmd)


def blender_media_viewer():
    bmv_cmd = "/proj/standard/share/blender-3.0/blender --app-template blender_media_viewer -w"
    debug.info(bmv_cmd)
    subprocess.Popen(shlex.split(bmv_cmd))


def update_download_progress(main_ui, percentage):
    main_ui.downloadProgressBar.setValue(int(percentage))


def after_video_download(main_ui, msg):
    main_ui.downloadProgressBar.hide()
    main_ui.urlBox.setReadOnly(False)
    main_ui.pathBox.setReadOnly(False)
    main_ui.cancelButt.setEnabled(False)
    main_ui.downloadButt.setEnabled(True)
    main_ui.downloadButt.show()
    main_ui.cancelButt.hide()
    messages(main_ui, "green", msg)


def download_video(main_ui):
    link = str(main_ui.urlBox.text().strip())
    down_dir = str(os.path.abspath(os.path.expanduser(main_ui.pathBox.text().strip())))
    path = str(os.path.abspath(os.path.expanduser(main_ui.pathBox.text().strip())))+os.sep+"%(title)s.%(ext)s"
    if link:
        if os.path.exists(down_dir):
            permitted = False
            for x in pastePermittedDirs:
                if x in down_dir:
                    permitted = True
            if permitted:
                main_ui.downloadProgressBar.show()
                main_ui.urlBox.setReadOnly(True)
                main_ui.pathBox.setReadOnly(True)
                main_ui.cancelButt.setEnabled(True)
                main_ui.downloadButt.setEnabled(False)
                main_ui.downloadButt.hide()
                main_ui.cancelButt.show()

                dT = DownloadVideoThread(path,link, app)
                dT.result.connect(lambda d, mu=main_ui: after_video_download(mu, d))
                dT.progress.connect(lambda u, mu=main_ui: update_download_progress(mu, u))
                # dT.finished.connect(lambda x : self.afterVideoDownload(x))
                dT.start()
            else:
                debug.info("No permission to write")
                messages(main_ui, "red", "Not permitted!")
        else:
            debug.info("No such directory")
            messages(main_ui, "red", "Folder does not exists!")
    else:
        debug.info("URL field is empty")
        messages(main_ui, "red", "URL field is empty")


def cancel_video_download(main_ui):
    debug.info(currDownloads)
    for key, value in currDownloads.items():
        try:
            debug.info(key)
            # os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            os.kill(key, signal.SIGTERM)
            subprocess.run("killall aria2c", shell=True)

            # TODO: Remove residuals from cancelled downloads
            debug.info(value)
            down_dir = os.sep.join(value.strip().split(os.sep)[:-1])
            debug.info(down_dir)

            # dirContents = os.listdir(downDir)
            # debug.info(dirContents)
            # for f in dirContents:
            #     if '.part' in f:
            #         debug.info(downDir+os.sep+f)
            #         rmCmd = "rm -frv \"{0}\" ".format(downDir+os.sep+f)
            #         try:
            #             subprocess.Popen(shlex.split(rmCmd))
            #         except:
            #             debug.info(str(sys.exc_info()))
        except:
            debug.info(str(sys.exc_info()))
    after_video_download(main_ui, "Cancelled")


class GenThumbThread(QThread):
    finished = Signal()
    # error = Signal(str)
    result = Signal(str)

    def __init__(self, dir_path, parent=None):
        super().__init__(parent)
        self.dir_path = dir_path
        self.thumbs = thumbs

    def run(self):
        all_files = [f for f in os.listdir(self.dir_path) if os.path.isfile(os.path.join(self.dir_path, f))]
        for f in all_files:
            # debug.info(f)
            if f.startswith("."):
                pass
            else:
                file_abs_path = os.path.join(self.dir_path, f)
                file_extension = os.path.splitext(file_abs_path)[1]
                ext = file_extension.replace(".", "").strip()

                if ext in mimeTypes["video"]:
                    debug.info(file_abs_path)
                    hex_file_path = hashlib.sha256(file_abs_path.encode()).hexdigest()
                    debug.info(hex_file_path)
                    self.thumbs[file_abs_path] = hex_file_path
                    thumb_image = filesThumbsDir + hex_file_path + ".jpeg"
                    if os.path.exists(thumb_image):
                        pass
                    else:
                        try:
                            gen_thumb_cmd = mimeConvertCmds["video"].format(file_abs_path, thumb_image)
                            subprocess.call(shlex.split(gen_thumb_cmd))
                        except:
                            debug.info(str(sys.exc_info()))

                if ext in mimeTypes["image"]:
                    debug.info(file_abs_path)
                    hex_file_path = hashlib.sha256(file_abs_path.encode()).hexdigest()
                    debug.info(hex_file_path)
                    self.thumbs[file_abs_path] = hex_file_path
                    thumb_image = filesThumbsDir + hex_file_path + ".jpeg"
                    if os.path.exists(thumb_image):
                        pass
                    else:
                        try:
                            gen_thumb_cmd = mimeConvertCmds["image"].format(file_abs_path, thumb_image)
                            subprocess.call(shlex.split(gen_thumb_cmd))
                        except:
                            debug.info(str(sys.exc_info()))
                        self.result.emit(thumb_image)

        with open(thumbs_conf_file, 'w') as conf_file:
            json.dump(self.thumbs, conf_file, sort_keys=True, indent=4)
        self.finished.emit()


class RsyncThread(QThread):
    progress_updated = Signal(int)
    finished = Signal()

    def __init__(self, source_path, destination_path, parent=None, remove_source_files=False):
        super().__init__(parent)
        self.source_path = source_path
        self.destination_path = destination_path
        self.remove_source_files = remove_source_files

    @Slot()
    def run(self):
        rsync_command = []
        if self.remove_source_files:
            rsync_command = ["rsync", "--remove-source-files", "-azHXW", "--info=progress2", self.source_path, self.destination_path]
        else:
            rsync_command = ["rsync", "-azHXW", "--info=progress2", self.source_path, self.destination_path]

        debug.info(rsync_command)
        process = Popen(rsync_command, stdout=PIPE, stderr=STDOUT, bufsize=1, universal_newlines=True)

        for line in process.stdout:
            sync_data = (tuple(filter(None, line.strip().split(' '))))
            # print (syn_data)
            if sync_data:
                percent = 0
                try:
                    percent = int(sync_data[1].split("%")[0])
                    # print (percent)
                except ValueError:
                    debug.info(str(sys.exc_info()))
                    percent = 0
                self.progress_updated.emit(percent)

        process.wait()
        self.finished.emit()


class DownloadVideoThread(QThread):
    progress = Signal(int)
    result = Signal(str)
    finished = Signal()

    def __init__(self, path, link, parent=None):
        super().__init__(parent)
        self.path = path
        self.link = link

    @Slot()
    def run(self):
        down_cmd = os.path.join(externalToolsDir, "yt-dlp_linux") + " --external-downloader aria2c " \
                    " --external-downloader-args '--summary-interval 1 --download-result=hide -c -s 10 -x 10 -k 1M' " \
                    "-o \"{0}\" \"{1}\" ".format(self.path, self.link)
        debug.info(down_cmd)
        try:
            # p = subprocess.Popen(shlex.split(downCmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            #                      bufsize=1,universal_newlines=True, preexec_fn=os.setsid)
            # currDownloads.append(p)
            # msg = ""

            p = Popen(split(down_cmd), stdout=PIPE, stderr=PIPE, universal_newlines=True)
            # currDownloads.append(p)
            currDownloads[p.pid] = self.path
            msg = ""
            for line in p.stdout:
                if line:
                    debug.info(line)
                    if "Unable to download webpage" in line:
                        msg = "Unable to download video"
                    elif "already been downloaded" in line:
                        msg = "Already been downloaded"
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
                        sync_data = (tuple(filter(None, line.strip().split('('))))
                        if sync_data:
                            percent = sync_data[1].split("%")[0].strip()
                            self.progress.emit(int(percent))
                    elif "Deleting original file" in line:
                        self.result.emit("Download finished")
                        self.finished.emit()
                        del currDownloads[p.pid]
                    else:
                        msg = "Failed"
            if p.returncode == 0:
                self.result.emit("Download finished")
                self.finished.emit()
            else:
                debug.info(f"Command failed with return code: {p.returncode}")
        except Exception as e:
            debug.info(str(sys.exc_info()))
        else:
            self.result.emit(msg)
        finally:
            self.finished.emit()
            return


class GetSizeThread(QThread):
    finished = Signal()
    result = Signal(str)

    def __init__(self, cmd, parent=None):
        super().__init__(parent)
        self.cmd = cmd

    def run(self):
        # try:
        #     p = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1,
        #                          universal_newlines=True)
        #     out, err = p.communicate()
        #     size = out.split("\t")[-2].split("\n")[1]
        # except :
        #     debug.info(str(sys.exc_info()))
        # else:
        #     self.result.emit(size)
        # finally:
        #     self.finished.emit()
        try:
            process = Popen(shlex.split(" ".join(self.cmd)), stdout=PIPE, stderr=STDOUT, bufsize=1,
                            universal_newlines=True)
            output, _ = process.communicate()

            # Process the output to get the size
            size_line = output.strip().split("\n")[-1]  # Get the last line which contains the total size
            size = size_line.split("\t")[0]  # Assuming the size is the first part of the line

            self.result.emit(size)
        except Exception as e:
            debug.info(f"Error getting size: {e}")
        finally:
            self.finished.emit()


def files_window(main_ui):
    global current_icon_files
    global current_list_files

    # threadpool = QtCore.QThreadPool()

    # self.loader = QUiLoader()
    # file = QFile(main_ui_file)
    # file.open(QFile.ReadOnly)
    # main_ui = main_ui
    # file.close()
    main_ui.setWindowTitle("FILES")
    main_ui.setWindowIcon(QtGui.QIcon(os.path.join(projDir, "imageFiles", "icons", "folder-main.svg")))

    # sS = open(os.path.join(projDir, "styleSheets", "dark.qss"), "r")
    # main_ui.setStyleSheet(sS.read())
    # sS.close()

    with open(style_sheet_path, "r") as sS:
        main_ui.setStyleSheet(sS.read())

    # os.environ['FILES_THEME'] = "dark"

    # currIconFiles = main_ui.iconFiles
    # currListFiles = main_ui.listFiles

    main_ui.currentFolderBox.clear()
    main_ui.currentFolderBox.setText(ROOTDIR)

    # main_ui.treeDirs.sortByColumn(0, QtCore.Qt.AscendingOrder)
    # currListFiles.sortByColumn(0, QtCore.Qt.AscendingOrder)

    root_dir_new = os.path.abspath(main_ui.currentFolderBox.text().strip())
    debug.info(root_dir_new)

    set_dir(main_ui, root_dir_new)

    open_dir(main_ui, dir_path=homeDir)
    init_config()
    load_favourites(main_ui)

    # main_ui.tabWidget.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
    # main_ui.tabWidget.customContextMenuRequested.connect(lambda x, context=main_ui.tabWidget.currentWidget().viewport(): self.popUpTabs(context, x))
    main_ui.tabWidget.customContextMenuRequested.connect(lambda x, mu=main_ui: tabs_popup(mu, x))
    # main_ui.connect(main_ui.tabWidget, SIGNAL('customContextMenuRequested(const QPoint &)'), self.popUpTabs)
    main_ui.tabWidget.currentChanged.connect(lambda x, mu=main_ui: current_tab_changed(mu, x))
    main_ui.tabWidget.tabCloseRequested.connect(lambda x, mu=main_ui: close_current_tab(mu, x))

    main_ui.changeViewButt.setIcon(QtGui.QIcon(icons_icon))
    main_ui.previousDirButt.setIcon(QtGui.QIcon(prev_dir_icon))
    main_ui.changeDirButt.setIcon(QtGui.QIcon(go_icon))
    main_ui.searchButt.setIcon(QtGui.QIcon(search_icon))
    main_ui.homeButt.setIcon(QtGui.QIcon(home_icon))
    main_ui.themeButt.setIcon(QtGui.QIcon(light_icon))

    main_ui.currentFolderBox.findChild(QtWidgets.QToolButton).setIcon(QtGui.QIcon(clear_icon))
    main_ui.searchBox.findChild(QtWidgets.QToolButton).setIcon(QtGui.QIcon(clear_icon))

    # self.changeViewSc = QShortcut(QKeySequence("Ctrl+V"), self)
    # self.changeViewSc.activated.connect(self.change_view)
    QShortcut(QKeySequence("Ctrl+T"), main_ui).activated.connect(lambda x, mainui=main_ui: tab_open_doubleclick(main_ui))
    # QShortcut(QKeySequence("Ctrl+W"),main_ui).activated.connect(lambda curr_tab_index = main_ui.tabWidget.currentIndex() :self.close_current_tab(currTabIndex))
    QShortcut(QKeySequence("Ctrl+F"), main_ui).activated.connect(main_ui.searchBox.setFocus)

    main_ui.changeViewButt.setShortcut(QtGui.QKeySequence("V"))
    main_ui.previousDirButt.setShortcut(QtGui.QKeySequence("Backspace"))
    main_ui.changeDirButt.setShortcut(QtGui.QKeySequence("Return"))

    main_ui.changeViewButt.setToolTip("Change View (V)")
    main_ui.previousDirButt.setToolTip("Previous Directory (Backspace)")
    main_ui.changeDirButt.setToolTip("Change Directory (Enter)")

    # main_ui.themeButt.clicked.connect(self.changeTheme)
    main_ui.homeButt.clicked.connect(lambda x, mu=main_ui: go_home(mu))
    main_ui.searchBox.textChanged.connect(lambda x, mu=main_ui: search(mu))
    main_ui.changeViewButt.clicked.connect(lambda x, mu=main_ui: change_view(mu))
    main_ui.previousDirButt.clicked.connect(lambda x, mu=main_ui: previous_dir(mu))
    main_ui.changeDirButt.clicked.connect(lambda x, mu=main_ui: change_dir(mu))
    main_ui.searchButt.clicked.connect(lambda x, mu=main_ui: search(mu))

    main_ui.videoDownloaderFrame.hide()
    main_ui.videoDownloaderButt.clicked.connect(lambda x, mu=main_ui: show_video_downloader(mu))
    main_ui.audioRestartButt.clicked.connect(lambda x: audio_restart())
    main_ui.fixPenDisplayButt.clicked.connect(lambda x: fix_pen_display())
    main_ui.blenderMediaViewerButt.clicked.connect(lambda x: blender_media_viewer())
    main_ui.downloadButt.clicked.connect(lambda x, mu=main_ui: download_video(mu))
    main_ui.cancelButt.clicked.connect(lambda x, mu=main_ui: cancel_video_download(mu))

    try:
        current_icon_files.customContextMenuRequested.connect(
            lambda x, mu=main_ui, context=current_icon_files.viewport(): files_popup(mu, context, x))
        current_icon_files.doubleClicked.connect(lambda x: open_file())
        current_list_files.customContextMenuRequested.connect(
            lambda x, mu=main_ui, context=current_list_files.viewport(): files_popup(mu, context, x))
        current_list_files.doubleClicked.connect(lambda x: open_file())
    except:
        debug.info(str(sys.exc_info()))

    main_ui.progressBar.hide()
    main_ui.downloadProgressBar.hide()
    main_ui.cancelButt.setEnabled(False)
    main_ui.cancelButt.hide()
    messages(main_ui, "white", "")

    main_ui.splitter01.setSizes([100, 140])
    # main_ui.searchButt.hide()

    try:
        current_list_files.setColumnWidth(0, 660)
        current_icon_files.hide()
    except:
        debug.info(str(sys.exc_info()))

    # main_ui.places_label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
    # main_ui.places_label.setAlignment(QtCore.Qt.AlignCenter)
    # main_ui.places_label.setText("<b>Places</b>")

    # main_ui.tools_label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
    main_ui.tools_label.setAlignment(QtCore.Qt.AlignCenter)
    main_ui.tools_label.setText("<b>Tools</b>")

    # main_ui.search_label.setStyleSheet(''' QLabel { font-size: 20px; } ''')
    # main_ui.search_label.setAlignment(QtCore.Qt.AlignCenter)
    # main_ui.search_label.setText("<b>Search</b>")

    main_ui.searchBox.setFocusPolicy(QtCore.Qt.StrongFocus)
    main_ui.searchBox.setFocus()

    tab_open_doubleclick(main_ui)

    # main_ui.showMaximized()
    # main_ui.update()


if __name__ == '__main__':
    setproctitle.setproctitle("FILES")
    loader = QUiLoader()
    app = QtWidgets.QApplication(sys.argv)
    window = loader.load(main_ui_file, None)
    files_window(window)
    window.showMaximized()
    window.update()
    sys.exit(app.exec())

