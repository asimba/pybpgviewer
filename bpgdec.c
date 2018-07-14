/*
 * BPG decoder command line utility
 *
 * Copyright (c) 2014 Fabrice Bellard
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <inttypes.h>
#include "libbpg.h"

static void rgba_save(BPGDecoderContext *img, const char *filename){
    BPGImageInfo img_info_s,*img_info=&img_info_s;
    BPGDecoderOutputFormat out_fmt=BPG_OUTPUT_FORMAT_RGBA32;
    FILE *f;
    int w,h,y,pnum,pden;
    bpg_decoder_get_info(img,img_info);
    w=img_info->width;
    h=img_info->height;
    f=fopen(filename,"wb");
    if(!f) exit(1);
    uint8_t *rgba_line=malloc(4*w);;
    fwrite(&w,sizeof(int),1,f);
    fwrite(&h,sizeof(int),1,f);
    while(1){
      if(bpg_decoder_start(img,out_fmt)<0) break;
      bpg_decoder_get_frame_duration(img,&pnum,&pden);
      fwrite(&pnum,sizeof(int),1,f);
      fwrite(&pden,sizeof(int),1,f);
      for(y=0;y<h; y++){
        bpg_decoder_get_line(img,rgba_line);
        fwrite(rgba_line,1,w*4,f);
      };
    };
    fclose(f);
    free(rgba_line);
}

int main(int argc, char **argv){
    FILE *f=fopen(argv[1],"rb");
    if(!f) exit(1);
    fseek(f,0,SEEK_END);
    int buf_len=ftell(f);
    fseek(f,0,SEEK_SET);
    uint8_t *buf=malloc(buf_len);
    if(fread(buf,1,buf_len,f)!=buf_len) exit(1);
    fclose(f);
    BPGDecoderContext *img=bpg_decoder_open();
    if(bpg_decoder_decode(img,buf,buf_len)<0) exit(1);
    free(buf);
    rgba_save(img,argv[2]);
    bpg_decoder_close(img);
    return 0;
}
