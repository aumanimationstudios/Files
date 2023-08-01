#!/usr/bin/python3
# *-* coding: utf-8 *-*

import sys
import os
import subprocess
import shlex

sourcePath = "/home/sanath.shetty/Downloads/test_Folder/Source_Path/test.mp4"
destPath = "/home/sanath.shetty/Downloads/test_Folder/Source_Path/Dest_Path/"

rsyncCommand = "rsync -azHXW --info=progress2 %s %s" %(sourcePath, destPath)

p = subprocess.Popen(shlex.split(rsyncCommand),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1, universal_newlines=True)
# for line in iter(p.stdout.readline, b''):
for line in p.stdout:
    synData = (tuple(filter(None, line.strip().split(' '))))
    print (synData)
    if synData:
        prctg = synData[1].split("%")[0]
        print (prctg)




# process = subprocess.Popen(rsyncCommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# while True:
#     output = process.stdout.readline().strip()
#     if output:
#         print(output)
#     else:
#         break

# p = subprocess.Popen(shlex.split(rsyncCommand), stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
# p = subprocess.Popen(shlex.split(rsyncCommand),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1, universal_newlines=True)
# for line in p.stdout:
#     if line:
#         print (line)
    # if "%" in line:
    #     synData = (tuple(filter(None, line.strip().split('%'))))
    #     print (synData)
    #     if synData:
    #         prctg = synData[0].split(" ")[1].strip()
    #         print (prctg)
