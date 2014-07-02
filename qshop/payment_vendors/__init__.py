from banktransfer.banktransfer import BanktransferPayment
from qshop import qshop_settings

if qshop_settings.ENABLE_PAYMENTS:
    if 'banktransfer' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from banktransfer.banktransfer import BanktransferPayment
    if 'paypal' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from paypal.paypal import PaypalPayment
    if 'webmoney' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from webmoney.webmoney import WebmoneyPayment
