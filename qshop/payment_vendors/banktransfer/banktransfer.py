from qshop.payment_vendors.payment import BasePayment
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class BanktransferPayment(BasePayment):
    def get_redirect_response(self, cart):
        return HttpResponseRedirect(reverse('cart_order_success'))

    def parse_response(self, request):
        raise NotImplementedError()
