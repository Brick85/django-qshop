from qshop.qshop_settings import CART_ORDER_FORM

if CART_ORDER_FORM:
    from sitemenu import import_item
    OrderForm = import_item(CART_ORDER_FORM)
else:
    from django import forms
    from .models import Order, DeliveryType
    from ..mails import sendMail
    from django.utils.translation import ugettext as _

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
                'is_delivery': forms.RadioSelect,
                'delivery_type': forms.RadioSelect
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

            self.refresh_instance_data()

        def refresh_instance_data(self):
            self.instance.cart = self.cart.cart
            self.instance.cart_text = self.cart.as_table(standalone=True)
            self.instance.cart_price = self.cart.total_price()
            self.instance.delivery_price = self.cart.delivery_price()

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

        def save(self, commit=True):
            instance = super(OrderForm, self).save(commit)
            self.cart.checkout()
            return instance
