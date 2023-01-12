#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


mimeTypes = {
    "image":["exr","hdr","jpeg","jpg","png","svg","tiff","tga","EXR","HDR","JPEG","JPG","PNG","SVG","TIFF","TGA"],
    "video":["avi","gif","mkv","mov","mp4","webm","webp","AVI","GIF","MKV","MOV","MP4","WEBM","WEBP"],
    "audio":["aac","flac","mp3","wav","AAC","FLAC","MP3","WAV"],
    "text": ["text","txt","log","TEXT","TXT","LOG"],

    # "text":['txt','py','sh','text','json','conf','yml','log']
    # "blender":[".blend",".blend1",".blend2"],
    # "office":[".ods",".doc",".xls",".xlsx",".txt",".docx"],
    # "krita":[".kra"],
    # "psd":[".psd"],
    # "pdf":[".pdf"],
    # "reel":[".reel"],
    # "pureref":[".pur"],
    # "edl":[".reel"]
}

mimeConvertCmds = {
    "image": "/usr/bin/convert \"{0}\" -sample 96x96 \"{1}\"",
    "video": "/usr/bin/ffmpeg -loglevel panic -i \"{0}\" -vframes 1 -an -vf scale=96:-1 -ss 0.1 -y \"{1}\""

    # "pdf": "/usr/bin/convert \"{0}\"[0] -sample 96x96 -alpha remove \"{1}\"",
    # "video": "/usr/bin/convert \"{0}[1]\" -sample 96x96 \"{1}\"",
    # "office" : "cp "+ os.path.join(base_dir,"etc","icons","libreOffice_logo.png") +" \"{1}\"",
    # "blender": os.path.join(base_dir,"tools","rbhus","blender-thumbnailer.py") +" \"{0}\" \"{1}\"",
    # "krita": os.path.join(base_dir,"tools","rbhus","krita-thumbnailer.py") +" \"{0}\"  \"{1}\"",
    # "pureref": "cp "+ os.path.join(base_dir,"etc","icons","pureref.png") +" \"{1}\""
}

mimeTypesOpenCmds = {
    # "image": "mpv --geometry=1920x1080 --image-display-duration=inf --loop-file=inf --input-conf={0} \"{1}\" ",
    # "image": "pqiv -i -t --bind-key='<Mouse-Scroll-1> { set_scale_level_relative(1.1) }' --bind-key='<Mouse-Scroll-2> { set_scale_level_relative(0.9) }' \"{1}\" ",
    # "image": "pqiv -i -t --bind-key='<Mouse-Scroll-1> { set_scale_level_relative(1.1); }' \"{1}\" ",
    "image": "pqiv -i -t -l --browse --max-depth=1 \"{1}\" ",
    "video": "mpv --screenshot-directory=/tmp/ --input-conf={0} \"{1}\" ",
    "audio": "mpv \"{0}\" ",
    "text": "leafpad \"{0}\" ",
    "pdf": "pdfReader \"{0}\" "

    # "blender": {"linux":["project_assigned_application"]}, # Just enter "project_assigned_application" to open certain kinds of files with project assigned apps.
    # "pdf": {"linux":["system_assigned_application"]}, # Just enter "system_assigned_application" to open certain kinds of files with project assigned apps.
    # "krita": {"linux":["krita"]},
    # "office": {"linux":["libreoffice","gnumeric","abiword"]},
    # "psd": {"linux":["krita"]},
    # "reel": {"linux":["mrViewer"]},
    # "pureref": {"linux":["pureref"]},
    # "edl": {"linux":["mrViewer"]},
}
