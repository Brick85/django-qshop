from qshop.payment_vendors.payment import BasePayment
from qshop import qshop_settings
from django.conf import settings
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
import hashlib


if not all([hasattr(settings, elem) for elem in ['WEBMONEY_E_WALLET', 'WEBMONEY_E_WALLET_SECRET']]):
    raise Exception('Project not configured to use webmoney. You must specify variables in settings:\n\nWEBMONEY_E_WALLET = ""\nWEBMONEY_E_WALLET_SECRET = ""')


class WebmoneyPayment(BasePayment):
    def get_redirect_response(self, order):
        cart = order.cart.get_cartobject()
        currency_code = cart.get_currency().code.upper()
        total_price = cart.total_price()
        total_price = int(total_price * 100) / 100.0
        total_price = "%.2f" % total_price


        if currency_code != "EUR":
            raise Exception('Unsupported currency')

        render_data = {
            'action': 'https://merchant.webmoney.ru/lmi/payment.asp',
            'fields': {
                'LMI_PAYEE_PURSE': settings.WEBMONEY_E_WALLET,
                'LMI_PAYMENT_AMOUNT': total_price,
                'LMI_PAYMENT_DESC': order.get_id(),
                'LMI_PAYMENT_NO': order.pk,

                "LMI_SUCCESS_URL": "{SITE_URL}{URL}".format(SITE_URL=settings.SITE_URL, URL=reverse('vendors_payment_webmoney_ok')),
                "LMI_SUCCESS_METHOD": "1",
                "LMI_FAIL_URL": "{SITE_URL}{URL}".format(SITE_URL=settings.SITE_URL, URL=reverse('cart_order_cancelled', args=(order.pk,))),
                "LMI_FAIL_METHOD": "1",
            }
        }

        order.add_log_message('Payment started')
        order.save()

        return render_to_response('qshop/payment_vendors/redirect_with_post.html', {
            'data': render_data,
        })

    def check_sign(self, post):
        check_str = post.get('LMI_PAYEE_PURSE')
        check_str += post.get('LMI_PAYMENT_AMOUNT')
        check_str += post.get('LMI_PAYMENT_NO')
        check_str += post.get('LMI_MODE')
        check_str += post.get('LMI_SYS_INVS_NO')
        check_str += post.get('LMI_SYS_TRANS_NO')
        check_str += post.get('LMI_SYS_TRANS_DATE')
        check_str += settings.WEBMONEY_E_WALLET_SECRET
        check_str += post.get('LMI_PAYER_PURSE')
        check_str += post.get('LMI_PAYER_WM')
        sign_hash = hashlib.md5(check_str).hexdigest().upper()

        if sign_hash == post.get('LMI_HASH'):
            return True
        return False

    def parse_response(self, request, order):
        order.add_log_message("Payment successfull")
        order.user_payed()
        order.save()
