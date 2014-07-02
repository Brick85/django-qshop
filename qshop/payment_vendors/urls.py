from django.conf.urls import patterns, url

urlpatterns = patterns('',
    url(r'^test_payment/$', 'qshop.payment_vendors.views.test_payment', name='test_payment'),
    url(r'^paypal/ok/(?P<order_id>\d+)/$', 'qshop.payment_vendors.views.vendors_payment_paypal_ok', name='vendors_payment_paypal_ok'),
)
