from django.template.loader import render_to_string
from django.contrib.sites.models import Site
import datetime
from overloadable_functions import count_delivery_price

from django.conf import settings

import models
from ..models import Currency
from qshop import qshop_settings


CART_ID = '%s-cart' % settings.ROOT_URLCONF


class ItemAlreadyExists(Exception):
    pass


class ItemDoesNotExist(Exception):
    pass


class ItemTooMany(Exception):
    pass


class Cart:
    def __init__(self, request, cart=None):
        if cart:
            self.cart = cart
            return
        cart_id = request.session.get(CART_ID)
        if cart_id:
            try:
                cart = models.Cart.objects.get(id=cart_id, checked_out=False)
            except models.Cart.DoesNotExist:
                cart = self.new(request)
        else:
            cart = self.new(request)
        self.cart = cart

    def __iter__(self):
        for item in self.get_products():
            yield item

    def get_products(self):
        try:
            return self._products
        except:
            self._products = self.cart.item_set.all()
            return self._products

    def total_price(self, in_default_currency=False):
        total_price = 0
        for item in self.get_products():
            total_price += item.total_price(in_default_currency=True)
        if in_default_currency:
            return float(total_price)
        else:
            return Currency.get_price(total_price)

    def total_fprice(self):
        return Currency.get_fprice(self.total_price(), format_only=True)

    def total_price_with_delivery(self):
        return Currency.get_price(self.total_price(in_default_currency=True) + self.delivery_price(in_default_currency=True))

    def total_fprice_with_delivery(self):
        return Currency.get_fprice(self.total_price_with_delivery(), format_only=True)

    def delivery_price(self, in_default_currency=False):
        try:
            self._delivery_price
        except:
            self._delivery_price = count_delivery_price(price=self.total_price(in_default_currency=True), weight=self.total_weight(), cart=self)
        if in_default_currency:
            return float(self._delivery_price)
        return Currency.get_price(self._delivery_price)

    def delivery_fprice(self):
        return Currency.get_fprice(self.delivery_price(), format_only=True)

    def total_weight(self):
        try:
            return self._total_weight
        except:
            total_weight = 0
            for item in self.get_products():
                total_weight += item.product.weight * item.quantity
            self._total_weight = total_weight
            return self._total_weight

    def total_fweight(self):
        return "%.2f" % self.total_weight()

    def total_products(self):
        try:
            return self._count
        except:
            self._count = self.cart.item_set.count()
        return self._count

    def total_products_with_qty(self):
        try:
            return self._count_with_qty
        except:
            self._count_with_qty = 0
            for item in self.get_products():
                self._count_with_qty += item.quantity
        return self._count_with_qty

    def new(self, request):
        cart = models.Cart()
        cart.save()
        request.session[CART_ID] = cart.id
        return cart

    def get_session_id(self, request):
        return request.session[CART_ID]

    def set_session_id(self, request, cart_id):
        request.session[CART_ID] = cart_id

    def add(self, product, quantity=1):
        self.clear_cache()
        if quantity <= 0:
            return False
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                product=product,
            )
        except models.Item.DoesNotExist:
            item = models.Item()
            item.cart = self.cart
            item.product = product
            item.unit_price = product.get_price(default_currency=True)
            item.quantity = quantity
            item.product_variation = product.selected_variation
            if item.product.can_be_purchased(item.quantity):
                item.save()
            else:
                e = ItemTooMany('Lack in stock!')
                e.product = item.product
                raise e
        else:
            item.quantity += int(quantity)
            if item.product.can_be_purchased(item.quantity):
                item.save()
            else:
                e = ItemTooMany('Lack in stock!')
                e.product = item.product
                raise e
        return True

    def remove(self, item_id):
        self.clear_cache()
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                pk=item_id,
            )
        except models.Item.DoesNotExist:
            pass
        else:
            item.delete()

    def update(self, item_id, quantity):
        self.clear_cache()
        if quantity <= 0:
            return self.remove(item_id)
        try:
            item = models.Item.objects.get(
                cart=self.cart,
                pk=item_id,
            )
            item.quantity = int(quantity)
            if item.product.can_be_purchased(item.quantity):
                item.save()
            else:
                e = ItemTooMany('Lack in stock!')
                e.product = item.product
                raise e
        except models.Item.DoesNotExist:
            pass

    def clear_cache(self):
        if hasattr(self, '_products'):
            del self._products
        if hasattr(self, '_delivery_price'):
            del self._delivery_price
        if hasattr(self, '_total_weight'):
            del self._total_weight
        if hasattr(self, '_count'):
            del self._count
        if hasattr(self, '_count_with_qty'):
            del self._count_with_qty

    def clear(self):
        for item in self.cart.item_set:
            item.delete()

    def as_table(self, standalone=False):
        link_add = ''
        image_add = ''
        if standalone:
            link_add = 'http://{0}'.format(Site.objects.get_current().domain if qshop_settings.CART_TABLE_LINK_ADD != None else qshop_settings.CART_TABLE_LINK_ADD)
            image_add = 'http://{0}'.format(Site.objects.get_current().domain if qshop_settings.CART_TABLE_IMAGE_ADD != None else qshop_settings.CART_TABLE_IMAGE_ADD)
        return render_to_string('qshop/cart/_cart_as_table.html', {
            'LINK_ADD': link_add,
            'IMAGE_ADD': image_add,
            'cart': self,
        })

    def checkout(self):
        self.cart.checked_out = True
        self.cart.save()
