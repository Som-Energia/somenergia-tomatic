#!/bin/bash

# Requires convert from imagemagik and inkscape

convert -density 300 -define icon:auto-resize=256,128,96,64,48,32,16 -background none tomatic/ui/public/tomatic-logo.svg tomatic/ui/public/tomatic-logo.ico
inkscape -C tomatic/ui/public/tomatic-logo.svg --export-filename=tomatic/ui/public/tomatic-logo.png -h 512 -w 512
inkscape -C tomatic/ui/public/tomatic-logo.svg --export-filename=tomatic/ui/public/tomatic-logo-24.png -h 24 -w 24
