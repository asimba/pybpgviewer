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
from os.path import exists,isfile,isdir,dirname,basename,realpath,join,\
    abspath,expanduser
from tempfile import mkstemp
from shutil import copyfile,rmtree
from subprocess import call,Popen,PIPE,STDOUT
from math import floor
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

#postinstall
path=join(expanduser('~'),\
    'Library/Saved Application State/org.asimbarsky.osx.bpgviewer.savedState')
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
        l=str(f.stdout.readlines()[1]).strip().strip('"').replace('-','_').replace('"','').replace('','')
        f.wait()
        self.locale=(l,'UTF-8')
    def find(self,key):
        try: wxu=True if wx.VERSION[0]>3 else False
        except: wxu=False
        if key in self.voc:
            if self.locale[0] in self.voc[key]:
                if wxu: return self.voc[key][self.locale[0]]
                else:
                    return self.voc[key][self.locale[0]].encode(\
                        self.locale[1])
        return key

t=translator()

def add(tr,key,language,translation):
    if key in tr.voc:
        tr.voc[key][language]=translation
    else:
        tr.voc[key]={language:translation}

def load(tr,data):
    if type(data)==tuple and len(data):
        for l in data:
            if type(l)==tuple and len(l)==3:
                add(tr,l[0],l[1],l[2])
            else:
                return

load(t,(\
    ("Please install","ru_RU","Пожалуйста, установите"),\
    ("or higher","ru_RU","или новее"),\
    ("Under Debian or Ubuntu you may try","ru_RU",
        "В Debian или Ubuntu Вы можете попробовать следующую команду"),\
    ("BPG decoder not found!\n","ru_RU","BPG декодер не найден!\n"),\
    ("BPG decoding error!\n","ru_RU","Ошибка при декодировании файла!\n"),\
    ("Unable to open ","ru_RU","Невозможно открыть файл "),\
    ("File","ru_RU","Файл"),("is not a BPG-File!","ru_RU",
        "не является файлом в формате BPG!"),\
    ("Press ⌘O to open BPG file...","ru_RU",
        "Нажмите ⌘O, чтобы открыть файл BPG..."),\
    ("Unable to create FIFO file!","ru_RU","Невозможно создать файл FIFO!"),\
    ("Loading...","ru_RU","Загрузка..."),\
    ("Rotating...","ru_RU","Поворот..."),\
    ("This is BPG image file viewer. Hot keys:\n","ru_RU",
        "Просмотр изображений в формате BPG. Клавиатурные сочетания:\n"),\
    ("Esc - close\n","ru_RU","Esc - выход\n"),\
    ("⌘O - open BPG image file\n","ru_RU","⌘O - открыть файл\n"),\
    ("⌘S - save a copy of the opened file as a PNG file\n","ru_RU",
        "⌘S - сохранить копию изображения в формате PNG\n"),\
    ("⌘C - save a copy of the opened file\n","ru_RU",
        "⌘C - сохранить копию исходного файла\n"),\
    ("⌘R - rotate 90 degrees clockwise\n","ru_RU",
        "⌘R - поворот на 90 градусов по часовой стрелке\n"),\
    ("⌘L - rotate 90 degrees counterclockwise\n","ru_RU",
        "⌘L - поворот на 90 градусов против часовой стрелки\n"),\
    ("⌘F - toggle full screen mode\n","ru_RU",
        "⌘F - включить/выключить полноэкранный режим\n"),\
    ("⌘T - toggle 'stay on top' mode\n","ru_RU",
        "⌘T - включить/выключить режим 'поверх остальных'\n"),\
    ("⌘Left,Home - jump to the first image in folder\n","ru_RU",
        "⌘Left,Home - перейти к первому изображению в папке\n"),\
    ("⌘Right,End - jump to the last image in folder\n","ru_RU",
        "⌘Right,End - перейти к последнему изображению в папке\n"),\
    ("+ - zoom in (up to 100%)\n","ru_RU",
        "+ - увеличить (не более чем до 100%)\n"),\
    ("- - zoom out (down to the smallest available size)\n","ru_RU",
        "- - уменьшить (до минимального доступного размера)\n"),\
    ("* - zoom out to fit window area\n","ru_RU",
        "* - уменьшить до размеров по умолчанию\n"),\
    ("Left,Up,Right,Down - move over the scaled image\n","ru_RU",
        "Left,Up,Right,Down - перемещение увеличенного изображения в окне просмотра\n"),\
    ("PgUp,Backspace,A,S - view previous file\n","ru_RU",
        "PgUp,Backspace,A,S - перейти к предыдущему файлу в директории\n"),\
    ("PgDown,Return,D,W - view next file\n","ru_RU",
        "PgDown,Return,D,W - перейти к следующему файлу в директории\n"),\
    ("Delete - delete current file\n","ru_RU",
        "Delete - удалить текущий файл\n"),\
    ("Help","ru_RU","Помощь"),\
    ("Delete file","ru_RU","Удалить файл"),\
    ("File deletion!","ru_RU","Удаление файла"),\
    ("Unable to delete:","ru_RU","Невозможно удалить:"),\
    ("Open BPG file","ru_RU","Открыть файл BPG"),\
    ("BPG files","ru_RU","Файлы BPG"),\
    ("Save BPG file as PNG file","ru_RU",
        "Сохранить копию изображения в формате PNG"),\
    ("PNG files","ru_RU","Файлы PNG"),\
    ("Saving PNG file...","ru_RU","Сохранение копии файла (PNG)..."),\
    ("Unable to save","ru_RU","Невозможно сохранить файл"),\
    ("Save a copy...","ru_RU","Сохранение копии файла..."),\
    ("Zooming in...","ru_RU","Увеличение..."),\
    ("Zooming out...","ru_RU","Уменьшение..."),
    ("Error!","ru_RU","Ошибка!"),\
))

