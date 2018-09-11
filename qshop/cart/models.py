import datetime

from django.conf import settings
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from qshop.mails import sendMail
from qshop import qshop_settings
from sitemenu import import_item

from ..models import Currency, Product, ProductVariation

PAYMENT_CLASSES = {}
if qshop_settings.ENABLE_PAYMENTS:
    for item in qshop_settings.PAYMENT_METHODS_ENABLED:
        PAYMENT_CLASSES[item] = import_item(qshop_settings.PAYMENT_METHODS_CLASSES_PATHS[item])
# Menu = import_item(MENUCLASS)


class Cart(models.Model):
    date_added = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_modified = models.DateTimeField(_('modification date'), auto_now=True)
    checked_out = models.BooleanField(default=False, verbose_name=_('checked out'))
    discount = models.PositiveSmallIntegerField(_('discount'), default=0)
    vat_reduction = models.PositiveSmallIntegerField(_('vat reduction'), default=0)

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-date_modified',)

    def __str__(self):
        return str(self.date_modified)

    def get_cartobject(self):
        from .cart import Cart as CartObject
        return CartObject(None, self)


class ItemManager(models.Manager):
    def get(self, *args, **kwargs):
        if 'product' in kwargs:
            kwargs['_real_product'] = kwargs['product']
            kwargs['_real_product_variation'] = kwargs['product'].selected_variation
            del(kwargs['product'])
        return super(ItemManager, self).get(*args, **kwargs)


class Item(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_('cart'), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('unit price'))
    _real_product = models.ForeignKey(Product, on_delete=models.CASCADE)
    _real_product_variation = models.ForeignKey(ProductVariation, blank=True, null=True, on_delete=models.CASCADE)

    objects = ItemManager()

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('cart',)

    def __str__(self):
        return '%s - %s' % (self.quantity, self.unit_price)

    def total_price(self, in_default_currency=False):
        if in_default_currency:
            single_price = self.unit_price
        else:
            single_price = Currency.get_price(self.unit_price)

        price = self.quantity * single_price
        return price

    def total_fprice(self):
        return Currency.get_fprice(self.total_price(), format_only=True)

    def get_product(self):
        self._real_product.selected_variation = self._real_product_variation
        return self._real_product

    def set_product(self, product):
        self._real_product = product
        self._real_product_variation = product.selected_variation

    product = property(get_product, set_product)

    def get_cartremove_url(self):
        return reverse('remove_from_cart', args=(self.pk,))


class OrderAbstract(models.Model):

    STATUSES = (
        (1, _('New')),
        (2, _('In Progress')),
        (3, _('Completed')),
        (4, _('Canceled')),
    )

    date_added = models.DateTimeField(_('date added'), auto_now_add=True)
    status = models.PositiveSmallIntegerField(_('status'), choices=STATUSES, default=1)
    manager_comments = models.TextField(_('manager comments'), blank=True)
    cart = models.ForeignKey(Cart, verbose_name=_('cart'), editable=False, on_delete=models.CASCADE)
    cart_text = models.TextField(_('cart text'), editable=False)

    if qshop_settings.ENABLE_PAYMENTS:
        paid = models.BooleanField(_('paid'), default=False)
        paid_log = models.TextField(_('paid log'), blank=True, null=True)
        payment_method = models.CharField(
            _('payment method'),
            max_length=16,
            choices=[(item, _(item)) for item in qshop_settings.PAYMENT_METHODS_ENABLED], default=qshop_settings.PAYMENT_METHODS_ENABLED[0]
        )
        payment_id = models.CharField(_('payment id'), max_length=256, null=True)

    class Meta:
        verbose_name = _('client order')
        verbose_name_plural = _('client orders')
        abstract = True

    def __str__(self):
        return u"%s (%s)" % (self.pk, self.date_added)

    def get_id(self):
        return "QS%d" % self.pk

    def get_description(self):
        return _(u"Order Nr. %s") % self.get_id()

    def finish_order(self, request):
        self.send_checkout_email()

    def get_cart_text(self):
        return mark_safe(self.cart_text)
    get_cart_text.allow_tags = True
    get_cart_text.short_description = _('cart text')

    def get_cartobject(self):
        return self.cart.get_cartobject()

    def get_total_price(self):
        return self.get_cartobject().total_price()

    if not qshop_settings.ENABLE_PAYMENTS:
        def get_redirect_response(self):
            return HttpResponseRedirect(reverse('cart_order_success'))
    else:
        def get_redirect_response(self):
            payment = PAYMENT_CLASSES[self.payment_method]()
            return payment.get_redirect_response(self)

        def add_log_message(self, msg):
            if self.paid_log is None:
                self.paid_log = u""
            self.paid_log += "[%s] %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), "%D %T"), msg)

        def user_paid(self):
            self.status = 2
            self.paid = True


