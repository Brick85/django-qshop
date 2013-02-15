from PIL import Image
from django.contrib.staticfiles import finders

def watermark_processor(image, watermark=False, **kwargs):
    if watermark:
        if not hasattr(watermark_processor, '_watermark_image'):
            watermark_processor._watermark_image = Image.open(finders.find(watermark))
        watermark_image = watermark_processor._watermark_image
        image.paste(watermark_image, ((image.size[0]-watermark_image.size[0]), (image.size[1]-watermark_image.size[1])), watermark_image)
    return image
