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
import locale,pickle,base64,zlib

if system()=="Windows":
    osflag=False
    from subprocess import STARTUPINFO
else:
    osflag=True
    from os import mkfifo,O_RDONLY,O_NONBLOCK
    from os import open as osopen
    from os import read as osread
    from os import close as osclose
    import errno

wxapp=False

class translator():
    def __init__(self):
        self.voc={}
        self.locale=locale.getdefaultlocale()

    def find(self,key):
        if self.voc.has_key(key):
            if self.voc[key].has_key(self.locale[0]):
                return self.voc[key][self.locale[0]].encode(self.locale[1])
        return key

t=translator()

t.voc=pickle.loads(zlib.decompress(base64.decodestring("\
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\
DI4er5Etym2dIo//B+VVV70=\
")))

def _(s):
    return t.find(s)

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
        MessageBox=ctypes.windll.user32.MessageBoxA
        MessageBox(0,msg,_('Error!'),16)

if not(osflag):
    try: import win32file,win32pipe
    except:
        msg=_("Please install")+" Python for Windows Extensions\n\
(http://sourceforge.net/projects/pywin32/)!"
        errmsg(msg)
        raise RuntimeError(msg)
    
try: import wx
except:
    msg=_("Please install")+" wxPython 2.8 "+_("or higher")+\
        " (http://www.wxpython.org/)!\n"+\
        _("Under Debian or Ubuntu you may try")+\
        ": sudo aptitude install python-wxgtk2.8"
    errmsg(msg)
    raise RuntimeError(msg)

try: import Image
except:
    msg=_("Please install")+" Python Imaging Library (PIL) 1.1.7 "+\
        _("or higher")+" \n(http://www.pythonware.com/products/pil/)!\n"+\
        _("Under Debian or Ubuntu you may try")+\
        ": sudo aptitude install python-imaging"
    errmsg(msg)
    raise RuntimeError(msg)

from wx.lib.embeddedimage import PyEmbeddedImage

