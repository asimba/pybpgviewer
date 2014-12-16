#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import argv,exit
from os import access,R_OK,close,remove
from stat import S_ISREG
from os.path import exists,isfile,dirname,realpath,join
from tempfile import mkstemp
from subprocess import Popen,PIPE,STDOUT
from platform import system
import wx

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
        print 'BPG decoder not found!\n'
        exit()
    bpgpath+=' -o '
    return bpgpath

def bpgdecode(cmd,filename):
    try:
        if not(isfile(filename) and access(filename,R_OK)): exit()
        t,p=mkstemp(suffix='.ppm',prefix='')
        close(t)
        remove(p)
    except: exit()
    cmd+=p+' '+realpath(filename)
    try:
        f=Popen(cmd,shell=True,stdin=None,stdout=None,stderr=None)
        f.wait()
    except:
        print 'BPG decoding error!\n'
        exit()
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
        self.bitmap_text=str(bitmap.GetWidth())+'x'+str(bitmap.GetHeight())
        if bitmap.GetWidth()>crect[2]:
            dx=float(crect[2])/float(bitmap.GetWidth())
        if bitmap.GetHeight()>crect[3]:
            dy=float(crect[3])/float(bitmap.GetHeight())
        if dx>dy:
            x=bitmap.GetWidth()*dy
            y=bitmap.GetHeight()*dy
        else:
            x=bitmap.GetWidth()*dx
            y=bitmap.GetHeight()*dx
        if x and y: bitmap=scale_bitmap(bitmap,x,y)
        self.bitmap=wx.StaticBitmap(self,-1,bitmap)
        self.SetFocus()
        self.bitmap.SetToolTipString(self.bitmap_text)
        grid_sizer=wx.GridSizer(1,1,0,0)
        grid_sizer.Add(self.bitmap,0,wx.ALIGN_CENTER_HORIZONTAL|\
            wx.ALIGN_CENTER_VERTICAL,0)
        self.SetSizer(grid_sizer)
        grid_sizer.Fit(self)
        self.Layout()

class bpgframe(wx.App):
    def __init__(self,parent,title,pngfile):
        super(bpgframe,self).__init__(parent)
        wx.InitAllImageHandlers()
        frame=DFrame(None,title,pngfile)
        self.SetTopWindow(frame)
        frame.Show()

if __name__=='__main__':
    if len(argv)==1: exit()
    bpgpath=bpggetcmd(argv[0])
    pngfile=bpgdecode(bpgpath,argv[1])
    app=bpgframe(None,realpath(argv[1]),pngfile)
    app.MainLoop()
    remove(pngfile)
