from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from qshop.cart.models import Order
from .swedbank import SwedbankResponse
from django.utils import translation
from django.core.mail import mail_admins
import pprint


@csrf_exempt
def payment_swedbank_return(request):
    swedbank = SwedbankResponse(get=request.GET, post=request.POST)

    if swedbank.is_valid_response():
        order = Order.objects.get(pk=swedbank.get_order_id())

        if swedbank.is_paid():
            order.add_log_message(u"payment ok: \n%s" % (swedbank.get_response()))
            order.user_paid()
            redirect_url = reverse('cart_order_success')
        else:
            if swedbank.is_canceled():
                order.add_log_message(u"payment canceled: \n%s" % (swedbank.get_response()))
                redirect_url = reverse('cart_order_cancelled', args=(order.id,))
            else:
                order.add_log_message(u"payment failed: \n%s" % (swedbank.get_response()))
                redirect_url = reverse('cart_order_error')
        order.save()

        if hasattr(order, 'language'):
            request.LANGUAGE_CODE = order.language
            request.LANG = request.LANGUAGE_CODE
            translation.activate(request.LANGUAGE_CODE)
    else:
        mail_admins("WARNING: Swedbank payment error: not valid response", pprint.pformat(swedbank.get_response()))
        redirect_url = reverse('cart_order_error')

    return HttpResponseRedirect(redirect_url)