bpglogo=PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABXAvmHAAAABHNCSVQICAgIfAhkiAAAAAlw"
    "SFlzAAABBgAAAQYBzdMzvAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoA"
    "AAa+SURBVGiB3ZpfbFPXHcc/59pOmjgozmxD0oSQRBlgddICYUpCpyotHSIPXbVqATa11ah4"
    "idYItWq7tZUQ6pq22gMSK1WqimoToEkLVfuABChPlgYh0iCiRTQVFUl8jWt3IcQuSWzHuT57"
    "cGJ843sdm+ZP1++bf+d7zvn+7u+c3/n5niuklOTCmTNnisbHRTvIp4DtwMNAFVCcs2PhiANB"
    "4BtgCMRZt1t6Ozs7Z3N1EmYOvP/++WKLZfpFkG8CFcssNl9MgujRNPvx7u6OuBHB0IHe3n+1"
    "Sqn8E6hfaYV5YlSI5O+7uvYNLm5QFht6e/uelVLx8sMRD1AvpeLt7e17dnGDLgIp8eJUvqPa"
    "bFZsNuv3UpZIzJFIzOXNF0I+19W193T694ID88vGS47N6XCU4XJV4HCU4XCso7T0oQdXnoGZ"
    "mRjh8D3C4Snu3JkkHJ7KRY8LkWxfWE5CSjm/YaeGMVk2FouCx1NPQ0P1sgheCiMjAYaHR9G0"
    "pBllVNPKPN3dHXElJXD6RUzEO53ltLc3r5p4gIaGatrbm3E6y80o9fOaEX19fUXj44QwSJVO"
    "Zzk7d/4cIVZQbQ5ICQMDnzMxETFqnnS7qVRSh1S2eItFoalp85qJBxACmpo2Y7FkJUuAivFx"
    "0a7Mn7BZ8HjqsdtLVlZhHrDbS/B4zDK6fEohVR7o4HCUreqaXwoNDdU4HGVGTdsVUrWNDi7X"
    "WlUO5jDR9LBCqjDTwcTbNYWJpioFg4PL4Vi34oIKhYmm4qztbbNZl+2EXU6Ulj5kWLZkWZaq"
    "bd555y/cunVLZysvL+f119/E7V4PgN+vcuTI4ay+jz76S1544WD696VLFzl16h+6WsjpdPLa"
    "a3/G5XJn9bfZrFl1U8GV2GeffUooFMyyOxwVHD58BICvvhqmv/9CFqe//wJPPLGLurp6rl//"
    "gv37f2s4x9xcgqNH/5aXnoIciMfjfPttCKfTSUlJybxtlvHx/6Jp95+Mz+czHWNuTgPg8uVL"
    "phyLJX9ZBTng96tIKfnwwxO0trYBIKWktbVZN6nPN8bmzVs4d64/bTt58u+89dYRrFYLAIOD"
    "g7S17eTo0WO6OQ4ePIDNVrQyDoyNjQGwaVNd2iaEIBaLUVNTo3OgtraW4uL7Ca601I6iKFRX"
    "p3g3blznySd3U1OzUTfHtm3b2b//dyvjgM83RlFREZWVlWlbOBzm7t27bNmyNW1TVR+PPdau"
    "63v7tp/KykpsNhuzs7OEQiHq6uqy5nj33b8WIqkwB1TVh91u5/Tpk2nb1atXKCtbR0tLCwDJ"
    "ZBJVVdm4sVbX98qV/6Qjd/u2n2QySW3tJgCmpu4RjUbT3IqKn2C15iet4AhMTk7yxht/Stss"
    "FgvHjh3HarUBEAwGSSQSfPzxR3zySR8A0WiU0dERursPpR8E3F+KL710iAsXzqXHHBr6Ip2S"
    "l92BxdA0LZ2RMsUFAgECgYCO+/jju+Y5KkA6An6/muaUlJTkLR4KcEBKiaqqdHX9kaef/g2Q"
    "Wi4vv3wIr9fL7t17gPtOZm5qIRT27t1Hc/OOeY4Pl8tNaWkpALt2/YrW1jYuXvw3S71oe2AH"
    "QqEQs7Oz7NjxCx555Gdpe1VV1aIzYIwNGyq5fPmK6Viq6tNt4FdfTS3JAweeQwjDPy+myJu9"
    "8GQXwr6AYDCIw+HI4PkMs0smVNWXNc5C302bsu25ULADmdklEonw9dc3qaur1/EyzwkjhELB"
    "LI6UEr9fpbHxp/lKAgpYQj6fDyEEzzzza50QTdPSp3KKN8aePR05x4pGo/T2HufEiY909lgs"
    "RktLm0kvYxTgwBhSSr788obOvnWrh/r6BgC++y5CJBJZMgLxeJxkMkksFtPZXS4XjY2N+UoC"
    "HmAJZaKpaRs9Pe9lcFIpNHNJGeH55/+AWPS6Y/36Dbz99nsmPcwhPvigT5e3bDYrHR07Cx5o"
    "NXD+/EDW/4GsCCQSc8zMxBab1xwzMzHDl8AKqZsRHcLhe6uhqSCYaIorpK51FpFzvh1eE5ho"
    "Ciqk7qR0uHNncsUFFQoTTd8owNBiazg8xchIwIC/NhgZCZhFYEgBcdaoZXh4lOnpqFHTqmJ6"
    "Osrw8KhJqziruN3SC2TFR9OSXLt2kwKLw2WFlHDt2k2zi45Jt1t6ldQ9rOgxYkxMRBgY+HxN"
    "IjE9Hc11NwCIns7OzlkFQNPsxwHDOE1MRPB6r67qnhgZCeD1Xs0hntF5zT+SS74F/F9fsy5g"
    "3okTLP+3EN8XcSHkwUzx8GP81ACgq2vfoKaVeUC8gkGKXUVMgnhF08o8RuIhx9cqC/ihf27z"
    "P7EZ5A4mdx+jAAAAAElFTkSuQmCC")

def errmsgbox(msg):
    if not(wxapp): app=wx.App(0)
    wx.MessageBox(msg,_('Error!'),wx.OK|wx.ICON_ERROR)
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
        msg=_('BPG decoder not found!\n')
        print msg
        errmsgbox(msg)
        exit()
    bpgpath+=' -o '
    return bpgpath