class OrderAbstractDefault(OrderAbstract):
    name = models.CharField(_('client name'), max_length=128)
    phone = models.CharField(_('phone'), max_length=32, blank=True, null=True)
    email = models.EmailField(_('email'))
    address = models.CharField(_('address'), max_length=128)


    comments = models.TextField(_('comments'), blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return u"%s (%s)" % (self.name, self.email)

    def save(self, *args, **kwargs):
        super(OrderAbstractDefault, self).save(*args, **kwargs)

    def get_comments(self):
        return mark_safe("<br />".join(self.comments.split("\n")))
    get_comments.short_description = _('comments')



class OrderExtendedAbstractDefault(OrderAbstract):
    INDIVIDUAL = 0
    LEGAL = 1

    PERSON_TYPE_CHOICES = (
        (INDIVIDUAL, _('Individual entity')),
        (LEGAL, _('Legal entity')),
    )

    DELIVERY_NO = 0
    DELIVERY_YES = 1
    DELIVERY_CHOICES = (
        (DELIVERY_NO, _('No, take in office')),
        (DELIVERY_YES, _('Yes')),
    )

    person_type = models.SmallIntegerField(_('Person type'), choices=PERSON_TYPE_CHOICES, default=INDIVIDUAL)

    # INDIVIDUAL PERSON
    first_name = models.CharField(_('first name'), max_length=70)
    last_name = models.CharField(_('last name'), max_length=70)
    phone = models.CharField(_('phone'), max_length=32, blank=True, null=True)
    email = models.EmailField(_('email'))
    comments = models.TextField(_('comments'), blank=True, null=True)

    # LEGAL ENTITY
    country = models.ForeignKey('DeliveryCountry', verbose_name=_('Country'), on_delete=models.PROTECT, blank=True, null=True)
    legal_name = models.CharField(_('Legal name'), max_length=255, null=True, blank=True)
    reg_number = models.CharField(_('Registration number'), max_length=50, null=True, blank=True)
    vat_reg_number = models.CharField(_(u'VAT registration number'), max_length=50, null=True, blank=True)
    juridical_address = models.CharField(_('Juridical address'), max_length=255, blank=True, null=True)
    bank_name = models.CharField(_('Bank name'), max_length=50, blank=True, null=True)
    iban = models.CharField('IBAN', default='', null=True, blank=True, max_length=100)

    # SHIPPING
    is_delivery = models.SmallIntegerField(_('Is delivery needed'), choices=DELIVERY_CHOICES, default=DELIVERY_NO)
    shipping_date = models.DateField(_('Shipping date'), blank=True, null=True)
    delivery_type = models.ForeignKey('DeliveryType', related_name="delivery_typ", blank=True, null=True, on_delete=models.SET_NULL)
    delivery_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('delivery price'), null=True, blank=True)
    cart_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('cart price'), null=True)
    delivery_country = models.ForeignKey('DeliveryCountry', related_name="delivery_cntr", blank=True, null=True, on_delete=models.SET_NULL)
    delivery_city = models.CharField(_('city'), max_length=128, blank=True, null=True)
    delivery_street = models.CharField(_('street'), max_length=128, blank=True, null=True)
    delivery_house = models.CharField(_('house'), max_length=128, blank=True, null=True)
    delivery_flat = models.CharField(_('flat'), max_length=128, blank=True, null=True)
    delivery_zip = models.CharField(_('zip'), max_length=128, blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        if self.is_legal:
            return u"%s (%s %s)" % (self.legal_name, self.first_name, self.last_name)
        return u"%s %s" % (self.first_name, self.last_name)

    @property
    def is_legal(self):
        return self.person_type == self.LEGAL

    @property
    def is_individual(self):
        return self.person_type == self.INDIVIDUAL

    @property
    def is_delivery_needed(self):
        return self.is_delivery == self.DELIVERY_YES

    def get_comments(self):
        return mark_safe("<br />".join(self.comments.split("\n")))
    get_comments.short_description = _('comments')

    def calculate_delivery(self, cart):
        pass

    def send_checkout_email(self):
        if hasattr(self, 'email'):
            return sendMail('order_sended', variables={
                    'order': self,
                },
                subject=_("Your order %s accepted") % self.get_id(),
                mails=[self.email]
            )
        return False


    @staticmethod
    def get_country_delivery_type_json():
        # json_output = {}
        # for country in DeliveryCountry.object.all():
        #     cn[country.pk] = {
        #         'pk': country.pk,
        #         'title': country.title
        #     }

        # json_output.append(cn);
        return "[{'ad': 'asd'}]"

class Order(import_item(qshop_settings.CART_ORDER_CLASS) if qshop_settings.CART_ORDER_CLASS else OrderAbstractDefault):
    pass


if qshop_settings.ENABLE_QSHOP_DELIVERY:
    class InvoiceManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(can_draw_up_an_invoice=True)

    class DeliveryCountryAbstract(models.Model):
        _translation_fields = ['title', 'vat_behavior_reason']
        VAT_NOTHING_TO_DO = 1
        VAT_MINUS_LEGAL = 2
        VAT_MINUS_LEGAL_VAT = 3

        VAT_BEHAVIOR_CHOICES = (
            (VAT_NOTHING_TO_DO, _('Nothing to do')),
            (VAT_MINUS_LEGAL, _('Take tax off a cart price')),
            (VAT_MINUS_LEGAL_VAT, _('Take tax off a cart price if legal entity with VAT')),
        )
        title = models.CharField(_('Country name'), max_length=100)
        vat_behavior = models.SmallIntegerField(choices=VAT_BEHAVIOR_CHOICES)
        vat_behavior_reason = models.CharField(_('VAT behavior reason, if reduce'), max_length=200, blank=True, null=True)
        can_draw_up_an_invoice = models.BooleanField(_('Can draw up an invoice?'), default=True, help_text=_('If legal entity'))
        iso2_code = models.CharField(_('Country 2 symbols ISO code'), max_length=2)
        sort_order = models.SmallIntegerField(_('Position'), default=0)


        objects = models.Manager() # The default manager.
        can_invoicing = InvoiceManager() # The Dahl-specific manager.

        class Meta:
            abstract = True
            verbose_name = _('delivery country')
            verbose_name_plural = _('delivery countries')
            ordering = ["sort_order", "title"]

        def __str__(self):
            return str(self.title)

        def get_vat_reduction(self, vat_nr, person_type):
            if person_type and int(person_type) == Order.LEGAL and \
                (self.vat_behavior == self.VAT_MINUS_LEGAL_VAT and vat_nr or self.vat_behavior == self.VAT_MINUS_LEGAL):
                return qshop_settings.VAT_PERCENTS
            return 0


        @classmethod
        def get_vat_reduction_static(cls, country_pk=None, vat_nr="", person_type=None):
            if country_pk:
                country = cls.objects.filter(pk=country_pk).first()
                if country:
                    return country.get_vat_reduction(vat_nr, person_type)

            return 0


    class DeliveryCountry(import_item(qshop_settings.DELIVERY_COUNTRY_CLASS) if qshop_settings.DELIVERY_COUNTRY_CLASS else DeliveryCountryAbstract):
        pass


    class DeliveryTypeAbstract(models.Model):
        _translation_fields = ['title', 'estimated_time']
        FLAT_QTY = 1
        DEPENDS_ON_SUM = 2

        PRICING_MODEL_CHOICES = (
            (FLAT_QTY, _('Amount of the items quantity')),
            (DEPENDS_ON_SUM, _('Amount of the order price')),

        )
        title = models.CharField(_('Delivery type name'), max_length=100)
        delivery_country = models.ManyToManyField('DeliveryCountry')
        estimated_time = models.CharField(_('Estimated time'), max_length=100)
        delivery_calculation = models.SmallIntegerField(_('Delivery calculation'), choices=PRICING_MODEL_CHOICES, default=FLAT_QTY)

        class Meta:
            abstract = True
            verbose_name = _('delivery type')
            verbose_name_plural = _('delivery types')

        @property
        def calculation_html(self):
            st = []
            for calc in self.deliverycalculation_set.all():
                st.append(calc.__str__())

            return mark_safe('<br>'.join(st))

        @property
        def countries_html(self):
            st = []
            for cn in self.delivery_country.all():
                st.append(cn.title)

            return mark_safe('<br>'.join(st))

        def check_country(self, country):
            cpk=country

            if isinstance(country, DeliveryCountry):
                cpk=country.pk

            ret = self.delivery_country.filter(pk=cpk).first()

            return True if ret else False


        def get_delivery_calculation(self, cart):
            ret = None
            if self.delivery_calculation == self.FLAT_QTY:
                ret = self.deliverycalculation_set.filter(value__gte=cart.total_products()).first()
            else:
                ret = self.deliverycalculation_set.filter(value__gte=cart.total_price_wo_discount()).first()

            return ret

        def get_delivery_price(self, country, cart):
            if self.check_country(country):
                dcalc = self.get_delivery_calculation(cart)
                return dcalc.delivery_price

            return 0


        @classmethod
        def get_delivery_price_static(cls, delivery_type_pk, country_pk, cart):
            if not delivery_type_pk and not country_pk:
                return 0

            dtype = cls.objects.get(pk=delivery_type_pk)
            return dtype.get_delivery_price(country_pk, cart)


        def __str__(self):
            return str(self.title)


    class DeliveryType(import_item(qshop_settings.DELIVERY_TYPE_CLASS) if qshop_settings.DELIVERY_TYPE_CLASS else DeliveryTypeAbstract):
        pass


    # class DeliveryTypeAddressAbstract(models.Model):
    #     _translation_fields = ['title']
    #     title = models.CharField(_('Address name'), max_length=100)
    #     delivery_country = models.ManyToManyField('DeliveryType')

    #     class Meta:
    #         abstract = True
    #         verbose_name = _('delivery type address')
    #         verbose_name_plural = _('delivery type adresses')

    #     def __str__(self):
    #         return str(self.title)

    # class DeliveryTypeAddress(import_item(qshop_settings.DELIVERY_TYPE_ADDRESS_CLASS) if qshop_settings.DELIVERY_TYPE_ADDRESS_CLASS else DeliveryTypeAddressAbstract):
    #     pass


    class DeliveryCalculationAbstract(models.Model):
        value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('calculation value'))
        delivery_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('price'))
        delivery_type = models.ForeignKey('DeliveryType', on_delete=models.CASCADE)

        class Meta:
            abstract = True
            verbose_name = _('delivery calculation')
            verbose_name_plural = _('delivery calculations')
            ordering = ['value']

        def __str__(self):
            return mark_safe(
                "{} - {}".format(self.value, Currency.get_fprice(self.delivery_price, format_only=True))
                )

    class DeliveryCalculation(import_item(qshop_settings.DELIVERY_CALCULATION_CLASS) if qshop_settings.DELIVERY_CALCULATION_CLASS else DeliveryCalculationAbstract):
        pass
