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
                    'delivery_country',
                    'delivery_type',
                    'delivery_city',
                    'delivery_street',
                    'delivery_house',
                    'delivery_flat',
                    'delivery_zip',
                ]
                widgets = {
                    'person_type': forms.RadioSelect,
                    'is_delivery': forms.RadioSelect
                }


            class Media:
                css = {
                    'all': ('qcart.css',)
                }
                js = ('qcart.js',)


            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)


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


            def clean(self):
                data = super(OrderForm, self).clean()
                person_type = data.get('person_type')
                is_delivery = data.get('is_delivery')
                delivery_country = data.get('delivery_country')
                delivery_type = data.get('delivery_type')

                if is_delivery == self._meta.model.DELIVERY_YES:
                    self.validate_required_field(data, 'delivery_country')
                    self.validate_required_field(data, 'delivery_type')
                    self.validate_required_field(data, 'delivery_city')
                    self.validate_required_field(data, 'delivery_street')
                    self.validate_required_field(data, 'delivery_house')
                    self.validate_required_field(data, 'delivery_flat')
                    self.validate_required_field(data, 'delivery_zip')

                    if delivery_country and delivery_type:
                        if not delivery_type.check_country(delivery_country.pk):
                            self._errors['delivery_type'] = self.error_class([
                                    _('This delivery type cannot deliver to choosed country')
                                ])

                if person_type == self._meta.model.LEGAL:
                    self.validate_required_field(data, 'country')
                    self.validate_required_field(data, 'legal_name')
                    self.validate_required_field(data, 'reg_number')
                    self.validate_required_field(data, 'juridical_address')
                    self.validate_required_field(data, 'bank_name')
                    self.validate_required_field(data, 'iban')

                return data



            def validate_required_field(self, cleaned_data, field_name, msg=None):
                if not msg:
                    msg = _('This field is required.')
                if(field_name in cleaned_data and not cleaned_data[field_name]):
                    self._errors[field_name] = self.error_class([msg])

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
