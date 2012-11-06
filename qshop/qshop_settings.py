from django.conf import settings
_ = lambda x: x

if not 'sitemenu' in settings.INSTALLED_APPS:
    raise Exception('Error! qShop requires django-sitemenu!')

PRODUCTS_ON_PAGE = getattr(settings, 'QSHOP_PRODUCTS_ON_PAGE', 2)

NEED_COUNT_IN_FILTER = getattr(settings, 'QSHOP_NEED_COUNT_IN_FILTER', True)


PRODUCT_CLASS              = getattr(settings, 'QSHOP_PRODUCT_CLASS',              None)

VARIATION_VALUE_CLASS      = getattr(settings, 'QSHOP_VARIATION_VALUE_CLASS',      None)
VARIATION_CLASS            = getattr(settings, 'QSHOP_VARIATION_CLASS',            None)

PRODUCT_IMAGE_CLASS        = getattr(settings, 'QSHOP_PRODUCT_IMAGE_CLASS',        None)

PARAMETERS_SET_CLASS       = getattr(settings, 'QSHOP_PARAMETERS_SET_CLASS',       None)
PARAMETER_CLASS            = getattr(settings, 'QSHOP_PARAMETER_CLASS',            None)
PARAMETER_VALUE_CLASS      = getattr(settings, 'QSHOP_PARAMETER_VALUE_CLASS',      None)
PRODUCT_TO_PARAMETER_CLASS = getattr(settings, 'QSHOP_PRODUCT_TO_PARAMETER_CLASS', None)


CART_ORDER_CLASS = getattr(settings, 'QSHOP_CART_ORDER_CLASS', None)


MAIL_TYPES = {
    'order_sended': {
        'reply_to_mail': 'qshop@qwe.lv',
        'subject_prefix': _('[qShop] '),
        'admin_mails': ['qshop_admin@qwe.lv'],
    },
}
