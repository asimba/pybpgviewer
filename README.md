bpgviewer
===========  
Simple BPG Image viewer  
This program allows you to view BPG Images.  
  
---  
_**If you wish, you may donate some BTC to:**_ 1NLW4Si8E4pSetVfAUEWMUAeC16rYnqFbd  
  
---  

_Dependencies of the source script (viewer only):_  

---  
* [python 3.x.x](https://www.python.org/)  
* [wxPython 4.x.x.x](http://www.wxpython.org/)  
* [Pillow](https://pillow.readthedocs.org/) at Ubuntu/Xubuntu)  
* [Python for Windows Extensions](http://sourceforge.net/projects/pywin32/) (for Windows version only)

---
_Notes:_  
- large images will be scaled to fit screen area  
- basic support for animated images (zooming, rotating and exporting for animated images are not supported)  
- in Ubuntu 18.04 environment you can try [x86 package](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-ubuntu-18.04-i386.deb) / [x86-64 package](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-ubuntu-18.04-amd64.deb).  
- in Ubuntu 20.04 environment you can try [x86-64 package](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-ubuntu-20.04-amd64.deb).  
- in MS Windows (Windows 7/Windows 8.1/Windows 10 32/64) environment you can use [statically linked x86 package](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-win32-portable.7z) / [statically linked x64 package](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-win64-portable.7z) portable version or try the [x86 installer](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-win32-setup.exe) / [x64 installer](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-win64-setup.exe).  
- in macOS 10.15 environment you can try [x86-64 package](https://github.com/asimba/pybpgviewer/releases/download/v1.28/bpgviewer-1.28-macos-10.15.dmg) (Note: no thumbnails generation in Finder).  
- embedded translations: Russian,English  
- thumbnails preview in Nautilus/Thunar (tested Ubuntu/Xubuntu 18.04/20.04 only)  
- thumbnails preview in Dolphin (KDE 5) (tested Kubuntu 18.04/20.04) (don't forget to turn on BPG preview in Dolphin settings after package installation)  
- thumbnails preview in Windows Explorer (for Windows Vista or higher)  
- drag & drop support for files and folders  

_Ubuntu/Xubuntu 18.04/20.04 Notes:_  
* You may need to run "sudo apt-get -f install" after package installation.  

---
_Hot keys (use 'Cmd' key instead of 'Ctrl' in macOS):_  

Key  | Action
----- | ------  
F1 | help message  
Esc | close  
Ctrl-O | open BPG image file  
Ctrl-S | save a copy of the opened file as a PNG file  
Ctrl-C | save a copy of the opened file  
Ctrl-R | rotate 90 degrees clockwise  
Ctrl-L | rotate 90 degrees counterclockwise  
Ctrl-F | toggle full screen mode  
Ctrl-T | toggle 'stay  on  top' mode  
Ctrl-Left,Home | jump to the first image in folder  
Ctrl-Right,End | jump to the last image in folder  
\+ | zoom in (up to 100%)  
\- | zoom out (down to the smallest available size)  
\* | zoom out to fit window area
Left,Up,Right,Down | move over the scaled image  
PgUp,Backspace,A,S | view previous file  
PgDown,Return,D,W | view next file  
Delete | delete current file  
