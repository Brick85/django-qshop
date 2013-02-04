from django.conf.urls import patterns, url
from .views import redirect_to_product

urlpatterns = patterns('',
    url(r'^show_product/(?P<product_id>\d+)/$', redirect_to_product, name='redirect_to_product'),
)
