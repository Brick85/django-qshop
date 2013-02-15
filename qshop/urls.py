from django.conf.urls import patterns, url
from .views import redirect_to_product, set_currency

urlpatterns = patterns('',
    url(r'^show_product/(?P<product_id>\d+)/$', redirect_to_product, name='redirect_to_product'),
    url(r'^shop_set_currency/$', set_currency, name='set_currency'),
    url(r'^shop_set_currency/(?P<currency_code>[\w]+)/$', set_currency, name='set_currency'),
)
