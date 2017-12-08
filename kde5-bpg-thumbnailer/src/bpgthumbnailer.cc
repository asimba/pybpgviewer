/*
Copyright (c) 2015 Alexey Simbarsky <asimbarsky@gmail.com>
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
#include "bpgthumbnailer.h"

extern "C"{
#include <libbpg.h>
    Q_DECL_EXPORT ThumbCreator *new_creator(){
        return new BPGThumbnailer;
    }
}

BPGThumbnailer::BPGThumbnailer(){}
BPGThumbnailer::~BPGThumbnailer(){}

bool BPGThumbnailer::create(const QString &path,int w,int h,QImage &img){
    Q_UNUSED(w)
    Q_UNUSED(h)
    bool bRet=false;
    uint8_t *buf;
    BPGDecoderContext *bpgimg;
    BPGImageInfo img_info_s,*img_info=&img_info_s;
    FILE *f;
    f=fopen(path.toUtf8().constData(),"rb");
    if(!f) return false;
    fseek(f,0,SEEK_END);
    int buf_len=ftell(f);
    fseek(f,0,SEEK_SET);
    buf=(uint8_t *)malloc(buf_len);
    if(buf==NULL){
      fclose(f);
      return false;
    }
    if(fread(buf,1,buf_len,f)!=(unsigned int)buf_len){
      fclose(f);
      free(buf);
      return false;
    }
    fclose(f);
    bpgimg=bpg_decoder_open();
    if(bpg_decoder_decode(bpgimg,buf,buf_len)<0){
      free(buf);
      return false;
    }
    free(buf);
    bpg_decoder_get_info(bpgimg,img_info);
    QImage *tmpimg=new QImage(img_info->width,img_info->height,QImage::Format_RGB888);
    if(tmpimg==NULL) return false;
    bpg_decoder_start(bpgimg,BPG_OUTPUT_FORMAT_RGB24);
    for (uint32_t y=0;y<img_info->height;y++) bpg_decoder_get_line(bpgimg,tmpimg->scanLine(y));
    bpg_decoder_close(bpgimg);
    img=tmpimg->scaled(w,h,Qt::KeepAspectRatio);
    delete tmpimg;
    if(!img.isNull()) bRet=true;
    return bRet;
}

ThumbCreator::Flags BPGThumbnailer::flags() const{
    return (Flags)(DrawFrame|BlendIcon);
}
