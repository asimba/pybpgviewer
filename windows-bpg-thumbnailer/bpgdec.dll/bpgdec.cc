/*
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
