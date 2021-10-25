#!/usr/bin/python2
# *-* coding: utf-8 *-*
__author__ = "Sanath Shetty K"
__license__ = "GPL"
__email__ = "sanathshetty111@gmail.com"


import vignette

thumb_image = vignette.create_thumbnail('/home/sanath.shetty/Downloads/cp.jpeg',128)
# thumb_image = vignette.try_get_thumbnail('/home/sanath.shetty/Downloads/cp.jpeg',128)

print (thumb_image)
