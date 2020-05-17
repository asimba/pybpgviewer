#include "libbpgdec.h"

uint8_t *bpg_to_rgb(const char *filename,int *width,int *height){
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

uint8_t *bpg_to_rgba(const char *filename,int *width,int *height){
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

uint8_t *bpg_to_rgba_view(const char *filename,int *rsize){
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
                ret=(uint8_t *)realloc(ret,size);
                if(!ret){
                  size=0;
                  break;
                };
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
