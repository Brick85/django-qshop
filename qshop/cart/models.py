from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..models import Currency
from ..models import Product

#from django.core.urlresolvers import reverse

class Cart(models.Model):
    date_added = models.DateTimeField(_('creation date'), auto_now_add=True)
    date_modified = models.DateTimeField(_('modification date'), auto_now=True)
    checked_out = models.BooleanField(default=False, verbose_name=_('checked out'))

    class Meta:
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-date_modified',)

    def __unicode__(self):
        return unicode(self.date_modified)

    def get_cartobject(self):
        from cart import Cart as CartObject
        return CartObject(None, self)


class Item(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_('cart'))
    quantity = models.PositiveIntegerField(verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=18, decimal_places=2, verbose_name=_('unit price'))
    product = models.ForeignKey(Product)

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('cart',)

    def __unicode__(self):
        return '%s - %s' % (self.quantity, self.unit_price)

    def total_price(self):
        return Currency.get_price(self.quantity * self.unit_price)

    def total_fprice(self):
        return Currency.get_fprice(self.total_price(), format_only=True)


# class Order(models.Model):

#     STATUSES = (
#         (1, _('New')),
#         (2, _('In Progress')),
#         (3, _('Completed')),
#     )
#     PAYMENT_METHODS = (
#         ('paypal', 'paypal'),
#         ('paypal_cc', 'paypal_cc'),
#         #('webmoney', 'webmoney'),
#         #('yandex', 'yandex'),
#         ('roboxchange', 'roboxchange'),
#         ('delayed', 'delayed'),
#     )
#     PAYMENT_METHODS_KEYS = [x[0] for x in PAYMENT_METHODS]

#     date_added           = models.DateTimeField(_('date added'), auto_now_add=True)
#     status               = models.PositiveSmallIntegerField(_('status'), choices=STATUSES, default=1)
#     manager_comments     = models.TextField(_('manager comments'), blank=True)
#     cart                 = models.ForeignKey(Cart, verbose_name=_('cart'))
#     cart_text            = models.TextField(_('cart text'))
#     user                 = models.ForeignKey(User, verbose_name=_('order user'))
#     payment_method       = models.CharField(_('payment method'), max_length=12, choices=PAYMENT_METHODS)
#     delayed_option       = models.ForeignKey(DelayedPaymentOption, verbose_name=_('delayed option'), null=True, blank=True)
#     payment_token        = models.CharField(_('payment token'), max_length=128, editable=False, blank=True, null=True, unique=True)
#     payed                = models.BooleanField(_('payed'), default=False)
#     payed_log            = models.TextField(_('payed log'), blank=True, null=True)

#     class Meta:
#         verbose_name = _('client order')
#         verbose_name_plural = _('client orders')


#     def __unicode__(self):
#         return u"%s %s (%s)" % (self.user.first_name, self.user.last_name, self.user.email)


#     def pay(self):
#         if self.payment_method == 'paypal' or self.payment_method == 'paypal_cc':
#             from vendors.paypal import Paypal
#             p = Paypal()
#             try:
#                 self.payment_token = p.set_checkout(self.cart.get_cartobject())
#                 self.save()
#                 self._redirect = p.REDIRECTURL % self.payment_token
#             except TypeError as e:
#                 self.payed_log = str(self.payed_log) + str(e)
#                 self.save()
#                 self._redirect = reverse('cart_order_error')

#         if self.payment_method == 'webmoney':
#             self._redirect = reverse('weboney_redirect', args=[self.pk])

#         if self.payment_method == 'roboxchange':
#             self._redirect = reverse('roboxchange_redirect', args=[self.pk])

#         if self.payment_method == 'delayed':
#             self._redirect = self.delayed_option.get_absolute_url()

#     def get_redirect(self):
#         return self._redirect

#     def user_payed(self):
#         self.payed = True
#         self.save()

#         cart = self.cart.get_cartobject()
#         products = cart.get_products()

#         subscription_add = 0

#         show_video_message = False

#         for product in products:
#             real_product = product.get_product()
#             subscription_add += real_product.subscription * product.quantity
#             if real_product.video_download:
#                 show_video_message = True
#             try:
#                 purchasedproduct = PurchasedProduct.objects.get(user=self.user, product=real_product)
#                 purchasedproduct.date = datetime.now()
#             except:
#                 purchasedproduct = PurchasedProduct()
#                 purchasedproduct.user = self.user
#                 purchasedproduct.product = real_product
#             if real_product.video_download:
#                 purchasedproduct.createsymlink()

#             purchasedproduct.save()

#         if subscription_add > 0:
#             show_video_message = True
#             profile = self.user.get_profile()
#             if datetime(profile.subscription.year, profile.subscription.month, profile.subscription.day) < datetime.today():
#                 profile.subscription = datetime.now()
#             profile.subscription = profile.subscription + timedelta(days=subscription_add)
#             profile.createsymlink()
#             profile.save()

#         from misc.functions import sendMailFromShop
#         from options.models import Option

#         opts = {
#             'cart_text': self.cart_text,
#             'order': self,
#             'user': self.user,
#             'show_video_message': show_video_message,
#         }

#         sendMailFromShop([self.user.email], _('Your order from Psyreal'), 'mails/order_to_user.html', opts)
#         sendMailFromShop(Option.getValues('mail_order'), _('[PSYREAL] Order %d payed') % self.id, 'mails/order_to_admin_payed.html', opts)


# class PurchasedProduct(models.Model):
#     user = models.ForeignKey(User)
#     product = models.ForeignKey(Product)
#     date = models.DateTimeField(auto_now=True)
#     symlink = models.CharField(max_length=128, blank=True, null=True, default=None)

#     class Meta:
#         unique_together = ("user", "product")

#     def createsymlink(self):
#         if not self.symlink and self.product.video_download:
#             self.symlink = self.product.video_download.createsymlink(self.user)

#     def expires(self):
#         return self.date + timedelta(days=DAYS_TO_SHOW_PURCHASED_PRODUCTS)
