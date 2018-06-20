from qshop.qshop_settings import CART_ORDER_FORM, ENABLE_QSHOP_DELIVERY

if CART_ORDER_FORM:
    from sitemenu import import_item
    OrderForm = import_item(CART_ORDER_FORM)
else:
    from django import forms
    from .models import Order
    from ..mails import sendMail
    from django.utils.translation import ugettext as _

    if ENABLE_QSHOP_DELIVERY:
        class OrderForm(forms.ModelForm):

            class Meta:
                model = Order
                fields = [
                    'person_type',
                    # individual fields
                    'first_name',
                    'last_name',
                    'phone',
                    'email',
                    'address',
                    'comments',

                    # legal fields
                    'country',
                    'legal_name',
                    'reg_number',
                    'vat_reg_number',
                    'juridical_address',
                    'bank_name',
                    'iban',

                    # delivery
                    'is_delivery',
                    'delivery_country'
                ]

            def save(self, cart, *args, **kwargs):
                kwargs['commit'] = False
                order = super(OrderForm, self).save(*args, **kwargs)

                order.cart = cart.cart
                order.cart_text = cart.as_table(standalone=True)
                order.cart_price = cart.total_price()

                order.save()

                if hasattr(order, 'email'):
                    sendMail(
                        'order_sended',
                        variables={
                            'order': order,
                        },
                        subject=_("Your order %s accepted") % order.get_id(),
                        mails=[order.email]
                    )

                return order

    else:
        class OrderForm(forms.ModelForm):

            class Meta:
                model = Order
                exclude = ('date_added', 'status', 'manager_comments', 'cart', 'cart_text')

            def save(self, cart, *args, **kwargs):
                kwargs['commit'] = False
                order = super(OrderForm, self).save(*args, **kwargs)

                order.cart = cart.cart
                order.cart_text = cart.as_table(standalone=True)

                order.save()

                if hasattr(order, 'email'):
                    sendMail(
                        'order_sended',
                        variables={
                            'order': order,
                        },
                        subject=_("Your order %s accepted") % order.get_id(),
                        mails=[order.email]
                    )

                return order
