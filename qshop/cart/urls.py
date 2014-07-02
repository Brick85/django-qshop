from django.conf.urls import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.show_cart, name='cart'),
    url(r'^add/(?P<product_id>\d+)/$', views.add_to_cart, name='add_to_cart'),
    url(r'^remove/(?P<item_id>\d+)/$', views.remove_from_cart, name='remove_from_cart'),
    url(r'^update/$', views.update_cart, name='update_cart'),

    url(r'^order/$', views.order_cart, name='order_cart'),
    url(r'^order/success/$', views.cart_order_success, name='cart_order_success'),
    url(r'^order/cancelled/$', views.cart_order_cancelled, name='cart_order_cancelled'),
    url(r'^order/error/$', views.cart_order_error, name='cart_order_error'),
    url(r'^order/cancelled/(?P<order_id>\d+)/$', views.cart_order_cancelled, name='cart_order_cancelled'),
)
