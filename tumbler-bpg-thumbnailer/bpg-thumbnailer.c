/*
Copyright (c) 2011 Nick Schermer <nick@xfce.org>
Copyright (c) 2012 Jannis Pohlmann <jannis@xfce.org>
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

#include <sys/types.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <glib.h>
#include <glib/gi18n.h>
#include <glib-object.h>
#include <tumbler/tumbler.h>
#include <gdk-pixbuf/gdk-pixbuf.h>

#include "libbpg.h"

G_BEGIN_DECLS

#define TYPE_BPG_THUMBNAILER_PROVIDER            (bpg_thumbnailer_provider_get_type())
#define BPG_THUMBNAILER_PROVIDER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj),TYPE_BPG_THUMBNAILER_PROVIDER,BPGThumbnailerProvider))
#define BPG_THUMBNAILER_PROVIDER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST ((klass),TYPE_BPG_THUMBNAILER_PROVIDER,BPGThumbnailerProviderClass))
#define IS_BPG_THUMBNAILER_PROVIDER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj),TYPE_BPG_THUMBNAILER_PROVIDER))
#define IS_BPG_THUMBNAILER_PROVIDER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass),TYPE_BPG_THUMBNAILER_PROVIDER)
#define BPG_THUMBNAILER_PROVIDER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj),TYPE_BPG_THUMBNAILER_PROVIDER,BPGThumbnailerProviderClass))
#define TYPE_BPG_THUMBNAILER            (bpg_thumbnailer_get_type())
#define BPG_THUMBNAILER(obj)            (G_TYPE_CHECK_INSTANCE_CAST((obj),TYPE_BPG_THUMBNAILER,BPGThumbnailer))
#define BPG_THUMBNAILER_CLASS(klass)    (G_TYPE_CHECK_CLASS_CAST((klass),TYPE_BPG_THUMBNAILER,BPGThumbnailerClass))
#define IS_BPG_THUMBNAILER(obj)         (G_TYPE_CHECK_INSTANCE_TYPE((obj),TYPE_BPG_THUMBNAILER))
#define IS_BPG_THUMBNAILER_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE((klass),TYPE_BPG_THUMBNAILER)
#define BPG_THUMBNAILER_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj),TYPE_BPG_THUMBNAILER,BPGThumbnailerClass))

typedef struct _BPGThumbnailerProviderClass BPGThumbnailerProviderClass;
typedef struct _BPGThumbnailerProvider      BPGThumbnailerProvider;
typedef struct _BPGThumbnailerClass         BPGThumbnailerClass;
typedef struct _BPGThumbnailer              BPGThumbnailer;

GType bpg_thumbnailer_provider_get_type(void)G_GNUC_CONST;
void  bpg_thumbnailer_provider_register(TumblerProviderPlugin *plugin);
GType bpg_thumbnailer_get_type(void)G_GNUC_CONST;
void  bpg_thumbnailer_register(TumblerProviderPlugin *plugin);

G_END_DECLS

G_MODULE_EXPORT void tumbler_plugin_initialize(TumblerProviderPlugin *plugin);
G_MODULE_EXPORT void tumbler_plugin_shutdown(void);
G_MODULE_EXPORT void tumbler_plugin_get_types(const GType **types,gint *n_types);

static GType type_list[1];

static GList *bpg_thumbnailer_provider_get_thumbnailers(TumblerThumbnailerProvider *provider){
  BPGThumbnailer     *thumbnailer;
  GList              *thumbnailers=NULL;
  static const gchar *uri_schemes[]={"file",NULL };
  const gchar        *mime_types[]={"image/bpg",NULL};
  thumbnailer=g_object_new(TYPE_BPG_THUMBNAILER,"uri-schemes",uri_schemes,"mime-types",mime_types,NULL);
  thumbnailers=g_list_append(thumbnailers,thumbnailer);
  return thumbnailers;
}

static void bpg_thumbnailer_provider_thumbnailer_provider_init(TumblerThumbnailerProviderIface *iface){
  iface->get_thumbnailers=bpg_thumbnailer_provider_get_thumbnailers;
}
static void bpg_thumbnailer_provider_class_init(BPGThumbnailerProviderClass *klass){}
static void bpg_thumbnailer_provider_class_finalize(BPGThumbnailerProviderClass *klass){}
static void bpg_thumbnailer_provider_init(BPGThumbnailerProvider *provider){}

struct _BPGThumbnailerProviderClass{GObjectClass __parent__;};
struct _BPGThumbnailerProvider{GObject __parent__;};

G_DEFINE_DYNAMIC_TYPE_EXTENDED(BPGThumbnailerProvider,bpg_thumbnailer_provider,G_TYPE_OBJECT,0,
                               TUMBLER_ADD_INTERFACE (TUMBLER_TYPE_THUMBNAILER_PROVIDER,bpg_thumbnailer_provider_thumbnailer_provider_init));

void bpg_thumbnailer_provider_register(TumblerProviderPlugin *plugin){
  bpg_thumbnailer_provider_register_type(G_TYPE_MODULE(plugin));
}

void tumbler_plugin_initialize(TumblerProviderPlugin *plugin){
  const gchar *mismatch;
  mismatch=tumbler_check_version(TUMBLER_MAJOR_VERSION,TUMBLER_MINOR_VERSION,TUMBLER_MICRO_VERSION);
  if(G_UNLIKELY(mismatch!=NULL)){
      g_warning(_("Version mismatch: %s"),mismatch);
      return;
    }
  bpg_thumbnailer_register(plugin);
  bpg_thumbnailer_provider_register(plugin);
  type_list[0]=TYPE_BPG_THUMBNAILER_PROVIDER;
}

void tumbler_plugin_shutdown(void){}

void tumbler_plugin_get_types(const GType **types,gint *n_types){
  *types=type_list;
  *n_types=G_N_ELEMENTS(type_list);
}

static void bpg_thumbnailer_create(TumblerAbstractThumbnailer *thumbnailer,GCancellable *cancellable,TumblerFileInfo *info);

struct _BPGThumbnailerClass{TumblerAbstractThumbnailerClass __parent__;};
struct _BPGThumbnailer{TumblerAbstractThumbnailer __parent__;};

G_DEFINE_DYNAMIC_TYPE(BPGThumbnailer,bpg_thumbnailer,TUMBLER_TYPE_ABSTRACT_THUMBNAILER);

void bpg_thumbnailer_register(TumblerProviderPlugin *plugin){
  bpg_thumbnailer_register_type (G_TYPE_MODULE (plugin));
}

static void bpg_thumbnailer_class_init(BPGThumbnailerClass *klass){
  TumblerAbstractThumbnailerClass *abstractthumbnailer_class;
  abstractthumbnailer_class=TUMBLER_ABSTRACT_THUMBNAILER_CLASS(klass);
  abstractthumbnailer_class->create=bpg_thumbnailer_create;
}

static void bpg_thumbnailer_class_finalize(BPGThumbnailerClass *klass){}
static void bpg_thumbnailer_init(BPGThumbnailer *thumbnailer){}

static GdkPixbuf *scale_pixbuf(GdkPixbuf *source,gint dest_width,gint dest_height){
  gdouble wratio;
  gdouble hratio;
  gint    source_width;
  gint    source_height;
  source_width=gdk_pixbuf_get_width(source);
  source_height=gdk_pixbuf_get_height(source);
  if (source_width<=dest_width && source_height<=dest_height) return g_object_ref(source);
  wratio=(gdouble)source_width/(gdouble)dest_width;
  hratio=(gdouble)source_height/(gdouble)dest_height;
  if(hratio>wratio) dest_width=rint(source_width/hratio);
  else dest_height=rint(source_height/wratio);
  return gdk_pixbuf_scale_simple(source,MAX(dest_width,1),MAX(dest_height,1),GDK_INTERP_BILINEAR);
}

static void free_buffer(guchar *pixels,gpointer data){g_free (pixels);}

static GdkPixbuf *gdkpixbuf_from_bpg(const char *filename){
    uint8_t *buf;
    BPGDecoderContext *img;
    BPGImageInfo img_info_s,*img_info=&img_info_s;
    FILE *f;
    f=fopen(filename,"rb");
    if(!f) return NULL;
    fseek(f,0,SEEK_END);
    int buf_len=ftell(f);
    fseek(f,0,SEEK_SET);
    buf=malloc(buf_len);
    if(buf==NULL){
      fclose(f);
      return NULL;
    }
    if(fread(buf,1,buf_len,f)!=buf_len){
      fclose(f);
      free(buf);
      return NULL;
    }
    fclose(f);
    img=bpg_decoder_open();
    if(bpg_decoder_decode(img,buf,buf_len)<0){
      free(buf);
      return NULL;
    }
    free(buf);
    bpg_decoder_get_info(img,img_info);
    guchar *pixdata=(guchar *)malloc(img_info->width*img_info->height*3);
    if(pixdata==NULL) return NULL;
    bpg_decoder_start(img,BPG_OUTPUT_FORMAT_RGB24);
    int shift=img_info->width*3;
    guchar *pixpntr=pixdata;
    int y;
    for (y=0;y<img_info->height;y++){
        bpg_decoder_get_line(img,pixpntr);
        pixpntr+=shift;
    };
    bpg_decoder_close(img);
    GdkPixbuf *pixbuf=gdk_pixbuf_new_from_data(pixdata,GDK_COLORSPACE_RGB,0,8,img_info->width,img_info->height,shift,free_buffer,NULL);
    return pixbuf;
}

static void bpg_thumbnailer_create(TumblerAbstractThumbnailer *thumbnailer,GCancellable *cancellable, TumblerFileInfo *info){
  TumblerThumbnailFlavor *flavor;
  TumblerImageData        data;
  TumblerThumbnail       *thumbnail;
  const gchar            *uri;
  gchar                  *path;
  GdkPixbuf              *pixbuf = NULL;
  GError                 *error = NULL;
  GFile                  *file;
  gint                    height;
  gint                    width;
  GdkPixbuf              *scaled;
  g_return_if_fail(IS_BPG_THUMBNAILER(thumbnailer));
  g_return_if_fail(cancellable==NULL || G_IS_CANCELLABLE(cancellable));
  g_return_if_fail(TUMBLER_IS_FILE_INFO(info));
  if(g_cancellable_is_cancelled(cancellable)) return;
  uri=tumbler_file_info_get_uri(info);
  file=g_file_new_for_uri(uri);
  thumbnail=tumbler_file_info_get_thumbnail(info);
  g_assert(thumbnail!=NULL);
  flavor=tumbler_thumbnail_get_flavor(thumbnail);
  g_assert(flavor!=NULL);
  tumbler_thumbnail_flavor_get_size(flavor,&width,&height);
  g_object_unref(flavor);

  path=g_file_get_path(file);
  if(path!=NULL && g_path_is_absolute(path)){
      pixbuf=gdkpixbuf_from_bpg(path);
      if(pixbuf==NULL){
          g_set_error_literal(&error,TUMBLER_ERROR,TUMBLER_ERROR_NO_CONTENT,
                              _("Thumbnail could not be inferred from file contents"));
        }
  }else{
      g_set_error_literal(&error,TUMBLER_ERROR,TUMBLER_ERROR_UNSUPPORTED,
                          _("Only local files are supported"));
  }
  g_free(path);
  g_object_unref(file);

  if(pixbuf!=NULL){
      scaled=scale_pixbuf(pixbuf,width,height);
      g_object_unref(pixbuf);
      pixbuf=scaled;
      data.data=gdk_pixbuf_get_pixels(pixbuf);
      data.has_alpha=gdk_pixbuf_get_has_alpha(pixbuf);
      data.bits_per_sample=gdk_pixbuf_get_bits_per_sample(pixbuf);
      data.width=gdk_pixbuf_get_width(pixbuf);
      data.height=gdk_pixbuf_get_height(pixbuf);
      data.rowstride=gdk_pixbuf_get_rowstride(pixbuf);
      data.colorspace=(TumblerColorspace)gdk_pixbuf_get_colorspace(pixbuf);
      tumbler_thumbnail_save_image_data(thumbnail,&data,tumbler_file_info_get_mtime(info),NULL,&error);
  }

  if(error!=NULL){
      g_signal_emit_by_name(thumbnailer,"error",uri,error->code,error->message);
      g_error_free (error);
  }else{
      g_signal_emit_by_name(thumbnailer,"ready",uri);
      g_object_unref(pixbuf);
  }
  g_object_unref (thumbnail);
}
