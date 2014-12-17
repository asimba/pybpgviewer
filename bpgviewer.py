#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv,exit
from os import access,R_OK,stat,close,remove
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
    p=None
    if len(filename)>4 and filename[-4:]=='.bpg':
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
            p=None
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
    def __init__(self,parent,title,pngfile):
        kwds={}
        args=[]
        kwds["style"]=wx.DEFAULT_FRAME_STYLE
        kwds["title"]=title
        kwds["parent"]=parent
        wx.Frame.__init__(self,*args,**kwds)
        bitmap=wx.Bitmap(pngfile)
        crect=wx.Display().GetClientArea()
        dx,dy=0.0,0.0
        x,y=0,0
        self.scale=100.0
        self.bitmap_text=str(bitmap.GetWidth())+'x'+str(bitmap.GetHeight())
        if bitmap.GetWidth()>crect[2]:
            dx=float(crect[2])/float(bitmap.GetWidth())
        if bitmap.GetHeight()>crect[3]:
            dy=float(crect[3])/float(bitmap.GetHeight())
        if dx>dy:
            x=bitmap.GetWidth()*dy
            y=bitmap.GetHeight()*dy
            self.scale=dy*100
        else:
            x=bitmap.GetWidth()*dx
            y=bitmap.GetHeight()*dx
            self.scale=dx*100
        if x and y: bitmap=scale_bitmap(bitmap,x,y)
        self.bitmap=wx.StaticBitmap(self,-1,bitmap)
        self.SetFocus()
        self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
        self.bitmap.SetToolTipString(self.imginfo)
        self.Title+=' ('+self.imginfo+')'
        grid_sizer=wx.GridSizer(1,1,0,0)
        grid_sizer.Add(self.bitmap,0,wx.ALIGN_CENTER_HORIZONTAL|\
            wx.ALIGN_CENTER_VERTICAL,0)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
        self.Bind(wx.EVT_KEY_DOWN,self.keypress)
        self.Layout()
        self.Center()

    def keypress(self,event):
        keycode=event.GetKeyCode()
        if keycode==wx.WXK_ESCAPE: self.Close()

class bpgframe(wx.App):
    def __init__(self,parent,title,pngfile):
        super(bpgframe,self).__init__(parent)
        frame=DFrame(None,title,pngfile)
        self.SetTopWindow(frame)
        frame.Show()

if __name__=='__main__':
    if len(argv)==1: exit()
    bpgpath=bpggetcmd(argv[0])
    pngfile=bpgdecode(bpgpath,argv[1])
    if pngfile:
        app=bpgframe(None,realpath(argv[1]),pngfile)
        wxapp=True
        app.MainLoop()
        try: remove(pngfile)
        except: pass
