from qshop.qshop_settings import CART_ORDER_FORM, ENABLE_QSHOP_DELIVERY, DELIVERY_REQUIRED, ENABLE_PAYMENTS, ENABLE_PROMO_CODES, PROMO_CODE_FORM
from django import forms

if CART_ORDER_FORM:
    from sitemenu import import_item
    OrderForm = import_item(CART_ORDER_FORM)

elif not ENABLE_QSHOP_DELIVERY:
    from .forms_simple import OrderBaseForm
    class OrderForm(OrderBaseForm):
        pass
else:
    from .forms_extended import OrderExtendedForm
    class OrderForm(OrderExtendedForm):
        pass


if ENABLE_PROMO_CODES:
    if PROMO_CODE_FORM:
        from sitemenu import import_item
        ApplyPromoForm = import_item(PROMO_CODE_FORM)
    else:
        from .forms_simple import ApplyPromoFormBase

        class ApplyPromoForm(ApplyPromoFormBase):
            pass
