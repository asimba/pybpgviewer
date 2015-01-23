#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Simple BPG Image viewer.

Copyright (c) 2014-2015, Alexey Simbarsky
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
from os import listdir,access,R_OK,stat,close,remove
from os.path import exists,isfile,dirname,basename,realpath,join
from tempfile import mkstemp
from shutil import copyfile
from subprocess import Popen,PIPE,STDOUT
from math import floor
import StringIO
from platform import system

if system()=="Windows":
    osflag=False
    from subprocess import STARTUPINFO
else:
    osflag=True
    from os import mkfifo,O_NONBLOCK,O_RDONLY
    import signal

    class TimeExceededError(Exception): pass

    def timeout(signum,frame):
        raise TimeExceededError,"Timed Out"

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

if not(osflag):
    try: import win32file,win32pipe
    except:
        msg="Please install Python for Windows Extensions\n\
(http://sourceforge.net/projects/pywin32/)!"
        errmsg(msg)
        raise RuntimeError(msg)
    
try: import wx
except:
    msg="Please install wxPython 2.8 or higher (http://www.wxpython.org/)!\n\
Under Debian or Ubuntu you may try: sudo aptitude install python-wxgtk2.8"
    errmsg(msg)
    raise RuntimeError(msg)

try: import Image
except:
    msg="Please install Python Imaging Library (PIL) 1.1.7 or higher \n\
(http://www.pythonware.com/products/pil/)!\n\
Under Debian or Ubuntu you may try: sudo aptitude install python-imaging"
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
        bpgpath=join(dirname(realpath(scriptname)),binname)
    if not(isfile(bpgpath)):
        msg='BPG decoder not found!\n'
        print msg
        errmsgbox(msg)
        exit()
    bpgpath+=' -o '
    return bpgpath

