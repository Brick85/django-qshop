from qshop.payment_vendors.payment import BasePayment
from django.core.urlresolvers import reverse

class BanktransferPayment(BasePayment):
    def get_redirect(self, cart):
        return reverse('cart_order_success')

    def parse_response(self, request):
        raise NotImplementedError()
