from qshop.qshop_settings import CART_ORDER_FORM, ENABLE_QSHOP_DELIVERY, DELIVERY_REQUIRED, ENABLE_PAYMENTS, ENABLE_PROMO_CODES
from django import forms
from django.utils.translation import ugettext as _


if CART_ORDER_FORM:
    from sitemenu import import_item
    OrderForm = import_item(CART_ORDER_FORM)

elif not ENABLE_QSHOP_DELIVERY:
    from .models import Order
    from ..mails import sendMail

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
else:
    from django import forms
    from .models import DeliveryType, DeliveryCountry, Order
    from ..mails import sendMail
    from django.utils.translation import ugettext as _

    class DeliveryCountrySelect(forms.Select):
        def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
            option = super(DeliveryCountrySelect, self).create_option(name, value, label, selected, index, subindex, attrs)
            if option['value']:
                delivery_type_ids = DeliveryType.objects.filter(delivery_country__id=option['value']).values_list('id', flat=True)
                option['attrs']['data-countries-pks'] = ','.join([str(pk) for pk in delivery_type_ids])


            return option


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
                'city',
                'address',
                'zip_code',
                'legal_name',
                'reg_number',
                'vat_reg_number',
                'bank_name',
                'bank_account',
                'iban',

                # delivery
                'delivery_type',
                'delivery_country',
                'delivery_city',
                'delivery_address',
                'delivery_zip_code',
            ]

            if ENABLE_PAYMENTS:
                fields.append('payment_method')

            if not DELIVERY_REQUIRED:
                fields.append('is_delivery')

            widgets = {
                'person_type': forms.RadioSelect,
                'is_delivery': forms.RadioSelect,
                'delivery_type': forms.RadioSelect,
                'delivery_country': DeliveryCountrySelect(attrs={
                    'data-toggle-scope': '.j_person_type-wrap',
                    'data-toggle-template': '.j_toggle'
                })
            }

        class Media:
            css = {
                'all': ('qcart.css',)
            }
            js = ('qcart.js',)

        def __init__(self, *args, **kwargs):
            self.cart = kwargs.pop('cart')
            # need to annulate, because delivery price and vat reduction are saved in model Cart
            self.cart.set_delivery_price(0)
            self.cart.set_vat_reduction(0)
            super().__init__(*args, **kwargs)
            self.fields['delivery_type'].empty_label = None
            self.refresh_instance_data()
            # if any delivery type dont exist in this delivery_country
            self.fields['delivery_country'].queryset = DeliveryCountry.objects.exclude(deliverytype=None)

            self.fields['country'].queryset = DeliveryCountry.can_invoicing.all()

        def refresh_instance_data(self):
            self.instance.cart = self.cart.cart
            self.instance.cart_text = self.cart.as_table(standalone=True)
            self.instance.cart_price = self.cart.total_price()
            self.instance.delivery_price = self.cart.delivery_price()
            self.instance.cart_vat_amount = self.cart.vat_amount()

        def clean(self):
            data = super(OrderForm, self).clean()
            person_type = data.get('person_type')
            is_delivery = data.get('is_delivery')
            delivery_country = data.get('delivery_country')
            delivery_type = data.get('delivery_type', None)
            vat_nr = data.get('vat_reg_number', None)
            country = data.get('country')

            if delivery_type:
                self.cart.set_delivery_price(delivery_type.get_delivery_price(delivery_country, self.cart))

            if country:
                self.cart.set_vat_reduction(country.get_vat_reduction(vat_nr, person_type))

            self.refresh_instance_data()

            if is_delivery == self._meta.model.DELIVERY_YES or is_delivery is None:
                self.validate_required_field(data, 'delivery_type')
                self.validate_required_field(data, 'delivery_country')
                self.validate_required_field(data, 'delivery_city')
                self.validate_required_field(data, 'delivery_address')
                self.validate_required_field(data, 'delivery_zip_code')

                if delivery_country and delivery_type:
                    if not delivery_type.check_country(delivery_country.pk):
                        self._errors['delivery_type'] = self.error_class([
                                _('This delivery type cannot deliver to choosed country')
                            ])

            if person_type == self._meta.model.LEGAL:
                self.validate_required_field(data, 'legal_name')
                self.validate_required_field(data, 'reg_number')
                self.validate_required_field(data, 'bank_name')
                self.validate_required_field(data, 'bank_account')
                self.validate_required_field(data, 'iban')
                self.validate_required_field(data, 'country')
                self.validate_required_field(data, 'city')
                self.validate_required_field(data, 'address')
                self.validate_required_field(data, 'zip_code')
            return data

        def validate_required_field(self, cleaned_data, field_name, msg=None):
            if not msg:
                msg = _('This field is required.')
            if(field_name in cleaned_data and not cleaned_data[field_name]):
                self._errors[field_name] = self.error_class([msg])

        def save(self, commit=True):
            instance = super(OrderForm, self).save(commit)
            self.cart.checkout()
            return instance

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

            if self.promo_code and self.promo_code.min_sum > self.cart.total_price_wo_discount():
                self.add_error('code', _('Cart total must be at least {}').format(self.promo_code.min_sum))
            return cleaned_data
