pybpgviewer
===========

Simple BPG Image viewer
This script allows to view BPG Images.

_Requirments:_  
[bpgdec](http://bellard.org/bpg/)  
[python 2.7.x](https://www.python.org/)  
[wxPython 3.0.1.x](http://www.wxpython.org/)  

_Note:_ large images will be scaled to fit screen area.  
_Usage:_ python bpgviewer.py input.bpg (Or just run 'python bpgviewer.py' and then use 'Ctrl-O' to open BPG image file).  

_Hot keys:_  
Key  | Action  
----- | ------  
test | test


F1 | help message  
Esc | close
Ctrl-O | open BPG image file
Ctrl-S | save a copy of the opened file as a PNG file
PgUp,Left,Up | view previous file
PgDown,Right,Down | view next file