class DFrame(wx.Frame):
    def bpgdecode(self,cmd,filename):
        msg=None
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
                    if osflag:
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
                if err: msg=_('BPG decoding error!\n')
        else: msg=_('File')+' \"%s\" '%filename+_('is not a BPG-File!')
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

    def deftitle(self):
        self.stitle(_('Press Ctrl+O to open BPG file...'))

    def getcsize(self):
        cr=wx.Display().GetClientArea()
        cw=self.GetSize()
        cc=self.GetClientSize()
        return cr[2]-cr[0]-cw[0]+cc[0],cr[3]-cr[1]-cw[1]+cc[1]

    def scalebitmap(self,width,height):
        if self.img:
            r=self.img.resize((int(width),int(height)),Image.NEAREST)
            return wx.BitmapFromBuffer(r.size[0],\
                        r.size[1],r.convert("RGB").tostring())
        else: return None

    def showbitmap(self,bitmap):
        if bitmap==None: self.showempty()
        else:
            self.bitmap.SetBitmap(bitmap)
            self.imginfo='%.2f'%self.scale+'%@'+self.bitmap_text
            self.bitmap.SetToolTipString(self.imginfo)
            x,y=bitmap.GetSize()
            self.panel.SetVirtualSize((x,y))
            self.panel.SetScrollbars(1,1,x,y)
            self.panel.SetScrollRate(1,1)
            cx,cy=self.getcsize()
            if x<=cx and y<=cy and not(self.IsMaximized()) and\
                not(self.IsFullScreen()):
                self.panel.SetInitialSize(size=(x,y))
                self.panel.SetClientSize((x,y))
                self.Layout()
                self.Fit()
                self.Center()
                return
            self.Layout()

    def emptybitmap(self):
        buffer=wx.EmptyBitmap(400,300)
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
            else: return wx.BitmapFromBuffer(self.img.size[0],\
                    self.img.size[1],self.img.convert("RGB").tostring())
        return None

    def showimage(self,filename):
        if type(filename) is unicode: filename=filename.encode(self.codepage)
        if len(filename) and self.bpgdecode(self.bpgpath,filename):
            if len(self.filelist)==0:
                self.filelist=self.getfilelist(dirname(realpath(filename)))
                self.index=0
                while(True):
                    if self.filelist[self.index]==realpath(filename): break
                    else: self.index+=1
                    if self.index>=len(self.filelist): break
        self.showbitmap(self.autoscaled())
        if len(self.imginfo): self.stitle(self.filelist[self.index]+\
            ' ('+self.imginfo+')')
        else: self.deftitle()

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

    def __init__(self,parent,scriptpath,title):
        kwds={}
        args=[]
        kwds["style"]=wx.DEFAULT_FRAME_STYLE
        kwds["title"]=title
        kwds["parent"]=parent
        wx.Frame.__init__(self,*args,**kwds)
        self.max=False
        self.codepage=locale.getdefaultlocale()[1]
        self.bpgpath=bpggetcmd(scriptpath)
        self.scale=100.0
        self.autoscale=100.0
        self.bitmap_text=''
        self.img=None
        self.imginfo=''
        self.fifo=''
        t,self.fifo=mkstemp(suffix='.ppm',prefix='')
        close(t)
        remove(self.fifo)
        if osflag:
            try: mkfifo(self.fifo,0700)
            except:
                msg=_('Unable to create FIFO file!')
                print msg
                errmsgbox(msg)
                exit()
        self.filelist=[]
        self.index=0
        self.SetInitialSize(size=(400,300))
        self.panel=wx.ScrolledWindow(self,-1,style=wx.WANTS_CHARS)
        self.sizer=wx.BoxSizer(wx.HORIZONTAL)
        self.psizer=wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.panel,1,wx.CENTER|wx.EXPAND,0)
        self.bitmap=wx.StaticBitmap(self.panel,bitmap=self.emptybitmap())
        self.psizer.Add(self.bitmap,1,wx.CENTER|wx.EXPAND,0)
        self.SetSizer(self.sizer)
        self.panel.SetSizer(self.psizer)
        self.showimage(title)
        self.sizer.Fit(self)
        self.panel.Bind(wx.EVT_KEY_DOWN,self.keydown)
        self.panel.Bind(wx.EVT_CHAR,self.keychar)
        self.panel.Bind(wx.EVT_MOTION,self.drag)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.bitmap.Bind(wx.EVT_MOTION,self.drag)
        self.bitmap.Bind(wx.EVT_MOUSE_EVENTS,self.drag)
        self.Bind(wx.EVT_SIZE,self.fresize)
        if osflag: self._icon=bpglogo.GetIcon()
        else:
            tmp_icon=bpglogo.GetImage()
            tmp_icon.Rescale(32,32,wx.IMAGE_QUALITY_HIGH)
            self._icon=wx.EmptyIcon()
            self._icon.CopyFromBitmap(wx.BitmapFromImage(tmp_icon))
        try: self.SetIcon(self._icon)
        except: pass
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
        if self.img:
            if event.Dragging():
                pos=event.GetPosition()
                if self.mpos!=None:
                    dx=self.mpos[0]-pos[0]
                    dy=self.mpos[1]-pos[1]
                    self.panel.Scroll(self.panel.GetScrollPos(wx.HORIZONTAL)+\
                        dx,self.panel.GetScrollPos(wx.VERTICAL)+dy)
                return
            if event.LeftDown():
                self.mpos=event.GetPosition()
                event.Skip()
            if event.LeftUp():
                self.mpos=None
                event.Skip()
        if event.ButtonDClick():
            self.maximize()
            return

    def rotate(self,dir):
        if self.img:
            self.stitle(_('Rotating...'))
            if dir: self.img=self.img.rotate(-90)
            else: self.img=self.img.rotate(90)
            if self.img:
                if self.scale!=100.0:
                    x=self.img.size[0]*(self.scale/100.0)
                    y=self.img.size[1]*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else: self.showbitmap(wx.BitmapFromBuffer(self.img.size[0],\
                        self.img.size[1],self.img.convert("RGB").tostring()))
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
        if self.scale==self.autoscale: self.showbitmap(self.autoscaled())
        if len(self.imginfo): self.stitle(self.filelist[self.index]+\
            ' ('+self.imginfo+')')
        else: self.deftitle()

    def maximize(self):
        if not(self.IsFullScreen()):
            if self.IsMaximized() or self.max:
                self.max=False
                self.Maximize(False)
            else:
                self.max=True
                self.Maximize()

    def keydown(self,event):
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
            _('Ctrl-O - open BPG image file\n')+\
            _('Ctrl-S - save a copy of the opened file as a PNG file\n')+\
            _('Ctrl-C - save a copy of the opened file\n')+\
            _('Ctrl-R - rotate 90 degrees clockwise\n')+\
            _('Ctrl-L - rotate 90 degrees counterclockwise\n')+\
            _('Ctrl-F - toggle full screen mode\n')+\
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
        try: cf_code=wx.WXK_CONTROL_F
        except: cf_code=6
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
            openFileDialog = wx.FileDialog(self,_('Open BPG file'),"","",\
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
        if keycode==ord('+'):
            if self.img and self.scale<100.0:
                self.stitle(_('Zooming in...'))
                self.scale+=5.0
                if self.scale>100.0: self.scale=100.0
                if self.scale!=100.0:
                    x=self.img.size[0]*(self.scale/100.0)
                    y=self.img.size[1]*(self.scale/100.0)
                    self.showbitmap(self.scalebitmap(x,y))
                else: self.showbitmap(wx.BitmapFromBuffer(self.img.size[0],\
                        self.img.size[1],self.img.convert("RGB").tostring()))
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
                else: self.showbitmap(wx.BitmapFromBuffer(self.img.size[0],\
                        self.img.size[1],self.img.convert("RGB").tostring()))
                if len(self.imginfo): self.stitle(self.filelist[self.index]+\
                    ' ('+self.imginfo+')')
                else: self.deftitle()
            return
        if keycode==ord('*'):
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
