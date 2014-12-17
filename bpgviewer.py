#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv,exit
from os import walk,access,R_OK,stat,close,remove
from os.path import exists,isfile,dirname,realpath,join
from tempfile import mkstemp
from subprocess import Popen,PIPE,STDOUT
from platform import system

osflag=True
if system()=="Windows": osflag=False
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
            if not(isfile(filename) and access(filename,R_OK)): exit()
            t,p=mkstemp(suffix='.png',prefix='')
            close(t)
            remove(p)
        except: exit()
        cmd+=p+' '+realpath(filename)
        try:
            f=Popen(cmd,shell=True,stdin=None,stdout=None,stderr=None)
            f.wait()
        except: msg='BPG decoding error!\n'
        if not(isfile(p)) or stat(p).st_size==0:
            msg='Unable to open: \"%s\"!'%filename
            p=''
    else:
        msg='File \"%s\" in not a BPG-File!'%filename
    if msg:
        print msg
        errmsgbox(msg)
    return p

def scale_bitmap(bitmap,width,height):
    image=wx.ImageFromBitmap(bitmap)
    image=image.Scale(width,height,wx.IMAGE_QUALITY_HIGH)
    result=wx.BitmapFromImage(image)
    return result

class DFrame(wx.Frame):
    def showimage(self,filename):
        if self.bitmap:
            self.Layout()
            self.Refresh()
            self.bitmap.Destroy()
            self.bitmap=None
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
            try: bitmap=wx.Bitmap(self.pngfile)
            except: bitmap=None
            if bitmap:
                crect=wx.Display().GetClientArea()
                dx,dy=0.0,0.0
                x,y=0,0
                self.bitmap_text=str(bitmap.GetWidth())+'x'+\
                    str(bitmap.GetHeight())
                if bitmap.GetWidth()>crect[2]:
                    dx=float(crect[2])/float(bitmap.GetWidth())
                if bitmap.GetHeight()>crect[3]:
                    dy=float(crect[3])/float(bitmap.GetHeight())
                if dx>dy:
                    self.SetSize((400,crect[3]))
                    wsize=self.GetClientSize()
                    dy=float(wsize[1])/float(bitmap.GetHeight())
                    x=bitmap.GetWidth()*dy
                    y=bitmap.GetHeight()*dy
                    self.scale=dy*100
                else:
                    self.SetSize((crect[2],300))
                    wsize=self.GetClientSize()
                    dx=float(wsize[0])/float(bitmap.GetWidth())
                    x=bitmap.GetWidth()*dx
                    y=bitmap.GetHeight()*dx
                    self.scale=dx*100
                if x and y: bitmap=scale_bitmap(bitmap,x,y)
                self.bitmap=wx.StaticBitmap(self.panel,-1,bitmap)
                self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
                self.bitmap.SetToolTipString(self.imginfo)
                self.grid_sizer.Add(self.bitmap,0,wx.ALIGN_CENTER_HORIZONTAL|\
                    wx.ALIGN_CENTER_VERTICAL,0)
                self.Layout()
                self.Fit()
                self.Update()
                wx.CallAfter(self.Center)
        else:
            self.bitmap=None
            self.imginfo=''
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
        self.bitmap=None
        self.bitmap_text=''
        self.imginfo=''
        self.pngfile=''
        self.filelist=[]
        self.index=0
        self.panel=wx.Panel(self,style=wx.WANTS_CHARS)
        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.grid_sizer=wx.GridSizer(1,1,0,0)
        self.panel.SetSizer(self.grid_sizer)
        self.SetMinSize((400,300))
        self.sizer.Add(self.panel,1,wx.EXPAND,0)
        self.SetSizer(self.sizer)
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
        if keycode==wx.WXK_PAGEDOWN or keycode==wx.WXK_NUMPAD_PAGEDOWN:
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
        if keycode==wx.WXK_PAGEUP or keycode==wx.WXK_NUMPAD_PAGEUP:
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
        event.Skip()

    def keychar(self,event):
        keycode=event.GetUniChar()
        try: co_code=wx.WXK_CONTROL_O
        except: co_code=15
        if keycode==co_code:
            openFileDialog = wx.FileDialog(self,'Open BPG file',"", "",\
                "BPG files (*.bpg)|*.bpg",wx.FD_OPEN|wx.FD_FILE_MUST_EXIST)
            status=openFileDialog.ShowModal()
            if status==wx.ID_CANCEL: return
            if status==wx.ID_OK:
                self.Title='Loading...'
                self.Layout()
                self.Update()
                self.showimage(openFileDialog.GetPath())
                openFileDialog.Destroy()
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
