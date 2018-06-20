import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect

from sitemenu import import_item
from ..models import Currency
from ..models import Product, ProductVariation

from qshop import qshop_settings
from django.conf import settings


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

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-date_modified',)

    def __str__(self):
        return str(self.date_modified)

    def get_cartobject(self):
        from cart import Cart as CartObject
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
        pass

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
    first_name = models.CharField(_('first name'), max_length=70, blank=True)
    last_name = models.CharField(_('last name'), max_length=70, blank=True)
    phone = models.CharField(_('phone'), max_length=32, blank=True, null=True)
    email = models.EmailField(_('email'))
    address = models.CharField(_('address'), max_length=128)
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
    delivery_country = models.ForeignKey('DeliveryCountry', related_name="delivery_cntr", blank=True, null=True, on_delete=models.SET_NULL)
    delivery_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('delivery price'), null=True, blank=True)
    cart_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('cart price'), null=True)


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

class Order(import_item(qshop_settings.CART_ORDER_CLASS) if qshop_settings.CART_ORDER_CLASS else OrderAbstractDefault):
    pass


if qshop_settings.ENABLE_QSHOP_DELIVERY:
    class DeliveryCountryAbstract(models.Model):
        _translation_fields = ['title']
        VAT_NOTHING_TO_DO = 1
        VAT_MINUS = 2
        VAT_MINUS_IF_JURIDICAL = 3

        VAT_BEHAVIOR_CHOICES = (
            (VAT_NOTHING_TO_DO, _('Nothing to do')),
            (VAT_MINUS, _('Take tax off a cart price')),
            (VAT_MINUS_IF_JURIDICAL, _('Take tax off a cart price if legal entity with VAT')),
        )
        title = models.CharField(_('Country name'), max_length=100)
        vat_behavior = models.SmallIntegerField(choices=VAT_BEHAVIOR_CHOICES)

        class Meta:
            abstract = True
            verbose_name = _('delivery country')
            verbose_name_plural = _('delivery countries')

        def __str__(self):
            return str(self.title)


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

        def __str__(self):
            return str(self.title)


    class DeliveryType(import_item(qshop_settings.DELIVERY_TYPE_CLASS) if qshop_settings.DELIVERY_TYPE_CLASS else DeliveryTypeAbstract):
        pass


    class DeliveryTypeAddressAbstract(models.Model):
        _translation_fields = ['title']
        title = models.CharField(_('Address name'), max_length=100)
        delivery_country = models.ManyToManyField('DeliveryType')

        class Meta:
            abstract = True
            verbose_name = _('delivery type address')
            verbose_name_plural = _('delivery type adresses')

        def __str__(self):
            return str(self.title)

    class DeliveryTypeAddress(import_item(qshop_settings.DELIVERY_TYPE_ADDRESS_CLASS) if qshop_settings.DELIVERY_TYPE_ADDRESS_CLASS else DeliveryTypeAbstract):
        pass


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
