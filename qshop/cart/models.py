from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from sitemenu import import_item
from ..models import Currency
from ..models import Product, ProductVariation

from ..qshop_settings import CART_ORDER_CLASS


class Cart(models.Model):
    date_added = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_modified = models.DateTimeField(_('modification date'), auto_now=True)
    checked_out = models.BooleanField(default=False, verbose_name=_('checked out'))
    discount = models.PositiveSmallIntegerField(_('discount'), default=0)

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-date_modified',)

    def __unicode__(self):
        return unicode(self.date_modified)

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
    cart = models.ForeignKey(Cart, verbose_name=_('cart'))
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('unit price'))
    _real_product = models.ForeignKey(Product)
    _real_product_variation = models.ForeignKey(ProductVariation, blank=True, null=True)

    objects = ItemManager()

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('cart',)

    def __unicode__(self):
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

    date_added           = models.DateTimeField(_('date added'), auto_now_add=True)
    status               = models.PositiveSmallIntegerField(_('status'), choices=STATUSES, default=1)
    manager_comments     = models.TextField(_('manager comments'), blank=True)
    cart                 = models.ForeignKey(Cart, verbose_name=_('cart'), editable=False)
    cart_text            = models.TextField(_('cart text'), editable=False)

    class Meta:
        verbose_name = _('client order')
        verbose_name_plural = _('client orders')
        abstract = True

    def __unicode__(self):
        return u"%s (%s)" % (self.pk, self.date_added)

    def get_id(self):
        return "QS%d" % self.pk

    def get_description(self):
        return _(u"Order Nr. %s") % self.get_id()

    def get_redirect(self):
        return reverse('cart_order_success')

    def finish_order(self, request):
        pass

    def get_cart_text(self):
        return self.cart_text.replace('\n', '')
    get_cart_text.allow_tags = True
    get_cart_text.short_description = _('cart text')


class OrderAbstractDefault(OrderAbstract):
    # PAYMENT_METHODS = (
    #     ('paypal', 'paypal'),
    #     #('webmoney', 'webmoney'),
    #     #('yandex', 'yandex'),
    #     ('roboxchange', 'roboxchange'),
    #     ('delayed', 'delayed'),
    # )
    # PAYMENT_METHODS_KEYS = [x[0] for x in PAYMENT_METHODS]
    # payed                = models.BooleanField(_('payed'), default=False)
    # payed_log            = models.TextField(_('payed log'), blank=True, null=True)

    name = models.CharField(_('name'), max_length=128)
    phone = models.CharField(_('phone'), max_length=32, blank=True, null=True)
    email = models.EmailField(_('email'))
    address = models.CharField(_('address'), max_length=128)
    comments = models.TextField(_('comments'), blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.email)

    def save(self, *args, **kwargs):
        #self.payed = True
        super(OrderAbstractDefault, self).save(*args, **kwargs)

    def get_comments(self):
        return mark_safe("<br />".join(self.comments.split("\n")))
    get_comments.short_description = _('comments')

    # def user_payed(self, payed_log=None):
    #     self.payed = True
    #     if payed_log:
    #         self.payed_log = payed_log
    #     self.save()


class Order(import_item(CART_ORDER_CLASS) if CART_ORDER_CLASS else OrderAbstractDefault):
    pass
