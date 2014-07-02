from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from qshop.cart.models import Order
from qshop import qshop_settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt


if qshop_settings.ENABLE_PAYMENTS:


    def test_payment(request):
        # order = Order.objects.get(pk=27)
        # payment = PaypalPayment()
        # payment.get_redirect(order)
        return HttpResponse('ok')

    if 'banktransfer' in qshop_settings.PAYMENT_METHODS_ENABLED:
        pass

    if 'paypal' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from qshop.payment_vendors import PaypalPayment
        def vendors_payment_paypal_ok(request, order_id):
            order = get_object_or_404(Order, pk=order_id, payed=False)
            payment = PaypalPayment()
            return payment.parse_response(request, order)


    if 'webmoney' in qshop_settings.PAYMENT_METHODS_ENABLED:
        from qshop.payment_vendors import WebmoneyPayment
        @csrf_exempt
        def vendors_payment_webmoney_ok(request):
            return HttpResponseRedirect(reverse('cart_order_success'))

        @csrf_exempt
        def vendors_payment_webmoney_fail(request):
            print request.POST
            return HttpResponseRedirect(reverse('cart_order_error'))

        @csrf_exempt
        def vendors_payment_webmoney_result(request):
            payment = WebmoneyPayment()
            if  'LMI_PAYEE_PURSE' not in request.POST or 'LMI_PREREQUEST' in request.POST:
                return HttpResponse('ok')
            else:
                if not payment.check_sign(request.POST):
                    return HttpResponse('sign')
                else:
                    order = get_object_or_404(Order, pk=request.POST.get('LMI_PAYMENT_NO'), payed=False)
                    payment.parse_response(request, order)
                    return HttpResponse('ok')
