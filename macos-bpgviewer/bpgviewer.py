#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Simple BPG Image viewer.

Copyright (c) 2014-2018, Alexey Simbarsky
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
* Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from sys import argv,exit,version_info
from os import listdir,access,R_OK,W_OK,stat,close,remove,mkdir
from os.path import exists,isfile,dirname,basename,realpath,join,abspath,expanduser
from tempfile import mkstemp
from shutil import copyfile,rmtree
from subprocess import call,Popen,PIPE,STDOUT
from math import floor
import StringIO
from struct import unpack
from platform import system
import locale,pickle,base64,zlib
from os import mkfifo,O_RDONLY,O_NONBLOCK
from os import open as osopen
from os import read as osread
from os import close as osclose
import wx
from PIL import Image
from PIL.Image import core as _imaging
from threading import Thread,Lock
import errno
#from Foundation import NSUserDefaults

#postinstall
path=join(expanduser('~'),'Library/Saved Application State/org.asimbarsky.osx.bpgviewer.savedState')
ipath=join(path,'installed')
if exists(path) and not exists(ipath):
    try:
        rmtree(path)
        mkdir(path)
        mkdir(ipath)
    except: pass
    f=Popen(['chmod','-w',path],False,stdin=None,stdout=None,stderr=None)
    f.wait()
    f=Popen(['qlmanage','-r'],False,stdin=None,stdout=None,stderr=None)
    f.wait()
#postinstall

wxapp=False

class translator():
    def __init__(self):
        self.voc={}
        f=Popen('defaults read -g "AppleLanguages"',shell=True,stdin=None,\
                stdout=PIPE,stderr=STDOUT)
        l=f.stdout.readlines()[1].strip().strip('"').replace('-','_')
        f.wait()
        self.locale=(l,'UTF-8')
    def find(self,key):
        if key in self.voc:
            if self.locale[0] in self.voc[key]:
                return self.voc[key][self.locale[0]].encode(self.locale[1])
        return key

t=translator()

t.voc=pickle.loads(zlib.decompress(base64.decodestring("\
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\
v/27oGeB/Ww8MB1koezyydXF8eg/cEBnVw==\
")))

def _(s):
    return t.find(s)

def __(s,codepage):
    if version_info[0]<3:
        if type(s) is unicode: s=s.encode(codepage)
    return s

def errmsgbox(msg):
    try: wx.MessageBox(msg,_('Error!'),wx.OK|wx.ICON_ERROR)
    except: pass
    wx.GetApp().GetTopWindow().Close()


def bpggetcmd():
    binname='bpgdec'
    bpgpath=join(dirname(realpath(argv[0])),binname)
    if not(isfile(bpgpath)):
        msg=_('BPG decoder not found!\n')
        print msg
        errmsgbox(msg)
        exit()
    return bpgpath

class GenBitmap(wx.Panel):
    def __init__(self,parent,ID,bitmap,pos=wx.DefaultPosition,
            size=wx.DefaultSize,style=0):
        if not style & wx.BORDER_MASK: style=style|wx.BORDER_NONE
        wx.Panel.__init__(self,parent,ID,pos,size,style)
        self._bitmap=bitmap
        self._clear=False
        self.SetInitialSize(size)
        self.Bind(wx.EVT_ERASE_BACKGROUND,lambda e: None)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
    def SetBitmap(self,bitmap):
        self._bitmap=bitmap
        self.SetInitialSize((bitmap.GetWidth(),bitmap.GetHeight()))
        self.Refresh()
    def GetBitmap(self): return self._bitmap
    def OnPaint(self, event):
        dc=wx.PaintDC(self)
        if self._clear: dc.Clear()
        if self._bitmap:
            dc.DrawBitmap(self._bitmap,0,0,True)
        self._clear=False

class DecodeThread(Thread):
    def __init__(self,parent,func):
        Thread.__init__(self)
        self.parent=parent
        self.func=func
    def run(self):
        if self.parent.dlock.acquire(False):
            self.func()
            self.parent.dlock.release()

SE_EVT_TYPE=wx.NewEventType()
SE_EVT_BNDR=wx.PyEventBinder(SE_EVT_TYPE,1)
class ShowEvent(wx.PyCommandEvent):
    def __init__(self,etype,eid):
        wx.PyCommandEvent.__init__(self,etype,eid)

