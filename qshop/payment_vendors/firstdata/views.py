from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.utils import translation

from sitemenu.helpers import get_client_ip
from qshop.cart.models import Order
from .firstdata import Firstdata


@csrf_exempt
def payment_firstdata_return(request):
    trans_id = request.POST['trans_id']

    order = Order.objects.get(payment_id=trans_id)

    merchant = Firstdata(verbose=False)

    trans_data = merchant.get_trans_result(trans_id, get_client_ip(request))

    if hasattr(order, 'language'):
        request.LANGUAGE_CODE = order.language
        request.LANG = request.LANGUAGE_CODE
        translation.activate(request.LANGUAGE_CODE)

    if trans_data['RESULT'] == 'OK':
        order.add_log_message(u"payment ok: \n%s\n%s" % (trans_data, request.POST))
        order.user_paid()
        order.save()
        redirect_url = reverse('cart_order_success')
    else:
        order.add_log_message(u"error in payment: \n%s\n%s" % (trans_data, request.POST))
        order.save()
        redirect_url = reverse('cart_order_error')

    return HttpResponseRedirect(redirect_url)
