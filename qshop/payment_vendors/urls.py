from django.conf.urls import url

from qshop import qshop_settings

if qshop_settings.ENABLE_PAYMENTS:
    from qshop.payment_vendors.views import test_payment
    urlpatterns = [
        url(r'^test_payment/$', test_payment, name='test_payment'),
    ]

    if 'banktransfer' in qshop_settings.PAYMENT_METHODS_ENABLED:
        pass
        # urlpatterns += patterns('',
        #     url(r'^banktransfer/ok/(?P<order_id>\d+)/$', 'qshop.payment_vendors.views.vendors_payment_banktransfer_ok', name='vendors_payment_banktransfer_ok'),
        # )
    if 'paypal' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from qshop.payment_vendors.views import vendors_payment_paypal_ok
        urlpatterns += [
            url(r'^paypal/ok/(?P<order_id>\d+)/$', vendors_payment_paypal_ok, name='vendors_payment_paypal_ok'),
        ]
    if 'webmoney' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from qshop.payment_vendors.views import vendors_payment_webmoney_ok
        from qshop.payment_vendors.views import vendors_payment_webmoney_result
        urlpatterns += [
            url(r'^webmoney/ok/$', vendors_payment_webmoney_ok, name='vendors_payment_webmoney_ok'),
            url(r'^webmoney/result/$', vendors_payment_webmoney_result, name='vendors_payment_webmoney_result'),
            # url(r'^webmoney/fail/$', 'qshop.payment_vendors.views.vendors_payment_webmoney_fail', name='vendors_payment_webmoney_fail'),
        ]
    if 'swedbank' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from qshop.payment_vendors.swedbank.views import payment_swedbank_return
        urlpatterns += [
            url(r'^swedbank/return/$', payment_swedbank_return, name="payment_swedbank_return"),
        ]
    if 'firstdata' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from qshop.payment_vendors.firstata.views import payment_firstdata_return
        urlpatterns += [
            url(r'^swedbank/return/$', payment_firstdata_return, name="payment_firstdata_return"),
        ]
