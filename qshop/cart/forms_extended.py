from django import forms
from django.utils.translation import ugettext as _

from ..mails import sendMail
from .models import Order
from qshop.qshop_settings import DELIVERY_REQUIRED, ENABLE_PAYMENTS, ENABLE_QSHOP_DELIVERY
from .models import PickupPoint
from django.db.models import Q


if ENABLE_QSHOP_DELIVERY:
    from .models import DeliveryCountry, DeliveryType
    class OrderExtendedForm(forms.ModelForm):
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
                'i_agree',

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
                'delivery_pickup_point'
            ]

            if ENABLE_PAYMENTS:
                fields.append('payment_method')

            if not DELIVERY_REQUIRED:
                fields.append('is_delivery')

            widgets = {
                'person_type': forms.RadioSelect,
                'is_delivery': forms.RadioSelect,
                'delivery_type': forms.RadioSelect,
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

            # if any delivery type didnt exist in this delivery_country
            self.fields['delivery_country'].queryset = DeliveryCountry.objects.exclude(deliverytype=None)
            self.fields['country'].queryset = DeliveryCountry.can_invoicing.all()
            self.fields['i_agree'].required = True


        def refresh_instance_data(self):
            self.instance.cart = self.cart.cart
            self.instance.cart_text = self.cart.as_table(standalone=True)
            self.instance.cart_price = self.cart.total_price()
            self.instance.delivery_price = self.cart.delivery_price()
            self.instance.cart_vat_amount = self.cart.vat_amount()

        def clean(self):
            data = super().clean()
            self.person_type = data.get('person_type')
            self.delivery_country = data.get('delivery_country')
            self.delivery_type = data.get('delivery_type', None)
            self.is_delivery = data.get('is_delivery')
            self.vat_nr = data.get('vat_reg_number', None)
            self.country = data.get('country')

            self.fields['delivery_type'].queryset = self.get_delivery_types()

            if self.delivery_type:
                self.cart.set_delivery_price(self.delivery_type.get_delivery_price(self.delivery_country, self.cart))


            if self.country:
                self.cart.set_vat_reduction(self.country.get_vat_reduction(self.vat_nr, self.person_type))

            self.refresh_instance_data()
            self.validate_legal_fields(data)
            self.clean_delivery_fields(data)

            return data


        def get_delivery_types(self):
            if self.delivery_country:
                return DeliveryType.objects.filter(
                    Q(delivery_country=self.delivery_country),
                    Q(min_order_amount__lte=self.cart.total_price()) | Q(min_order_amount__isnull=True),
                    Q(max_order_amount__gte=self.cart.total_price()) | Q(max_order_amount__isnull=True)
                )

            return DeliveryType.objects.none()


        def process_delivery_data(self, data):
            delivery_type = data.get('delivery_type', None)
            required_fields = ['delivery_type']
            if delivery_type:
                if delivery_type.pickuppoint_set.first():
                    del self.fields['delivery_city']
                    del self.fields['delivery_zip_code']
                    del self.fields['delivery_address']
                    required_fields = required_fields + ['delivery_country', 'delivery_pickup_point']
                else:
                    del self.fields['delivery_pickup_point']
                    required_fields = required_fields + ['delivery_country', 'delivery_city', 'delivery_address', 'delivery_zip_code']
            else:
                del self.fields['delivery_city']
                del self.fields['delivery_zip_code']
                del self.fields['delivery_address']
                del self.fields['delivery_pickup_point']
            return required_fields

        def clean_delivery_country(self):
            data = self.cleaned_data['delivery_country']

            if data:
                self.fields['delivery_pickup_point'].queryset = PickupPoint.objects.filter(delivery_type__delivery_country=data)
            return data


        def clean_delivery_fields(self, data):
            if self.is_delivery == self._meta.model.DELIVERY_YES or self.is_delivery is None:
                for field in self.process_delivery_data(data):
                    self._validate_required_field(data, field)

                if self.delivery_country and self.delivery_type:
                    if not self.delivery_type.check_country(self.delivery_country.pk):
                        self._errors['delivery_type'] = self.error_class([
                                _('This delivery type cannot deliver to choosed country')
                            ])


        def get_required_legal_fields(self):
            return ['legal_name', 'reg_number', 'country', 'city', 'address', 'zip_code']


        def validate_legal_fields(self, data):
            if self.person_type == self._meta.model.LEGAL:
                for field in self.get_required_legal_fields():
                    self._validate_required_field(data, field)


        def _validate_required_field(self, cleaned_data, field_name, msg=None):
            if not msg:
                msg = _('This field is required.')
            if(field_name in cleaned_data and not cleaned_data[field_name]):
                self._errors[field_name] = self.error_class([msg])


        def save(self, commit=True):
            if DELIVERY_REQUIRED:
                self.instance.is_delivery = Order.DELIVERY_YES
            instance = super().save(commit)
            self.cart.checkout()
            return instance
