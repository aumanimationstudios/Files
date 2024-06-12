#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


from PySide6 import QtCore, QtUiTools, QtGui, QtWidgets
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem, QWidget
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *


def icon_files_widget():
    icon_files = QtWidgets.QListView()
    icon_files.setFocusPolicy(Qt.NoFocus)
    icon_files.setContextMenuPolicy(Qt.CustomContextMenu)
    icon_files.setDragEnabled(False)
    icon_files.setDragDropMode(QAbstractItemView.NoDragDrop)
    icon_files.setDefaultDropAction(Qt.IgnoreAction)
    icon_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
    icon_files.setIconSize(QSize(128,128))
    icon_files.setTextElideMode(Qt.ElideRight)
    # iconFiles.setMovement(QListView.Static)
    icon_files.setFlow(QListView.LeftToRight)
    icon_files.setWrapping(True)
    icon_files.setResizeMode(QListView.Adjust)
    # iconFiles.setLayoutMode(QListView.SinglePass)
    icon_files.setGridSize(QSize(200,200))
    icon_files.setViewMode(QListView.IconMode)
    # iconFiles.setModelColumn(0)
    # iconFiles.setUniformItemSizes(False)
    icon_files.setWordWrap(True)
    return icon_files


def list_files_widget():
    list_files = QtWidgets.QTreeView()
    list_files.setFocusPolicy(Qt.NoFocus)
    list_files.setContextMenuPolicy(Qt.CustomContextMenu)
    list_files.setDragEnabled(False)
    list_files.setDragDropMode(QAbstractItemView.NoDragDrop)
    list_files.setDefaultDropAction(Qt.IgnoreAction)
    list_files.setSelectionMode(QAbstractItemView.ExtendedSelection)
    list_files.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    list_files.setRootIsDecorated(False)
    list_files.setUniformRowHeights(True)
    list_files.setItemsExpandable(False)
    list_files.setSortingEnabled(True)
    # listFiles.setWordWrap(False)
    list_files.setExpandsOnDoubleClick(False)
    list_files.sortByColumn(0, Qt.AscendingOrder)
    list_files.setColumnWidth(0, 400)
    return list_files

