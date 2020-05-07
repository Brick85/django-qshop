from django import forms
from django.utils.translation import ugettext as _
from qshop.qshop_settings import ENABLE_PROMO_CODES

from ..mails import sendMail
from .models import Order


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


if ENABLE_PROMO_CODES:
    from ..models import PromoCode

    class ApplyPromoFormBase(forms.Form):
        code = forms.CharField(label=_('Promo code'))

        def __init__(self, *args, **kwargs):
            self.cart = kwargs.pop('cart', None)
            super(ApplyPromoFormBase, self).__init__(*args, **kwargs)

        def clean(self):
            cleaned_data = super(ApplyPromoFormBase, self).clean()
            self.promo_code = PromoCode.find_by_code(cleaned_data.get('code', None))

            if not self.promo_code:
                self.add_error('code', _('Invalid promo code'))

            if self.promo_code and self.promo_code.min_sum > self.cart.total_price_wo_discount_wo_vat_reduction():
                self.add_error('code', _('Cart total must be at least {}').format(self.promo_code.min_sum))
            return cleaned_data
