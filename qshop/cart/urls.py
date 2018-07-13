from django.conf.urls import url

from qshop.qshop_settings import CART_ORDER_VIEW, ENABLE_QSHOP_DELIVERY

from .views import (OrderDetailView, CartDetailView, add_to_cart, cart_order_cancelled,
                    cart_order_error, cart_order_success, remove_from_cart, update_cart)
# GetAvailableDeliveryTypesView
if CART_ORDER_VIEW:
    from sitemenu import import_item
    qshop_order_view = import_item(CART_ORDER_VIEW)

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

# if ENABLE_QSHOP_DELIVERY:
#     urlpatterns += [
#         url(r'^deliverytypes/(?P<country_id>\d+)/$', GetAvailableDeliveryTypesView.as_view(), name='ajax_get_delivery_types'),
#     ]

if CART_ORDER_VIEW:
    urlpatterns += [
        url(r'^order/$', qshop_order_view, name='order_cart')
    ]
else:
    urlpatterns += [
        url(r'^order/$', OrderDetailView.as_view(), name='order_cart')
    ]
