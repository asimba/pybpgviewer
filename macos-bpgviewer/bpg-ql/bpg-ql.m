#include <CoreFoundation/CoreFoundation.h>
#include <CoreServices/CoreServices.h>
#include <QuickLook/QuickLook.h>
#import <Foundation/Foundation.h>
#include "libbpg.h"

OSStatus GeneratePreviewForURL(void *thisInterface, QLPreviewRequestRef preview, CFURLRef url, CFStringRef contentTypeUTI, CFDictionaryRef options);
void CancelPreviewGeneration(void *thisInterface, QLPreviewRequestRef preview);
OSStatus GenerateThumbnailForURL(void *thisInterface, QLThumbnailRequestRef thumbnail, CFURLRef url, CFStringRef contentTypeUTI, CFDictionaryRef options, CGSize maxSize);
void CancelThumbnailGeneration(void *thisInterface, QLThumbnailRequestRef thumbnail);

CGImageRef CreateImageForURL(CFURLRef url)
{
    NSData *fileData = [[NSData alloc] initWithContentsOfURL:(__bridge NSURL *)url];
    BPGDecoderContext *img = bpg_decoder_open();
    if (bpg_decoder_decode(img, fileData.bytes, (int)fileData.length) < 0) return NULL;
    BPGImageInfo img_info;
    bpg_decoder_get_info(img, &img_info);
    int w = img_info.width;
    int h = img_info.height;
    uint8_t *rgb_data = malloc(3 * w * h);
    bpg_decoder_start(img, BPG_OUTPUT_FORMAT_RGB24);
    for (int y = 0; y < h; ++y) bpg_decoder_get_line(img, &rgb_data[y * w * 3]);
    bpg_decoder_close(img);
    CGDataProviderRef data_provider = CGDataProviderCreateWithData(NULL, rgb_data, 3 * w * h, NULL);
    CGColorSpaceRef colorSpace = CGColorSpaceCreateDeviceRGB();
    CGImageRef cgImage = CGImageCreate(w, h, 8, 24, 3 * w, colorSpace,
        kCGBitmapByteOrderDefault | kCGImageAlphaNone,data_provider,NULL,true,kCGRenderingIntentDefault);
    CGColorSpaceRelease(colorSpace);
    free(rgb_data);
    return cgImage;
}

OSStatus GeneratePreviewForURL(void *thisInterface, QLPreviewRequestRef preview, CFURLRef url, CFStringRef contentTypeUTI, CFDictionaryRef options)
{
    CGImageRef image = CreateImageForURL(url);
    if (!image) return -1;
    CGFloat width = CGImageGetWidth(image);
    CGFloat height = CGImageGetHeight(image);
    @autoreleasepool {
        NSDictionary *newOpt = [NSDictionary  dictionaryWithObjectsAndKeys:(NSString *)[(__bridge NSDictionary *)options objectForKey:(NSString *)kQLPreviewPropertyDisplayNameKey], kQLPreviewPropertyDisplayNameKey, [NSNumber numberWithFloat:width], kQLPreviewPropertyWidthKey, [NSNumber numberWithFloat:height], kQLPreviewPropertyHeightKey, nil];
        CGContextRef ctx = QLPreviewRequestCreateContext(preview, CGSizeMake(width, height), YES, (__bridge CFDictionaryRef)newOpt);
        CGContextDrawImage(ctx, CGRectMake(0,0,width,height), image);
        QLPreviewRequestFlushContext(preview, ctx);
        CGImageRelease(image);
        CGContextRelease(ctx);
    }
    return noErr;
}

OSStatus GenerateThumbnailForURL(void *thisInterface, QLThumbnailRequestRef thumbnail, CFURLRef url, CFStringRef contentTypeUTI, CFDictionaryRef options, CGSize maxSize)
{
    CGImageRef image = CreateImageForURL(url);
    if (!image) return -1;
    QLThumbnailRequestSetImage(thumbnail, image, nil);
    CGImageRelease(image);
    return noErr;
}

void CancelPreviewGeneration(void *thisInterface, QLPreviewRequestRef preview){}
void CancelThumbnailGeneration(void *thisInterface, QLThumbnailRequestRef thumbnail){}
