/*
Copyright (c) 2014-2020 Alexey Simbarsky <asimbarsky@gmail.com>
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of
the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public
License along with this program; if not, write to the Free
Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
Boston, MA 02110-1301, USA.
*/

#include <QImage>
#include <QPainter>
#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "bpg-thumbnailer.h"

extern "C"{
  #include <libbpgdec.h>
  Q_DECL_EXPORT ThumbCreator *new_creator(){
    return new BPGThumbnailer;
  }
}

BPGThumbnailer::BPGThumbnailer(){}
BPGThumbnailer::~BPGThumbnailer(){}

void free_buf(void *buf){ free(buf); }

bool BPGThumbnailer::create(const QString &path,int w,int h,QImage &img){
  Q_UNUSED(w)
  Q_UNUSED(h)
  bool bRet=false;
  int width=0,height=0;
  uint8_t *pixdata=bpg_to_rgba(path.toUtf8().constData(),&width,&height);
  if(pixdata==NULL) return false;
  QImage *tmpimg=new QImage(pixdata,width,height,QImage::Format_RGBA8888,free_buf,pixdata);
  if(tmpimg==NULL) return false;
  img=tmpimg->scaled(w,h,Qt::KeepAspectRatio);
  delete tmpimg;
  if(!img.isNull()) bRet=true;
  return bRet;
}

ThumbCreator::Flags BPGThumbnailer::flags() const{
  return (Flags)(DrawFrame|BlendIcon);
}
