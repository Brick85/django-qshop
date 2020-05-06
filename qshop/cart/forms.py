from qshop.qshop_settings import CART_ORDER_FORM, ENABLE_QSHOP_DELIVERY, DELIVERY_REQUIRED, ENABLE_PAYMENTS, ENABLE_PROMO_CODES
from django import forms
from django.utils.translation import ugettext as _
from .forms_simple import OrderBaseForm

if CART_ORDER_FORM:
    from sitemenu import import_item
    OrderForm = import_item(CART_ORDER_FORM)

elif not ENABLE_QSHOP_DELIVERY:
    class OrderForm(OrderBaseForm):
        pass
else:
    class OrderForm(OrderExtendedForm):
        pass


if ENABLE_PROMO_CODES:
    from ..models import PromoCode

    class ApplyPromoForm(forms.Form):
        code = forms.CharField(label=_('Promo code'))

        def __init__(self, *args, **kwargs):
            self.cart = kwargs.pop('cart', None)
            super(ApplyPromoForm, self).__init__(*args, **kwargs)

        def clean(self):
            cleaned_data = super(ApplyPromoForm, self).clean()
            self.promo_code = PromoCode.find_by_code(cleaned_data.get('code', None))

            if not self.promo_code:
                self.add_error('code', _('Invalid promo code'))

            if self.promo_code and self.promo_code.min_sum > self.cart.total_price_wo_discount_wo_vat_reduction():
                self.add_error('code', _('Cart total must be at least {}').format(self.promo_code.min_sum))
            return cleaned_data
