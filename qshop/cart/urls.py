from django.conf.urls.defaults import patterns, url
import views

urlpatterns = patterns('',
    url(r'^$', views.show_cart, name='cart'),
    url(r'^add/(?P<product_id>\d+)/$', views.add_to_cart, name='add_to_cart'),
    url(r'^remove/(?P<product_id>\d+)/$', views.remove_from_cart, name='remove_from_cart'),
    url(r'^update/$', views.update_cart, name='update_cart'),

    # url(r'^order/$', 'order_cart', name='order_cart'),
    # url(r'^order/success/', 'cart_order_success', name='cart_order_success'),
    # url(r'^order/cancelled/', 'cart_order_cancelled', name='cart_order_cancelled'),
    # url(r'^order/error/', 'cart_order_error', name='cart_order_error')
)
