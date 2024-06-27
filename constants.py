#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


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
    "image": "/usr/bin/magick \"{0}\" -sample 96x96 \"{1}\"",
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
    "image": "ristretto \"{1}\" ",
    "video": "mpv --screenshot-directory=/tmp/ --input-conf={0} \"{1}\" ",
    "audio": "mpv --lavfi-complex='[aid1]asplit[ao][a]; [a]showcqt=s=1024x512:r=60[vo]' \"{0}\" ",
    "text": "mousepad \"{0}\" ",
    "pdf": "atril \"{0}\" ",
    "pureref" : "pureref \"{0}\" "

    # "image": "pqiv -i -t -l --browse --max-depth=1 \"{1}\" ",
    # "image": "pqiv -i -t --bind-key='<Mouse-Scroll-1> { set_scale_level_relative(1.1) }' --bind-key='<Mouse-Scroll-2> { set_scale_level_relative(0.9) }' \"{1}\" ",
    # "image": "pqiv -i -t --bind-key='<Mouse-Scroll-1> { set_scale_level_relative(1.1); }' \"{1}\" ",

    # "audio": "mpv --lavfi-complex='[aid1] asplit [ao] [v] ; [v] showwaves=mode=line:split_channels=1 [vo]' \"{0}\" ",
    # "audio": "mpv --lavfi-complex='[aid1]asplit[ao][a]; [a]showcqt[vo]' \"{0}\" ",

    # "audio": "mpv --lavfi-complex='[aid1]asplit[ao][a]; [a]avectorscope=m=polar:s=800x400[vo]' \"{0}\" ",
    # "audio": "mpv --lavfi-complex='[aid1]asplit[ao][a]; [a]showspectrum=color=fire:scale=log:orientation=vertical:overlap=1:s=1024x512[vo]' \"{0}\" ",
    # "audio": "mpv --lavfi-complex='-i gradients=n=7:type=circular,format=rgb0' \"{0}\" ",
    # "audio": "mpv --lavfi-complex='-i gradients=n=7:type=circular,format=rgb0' \"{0}\" ",

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
