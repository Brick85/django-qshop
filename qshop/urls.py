from django.conf.urls import url, include

from .views import redirect_to_product, set_currency
from . import qshop_settings

urlpatterns = [
    url(r'^show-product/(?P<product_id>\d+)/$', redirect_to_product, name='redirect_to_product'),
    url(r'^shop-set-currency/$', set_currency, name='set_currency'),
    url(r'^shop-set-currency/(?P<currency_code>[\w]+)/$', set_currency, name='set_currency'),
]

if qshop_settings.ENABLE_PAYMENTS:
    urlpatterns += [
        url(r'^vendors/', include('qshop.payment_vendors.urls')),
    ]
