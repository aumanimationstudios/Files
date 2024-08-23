#!/usr/bin/env python
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"

import os

homeDir = os.path.expanduser("~")
bluepixelsDownloadDir = "/opt/home/bluepixels/Downloads"
crapDir = "/blueprod/CRAP/crap"
crapAliasDir = "/crap/crap.server"

icons = {
    "home": "home.svg",
    "dark": "moon.svg",
    "light": "sun.svg",
    "list": "layout-list.svg",
    "icons": "layout-grid.svg",
    "prev_dir": "go-up.svg",
    "go": "rotate-cw.svg",
    "search": "search.svg",
    "clear": "clear.svg",
    "close": "cross-white.svg",
    "add": "plus.svg",
    "remove": "minus.svg",
    "rename": "edit.svg",
    "copy": "copy.svg",
    "cut": "cut.svg",
    "paste": "paste.svg",
    "delete": "delete.svg",
    "new_folder": "new-folder.svg",
    "add_favourites": "add-favourites.svg",
    "details": "info.svg",
    "help": "help.svg",
    "home_g": "home-green.svg",
    "folder": "folder-other.svg",
    "server": "server-green.svg",
    "download": "download-green.svg",
    "temp": "folder-temp-green.svg"
}

dirPermissions = {
    "renamePermittedDirs": [bluepixelsDownloadDir, crapDir, crapAliasDir, homeDir],
    "cutCopyPermittedDirs": [bluepixelsDownloadDir, crapDir, crapAliasDir, homeDir],
    "pastePermittedDirs": [crapDir, crapAliasDir, homeDir],  # REMINDER : Do NOT add bluepixels downloads folder
    "deletePermittedDirs": [bluepixelsDownloadDir, crapDir, crapAliasDir, homeDir],
    "newFolderPermittedDirs": [bluepixelsDownloadDir, crapDir, crapAliasDir, homeDir],
    "prohibitedDirs": ["/blueprod/STOR", "/proj", "/library","/aumbackup"]
}

mimeTypes = {
    "image": ["exr","hdr","jpeg","jpg","png","svg","tiff","tga","EXR","HDR","JPEG","JPG","PNG","SVG","TIFF","TGA","WEBM","WEBP","webm","webp"],
    "video": ["avi","gif","mkv","mov","mp4","AVI","GIF","MKV","MOV","MP4","WEBM","WEBP","webm","webp"],
    "audio": ["aac","flac","mp3","wav","AAC","FLAC","MP3","WAV","m4a","M4A"],
    "text": ["text","txt","log","TEXT","TXT","LOG"],
    "pdf": ["pdf"],
    "pureref": ["pureref","pur"],

    # "blender": ["blend"],
    # "office":[".ods",".doc",".xls",".xlsx",".txt",".docx"],
    # "krita":[".kra"],
    # "psd":[".psd"],
}

mimeConvertCmds = {
    # "image": "/usr/bin/magick \"{0}\" -sample 96x96 \"{1}\"",
    "image": "/usr/bin/ffmpeg -loglevel panic -i \"{0}\" -vf scale=96:-1 -y \"{1}\"",
    "video": "/usr/bin/ffmpeg -loglevel panic -i \"{0}\" -vf scale=96:-1 -y \"{1}\"",
    # "video": "/usr/bin/ffmpeg -loglevel panic -i \"{0}\" -vframes 1 -an -vf scale=96:-1 -ss 0.1 -y \"{1}\""

    # "pdf": "/usr/bin/convert \"{0}\"[0] -sample 96x96 -alpha remove \"{1}\"",
    # "video": "/usr/bin/convert \"{0}[1]\" -sample 96x96 \"{1}\"",
    # "office" : "cp "+ os.path.join(base_dir,"etc","icons","libreOffice_logo.png") +" \"{1}\"",
    # "blender": os.path.join(base_dir,"tools","rbhus","blender-thumbnailer.py") +" \"{0}\" \"{1}\"",
    # "krita": os.path.join(base_dir,"tools","rbhus","krita-thumbnailer.py") +" \"{0}\"  \"{1}\"",
    # "pureref": "cp "+ os.path.join(base_dir,"etc","icons","pureref.png") +" \"{1}\""
}

mimeTypesOpenCmds = {

    # "image": "mpv --geometry=1920x1080 --image-display-duration=inf --loop-file=inf --input-conf={0} \"{1}\" ",
    "image": "ristretto \"{1}\" ",
    "video": "mpv --screenshot-directory=/tmp/ --input-conf={0} \"{1}\" ",
    "audio": "mpv --lavfi-complex='[aid1]asplit[ao][a]; [a]showcqt=s=1024x512:r=60[vo]' \"{0}\" ",
    "text": "mousepad \"{0}\" ",
    "pdf": "atril \"{0}\" ",
    "pureref" : "pureref \"{0}\" "

    # "blender": {"linux":["project_assigned_application"]}, # Just enter "project_assigned_application" to open certain kinds of files with project assigned apps.
    # "pdf": {"linux":["system_assigned_application"]}, # Just enter "system_assigned_application" to open certain kinds of files with project assigned apps.
    # "krita": {"linux":["krita"]},
    # "office": {"linux":["libreoffice","gnumeric","abiword"]},
    # "psd": {"linux":["krita"]},
    # "reel": {"linux":["mrViewer"]},
    # "pureref": {"linux":["pureref"]},
    # "edl": {"linux":["mrViewer"]},
}

mimeTypesOpenWithCmds = {
    "image": {
            "gwenview": "/usr/bin/gwenview \"{0}\" ",
            "ristretto": "/usr/bin/ristretto \"{0}\" ",
            "djv_view": "/usr/local/bin/djv_view \"{0}\" ",
            "djv_view_v2": "/usr/local/bin/djv_view_v2 \"{0}\" "
            },
    "video": {
            "mpv": "/usr/bin/mpv \"{0}\" ",
            "djv_view": "/usr/local/bin/djv_view \"{0}\" ",
            "djv_view_v2": "/usr/local/bin/djv_view_v2 \"{0}\" "
            },
    "audio": {
            "mpv": "/usr/bin/mpv --lavfi-complex='[aid1]asplit[ao][a]; [a]showcqt=s=1024x512:r=60[vo]' \"{0}\" "
            },
    "text": {
            "mousepad": "/usr/bin/mousepad \"{0}\" "
            },
    "pdf": {
            "atril": "/usr/bin/atril \"{0}\" "
            },
    "pureref": {
                "pureref": "/usr/local/bin/pureref \"{0}\" "
                },
}
