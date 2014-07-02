from qshop.payment_vendors.payment import BasePayment
from qshop import qshop_settings
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect



ALLOWED_CURRENCIES = ('AUD', 'BRL', 'CAD', 'CZK', 'DKK', 'EUR', 'HKD', 'HUF', 'ILS', 'JPY', 'MYR', 'MXN', 'NOK', 'NZD', 'PHP', 'PLN', 'GBP', 'RUB', 'SGD', 'SEK', 'CHF', 'TWD', 'THB', 'TRY', 'USD')


if not all([hasattr(settings, elem) for elem in ['PAYPAL_MODE', 'PAYPAL_CLIENTID', 'PAYPAL_SECRET']]):
    raise Exception('Project not configured to use paypal. You must specify variables in settings:\n\nPAYPAL_MODE = "sandbox" #  live\nPAYPAL_CLIENTID = ""\nPAYPAL_SECRET = ""')

try:
    import paypalrestsdk
except ImportError:
    raise Exception('Paypal module needs paypalrestsdk.\nRun:\n    pip install paypalrestsdk')


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENTID,
    "client_secret": settings.PAYPAL_SECRET
})


class PaypalPayment(BasePayment):

    def get_redirect_response(self, order):
        cart = order.cart.get_cartobject()
        currency_code = cart.get_currency().code.upper()
        total_price = cart.total_price()
        total_price = int(total_price * 100) / 100.0
        total_price = "%.2f" % total_price


        if currency_code not in ALLOWED_CURRENCIES:
            raise Exception('Unsupported currency')

        options = {
            "intent":  "sale",
            "payer":  {
                "payment_method":  "paypal"
            },
            "redirect_urls": {
                "return_url": "{SITE_URL}{URL}".format(SITE_URL=settings.SITE_URL, URL=reverse('vendors_payment_paypal_ok', args=(order.pk,))),
                "cancel_url": "{SITE_URL}{URL}".format(SITE_URL=settings.SITE_URL, URL=reverse('cart_order_cancelled', args=(order.pk,)))
            },
            "transactions":  []
        }

        options['transactions'].append(
                {
                    ### ItemList
                    "item_list": {
                        "items": [
                            {
                                "name": order.get_id(),
                                #"sku": "item",
                                "price": total_price,
                                "currency": currency_code,
                                "quantity": 1
                            }
                        ]
                    },
                    ###Amount
                    # Let's you specify a payment amount.
                    "amount":  {
                        "total":  total_price,
                        "currency":  currency_code
                    },
                    #"description":  "This is the payment transaction description."
                }
        )

        payment = paypalrestsdk.Payment(options)

        # Create Payment and return status
        if payment.create():
            order.add_log_message("Payment[%s] created successfully" % (payment.id))
            order.payment_id = payment.id
            # Redirect the user to given approval url
            for link in payment.links:
                if link.method == "REDIRECT":
                    redirect_url = link.href
                    order.add_log_message("Redirect for approval: %s" % (redirect_url) )
                    order.save()
                    return HttpResponseRedirect(redirect_url)

            order.add_log_message("ERROR: No link in response")
        else:
            order.add_log_message("Error while creating payment:")
            order.add_log_message(payment.error)
        order.save()
        raise Exception('Error processing paypal payment')

    def parse_response(self, request, order):
        payer_id = request.GET.get('PayerID')

        payment = paypalrestsdk.Payment.find(order.payment_id)
        if payment.execute({"payer_id": payer_id}):
            order.add_log_message("Payment[%s] execute successfully"%(payment.id))
            order.user_payed()
        else:
            order.add_log_message("ERROR executing payment!")
            order.add_log_message(payment.error)

        order.save()

        return HttpResponseRedirect(reverse('cart_order_success'))
