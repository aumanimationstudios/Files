#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"

import os
import sys
import argparse

homeDir = os.path.expanduser("~")
configDir = homeDir+os.sep+".config/tray-server"
configFiles = {}
configFiles['mainConfigFile'] = configDir+os.sep+"per-app-framework-default"
configFiles['blenderConfigFile'] = configDir+os.sep+"blender"
configFiles['kritaConfigFile'] = configDir+os.sep+"krita"

device_list = os.popen("xsetwacom --list devices").read()
print(device_list)

if device_list:
    device = device_list.split("id:")

    device_name = " ".join(device[0].strip().split(' ')[:-2])
    print(device_name)

    for conf in configFiles.values():
        try:
            with open(conf, "w") as file:
                file.write("#!/bin/sh" + "\n")
                file.write("/usr/bin/xsetwacom --set '" + device_name + " Pen stylus'" + " MapToOutput HEAD-0 " + "\n")
                file.write("/usr/bin/xsetwacom --set '" + device_name + " Pen eraser'" + " MapToOutput HEAD-0 " + "\n")
                file.write("/usr/bin/xsetwacom --set '" + device_name + " Finger touch'" + " Touch off " + "\n")
            os.chmod(conf, 0o777)
            os.system(conf)
        except:
            print(str(sys.exc_info()))

else:
    print("Please connect a wacom device")
