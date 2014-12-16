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
    if system()=="Windows":
        bpgpath=realpath('bpgdec.exe')
    else:
        bpgpath='/usr/bin/bpgdec'
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
        t,p=mkstemp(suffix='.png',prefix='')
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

class DPanel(wx.Panel):
    def __init__(self,parent,path):
        super(DPanel,self).__init__(parent,-1)
        bitmap=wx.Bitmap(path)
        crect=wx.Display().GetClientArea()
        dx,dy=0.0,0.0
        x,y=0,0
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
        control=wx.StaticBitmap(self,-1,bitmap)
        control.SetPosition((0,0))

class DFrame(wx.Frame):
    def __init__(self,parent,title,pngfile):
        super(DFrame,self).__init__(parent, title=title)
        self.Maximize()
        self.frame=DPanel(self,pngfile)
    
if __name__=='__main__':
    if len(argv)==1: exit()
    bpgpath=bpggetcmd(argv[0])
    pngfile=bpgdecode(bpgpath,argv[1])
    app=wx.App()
    frame=DFrame(None,realpath(argv[1]),pngfile)
    frame.Show()
    app.MainLoop()
    remove(pngfile)
