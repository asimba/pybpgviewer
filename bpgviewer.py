#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Simple BPG Image viewer.

Copyright (c) 2014, Alexey Simbarsky
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

from sys import argv,exit
from os import walk,access,R_OK,stat,close,remove
from os.path import exists,isfile,dirname,basename,realpath,join
from tempfile import mkstemp
from subprocess import Popen,PIPE,STDOUT
from shutil import copyfile
from math import floor
from platform import system

if system()=="Windows":
    osflag=False
    from subprocess import STARTUPINFO
else: osflag=True
wxapp=False

def errmsg(msg):
    if osflag:
        try:
            f=Popen(['notify-send',msg],False,stdin=None,stdout=None,\
            stderr=None)
            f.wait()
        except:
            try:
                f=Popen(['xmessage',msg],False,stdin=None,stdout=None,\
                    stderr=None)
                f.wait()
            except: pass
    else:
        import ctypes
        MessageBox=ctypes.windll.user32.MessageBoxW
        MessageBox(0,unicode(msg),u'Error!',16)

try: import wx
except:
    msg="Please install wxPython 2.8 or higher (http://www.wxpython.org/)!\n\
Under Debian or Ubuntu you may try: sudo aptitude install python-wxgtk2.8"
    errmsg(msg)
    raise RuntimeError(msg)

def errmsgbox(msg):
    if not(wxapp): app=wx.App(0)
    wx.MessageBox(msg,'Error!',wx.OK|wx.ICON_ERROR)
    if not(wxapp): app.Exit()

def bpggetcmd(scriptname):
    binname='bpgdec'
    if system()=="Windows":
        binname+='.exe'
        bpgpath=realpath(binname)
    else:
        bpgpath='/usr/bin/'+binname
    if not(exists(bpgpath)):
        bpgpath=join(dirname(realpath(scriptname)),'bpgdec')
    if not(isfile(bpgpath)):
        msg='BPG decoder not found!\n'
        print msg
        errmsgbox(msg)
        exit()
    bpgpath+=' -o '
    return bpgpath

def bpgdecode(cmd,filename):
    msg=None
    p=''
    if len(filename)>4 and filename[-4:].lower()=='.bpg':
        try:
            if not(isfile(filename) and access(filename,R_OK)):
                msg='Unable to open \"%s\"!'%filename
            else:
                t,p=mkstemp(suffix='.png',prefix='')
                close(t)
                remove(p)
        except: return ''
        if not(msg):
            cmd+=p+' '+realpath(filename)
            try:
                if osflag:
                    f=Popen(cmd,shell=True,stdin=None,stdout=None,stderr=None)
                else:
                    si=STARTUPINFO()
                    si.dwFlags|=1
                    si.wShowWindow=0
                    f=Popen(self.cmd,shell=False,stdin=None,stdout=None,\
                        stderr=None,bufsize=0,startupinfo=si)
                f.wait()
            except: msg='BPG decoding error!\n'
            if not(msg):
                if not(isfile(p)) or stat(p).st_size==0:
                    msg='Unable to open: \"%s\"!'%filename
    else: msg='File \"%s\" in not a BPG-File!'%filename
    if msg:
        print msg
        errmsgbox(msg)
        p=''
    return p