class DFrame(wx.Frame):
    def bpgdecode(self,cmd,filename):
        msg=None
        self.img=None
        if len(filename)>4 and filename[-4:].lower()=='.bpg':
            try:
                if not(isfile(filename) and access(filename,R_OK)):
                    msg='Unable to open \"%s\"!'%filename
            except: return False
            if not(msg):
                err=0
                try:
                    imbuffer=''
                    if osflag:
                        cmd+=self.fifo+' "'+realpath(filename)+'"'+\
                            ' >/dev/null 2>&1'
                        f=Popen(cmd,shell=True,stdin=None,stdout=None,\
                            stderr=None)
                        signal.signal(signal.SIGALRM,timeout)
                        signal.alarm(8)
                        try: fifo=open(self.fifo,mode='rb')
                        except TimeExceededError:
                            try: fifo.close()
                            except: pass
                            fifo=None
                        finally: signal.alarm(0)
                        if fifo:
                            while True:
                                if f.poll()!=None: break;
                                data=fifo.read()
                                if len(data): imbuffer+=data
                            fifo.close()
                    else:
                        si=STARTUPINFO()
                        si.dwFlags|=1
                        si.wShowWindow=0
                        pname='\\\\.\\pipe\\'+basename(self.fifo)
                        tpipe=win32pipe.CreateNamedPipe(
                            pname,
                            win32pipe.PIPE_ACCESS_DUPLEX,
                            win32pipe.PIPE_TYPE_BYTE|win32pipe.PIPE_WAIT,
                            1,16777216,16777216,2000,None)
                        cmd+=pname+' "'+realpath(filename)+'"'
                        f=Popen(cmd,shell=False,stdin=None,stdout=None,\
                            stderr=None,bufsize=0,startupinfo=si)
                        win32pipe.ConnectNamedPipe(tpipe,None)
                        imbuffer=''
                        if tpipe:
                            while True:
                                data=None
                                try: data=win32file.ReadFile(tpipe,16777216)
                                except: data=None
                                if not(data): break
                                if data[0]!=0: break
                                if len(data[1]): imbuffer+=data[1]
                        win32pipe.DisconnectNamedPipe(tpipe)
                        f.wait()
                    if len(imbuffer):
                        try: self.img=Image.open(StringIO.StringIO(imbuffer))
                        except: err=1
                        del imbuffer
                    else: err=1
                except: err=1
                if err: msg='BPG decoding error!\n'
        else: msg='File \"%s\" in not a BPG-File!'%filename
        if msg:
            print msg
            errmsgbox(msg)
            if self.img:
                del self.img
                self.img=None
        else: return True
        return False

    def stitle(self,title):
        self.Title=title
        if osflag: self.Update()
        else: self.Refresh()

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
        if not(x>=crect[2]) and not(y>=crect[3]) and not(self.IsMaximized()):
            self.panel.SetInitialSize(size=(x,y))
            self.panel.SetClientSize((x,y))
            self.Fit()
            wx.CallAfter(self.Center)
        self.Layout()

    def showempty(self):
        if self.bitmap_original:
            try: del self.bitmap_original
            except: pass
            self.bitmap_original=None
            buffer=wx.EmptyBitmap(400,300)
            dc=wx.BufferedDC(None,buffer)
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            dc.Destroy()
            self.showbitmap(buffer)
        self.imginfo=''

    def showimage(self,filename):
        if len(filename) and self.bpgdecode(self.bpgpath,filename):
            if len(self.filelist)==0:
                self.filelist=self.getfilelist(dirname(realpath(filename)))
                self.index=0
                while(True):
                    if self.filelist[self.index]==realpath(filename): break
                    else: self.index+=1
                    if self.index>=len(self.filelist): break
            try:
                if self.img:
                    wxim=apply(wx.EmptyImage,self.img.size)
                    wxim.SetData(self.img.convert("RGB").tostring())
                    self.bitmap_original=wx.BitmapFromImage(wxim)
                    del self.img
                    self.img=None
                    del wxim
                else:
                    try: del self.bitmap_original
                    except: pass
                    self.bitmap_original=None
            except:
                try: del self.bitmap_original
                except: pass
                self.bitmap_original=None
            if self.bitmap_original:
                if self.IsMaximized():
                    cr=self.GetClientSize()
                    cx=cr[0]
                    cy=cr[1]
                else:
                    cr=wx.Display().GetClientArea()
                    cx=cr[2]
                    cy=cr[3]
                d=0.0
                x=self.bitmap_original.GetWidth()
                y=self.bitmap_original.GetHeight()
                self.bitmap_text=str(x)+'x'+str(y)
                d0=float(cx)/float(x)
                d1=float(cy)/float(y)
                if d0<1.0 or d1<1.0:
                    d=d0 if d0<d1 else d1
                    if not(self.IsMaximized()): d*=0.95
                    x=floor(x*d)
                    y=floor(y*d)
                    self.scale=d*100.0
                    self.autoscale=self.scale
                    self.showbitmap(self.scalebitmap(x,y))
                else: self.showbitmap(self.bitmap_original)
        else: self.showempty()
        if len(self.imginfo): self.stitle(filename+' ('+self.imginfo+')')
        else: self.stitle('Press Ctrl+O to open BPG file...')

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
        self.bitmap_original=None
        self.bitmap_text=''
        self.img=None
        self.imginfo=''
        self.fifo=''
        t,self.fifo=mkstemp(suffix='.ppm',prefix='')
        close(t)
        remove(self.fifo)
        if osflag: mkfifo(self.fifo,0777)
        self.filelist=[]
        self.index=0
        self.SetInitialSize(size=(400,300))
        self.panel=wx.ScrolledWindow(self,-1,style=wx.WANTS_CHARS)
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.psizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel,1,wx.ALIGN_CENTER_HORIZONTAL|\
            wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND,0)
        buffer=wx.EmptyBitmap(400,300)
        dc=wx.BufferedDC(None,buffer)
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.Destroy()
        self.bitmap=wx.StaticBitmap(self.panel,bitmap=buffer)
        self.psizer.Add(self.bitmap,1,wx.ALIGN_CENTER_HORIZONTAL|\
            wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ADJUST_MINSIZE,0)
        self.SetSizer(self.sizer)
        self.panel.SetSizer(self.psizer)
        self.showimage(title)
        self.sizer.Fit(self)
        self.panel.Bind(wx.EVT_KEY_DOWN,self.keydown)
        self.panel.Bind(wx.EVT_CHAR,self.keychar)
        self.panel.Bind(wx.EVT_LEFT_DCLICK,self.maximize)
        self.bitmap.Bind(wx.EVT_LEFT_DCLICK,self.maximize)
        self.Layout()
        self.Center()
        self.panel.SetFocus()

    def previous(self):
        if len(self.filelist):
            old=self.index
            if self.index: self.index-=1
            else: self.index=len(self.filelist)-1
            if self.index!=old:
                self.stitle('Loading...')
                self.showimage(self.filelist[self.index])

    def next(self):
        if len(self.filelist):
            old=self.index
            if self.index<len(self.filelist)-1: self.index+=1
            else: self.index=0
            if self.index!=old:
                self.stitle('Loading...')
                self.showimage(self.filelist[self.index])

    def rotate(self,dir):
        if self.bitmap_original:
            self.stitle('Rotating...')
            wxim=self.bitmap_original.ConvertToImage()
            try: del self.bitmap_original
            except: pass
            self.bitmap_original=wx.BitmapFromImage(\
                wxim.Rotate90(clockwise=dir))
            del wxim
            if self.bitmap_original:
                if self.scale!=100.0:
                    x=self.bitmap_original.GetWidth()*(self.scale/100.0)
                    y=self.bitmap_original.GetHeight()*(self.scale/100.0)
                    bitmap=self.scalebitmap(x,y)
                else: bitmap=self.bitmap_original
            self.showbitmap(bitmap)
            if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                ' ('+self.imginfo+')')

    def maximize(self,event):
        if not(self.IsMaximized()):
            self.Maximize()
            if osflag: self.Update()
            else: self.Refresh()

    def keydown(self,event):
        keycode=event.GetKeyCode()
        if keycode==wx.WXK_ESCAPE:
            self.Close()
            return
        if keycode==wx.WXK_PAGEUP or keycode==wx.WXK_NUMPAD_PAGEUP or\
            keycode==wx.WXK_BACK:
            self.previous()
            return
        if keycode==wx.WXK_PAGEDOWN or keycode==wx.WXK_NUMPAD_PAGEDOWN or\
            keycode==wx.WXK_RETURN:
            self.next()
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
            'Ctrl-C - save a copy of the opened file\n'+\
            'Ctrl-R - rotate 90 degrees clockwise\n'+\
            'Ctrl-L - rotate 90 degrees counterclockwise\n'+\
            '+ - zoom in (up to 100%)\n'+\
            '- - zoom out (down to the smallest available size)\n'+\
            '* - zoom out to fit window area\n'+\
            'Left,Up,Right,Down - move over the scaled image\n'+\
            'PgUp,Backspace - view previous file\n'+\
            'PgDown,Return - view next file\n'+\
            'Delete - delete current file\n','Help',\
            wx.OK|wx.ICON_INFORMATION)
            return
        if keycode==wx.WXK_DELETE or keycode==wx.WXK_NUMPAD_DELETE:
            if len(self.filelist) and self.bitmap_original:
                if wx.MessageBox('Delete file "'+self.filelist[self.index]+\
                    '"?','File deletion!',wx.YES_NO|wx.ICON_WARNING|\
                    wx.NO_DEFAULT)==wx.YES:
                    index=self.index
                    try: remove(self.filelist[index])
                    except:
                        msg='Unable to delete: \"%s\"!'%self.filelist[index]
                        errmsgbox(msg)
                        return
                    self.filelist.pop(index)
                    if len(self.filelist):
                        if index>=len(self.filelist): self.index=0
                        self.stitle('Loading...')
                        self.showimage(self.filelist[self.index])
                    else:
                        self.showempty()
                        self.stitle('Press Ctrl+O to open BPG file...')
            return
        event.Skip()

    def keychar(self,event):
        keycode=event.GetUniChar()
        try: co_code=wx.WXK_CONTROL_O
        except: co_code=15
        try: cs_code=wx.WXK_CONTROL_S
        except: cs_code=19
        try: cc_code=wx.WXK_CONTROL_C
        except: cc_code=3
        try: cr_code=wx.WXK_CONTROL_R
        except: cr_code=18
        try: cl_code=wx.WXK_CONTROL_L
        except: cl_code=12
        if osflag: rt_code=370
        else: rt_code=13
        if keycode==rt_code:
            self.next()
            return
        if keycode==co_code:
            openFileDialog = wx.FileDialog(self,'Open BPG file',"","",\
                "BPG files (*.bpg)|*.bpg",wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
            status=openFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                self.stitle('Loading...')
                self.filelist=[]
                self.showimage(openFileDialog.GetPath())
                openFileDialog.Destroy()
            return
        if keycode==cs_code and len(self.ppmfile) and self.bitmap_original:
            saveFileDialog=wx.FileDialog(self,"Save BPG file as PNG file","",\
                basename(self.filelist[self.index])[:-4],\
                "PNG files (*.png)|*.png",wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
            status=saveFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                dst=saveFileDialog.GetPath()
                try:
                    if exists(dst): remove(dst)
                    self.bitmap_original.SaveFile(dst,wx.BITMAP_TYPE_PNG)
                except: errmsgbox('Unable to save \"%s\"!'%dst)
                return
        if keycode==cc_code and len(self.ppmfile) and self.bitmap_original:
            saveFileDialog=wx.FileDialog(self,"Save a copy...","",\
                basename(self.filelist[self.index])[:-4],\
                "BPG files (*.bpg)|*.bpg",wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT)
            status=saveFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                dst=saveFileDialog.GetPath()
                try:
                    if exists(dst) and\
                        abspath(self.filelist[self.index])!=dst: remove(dst)
                    copyfile(self.filelist[self.index],dst)
                except: errmsgbox('Unable to save \"%s\"!'%dst)
                return
        if keycode==ord('+'):
            if self.bitmap_original and self.scale<100.0:
                self.stitle('Zooming in...')
                self.scale+=5.0
                if self.scale>100.0: self.scale=100.0
                if self.scale!=100.0:
                    x=self.bitmap_original.GetWidth()*(self.scale/100.0)
                    y=self.bitmap_original.GetHeight()*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else: self.showbitmap(self.bitmap_original)
                if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                    ' ('+self.imginfo+')')
                else: self.stitle('Press Ctrl+O to open BPG file...')
            return
        if keycode==ord('-'):
            if self.bitmap_original and self.scale>self.autoscale:
                self.stitle('Zooming out...')
                self.scale-=5.0
                if self.scale<self.autoscale: self.scale=self.autoscale
                if self.scale!=100.0:
                    x=self.bitmap_original.GetWidth()*(self.scale/100.0)
                    y=self.bitmap_original.GetHeight()*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else: self.showbitmap(self.bitmap_original)
                if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                    ' ('+self.imginfo+')')
                else: self.stitle('Press Ctrl+O to open BPG file...')
            return
        if keycode==ord('*'):
            if self.bitmap_original:
                csize=self.GetClientSize()
                d=0.0
                x=self.bitmap_original.GetWidth()
                y=self.bitmap_original.GetHeight()
                self.bitmap_text=str(x)+'x'+str(y)
                d0=float(csize[0])/float(x)
                d1=float(csize[1])/float(y)
                if d0<1.0 or d1<1.0:
                    d=d0 if d0<d1 else d1
                    x=floor(x*d)
                    y=floor(y*d)
                    scale=d*100.0
                    if self.scale!=scale:
                        self.scale=scale
                        self.showbitmap(self.scalebitmap(x,y))
                if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                    ' ('+self.imginfo+')')
                else: self.stitle('Press Ctrl+O to open BPG file...')
            return
        if keycode==cr_code:
            self.rotate(True)
            return
        if keycode==cl_code:
            self.rotate(False)
            return
        event.Skip()

    def __del__(self):
        if osflag and exists(self.fifo):
            try: remove(self.fifo)
            except: pass

class bpgframe(wx.App):
    def __init__(self,parent,title,filename):
        super(bpgframe,self).__init__(parent)
        frame=DFrame(None,title,filename)
        self.SetTopWindow(frame)
        frame.Show()

if __name__=='__main__':
    wxapp=True
    if len(argv)==1: app=bpgframe(None,argv[0],'')
    else: app=bpgframe(None,argv[0],realpath(argv[1]))
    app.MainLoop()
