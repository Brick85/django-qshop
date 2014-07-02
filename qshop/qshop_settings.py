from django.conf import settings
_ = lambda x: x

if not 'sitemenu' in settings.INSTALLED_APPS:
    raise Exception('Error! qShop requires django-sitemenu!')

PRODUCTS_ON_PAGE = getattr(settings, 'QSHOP_PRODUCTS_ON_PAGE', 10)


PRODUCT_CLASS              = getattr(settings, 'QSHOP_PRODUCT_CLASS',              None)

VARIATION_VALUE_CLASS      = getattr(settings, 'QSHOP_VARIATION_VALUE_CLASS',      None)
VARIATION_CLASS            = getattr(settings, 'QSHOP_VARIATION_CLASS',            None)

PRODUCT_IMAGE_CLASS        = getattr(settings, 'QSHOP_PRODUCT_IMAGE_CLASS',        None)

PARAMETERS_SET_CLASS       = getattr(settings, 'QSHOP_PARAMETERS_SET_CLASS',       None)
PARAMETER_CLASS            = getattr(settings, 'QSHOP_PARAMETER_CLASS',            None)
PARAMETER_VALUE_CLASS      = getattr(settings, 'QSHOP_PARAMETER_VALUE_CLASS',      None)
PRODUCT_TO_PARAMETER_CLASS = getattr(settings, 'QSHOP_PRODUCT_TO_PARAMETER_CLASS', None)

CURRENCY_CLASS             = getattr(settings, 'QSHOP_CURRENCY_CLASS',             None)

LOAD_ADDITIONAL_MODELS     = getattr(settings, 'QSHOP_LOAD_ADDITIONAL_MODELS',     None)


CART_ORDER_CLASS = getattr(settings, 'QSHOP_CART_ORDER_CLASS', None)
CART_ORDER_FORM = getattr(settings, 'QSHOP_CART_ORDER_FORM', None)

CART_ORDER_CUSTOM_ADMIN = getattr(settings, 'QSHOP_CART_ORDER_CUSTOM_ADMIN', False)
CART_ORDER_VIEW = getattr(settings, 'QSHOP_CART_ORDER_VIEW', False)

CART_TABLE_LINK_ADD = getattr(settings, 'QSHOP_CART_TABLE_LINK_ADD', None)
CART_TABLE_IMAGE_ADD = getattr(settings, 'QSHOP_CART_TABLE_IMAGE_ADD', None)

MAIL_TYPES = getattr(settings, 'QSHOP_MAIL_TYPES', {
    'order_sended': {
        'reply_to_mail': 'qshop@qwe.lv',
        'subject_prefix': _('[qShop] '),
        'admin_mails': ['qshop_admin@qwe.lv'],
    },
})

# PAGES = getattr(settings, 'QSHOP_PAGES', (
#     ('prod', 'Products page', 'qshop.views.render_shopspage'),
# ))

# sitemenu_settings.PAGES += (
#     ('', '---------', ''),
# )

# sitemenu_settings.PAGES += PAGES

FILTERS_ENABLED = getattr(settings, 'QSHOP_FILTERS_ENABLED', True)
FILTERS_NEED_COUNT = getattr(settings, 'QSHOP_FILTERS_NEED_COUNT', True)
FILTERS_PRECLUDING = getattr(settings, 'QSHOP_FILTERS_PRECLUDING', True)

FILTERS_FIELDS = getattr(settings, 'QSHOP_FILTERS_FIELDS', [])

FILTERS_ORDER = getattr(settings, 'QSHOP_FILTERS_ORDER', [
    'p',  # properties
    'v',  # variations
])

VARIATION_FILTER_NAME = getattr(settings, 'QSHOP_VARIATION_FILTER_NAME', _('Variation'))  # or add "def get_variation_name(self):" to ProductsSet or Menu

FILTER_BY_VARIATION_TYPE = getattr(settings, 'QSHOP_FILTER_BY_VARIATION_TYPE', 'and')

CART_DELIVERY_FUNCTION = getattr(settings, 'QSHOP_CART_DELIVERY_FUNCTION', 'qshop.cart.overloadable_functions.count_delivery_price')


##### payments
ENABLE_PAYMENTS = getattr(settings, 'QSHOP_ENABLE_PAYMENTS', False)
PAYMENT_METHODS_CLASSES_PATHS = {
    'banktransfer': 'qshop.payment_vendors.BanktransferPayment',
    'paypal': 'qshop.payment_vendors.PaypalPayment',
    'webmoney': 'qshop.payment_vendors.WebmoneyPayment',
    #('yandex', 'yandex'),
    #('roboxchange', 'roboxchange'),
    #('delayed', 'delayed'),
}
PAYMENT_METHODS_ENABLED = getattr(settings, 'QSHOP_PAYMENT_METHODS_ENABLED', ['banktransfer', 'paypal', 'webmoney'])
