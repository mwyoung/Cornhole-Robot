#!/bin/bash

for i in *.svg; do
    if [ ! -f "${i%.svg}.png" ]; then
        #convert -units PixelsPerInch "$i" -density 1200 "${i%.svg}.png"
        inkscape "$i" --export-dpi 600 --export-background="#ffffff" \
            --export-area-drawing --export-png="${i%.svg}.png"
    fi
done
