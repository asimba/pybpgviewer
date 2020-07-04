/*
Copyright (c) 2014-2020, Alexey Simbarsky
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
*/

#include <sys/types.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#ifdef __cplusplus
extern "C"{
#endif
#include <libbpg.h>
#ifdef __cplusplus
}
#endif
#include "bpgdec.h"

DLL_EXPORT uint8_t *bpg_to_rgb(const char *filename,int *width,int *height){
  FILE *f=fopen(filename,"rb");
  uint8_t *ret=NULL;
  if(f){
    fseek(f,0,SEEK_END);
    int buf_len=ftell(f);
    fseek(f,0,SEEK_SET);
    uint8_t *buf=(uint8_t *)malloc(buf_len);
    if(buf){
      if(fread(buf,1,buf_len,f)==buf_len){
        BPGDecoderContext *img=bpg_decoder_open();
        if(bpg_decoder_decode(img,buf,buf_len)>=0){
          BPGImageInfo img_info_s,*img_info=&img_info_s;
          BPGDecoderOutputFormat out_fmt=BPG_OUTPUT_FORMAT_RGB24;
          bpg_decoder_get_info(img,img_info);
          *width=img_info->width;
          *height=img_info->height;
          ret=(uint8_t *)malloc(img_info->width*img_info->height*3);
          if(ret&&(bpg_decoder_start(img,out_fmt)>=0)){
            int line_size=3*img_info->width;
            uint8_t *write_ptr=ret;
            for(int y=0;y<img_info->height; y++){
              bpg_decoder_get_line(img,write_ptr);
              write_ptr+=line_size;
            };
          };
        };
        bpg_decoder_close(img);
      };
      free(buf);
    };
    fclose(f);
  };
  return ret;
}

DLL_EXPORT uint8_t *bpg_to_rgba(const char *filename,int *width,int *height){
  FILE *f=fopen(filename,"rb");
  uint8_t *ret=NULL;
  if(f){
    fseek(f,0,SEEK_END);
    int buf_len=ftell(f);
    fseek(f,0,SEEK_SET);
    uint8_t *buf=(uint8_t *)malloc(buf_len);
    if(buf){
      if(fread(buf,1,buf_len,f)==buf_len){
        BPGDecoderContext *img=bpg_decoder_open();
        if(bpg_decoder_decode(img,buf,buf_len)>=0){
          BPGImageInfo img_info_s,*img_info=&img_info_s;
          BPGDecoderOutputFormat out_fmt=BPG_OUTPUT_FORMAT_RGBA32;
          bpg_decoder_get_info(img,img_info);
          *width=img_info->width;
          *height=img_info->height;
          ret=(uint8_t *)malloc(img_info->width*img_info->height*4);
          if(ret&&(bpg_decoder_start(img,out_fmt)>=0)){
            int line_size=4*img_info->width;
            uint8_t *write_ptr=ret;
            for(int y=0;y<img_info->height; y++){
              bpg_decoder_get_line(img,write_ptr);
              write_ptr+=line_size;
            };
          };
        };
        bpg_decoder_close(img);
      };
      free(buf);
    };
    fclose(f);
  };
  return ret;
}

DLL_EXPORT uint8_t *bpg_to_rgba_view(const char *filename,int *rsize){
  FILE *f=fopen(filename,"rb");
  uint8_t *ret=NULL;
  int size=0;
  if(f){
    fseek(f,0,SEEK_END);
    int buf_len=ftell(f);
    fseek(f,0,SEEK_SET);
    uint8_t *buf=(uint8_t *)malloc(buf_len);
    if(buf){
      if(fread(buf,1,buf_len,f)==buf_len){
        BPGDecoderContext *img=bpg_decoder_open();
        if(bpg_decoder_decode(img,buf,buf_len)>=0){
          BPGImageInfo img_info_s,*img_info=&img_info_s;
          BPGDecoderOutputFormat out_fmt=BPG_OUTPUT_FORMAT_RGBA32;
          int w,h,y,pnum,pden;
          bpg_decoder_get_info(img,img_info);
          w=img_info->width;
          h=img_info->height;
          size+=(sizeof(int)+w*h)*4;
          ret=(uint8_t *)malloc(size);
          if(ret){
            int free_size=size,line_size=4*w,page_size=2*sizeof(int)+4*w*h;
            uint8_t *write_ptr=ret;
            memcpy(write_ptr,&w,sizeof(int));
            write_ptr+=sizeof(int);
            memcpy(write_ptr,&h,sizeof(int));
            write_ptr+=sizeof(int);
            free_size-=(2*sizeof(int));
            while(1){
              if(bpg_decoder_start(img,out_fmt)<0) break;
              if(free_size<=0){
                size+=page_size;
                free_size+=page_size;
                int shift=(int)(write_ptr-ret);
                ret=(uint8_t *)realloc(ret,size);
                if(!ret){
                  size=0;
                  break;
                };
                write_ptr=ret+shift;
              };
              bpg_decoder_get_frame_duration(img,&pnum,&pden);
              memcpy(write_ptr,&pnum,sizeof(int));
              write_ptr+=sizeof(int);
              memcpy(write_ptr,&pden,sizeof(int));
              write_ptr+=sizeof(int);
              free_size-=(2*sizeof(int));
              for(y=0;y<h; y++){
                bpg_decoder_get_line(img,write_ptr);
                write_ptr+=line_size;
                free_size-=line_size;
              };
            };
          }
          else size=0;
        };
        bpg_decoder_close(img);
      };
      free(buf);
    };
    fclose(f);
  };
  *rsize=size;
  return ret;
}

DLL_EXPORT bool bpgdec_buffer_getwh(void *buffer,int buf_len,int &w,int &h){
    BPGDecoderContext *img;
    BPGImageInfo img_info;
    img=bpg_decoder_open();
    if(bpg_decoder_decode(img,(uint8_t*)buffer,buf_len)<0) return false;
    bpg_decoder_get_info(img,&img_info);
    bpg_decoder_close(img);
    w=img_info.width;
    h=img_info.height;
    return true;
}

DLL_EXPORT bool bpgdec_buffer(void *buffer,int buf_len,void *pixdata,int w,int h){
    if(pixdata==NULL) return false;
    BPGDecoderContext *img;
    img=bpg_decoder_open();
    if(bpg_decoder_decode(img,(uint8_t*)buffer,buf_len)<0) return false;
    bpg_decoder_start(img,BPG_OUTPUT_FORMAT_RGB24);
    int shift=w*3;
    uint8_t *pixpntr=(uint8_t *)pixdata;
    for(int y=0;y<h;y++){
        bpg_decoder_get_line(img,pixpntr);
        pixpntr+=shift;
    };
    bpg_decoder_close(img);
    return true;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL,DWORD fdwReason,LPVOID lpvReserved){
    return TRUE;
}
