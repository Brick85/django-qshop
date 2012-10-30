from django.conf import settings

if not 'sitemenu' in settings.INSTALLED_APPS:
    raise Exception('Error! qShop requires django-sitemenu!')

PRODUCTS_ON_PAGE = getattr(settings, 'QSHOP_PRODUCTS_ON_PAGE', 2)

NEED_COUNT_IN_FILTER = getattr(settings, 'QSHOP_NEED_COUNT_IN_FILTER', True)
