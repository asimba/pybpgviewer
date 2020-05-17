#ifndef bpgdec_h__
#define bpgdec_h__

  #include <stdlib.h>
  #include <stdio.h>
  #include <math.h>
  #include <inttypes.h>
  #include <string.h>
  #include <malloc.h>
  #include <libbpg.h>

  extern uint8_t *bpg_to_rgb(const char *filename,int *width,int *height);
  extern uint8_t *bpg_to_rgba(const char *filename,int *width,int *height);
  extern uint8_t *bpg_to_rgba_view(const char *filename, int *size);

#endif
