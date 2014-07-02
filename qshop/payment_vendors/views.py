from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from qshop.payment_vendors import PaypalPayment
from qshop.cart.models import Order


def test_payment(request):
    order = Order.objects.get(pk=27)
    payment = PaypalPayment()
    payment.get_redirect(order)
    return HttpResponse('ok')

def vendors_payment_paypal_ok(request, order_id):
    order = get_object_or_404(Order, pk=order_id, payed=False)
    payment = PaypalPayment()
    return payment.parse_response(request, order)