class DFrame(wx.Frame):
    def bpgdecode(self,filename,retries=2):
        msg=None
        retries=2
        cmd='"'+self.bpgpath+'" -o '
        if self.img:
            del self.img
            self.img=None
        if len(filename)>4 and filename[-4:].lower()=='.bpg':
            try:
                if not(isfile(filename) and access(filename,R_OK)):
                    msg=_('Unable to open')+'\"%s\"!'%filename
            except: return False
            if not(msg):
                err=0
                try:
                    imbuffer=''
                    fifo=osopen(self.fifo,O_RDONLY|O_NONBLOCK)
                    cmd+=self.fifo+' "'+realpath(filename)+'"'+\
                        ' >/dev/null 2>&1'
                    f=Popen(cmd,shell=True,stdin=None,stdout=None,\
                        stderr=None)
                    if fifo:
                        while True:
                            if f.poll()!=None: break;
                            try: data=osread(fifo,16777216)
                            except OSError as e:
                                if e.errno==errno.EAGAIN or\
                                    e.errno==errno.EWOULDBLOCK: data=''
                                else: raise
                            if len(data): imbuffer+=data
                        osclose(fifo)
                    if len(imbuffer):
                        if imbuffer[0]=='a': mode='RGBA'
                        else: mode='RGB'
                        x,=unpack("i",imbuffer[1:5])
                        y,=unpack("i",imbuffer[5:9])
                        try: self.img=Image.frombytes(mode,(x,y),imbuffer[9:])
                        except:
                            if retries:
                                retries-=1
                                self.bpgdecode(filename,retries-1)
                            else: err=1
                        del imbuffer
                    else: err=1
                except: err=1
                if err: msg=_('BPG decoding error!\n')
        else: msg=_('File')+' \"%s\" '%filename+_('is not a BPG-File!')
        if msg and retries==2:
            print msg
            errmsgbox(msg)
            if self.img:
                del self.img
                self.img=None
        else: return True
        return False
    def stitle(self,title):
        self.Title=title
        self.Update()
    def deftitle(self):
        self.stitle(_('Press ⌘O to open BPG file...'))
    def getcsize(self):
        cr=wx.Display().GetClientArea()
        cw=self.GetSize()
        cc=self.GetClientSize()
        return cr[2]-cr[0]-cw[0]+cc[0],cr[3]-cr[1]-cw[1]+cc[1]
    def bitmapfrompil(self,img):
        if img.mode[-1]=='A':
            return wx.Bitmap.FromBufferRGBA(img.size[0],\
                img.size[1], img.convert("RGBA").tobytes())
        else:
            return wx.Bitmap.FromBuffer(img.size[0],img.size[1],\
                img.convert("RGB").tobytes())
    def scalebitmap(self,width,height):
        if self.img:
            return self.bitmapfrompil(self.img.resize((int(width),\
                int(height)),Image.ANTIALIAS))
        else: return None
    def showbitmap(self,bitmap):
        self.bitmap._clear=True
        if bitmap==None: self.showempty()
        else:
            self.bitmap.SetBitmap(bitmap)
            self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
            self.bitmap.SetToolTip(self.imginfo)
            x,y=bitmap.GetSize()
            self.panel.SetVirtualSize((x,y))
            self.panel.SetScrollbars(1,1,x,y)
            self.panel.SetScrollRate(1,1)
            cx,cy=self.getcsize()
            if not(self.IsMaximized()) and not(self.IsFullScreen()) and\
                x<=cx and y<=cy:
                self.panel.SetInitialSize(size=(x,y))
                self.panel.SetClientSize((x,y))
                self.Layout()
                self.Fit()
                self.Center()
            else: self.Layout()
    def emptybitmap(self):
        buffer=wx.Bitmap(400,300)
        dc=wx.BufferedDC(None,buffer)
        dc.SetBackground(wx.Brush(self.panel.GetBackgroundColour()))
        dc.Clear()
        dc.Destroy()
        return buffer
    def showempty(self):
        if self.img:
            try: del self.img
            except: pass
            self.img=None
            self.showbitmap(self.emptybitmap())
        self.imginfo=''
    def autoscaled(self):
        if self.img:
            if self.IsFullScreen(): cx,cy=wx.DisplaySize()
            else:
                if self.IsMaximized() or self.max: cx,cy=self.GetClientSize()
                else: cx,cy=self.getcsize()
            d=0.0
            x=self.img.size[0]
            y=self.img.size[1]
            self.bitmap_text=str(x)+'x'+str(y)
            d0=float(cx)/float(x)
            d1=float(cy)/float(y)
            if d0<1.0 or d1<1.0:
                d=d0 if d0<d1 else d1
                x=floor(x*d)
                y=floor(y*d)
                self.scale=d*100.0
                self.autoscale=self.scale
                return self.scalebitmap(x,y)
            else:
                self.scale=100.0
                self.autoscale=self.scale
                return self.bitmapfrompil(self.img)
        return None
    def _showimage(self,filename):
        filename=__(filename,self.codepage)
        if len(filename) and self.bpgdecode(filename):
            if len(self.filelist)==0:
                self.filelist=self.getfilelist(dirname(realpath(filename)))
                self.index=0
                while(True):
                    if self.filelist[self.index]==realpath(filename): break
                    else: self.index+=1
                    if self.index>=len(self.filelist): break
        wx.PostEvent(self,ShowEvent(SE_EVT_TYPE,-1))
    def _evt_showimage(self,evt):
        self.showbitmap(self.autoscaled())
        if len(self.imginfo): self.stitle(self.filelist[self.index]+\
            ' ('+self.imginfo+')')
        else: self.deftitle()
    def showimage(self,filename):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        self.dthread=DecodeThread(self,lambda: self._showimage(filename))
        self.dthread.start()
    def getfilelist(self,dirname):
        filelist=[]
        for f in sorted(listdir(dirname)):
            fname=realpath(join(dirname,f))
            try:
                if access(fname,R_OK) and isfile(fname) and\
                    fname[-4:].lower()=='.bpg':
                    if type(fname) is unicode:
                        fname=fname.encode(self.codepage)
                    filelist.append(fname)
            except: pass
        return filelist
    def __init__(self,parent,title):
        kwds={}
        args=[]
        kwds["style"]=wx.DEFAULT_FRAME_STYLE
        kwds["title"]=title
        kwds["parent"]=parent
        wx.Frame.__init__(self,*args,**kwds)
        self.max=False
        self.codepage=locale.getdefaultlocale()[1]
        self.bpgpath=bpggetcmd()
        self.scale=100.0
        self.autoscale=100.0
        self.bitmap_text=''
        self.img=None
        self.imginfo=''
        self.fifo=''
        self.mpos=None
        self.dlock=Lock()
        t,self.fifo=mkstemp(suffix='.rgb',prefix='')
        close(t)
        remove(self.fifo)
        try: mkfifo(self.fifo,0o766)
        except:
            msg=_('Unable to create FIFO file!')
            print msg
            errmsgbox(msg)
            exit()
        self.filelist=[]
        self.index=0
        self.SetDoubleBuffered(True)
        self.SetInitialSize(size=(400,300))
        self.panel=wx.ScrolledWindow(self,-1,style=wx.WANTS_CHARS)
        self.psizer=wx.FlexGridSizer(1,1,0,0)
        self.psizer.AddGrowableCol(0)
        self.psizer.AddGrowableRow(0)
        self.bitmap=GenBitmap(self.panel,-1,style=wx.WANTS_CHARS,
            bitmap=self.emptybitmap())
        self.psizer.Add(self.bitmap,1,wx.ALIGN_CENTER,0)
        self.panel.SetSizer(self.psizer)
        self.sizer=wx.FlexGridSizer(1,1,0,0)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
        self.sizer.Add(self.panel,1,wx.ALIGN_CENTER,0)
        self.SetSizer(self.sizer)
        self.showimage(title)
        self.bitmap.Bind(wx.EVT_KEY_DOWN,self.keydown)
        self.bitmap.Bind(wx.EVT_CHAR,self.keychar)
        self.bitmap.Bind(wx.EVT_TEXT_ENTER,self.keychar)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.bitmap.Bind(wx.EVT_MOTION,self.drag)
        self.bitmap.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.Bind(wx.EVT_SIZE,self.fresize)
        self.Bind(wx.EVT_ERASE_BACKGROUND,lambda e: None)
        self.Bind(SE_EVT_BNDR,self._evt_showimage)
        self.Layout()
        self.Center()
        self.panel.SetFocus()
    def loadindex(self,old):
        if self.index!=old:
            self.stitle(_('Loading...'))
            self.showimage(self.filelist[self.index])
    def previous(self):
        if len(self.filelist):
            old=self.index
            if self.index: self.index-=1
            else: self.index=len(self.filelist)-1
            self.loadindex(old)
    def next(self):
        if len(self.filelist):
            old=self.index
            if self.index<len(self.filelist)-1: self.index+=1
            else: self.index=0
            self.loadindex(old)
    def drag(self,event):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        if self.img:
            if event.Dragging():
                pos=event.GetPosition()
                if self.mpos!=None:
                    px,py=self.panel.GetScrollPixelsPerUnit()
                    dx=self.mpos[0]-pos[0]
                    dy=self.mpos[1]-pos[1]
                    self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)+\
                        dx/px,self.panel.GetScrollPos(wx.VERTICAL)+dy/py)
                return
            if event.LeftDown():
                self.mpos=event.GetPosition()
                return
            if event.LeftUp():
                self.mpos=None
                return
        if event.ButtonDClick():
            self.mpos=None
            self.maximize()
    def rotate(self,dir):
        if self.img:
            self.stitle(_('Rotating...'))
            if dir: self.img=self.img.rotate(-90,expand=1)
            else: self.img=self.img.rotate(90,expand=1)
            if self.img:
                if self.scale!=100.0:
                    x=self.img.size[0]*(self.scale/100.0)
                    y=self.img.size[1]*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else:
                    if self.img.mode[-1]=='A':
                        self.showbitmap(wx.Bitmap.FromBufferRGBA(self.img.size[0],\
                             self.img.size[1],self.img.convert("RGBA").tobytes()))
                    else:
                        self.showbitmap(wx.Bitmap.FromBuffer(self.img.size[0],\
                            self.img.size[1],self.img.convert("RGB").tobytes()))
            if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                ' ('+self.imginfo+')')
    def fresize(self,event):
        x,y=self.GetClientSize()
        self.panel.SetInitialSize(size=(x,y))
        self.panel.SetClientSize((x,y))
        if not(self.IsFullScreen()):
            fx,fy=self.GetSize()
            cr=wx.Display().GetClientArea()
            cx=cr[2]-cr[0]
            cy=cr[3]-cr[1]
            if fx==cx and fy==cy or self.IsMaximized():
                self.max=True
                self.autoimg()
            else: self.max=False
        self.Layout()
    def autoimg(self):
        if self.scale==self.autoscale:
            self.showbitmap(self.autoscaled())
            if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                ' ('+self.imginfo+')')
            else: self.deftitle()
    def maximize(self):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        if not(self.IsFullScreen()):
            if self.IsMaximized() or self.max:
                self.max=False
                self.Maximize(False)
            else:
                self.max=True
                self.Maximize()
    def keydown(self,event):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        keycode=event.GetKeyCode()
        if keycode==wx.WXK_ESCAPE:
            self.Close()
            return
        if keycode in [wx.WXK_PAGEUP,wx.WXK_NUMPAD_PAGEUP,wx.WXK_BACK]:
            self.previous()
            return
        if keycode in [wx.WXK_PAGEDOWN,wx.WXK_NUMPAD_PAGEDOWN,wx.WXK_RETURN]:
            self.next()
            return
        if keycode in [wx.WXK_LEFT,wx.WXK_NUMPAD_LEFT]:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)-5,\
                self.panel.GetScrollPos(wx.VERTICAL))
            return
        if keycode in [wx.WXK_RIGHT,wx.WXK_NUMPAD_RIGHT]:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)+5,\
                self.panel.GetScrollPos(wx.VERTICAL))
            return
        if keycode in [wx.WXK_UP,wx.WXK_NUMPAD_UP]:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL),\
                self.panel.GetScrollPos(wx.VERTICAL)-5)
            return
        if keycode in [wx.WXK_DOWN,wx.WXK_NUMPAD_DOWN]:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL),\
                self.panel.GetScrollPos(wx.VERTICAL)+5)
            return
        if keycode==wx.WXK_F1:
            wx.MessageBox(_('This is BPG image file viewer. Hot keys:\n')+\
            _('Esc - close\n')+\
            _('⌘O - open BPG image file\n')+\
            _('⌘S - save a copy of the opened file as a PNG file\n')+\
            _('⌘C - save a copy of the opened file\n')+\
            _('⌘R - rotate 90 degrees clockwise\n')+\
            _('⌘L - rotate 90 degrees counterclockwise\n')+\
            _('⌘F - toggle full screen mode\n')+\
            _('+ - zoom in (up to 100%)\n')+\
            _('- - zoom out (down to the smallest available size)\n')+\
            _('* - zoom out to fit window area\n')+\
            _('Left,Up,Right,Down - move over the scaled image\n')+\
            _('PgUp,Backspace,A,S - view previous file\n')+\
            _('PgDown,Return,D,W - view next file\n')+\
            _('Delete - delete current file\n'),_('Help'),\
            wx.OK|wx.ICON_INFORMATION)
            return
        if keycode in [wx.WXK_DELETE,wx.WXK_NUMPAD_DELETE]:
            if len(self.filelist) and self.img:
                if wx.MessageBox(_('Delete file')+' "'+\
                    self.filelist[self.index]+'"?',_('File deletion!'),\
                    wx.YES_NO|wx.ICON_WARNING|wx.NO_DEFAULT)==wx.YES:
                    index=self.index
                    try: remove(self.filelist[index])
                    except:
                        msg=_('Unable to delete:')+\
                            ' \"%s\"!'%self.filelist[self.index]
                        errmsgbox(msg)
                        return
                    self.filelist.pop(index)
                    if len(self.filelist):
                        if index>=len(self.filelist): self.index=0
                        self.loadindex(None)
                    else:
                        self.showempty()
                        self.deftitle()
            return
        event.Skip()
    def keychar(self,event):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        keycode=event.GetKeyCode()
        if event.CmdDown():
            if keycode in [ord('O'),ord('o')]: keycode=15
            if keycode in [ord('S'),ord('s')]: keycode=19
            if keycode in [ord('C'),ord('c')]: keycode=3
            if keycode in [ord('R'),ord('r')]: keycode=18
            if keycode in [ord('L'),ord('l')]: keycode=12
            if keycode in [ord('F'),ord('f')]: keycode=6
        else:
            if keycode==15: keycode=0
        co_code=15
        cs_code=19
        cc_code=3
        cr_code=18
        cl_code=12
        rt_code=370
        cf_code=6
        if keycode==cf_code:
            if self.IsFullScreen():
                self.ShowFullScreen(False,style=wx.DEFAULT_FRAME_STYLE)
            else:
                self.ShowFullScreen(True,style=wx.FULLSCREEN_ALL)
                self.autoimg()
            return
        if keycode in [rt_code,ord('D'),ord('W'),ord('d'),ord('w')]:
            self.next()
            return
        if keycode in [ord('A'),ord('S'),ord('a'),ord('s')]:
            self.previous()
            return
        if keycode==co_code:
            openFileDialog=wx.FileDialog(self,_('Open BPG file'),"","",\
                _("BPG files")+" (*.bpg)|*.bpg",\
                wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
            status=openFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                self.stitle(_('Loading...'))
                self.filelist=[]
                self.showimage(openFileDialog.GetPath())
                openFileDialog.Destroy()
            return
        if keycode==cs_code and self.img:
            saveFileDialog=wx.FileDialog(self,_("Save BPG file as PNG file"),\
                "",basename(self.filelist[self.index])[:-4]+'.png',\
                _("PNG files")+" (*.png)|*.png",\
                wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
            status=saveFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                dst=saveFileDialog.GetPath()
                if type(dst) is unicode: dst=dst.encode(self.codepage)
                if dst[-4:].lower()!='.png': dst+='.png'
                ttitle=self.Title
                self.stitle(_('Saving PNG file...'))
                try:
                    if exists(dst): remove(dst)
                    self.img.save(dst,'PNG',optimize=True)
                except: errmsgbox(_('Unable to save')+' \"%s\"!'%dst)
                self.stitle(ttitle)
                return
        if keycode==cc_code and self.img:
            saveFileDialog=wx.FileDialog(self,_("Save a copy..."),"",\
                basename(self.filelist[self.index])[:-4],\
                _("BPG files")+" (*.bpg)|*.bpg",\
                wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
            status=saveFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                dst=saveFileDialog.GetPath()
                try:
                    if type(dst) is unicode: dst=dst.encode(self.codepage)
                    if exists(dst) and\
                        abspath(self.filelist[self.index])!=dst: remove(dst)
                    copyfile(self.filelist[self.index],dst)
                except: errmsgbox(_('Unable to save')+' \"%s\"!'%dst)
                return
        if keycode in [ord('+'),ord('=')]:
            if self.img and self.scale<100.0:
                self.stitle(_('Zooming in...'))
                self.scale+=5.0
                if self.scale>100.0: self.scale=100.0
                if self.scale!=100.0:
                    x=self.img.size[0]*(self.scale/100.0)
                    y=self.img.size[1]*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else:
                    if self.img.mode[-1]=='A':
                        self.showbitmap(wx.BitmapFromBufferRGBA(self.img.size[0],\
                            self.img.size[1],self.img.convert("RGBA").tobytes()))
                    else:
                        self.showbitmap(wx.BitmapFromBuffer(self.img.size[0],\
                            self.img.size[1],self.img.convert("RGB").tobytes()))
                if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                    ' ('+self.imginfo+')')
                else: self.deftitle()
            return
        if keycode==ord('-'):
            if self.img and self.scale>self.autoscale:
                self.stitle(_('Zooming out...'))
                self.scale-=5.0
                if self.scale<self.autoscale: self.scale=self.autoscale
                if self.scale!=100.0:
                    x=self.img.size[0]*(self.scale/100.0)
                    y=self.img.size[1]*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else:
                    if self.img.mode[-1]=='A':
                        self.showbitmap(wx.BitmapFromBufferRGBA(self.img.size[0],\
                            self.img.size[1],self.img.convert("RGBA").tobytes()))
                    else:
                        self.showbitmap(wx.BitmapFromBuffer(self.img.size[0],\
                            self.img.size[1],self.img.convert("RGB").tobytes()))
                if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                    ' ('+self.imginfo+')')
                else: self.deftitle()
            return
        if keycode in [ord('*'),ord('8')]:
            if self.img:
                cx,cy=self.GetClientSize()
                x,y=self.bitmap.GetSize()
                if cx<x or cy<y:
                    x=self.img.size[0]
                    y=self.img.size[1]
                    d0=float(cx)/float(x)
                    d1=float(cy)/float(y)
                    self.scale=d0 if d0<d1 else d1
                    x=floor(x*self.scale)
                    y=floor(y*self.scale)
                    self.scale*=100.0
                    self.autoscale=self.scale
                    self.showbitmap(self.scalebitmap(x,y))
                    if len(self.imginfo):
                        self.stitle(self.filelist[self.index]+\
                        ' ('+self.imginfo+')')
                    else: self.deftitle()
            return
        if keycode==cr_code:
            self.rotate(True)
            return
        if keycode==cl_code:
            self.rotate(False)
            return
        event.Skip()
    def __del__(self):
        if exists(self.fifo):
            try: remove(self.fifo)
            except: pass

class bpgframe(wx.App):
    def BringWindowToFront(self):
        try:
            self.GetTopWindow().Raise()
        except:
            pass
    def OnActivate(self, event):
        if event.GetActive():
            self.BringWindowToFront()
        event.Skip()
    def MacReopenApp(self):
        self.BringWindowToFront()
    def __init__(self,parent,filename):
        super(bpgframe,self).__init__(parent)
        frame=DFrame(None,filename)
        self.SetTopWindow(frame)
        self.SetExitOnFrameDelete(True)
        self.Bind(wx.EVT_ACTIVATE_APP,self.OnActivate)
        wx.CallAfter(frame.Show)
        wx.CallAfter(frame.Raise)

if __name__=='__main__':
    wxapp=True
    if len(argv)==1: app=bpgframe(None,'')
    else: app=bpgframe(None,realpath(argv[1]))
    app.MainLoop()