class DFrame(wx.Frame):
    def scalebitmap(self,width,height):
        return wx.BitmapFromImage(\
            wx.ImageFromBitmap(self.bitmap_original).Scale(width,height,\
            wx.IMAGE_QUALITY_HIGH))

    def showbitmap(self,bitmap):
        self.bitmap.SetBitmap(bitmap)
        self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
        self.bitmap.SetToolTipString(self.imginfo)
        x=bitmap.GetWidth()
        y=bitmap.GetHeight()
        self.panel.SetVirtualSize((x,y))
        self.panel.SetScrollbars(5,5,x,y)
        crect=wx.Display().GetClientArea()
        if not(x>crect[2]) and not(y>crect[3]) and not(self.IsMaximized()):
            self.panel.SetInitialSize(size=(x,y))
            self.SetInitialSize(size=(x,y))
        else: wx.CallAfter(self.Center)
        self.Fit()
        self.Layout()
        wx.CallAfter(self.Update)

    def showimage(self,filename):
        if len(self.pngfile):
            try: remove(self.pngfile)
            except: pass
            self.pngfile=''
        if len(filename): self.pngfile=bpgdecode(self.bpgpath,filename)
        else: self.pngfile=''
        if len(self.pngfile):
            if len(self.filelist)==0:
                self.filelist=self.getfilelist(dirname(realpath(filename)))
                self.index=0
                while(True):
                    if self.filelist[self.index]==realpath(filename): break
                    else: self.index+=1
                    if self.index>=len(self.filelist): break
            try: self.bitmap_original=wx.Bitmap(self.pngfile)
            except: self.bitmap_original=None
            if self.bitmap_original:
                crect=wx.Display().GetClientArea()
                d=0.0
                x=self.bitmap_original.GetWidth()
                y=self.bitmap_original.GetHeight()
                self.bitmap_text=str(x)+'x'+str(y)
                d0=float(crect[2])/float(x)
                d1=float(crect[3])/float(y)
                if d0<1.0 or d1<1.0:
                    d=d0 if d0<d1 else d1
                    d*=0.95
                    x=floor(x*d)
                    y=floor(y*d)
                    self.scale=d
                    self.scale*=100.0
                    self.autoscale=self.scale
                    bitmap=self.scalebitmap(x,y)
                else: bitmap=self.bitmap_original
                self.showbitmap(bitmap)
        else: self.imginfo=''
        if len(self.imginfo): self.Title=filename+' ('+self.imginfo+')'
        else: self.Title='Press Ctrl+O to open BPG file...'

    def getfilelist(self,dirname):
        filelist=[]
        for root,dirs,files in walk(dirname,topdown=False):
            if root==dirname:
                for f in sorted(files):
                    fname=realpath(join(root,f))
                    try:
                        if access(fname,R_OK) and fname[-4:].lower()=='.bpg':
                            filelist.append(fname)
                    except: pass
        return filelist

    def __init__(self,parent,scriptpath,title):
        kwds={}
        args=[]
        kwds["style"]=wx.DEFAULT_FRAME_STYLE
        kwds["title"]=title
        kwds["parent"]=parent
        wx.Frame.__init__(self,*args,**kwds)
        self.bpgpath=bpggetcmd(scriptpath)
        self.scale=100.0
        self.autoscale=100.0
        crect=wx.Display().GetClientArea()
        self.bitmap_original=None
        self.bitmap_text=''
        self.imginfo=''
        self.pngfile=''
        self.filelist=[]
        self.index=0
        self.SetInitialSize(size=(400,300))
        self.panel=wx.ScrolledWindow(self,-1,style=wx.WANTS_CHARS)
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.psizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel,1,wx.CENTER|wx.ALL|wx.EXPAND,0)
        self.bitmap=wx.StaticBitmap(self.panel,\
            bitmap=wx.EmptyBitmap(400,300))
        self.psizer.Add(self.bitmap,1,wx.CENTER|wx.ALL|wx.ADJUST_MINSIZE,0)
        self.SetSizer(self.sizer)
        self.panel.SetSizer(self.psizer)
        self.showimage(title)
        self.sizer.Fit(self)
        self.panel.Bind(wx.EVT_KEY_DOWN,self.keydown)
        self.panel.Bind(wx.EVT_CHAR,self.keychar)
        self.Layout()
        self.Center()
        self.panel.SetFocus()

    def keydown(self,event):
        keycode=event.GetKeyCode()
        if keycode==wx.WXK_ESCAPE:
            self.Close()
            return
        if keycode==wx.WXK_PAGEUP or keycode==wx.WXK_NUMPAD_PAGEUP:
            if len(self.filelist):
                old=self.index
                if self.index: self.index-=1
                else: self.index=len(self.filelist)-1
                if self.index!=old:
                    self.Title='Loading...'
                    self.Layout()
                    self.Update()
                    self.showimage(self.filelist[self.index])
            return
        if keycode==wx.WXK_PAGEDOWN or keycode==wx.WXK_NUMPAD_PAGEDOWN:
            if len(self.filelist):
                old=self.index
                if self.index<len(self.filelist)-1: self.index+=1
                else: self.index=0
                if self.index!=old:
                    self.Title='Loading...'
                    self.Layout()
                    self.Update()
                    self.showimage(self.filelist[self.index])
            return
        if keycode==wx.WXK_LEFT or keycode==wx.WXK_NUMPAD_LEFT:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)-1,\
                self.panel.GetScrollPos(wx.VERTICAL))
            return
        if keycode==wx.WXK_RIGHT or keycode==wx.WXK_NUMPAD_RIGHT:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)+1,\
                self.panel.GetScrollPos(wx.VERTICAL))
            return
        if keycode==wx.WXK_UP or keycode==wx.WXK_NUMPAD_UP:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL),\
                self.panel.GetScrollPos(wx.VERTICAL)-1)
            return
        if keycode==wx.WXK_DOWN or keycode==wx.WXK_NUMPAD_DOWN:
            self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL),\
                self.panel.GetScrollPos(wx.VERTICAL)+1)
            return
        if keycode==wx.WXK_F1:
            wx.MessageBox('This is BPG image file viewer. Hot keys:\n'+\
            'Esc - close\n'+\
            'Ctrl-O - open BPG image file\n'+\
            'Ctrl-S - save a copy of the opened file as a PNG file\n'+\
            '+ - zoom in (up to 100%)\n'+\
            '- - zoom out (down to the smallest avaliable size)\n'+\
            'Left,Up,Right,Down - move over the scaled image\n'+\
            'PgUp - view previous file\n'+\
            'PgDown - view next file\n','Help',\
            wx.OK|wx.ICON_INFORMATION)
            return
        event.Skip()

    def keychar(self,event):
        keycode=event.GetUniChar()
        try: co_code=wx.WXK_CONTROL_O
        except: co_code=15
        try: cs_code=wx.WXK_CONTROL_S
        except: cs_code=19
        if keycode==co_code:
            openFileDialog = wx.FileDialog(self,'Open BPG file',"","",\
                "BPG files (*.bpg)|*.bpg",wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
            status=openFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                self.Title='Loading...'
                self.Layout()
                self.Update()
                self.showimage(openFileDialog.GetPath())
                openFileDialog.Destroy()
            return
        if keycode==cs_code and len(self.pngfile):
            saveFileDialog=wx.FileDialog(self,"Save BPG file as PNG file","",\
                basename(self.filelist[self.index])[:-4],\
                "PNG files (*.png)|*.png",wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
            status=saveFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                dst=saveFileDialog.GetPath()
                try:
                    if exists(dst): remove(dst)
                    copyfile(self.pngfile,dst)
                except: errmsgbox('Unable to save \"%s\"!'%dst)
                return
        if keycode==ord('+'):
            if self.scale<100.0:
                self.scale+=5.0
                if self.scale>100: self.scale=100.0
                x=self.bitmap_original.GetWidth()*(self.scale/100.0)
                y=self.bitmap_original.GetHeight()*(self.scale/100.0)
                bitmap=self.scalebitmap(x,y)
                self.Title='Zooming in...'
                self.Layout()
                self.Update()
                self.showbitmap(bitmap)
                if len(self.imginfo): self.Title=self.filelist[self.index]+\
                    ' ('+self.imginfo+')'
                else: self.Title='Press Ctrl+O to open BPG file...'
                wx.CallAfter(self.Update)
            return
        if keycode==ord('-'):
            if self.scale>self.autoscale:
                self.scale-=5.0
                if self.scale<self.autoscale: self.scale=self.autoscale
                x=self.bitmap_original.GetWidth()*(self.scale/100.0)
                y=self.bitmap_original.GetHeight()*(self.scale/100.0)
                bitmap=self.scalebitmap(x,y)
                self.Title='Zooming out...'
                self.Layout()
                self.Update()
                self.showbitmap(bitmap)
                if len(self.imginfo): self.Title=self.filelist[self.index]+\
                    ' ('+self.imginfo+')'
                else: self.Title='Press Ctrl+O to open BPG file...'
                wx.CallAfter(self.Update)
            return
        event.Skip()

    def __del__(self):
        if len(self.pngfile):
            try: remove(self.pngfile)
            except: pass

class bpgframe(wx.App):
    def __init__(self,parent,title,pngfile):
        super(bpgframe,self).__init__(parent)
        frame=DFrame(None,title,pngfile)
        self.SetTopWindow(frame)
        frame.Show()

if __name__=='__main__':
    wxapp=True
    if len(argv)==1: app=bpgframe(None,argv[0],'')
    else: app=bpgframe(None,argv[0],realpath(argv[1]))
    app.MainLoop()
