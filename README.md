bpgviewer
===========  
Simple BPG Image viewer  
This program allows you to view BPG Images.  

_Dependencies of the source script (viewer only):_  

---  
* patched version of [bpgdec](http://bellard.org/bpg/) (diff file supplied)  
* [python 2.7.x](https://www.python.org/)  
* [wxPython 3.0.x.x](http://www.wxpython.org/)  
* [Python Imaging Library (PIL) 1.1.7](http://www.pythonware.com/products/pil/)  
* [Python for Windows Extensions](http://sourceforge.net/projects/pywin32/) (for Windows version only)

---
_Notes:_  
* large images will be scaled to fit screen area  
* embedded translations: Russian,English  
* thumbnails preview in Nautilus/Thunar (Ubuntu/Xubuntu 12.04/14.04 only)  
* thumbnails preview in Dolphin (KDE 4) (Kubuntu 14.04) (don't forget to turn on BPG preview in Dolphin settings after package installation)  
* thumbnails preview in Windows Explorer (for Windows Vista or higher)  

_Linux Mint "Rafaella" (Mate) Notes:_
* To enable image thumbnail preview in Thunar you must install additionally thumbler (D-Bus thumbnailing service) and restart Thunar.  
* To enable image thumbnail preview in Dolphin:  
  a) install following packages: kfind, baloo, kdebase-apps, kde-runtime  
  b) in Dolphin go to Control->General->Previews and enable "BPG image files" then press "Ok"  

---
_Usage:_ python bpgviewer.py input.bpg (Or just run 'python bpgviewer.py' and then use 'Ctrl-O' to open BPG image file). 

---  
In Ubuntu environment you can try [debian package for x86](https://github.com/asimba/pybpgviewer/releases/download/v1.21/bpgviewer_1.21-ubuntu_i386.deb) or [debian package for x86-64](https://github.com/asimba/pybpgviewer/releases/download/v1.21/bpgviewer_1.21-ubuntu_amd64.deb) (prebuilt plugins for the file browsers are included).  

---  
In MS Windows (Windows XP/Windows 7/Windows 8.1/Windows 10 32/64) environment you can use [statically linked](https://github.com/asimba/pybpgviewer/releases/download/v1.21/bpgviewer-1.21-win32-portable.7z) (by [cx_Freeze](http://cx-freeze.sourceforge.net/)) portable version or try the [installer](https://github.com/asimba/pybpgviewer/releases/download/v1.21/bpgviewer-1.21-setup.zip).  

---
_Hot keys:_  

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
+ | zoom in (up to 100%)  
- | zoom out (down to the smallest available size)  
* | zoom out to fit window area
Left,Up,Right,Down | move over the scaled image  
PgUp,Backspace,A,S | view previous file  
PgDown,Return,D,W | view next file  
Delete | delete current file  
