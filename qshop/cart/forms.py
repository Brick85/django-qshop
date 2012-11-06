from django import forms
from models import Order
from ..mails import sendMail
from django.utils.translation import ugettext as _


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ('date_added', 'status', 'manager_comments', 'cart', 'cart_text')

    def save(self, cart, *args, **kwargs):
        kwargs['commit'] = False
        order = super(OrderForm, self).save(*args, **kwargs)

        order.cart = cart.cart
        order.cart_text = cart.as_table()

        order.save()

        if hasattr(order, 'email'):
            sendMail('order_sended',
                     variables={
                        'order': order,
                     },
                     subject=_('Your order %s accepted') % order.get_id(),
                     mails=[order.email]
            )

        return order
