from django.conf.urls import patterns, url, include
from .views import redirect_to_product, set_currency
import qshop_settings

urlpatterns = patterns('',
    url(r'^show_product/(?P<product_id>\d+)/$', redirect_to_product, name='redirect_to_product'),
    url(r'^shop_set_currency/$', set_currency, name='set_currency'),
    url(r'^shop_set_currency/(?P<currency_code>[\w]+)/$', set_currency, name='set_currency'),
)

if qshop_settings.ENABLE_PAYMENTS:
    urlpatterns += patterns('',
        url(r'^vendors/', include('qshop.payment_vendors.urls')),
    )
