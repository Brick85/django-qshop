from django.conf import settings
_ = lambda x: x

if not 'sitemenu' in settings.INSTALLED_APPS:
    raise Exception('Error! qShop requires django-sitemenu!')

PRODUCTS_ON_PAGE = getattr(settings, 'QSHOP_PRODUCTS_ON_PAGE', 10)


PRODUCT_CLASS = getattr(settings, 'QSHOP_PRODUCT_CLASS', None)

VARIATION_VALUE_CLASS = getattr(settings, 'QSHOP_VARIATION_VALUE_CLASS', None)
VARIATION_CLASS = getattr(settings, 'QSHOP_VARIATION_CLASS', None)

PRODUCT_IMAGE_CLASS = getattr(settings, 'QSHOP_PRODUCT_IMAGE_CLASS', None)

PARAMETERS_SET_CLASS = getattr(settings, 'QSHOP_PARAMETERS_SET_CLASS', None)
PARAMETER_CLASS = getattr(settings, 'QSHOP_PARAMETER_CLASS', None)
PARAMETER_VALUE_CLASS = getattr(settings, 'QSHOP_PARAMETER_VALUE_CLASS', None)
PRODUCT_TO_PARAMETER_CLASS = getattr(settings, 'QSHOP_PRODUCT_TO_PARAMETER_CLASS', None)

CURRENCY_CLASS = getattr(settings, 'QSHOP_CURRENCY_CLASS', None)

LOAD_ADDITIONAL_MODELS = getattr(settings, 'QSHOP_LOAD_ADDITIONAL_MODELS', None)


CART_CLASS = getattr(settings, 'QSHOP_CART_CLASS', 'qshop.cart.cart.Cart') # cart class
CART_ORDER_CLASS = getattr(settings, 'QSHOP_CART_ORDER_CLASS', None) # cart model
CART_ORDER_FORM = getattr(settings, 'QSHOP_CART_ORDER_FORM', None)
CART_MODEL_CLASS = getattr(settings, 'QSHOP_CART_MODEL_CLASS', None)
ITEM_CLASS = getattr(settings, 'QSHOP_ITEM_CLASS', None)

CART_ORDER_CUSTOM_ADMIN = getattr(settings, 'QSHOP_CART_ORDER_CUSTOM_ADMIN', False)
CART_ORDER_VIEW = getattr(settings, 'QSHOP_CART_ORDER_VIEW', False)

CART_TABLE_LINK_ADD = getattr(settings, 'QSHOP_CART_TABLE_LINK_ADD', None)
CART_TABLE_IMAGE_ADD = getattr(settings, 'QSHOP_CART_TABLE_IMAGE_ADD', None)


# DELIVERY OPTIONS
ENABLE_QSHOP_DELIVERY = getattr(settings, 'QSHOP_ENABLE_QSHOP_DELIVERY', False)
DELIVERY_REQUIRED = getattr(settings, 'QSHOP_DELIVERY_REQUIRED', False)
VAT_PERCENTS = getattr(settings, 'QSHOP_VAT_PERCENTS', 21)
DELIVERY_COUNTRY_CLASS = getattr(settings, 'QSHOP_DELIVERY_COUNTRY_CLASS', 'qshop.cart.models.DeliveryCountryAbstract')
DELIVERY_TYPE_CLASS = getattr(settings, 'QSHOP_DELIVERY_TYPE_CLASS', None)
DELIVERY_CALCULATION_CLASS = getattr(settings, 'QSHOP_DELIVERY_CALCULATION_CLASS', None)
PICKUP_POINT_CLASS = getattr(settings, 'QSHOP_PICKUP_POINT_CLASS', None)

# DELIVERY_TYPE_ADDRESS_CLASS = getattr(settings, 'QSHOP_DELIVERY_TYPE_ADDRESS_CLASS', None)

# EXTEND CART OPTION

if ENABLE_QSHOP_DELIVERY:
    if not CART_ORDER_CLASS:
        CART_ORDER_CLASS = 'qshop.cart.models.OrderExtendedAbstractDefault'

# PROMOCODE OPTIONS
ENABLE_PROMO_CODES = getattr(settings, 'QSHOP_ENABLE_PROMO_CODES', False)
PROMO_CODE_CLASS = getattr(settings, 'QSHOP_PROMO_CODE_CLASS', False)
PROMO_CODE_FORM = getattr(settings, 'QSHOP_PROMO_CODE_FORM', False)

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
PAYMENT_METHODS_CLASSES_PATHS = getattr(settings, 'QSHOP_PAYMENT_METHODS_CLASSES_PATHS', {
    'banktransfer': 'qshop.payment_vendors.BanktransferPayment',
    'paypal': 'qshop.payment_vendors.PaypalPayment',
    'webmoney': 'qshop.payment_vendors.WebmoneyPayment',
    'swedbank': 'qshop.payment_vendors.SwedbankPayment',
    'firstdata': 'qshop.payment_vendors.FirstdataPayment',
    #('yandex', 'yandex'),
    #('roboxchange', 'roboxchange'),
    #('delayed', 'delayed'),
})
PAYMENT_METHODS_ENABLED = getattr(settings, 'QSHOP_PAYMENT_METHODS_ENABLED', ['banktransfer', 'paypal', 'webmoney', 'swedbank', 'firstdata'])
