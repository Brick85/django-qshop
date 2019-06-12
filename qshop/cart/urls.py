from django.conf.urls import url

from qshop.qshop_settings import CART_ORDER_VIEW, ENABLE_QSHOP_DELIVERY, ENABLE_PROMO_CODES

from .views import (OrderDetailView, AjaxOrderDetailView, CartDetailView, add_to_cart, cart_order_cancelled,
                    cart_order_error, cart_order_success, remove_from_cart, update_cart)

if CART_ORDER_VIEW:
    from sitemenu import import_item
    qshop_order_view = import_item(CART_ORDER_VIEW)

if ENABLE_PROMO_CODES:
    from .views import ApplyPromoView


urlpatterns = [
    url(r'^$', CartDetailView.as_view(), name='cart'),
    url(r'^add/(?P<product_id>\d+)/$', add_to_cart, name='add_to_cart'),
    url(r'^remove/(?P<item_id>\d+)/$', remove_from_cart, name='remove_from_cart'),
    url(r'^update/$', update_cart, name='update_cart'),

    url(r'^order/success/$', cart_order_success, name='cart_order_success'),
    url(r'^order/cancelled/$', cart_order_cancelled, name='cart_order_cancelled'),
    url(r'^order/error/$', cart_order_error, name='cart_order_error'),
    url(r'^order/cancelled/(?P<order_id>\d+)/$', cart_order_cancelled, name='cart_order_cancelled'),
]

if ENABLE_QSHOP_DELIVERY:
    urlpatterns += [
        url(r'^order/$', OrderDetailView.as_view(), name='order_cart'),
        url(r'^order/ajax-submit-order/$', AjaxOrderDetailView.as_view(), name='ajax_order_cart'),
    ]

if CART_ORDER_VIEW:
    urlpatterns += [
        url(r'^order/$', qshop_order_view, name='order_cart')
    ]
elif not ENABLE_QSHOP_DELIVERY:
    from . import views
    urlpatterns += [
        url(r'^order/$', views.order_cart, name='order_cart'),
    ]

if ENABLE_PROMO_CODES:
    urlpatterns += [
        url(r'^apply-promo/$', ApplyPromoView.as_view(), name='apply_promo'),
    ]
