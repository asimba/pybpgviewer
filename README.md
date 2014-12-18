pybpgviewer
===========

Simple BPG Image viewer
This script allows to view BPG Images.

Requirments:  
[bpgdec](http://bellard.org/bpg/)  
[python 2.7.x](https://www.python.org/)  
[wxPython 3.0.1.x](http://www.wxpython.org/)  

Note: large images will be scaled to fit screen area.  
Usage: python bpgviewer.py input.bpg  
Or just run 'python bpgviewer.py' and then use 'Ctrl-O' to open BPG image file.

Hot keys:  
F1 - help message  
Esc - close  
Ctrl-O - open BPG image file  
Ctrl-S - save a copy of the opened file as a PNG file  
PgUp,Left,Up - view previous file  
PgDown,Right,Down - view next file  
