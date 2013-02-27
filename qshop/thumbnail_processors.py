from PIL import Image
from django.conf import settings
from django.contrib.staticfiles import finders

def watermark_processor(image, watermark=None, **kwargs):
    if watermark!=None:
        if not hasattr(watermark_processor, '_watermarks'):
            watermark_processor._watermarks = {}
        if not watermark in watermark_processor._watermarks:
            watermark_processor._watermarks[watermark] = Image.open(finders.find(settings.WATERMARKS[watermark]))
        watermark_image = watermark_processor._watermarks[watermark]
        image.paste(watermark_image, ((image.size[0]-watermark_image.size[0]), (image.size[1]-watermark_image.size[1])), watermark_image)
    return image
