from django.conf.urls import patterns, url

from qshop import qshop_settings

if qshop_settings.ENABLE_PAYMENTS:

    urlpatterns = patterns('',
        url(r'^test_payment/$', 'qshop.payment_vendors.views.test_payment', name='test_payment'),
    )

    if 'banktransfer' in qshop_settings.PAYMENT_METHODS_ENABLED:
        pass
        # urlpatterns += patterns('',
        #     url(r'^banktransfer/ok/(?P<order_id>\d+)/$', 'qshop.payment_vendors.views.vendors_payment_banktransfer_ok', name='vendors_payment_banktransfer_ok'),
        # )
    if 'paypal' in qshop_settings.PAYMENT_METHODS_ENABLED:
        urlpatterns += patterns('',
            url(r'^paypal/ok/(?P<order_id>\d+)/$', 'qshop.payment_vendors.views.vendors_payment_paypal_ok', name='vendors_payment_paypal_ok'),
        )
    if 'webmoney' in qshop_settings.PAYMENT_METHODS_ENABLED:
        urlpatterns += patterns('',
            url(r'^webmoney/ok/$', 'qshop.payment_vendors.views.vendors_payment_webmoney_ok', name='vendors_payment_webmoney_ok'),
            url(r'^webmoney/result/$', 'qshop.payment_vendors.views.vendors_payment_webmoney_result', name='vendors_payment_webmoney_result'),
            # url(r'^webmoney/fail/$', 'qshop.payment_vendors.views.vendors_payment_webmoney_fail', name='vendors_payment_webmoney_fail'),
        )
