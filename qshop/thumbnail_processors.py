from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders


def watermark_processor(image, wm=None, wmp="bl", **kwargs):
    if wm is not None:
        if not hasattr(watermark_processor, '_watermarks'):
            watermark_processor._watermarks = {}
        if not wm in watermark_processor._watermarks:
            watermark_processor._watermarks[wm] = Image.open(finders.find(settings.WATERMARKS[wm]))
        watermark_image = watermark_processor._watermarks[wm]
        if wmp == "bl":
            image.paste(watermark_image, ((image.size[0]-watermark_image.size[0]), (image.size[1]-watermark_image.size[1])), watermark_image)
        else:
            image.paste(watermark_image, ((image.size[0]/2-watermark_image.size[0]/2), (image.size[1]/2-watermark_image.size[1]/2)), watermark_image)
    return image