def _(s):
    return t.find(s)

def __(s,codepage):
    if version_info[0]<3:
        if type(s) is unicode: s=s.encode(codepage)
    return s

def errmsgbox(msg):
    print(msg)
    try: wx.MessageBox(msg,_('Error!'),wx.OK|wx.ICON_ERROR)
    except: pass

def bpggetcmd():
    binname='bpgdec'
    bpgpath=join(dirname(realpath(argv[0])),binname)
    if not(isfile(bpgpath)):
        msg=_('BPG decoder not found!\n')
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
    def OnPaint(self,event):
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
    def __init__(self,etype,eid,value=None):
        wx.PyCommandEvent.__init__(self,etype,eid)
        self.value=value

class FileDropTarget(wx.FileDropTarget):
    def __init__(self,obj):
        wx.FileDropTarget.__init__(self)
        self.obj=obj
    def OnDropFiles(self,x,y,filenames):
        self.obj.showempty()
        self.obj.index=0
        self.obj.filelist=[]
        self.obj.showimage(self.obj.checkpath(filenames[0]))
        return True

class DFrame(wx.Frame):
    def bpgdecode(self,filename):
        msg=None
        cmd='"'+self.bpgpath+'"'
        self.frames_index=0
        if len(self.frames): self.frames=[]
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
                    if version_info[0]<3: imbuffer=''
                    else: imbuffer=b''
                    t,tmp=mkstemp(suffix='.rgb',prefix='')
                    close(t)
                    cmd+=' "'+realpath(filename)+'" '+tmp+' >/dev/null 2>&1'
                    f=Popen(cmd,shell=True,stdin=None,stdout=None,stderr=None)
                    f.wait()
                    fifo=osopen(tmp,O_RDONLY|O_NONBLOCK)
                    if fifo:
                        while True:
                            try: data=osread(fifo,16777216)
                            except OSError as e:
                                if e.errno==errno.EAGAIN or\
                                    e.errno==errno.EWOULDBLOCK:
                                        data=''
                                        continue
                                else: raise
                            if len(data): imbuffer+=data
                            else: break
                        osclose(fifo)
                    if exists(tmp):
                        try: remove(tmp)
                        except: pass
                    if len(imbuffer):
                        x,=unpack("i",imbuffer[0:4])
                        y,=unpack("i",imbuffer[4:8])
                        n,=unpack("i",imbuffer[8:12])
                        d,=unpack("i",imbuffer[12:16])
                        if n==0 and d==1:
                            try:
                                self.img=Image.frombytes('RGBA',(x,y),
                                    imbuffer[16:])
                            except: err=1
                        else:
                            self.scale=100.0
                            self.autoscale=self.scale
                            self.bitmap_text=str(x)+'x'+str(y)
                            self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
                            ishift=8
                            dr=n*1000/d
                            while True:
                                try:
                                    n,=unpack("i",imbuffer[ishift:ishift+4])
                                    ishift+=4
                                    d,=unpack("i",imbuffer[ishift:ishift+4])
                                    ishift+=4
                                except: break
                                try:
                                    img=Image.frombytes('RGBA',(x,y),
                                        imbuffer[ishift:])
                                except: break
                                ishift+=(x*y*4)
                                self.frames.append([self.bitmapfrompil(img),n*1000/d])
                            else: err=1
                        del imbuffer
                    else: err=1
                except: err=1
                if err: msg=_('BPG decoding error!\n')
        else: msg=_('File')+' \"%s\" '%filename+_('is not a BPG-File!')
        if msg:
            wx.PostEvent(self,ShowEvent(SE_EVT_TYPE,-1,value=msg))
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
        if wx.VERSION[0]<4:
            return wx.BitmapFromBufferRGBA(img.size[0],\
                img.size[1],img.convert("RGBA").tobytes())
        else:
            return wx.Bitmap.FromBufferRGBA(img.size[0],\
                img.size[1],img.convert("RGBA").tobytes())
    def scaleframe(self,img,width,height):
        if img:
            return self.bitmapfrompil(img.resize((int(width),\
                int(height)),Image.ANTIALIAS))
        else: return None
    def scalebitmap(self,width,height):
        if self.img:
            return self.scaleframe(self.img,width,height)
        else: return None
    def showsingleframe(self,bitmap):
        self.bitmap.SetBitmap(bitmap)
        if wx.VERSION[0]<4: self.bitmap.SetToolTipString(self.imginfo)
        else: self.bitmap.SetToolTip(self.imginfo)
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
        else: self.Layout()
    def shownextframe(self,event):
        if len(self.frames):
            self.frames_index+=1
            if self.frames_index==len(self.frames): self.frames_index=0
            self.showsingleframe(self.frames[self.frames_index][0])
            self.frame_timer.Start(self.frames[self.frames_index][1],
                wx.TIMER_ONE_SHOT)
    def showframes(self):
        self.bitmap._clear=True
        if len(self.frames)==0: self.showempty()
        else:
            bitmap=self.frames[0][0]
            self.showsingleframe(bitmap)
            self.frame_timer.Start(self.frames[self.frames_index][1],
                wx.TIMER_ONE_SHOT)
    def showbitmap(self,bitmap):
        self.bitmap._clear=True
        if bitmap==None: self.showempty()
        else:
            self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
            self.showsingleframe(bitmap)
    def emptybitmap(self):
        buffer=wx.Bitmap(400,300)
        dc=wx.BufferedDC(None,buffer)
        dc.SetBackground(wx.Brush(self.panel.GetBackgroundColour()))
        dc.Clear()
        dc.Destroy()
        return buffer
    def showempty(self):
        if len(self.frames): self.frames=[]
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
        if len(filename) and self.bpgdecode(filename):
            if len(self.filelist)==0:
                self.filelist=self.getfilelist(dirname(realpath(filename)))
                self.index=0
                while(True):
                    if self.index>=len(self.filelist): break
                    if self.filelist[self.index]==realpath(filename): break
                    else: self.index+=1
                    if self.index>=len(self.filelist): break
        wx.PostEvent(self,ShowEvent(SE_EVT_TYPE,-1))
    def _evt_showimage(self,evt):
        if evt.value: errmsgbox(evt.value)
        else:
            if self.img:
                self.showbitmap(self.autoscaled())
                wx.CallAfter(self.Center)
            elif len(self.frames):
                self.showframes()
                wx.CallAfter(self.Center)
            if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                ' ('+self.imginfo+')')
            else: self.deftitle()
    def showimage(self,filename):
        if not self.dlock.acquire(False): return
        self.dlock.release()
        if self.frame_timer.IsRunning(): self.frame_timer.Stop()
        self.dthread=DecodeThread(self,lambda: self._showimage(filename))
        self.dthread.start()
    def getfilelist(self,dirname):
        filelist=[]
        for f in sorted(listdir(dirname)):
            fname=realpath(join(dirname,f))
            try:
                if access(fname,R_OK) and isfile(fname) and\
                    fname[-4:].lower()=='.bpg':
                    filelist.append(fname)
            except: pass
        return filelist
    def checkpath(self,path):
        if isdir(path):
            self.filelist=self.getfilelist(realpath(path))
            if len(self.filelist): path=self.filelist[0]
        return path
    def __init__(self,parent,title):
        kwds={}
        args=[]
        kwds["style"]=wx.DEFAULT_FRAME_STYLE
        kwds["title"]=title
        kwds["parent"]=parent
        wx.Frame.__init__(self,*args,**kwds)
        self.dt=FileDropTarget(self)
        self.SetDropTarget(self.dt)
        self.max=False
        self.codepage=locale.getdefaultlocale()[1]
        self.bpgpath=bpggetcmd()
        self.scale=100.0
        self.autoscale=100.0
        self.bitmap_text=''
        self.img=None
        self.frames=[]
        self.frames_index=0
        self.frame_timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.shownextframe,self.frame_timer)
        self.imginfo=''
        self.fifo=''
        self.mpos=None
        self.dlock=Lock()
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
        self.bitmap.Bind(wx.EVT_KEY_DOWN,self.keydown)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.bitmap.Bind(wx.EVT_MOTION,self.drag)
        self.bitmap.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.Bind(wx.EVT_SIZE,self.fresize)
        self.Bind(wx.EVT_ERASE_BACKGROUND,lambda e: None)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(SE_EVT_BNDR,self._evt_showimage)
        self.Layout()
        self.Center()
        self.panel.SetFocus()
        wx.CallLater(1000,self.showimage,title)
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
    def first(self):
        if len(self.filelist) and self.index:
            self.index=0
            self.loadindex(1)
    def last(self):
        if len(self.filelist) and self.index!=len(self.filelist)-1:
            self.index=len(self.filelist)-1
            self.loadindex(0)
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
        if len(self.frames):
            if self.frame_timer.IsRunning(): self.frame_timer.Stop()
            wx.CallAfter(self.showframes)
        elif self.scale==self.autoscale:
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
        if event.ControlDown():
            if keycode==ord('F'):
                if self.IsFullScreen():
                    self.ShowFullScreen(False,style=wx.DEFAULT_FRAME_STYLE)
                else:
                    self.ShowFullScreen(True,style=wx.FULLSCREEN_ALL)
                    self.autoimg()
                return
            if keycode==ord('O'):
                openFileDialog = wx.FileDialog(self,_('Open BPG file'),"","",\
                    _("BPG files")+" (*.bpg)|*.bpg",\
                    wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
                status=openFileDialog.ShowModal()
                if status==wx.ID_CANCEL: return
                if status==wx.ID_OK:
                    self.stitle(_('Loading...'))
                    self.filelist=[]
                    filename=openFileDialog.GetPath()
                    openFileDialog.Destroy()
                    self.showimage(filename)
                return
            if keycode==ord('S') and self.img:
                saveFileDialog=wx.FileDialog(self,_("Save BPG file as PNG file"),\
                    "",basename(self.filelist[self.index])[:-4]+'.png',\
                    _("PNG files")+" (*.png)|*.png",\
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                status=saveFileDialog.ShowModal()
                if status==wx.ID_CANCEL: return
                if status==wx.ID_OK:
                    dst=saveFileDialog.GetPath()
                    if dst[-4:].lower()!='.png': dst+='.png'
                    ttitle=self.Title
                    self.stitle(_('Saving PNG file...'))
                    try:
                        if exists(dst): remove(dst)
                        self.img.save(dst,'PNG',optimize=True)
                    except: errmsgbox(_('Unable to save')+' \"%s\"!'%dst)
                    self.stitle(ttitle)
                    return
            if keycode==ord('C') and (self.img or len(self.frames)):
                saveFileDialog=wx.FileDialog(self,_("Save a copy..."),"",\
                    basename(self.filelist[self.index])[:-4],\
                    _("BPG files")+" (*.bpg)|*.bpg",\
                    wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
                status=saveFileDialog.ShowModal()
                if status==wx.ID_CANCEL: return
                if status==wx.ID_OK:
                    dst=saveFileDialog.GetPath()
                    try:
                        if exists(dst) and\
                            abspath(self.filelist[self.index])!=dst: remove(dst)
                        copyfile(self.filelist[self.index],dst)
                    except: errmsgbox(_('Unable to save')+' \"%s\"!'%dst)
                    return
            if keycode==ord('R'):
                self.rotate(True)
                return
            if keycode==ord('L'):
                self.rotate(False)
                return
            if keycode in [wx.WXK_LEFT,wx.WXK_NUMPAD_LEFT]:
                self.first()
                return
            if keycode in [wx.WXK_RIGHT,wx.WXK_NUMPAD_RIGHT]:
                self.last()
                return
            if keycode==ord('T'):
                style=self.GetWindowStyle()
                if wx.STAY_ON_TOP&style:
                    self.SetWindowStyle(style&~wx.STAY_ON_TOP)
                else: self.SetWindowStyle(style|wx.STAY_ON_TOP)
                self.Refresh()
                self.Raise()
                return
        else:
            if keycode==wx.WXK_HOME:
                self.first()
                return
            if keycode==wx.WXK_END:
                self.last()
                return
            if keycode==wx.WXK_ESCAPE:
                self.Close()
                return
            if keycode in [wx.WXK_PAGEUP,wx.WXK_NUMPAD_PAGEUP,wx.WXK_BACK]:
                self.previous()
                return
            if keycode in [wx.WXK_PAGEDOWN,wx.WXK_NUMPAD_PAGEDOWN,\
                wx.WXK_RETURN]:
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
                _('⌘T - toggle \'stay on top\' mode\n')+\
                _('⌘Left,Home - jump to the first image in folder\n')+\
                _('⌘Right,End - jump to the last image in folder\n')+\
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
                if len(self.filelist) and (self.img or len(self.frames)):
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
            if keycode in [wx.WXK_RETURN,ord('D'),ord('W')]:
                self.next()
                return
            if keycode in [ord('A'),ord('S')]:
                self.previous()
                return
            if keycode in [wx.WXK_NUMPAD_ADD,ord('=')]:
                if self.img and self.scale<100.0:
                    self.stitle(_('Zooming in...'))
                    self.scale+=5.0
                    if self.scale>100.0: self.scale=100.0
                    if self.scale!=100.0:
                        x=self.img.size[0]*(self.scale/100.0)
                        y=self.img.size[1]*(self.scale/100.0)
                        self.showbitmap(self.scalebitmap(x,y))
                    else: self.showbitmap(self.bitmapfrompil(self.img))
                    if len(self.imginfo): self.stitle(\
                        self.filelist[self.index]+' ('+self.imginfo+')')
                    else: self.deftitle()
                return
            if keycode in [wx.WXK_NUMPAD_SUBTRACT,ord('-')]:
                if self.img and self.scale>self.autoscale:
                    self.stitle(_('Zooming out...'))
                    self.scale-=5.0
                    if self.scale<self.autoscale: self.scale=self.autoscale
                    if self.scale!=100.0:
                        x=self.img.size[0]*(self.scale/100.0)
                        y=self.img.size[1]*(self.scale/100.0)
                        self.showbitmap(self.scalebitmap(x,y))
                    else: self.showbitmap(self.bitmapfrompil(self.img))
                    if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                        ' ('+self.imginfo+')')
                    else: self.deftitle()
                return
            if keycode in [wx.WXK_NUMPAD_MULTIPLY,ord('8')]:
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
        event.Skip()
    def OnClose(self,event):
        if self.frame_timer.IsRunning(): self.frame_timer.Stop()
        event.Skip()
    def __del__(self):
        if self.frame_timer.IsRunning(): self.frame_timer.Stop()

class bpgframe(wx.App):
    def BringWindowToFront(self):
        try: self.GetTopWindow().Raise()
        except: pass
    def OnActivate(self, event):
        if event.GetActive(): self.BringWindowToFront()
        event.Skip()
    def OnInit(self):
        return True
    def MacOpenFile(self,filename):
        if hasattr(self,'frame'):
            self.BringWindowToFront()
            self.frame.showimage(self.frame.checkpath(filename))
    def MacReopenApp(self):
        self.BringWindowToFront()
    def __init__(self,parent,filename):
        super(bpgframe,self).__init__(parent)
        self.frame=DFrame(None,filename)
        self.SetTopWindow(self.frame)
        self.SetExitOnFrameDelete(True)
        self.Bind(wx.EVT_ACTIVATE_APP,self.OnActivate)
        wx.CallAfter(self.frame.Show)
        wx.CallAfter(self.frame.Raise)

if __name__=='__main__':
    wxapp=True
    if len(argv)==1: app=bpgframe(None,'')
    else: app=bpgframe(None,realpath(argv[1]))
    app.MainLoop()
