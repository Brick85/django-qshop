from .models import Order
from ..mails import sendMail
from django import forms


class OrderBaseForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('date_added', 'status', 'manager_comments', 'cart', 'cart_text')

    def save(self, cart, *args, **kwargs):
        kwargs['commit'] = False
        order = super(OrderBaseForm, self).save(*args, **kwargs)

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