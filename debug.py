#!/usr/bin/env python2.7
#-*- coding: utf-8 -*-
__author__ = "Shrinidhi Rao"
__license__ = "GPL"
__email__ = "shrinidhi666@gmail.com"

import os

from logging import *
import tempfile

# tempDir = tempfile.gettempdir()
tempDir = "/crap/LOCAL.crap"
user = os.environ['USER']

FORMAT = "%(asctime)s : %(pathname)s : %(funcName)s - %(levelname)s - %(lineno)d - %(message)s"
basicConfig(filename=tempDir + os.sep + "Files_" + user + ".log",filemode='a', format=FORMAT, level=INFO)
