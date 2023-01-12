#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


import sys
import os
from PyQt5.QtWidgets import QApplication, QFileSystemModel, QListWidgetItem
from PyQt5 import QtCore, uic, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


def iconFiles():
    iconFiles = QtWidgets.QListView()
    iconFiles.setFocusPolicy(Qt.NoFocus)
    iconFiles.setContextMenuPolicy(Qt.CustomContextMenu)
    iconFiles.setDragEnabled(False)
    iconFiles.setDragDropMode(QAbstractItemView.NoDragDrop)
    iconFiles.setDefaultDropAction(Qt.IgnoreAction)
    iconFiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
    iconFiles.setIconSize(QSize(128,128))
    iconFiles.setTextElideMode(Qt.ElideRight)
    # iconFiles.setMovement(QListView.Static)
    iconFiles.setFlow(QListView.LeftToRight)
    iconFiles.setWrapping(True)
    iconFiles.setResizeMode(QListView.Adjust)
    # iconFiles.setLayoutMode(QListView.SinglePass)
    iconFiles.setGridSize(QSize(200,200))
    iconFiles.setViewMode(QListView.IconMode)
    # iconFiles.setModelColumn(0)
    # iconFiles.setUniformItemSizes(False)
    iconFiles.setWordWrap(True)
    return iconFiles


def listFiles():
    listFiles = QtWidgets.QTreeView()
    listFiles.setFocusPolicy(Qt.NoFocus)
    listFiles.setContextMenuPolicy(Qt.CustomContextMenu)
    listFiles.setDragEnabled(False)
    listFiles.setDragDropMode(QAbstractItemView.NoDragDrop)
    listFiles.setDefaultDropAction(Qt.IgnoreAction)
    listFiles.setSelectionMode(QAbstractItemView.ExtendedSelection)
    listFiles.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
    listFiles.setRootIsDecorated(False)
    listFiles.setUniformRowHeights(True)
    listFiles.setItemsExpandable(False)
    listFiles.setSortingEnabled(True)
    # listFiles.setWordWrap(False)
    listFiles.setExpandsOnDoubleClick(False)
    listFiles.sortByColumn(0, Qt.AscendingOrder)
    listFiles.setColumnWidth(0, 400)
    return listFiles
