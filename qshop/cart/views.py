from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

from . import Cart, ItemAlreadyExists, ItemDoesNotExist, ItemTooMany
from ..models import Product
from .forms import OrderForm
from .models import Order

from qshop.qshop_settings import CART_ORDER_VIEW

import re

if CART_ORDER_VIEW:
    from sitemenu import import_item
    qshop_order_view = import_item(CART_ORDER_VIEW)


def add_to_cart(request, product_id):
    cart = Cart(request)

    quantity = request.GET.get('quantity', 1)
    variation_id = request.GET.get('variation', None)
    variation_quantities = {}

    if not variation_id:
        variation_quantity_re = re.compile('^variation_quantity_(\d+)$')
        for item in request.GET:
            match = variation_quantity_re.match(item)
            if match:
                try:
                    variation_quantities[int(match.group(1))] = int(request.GET.get(item))
                except ValueError:
                    pass

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.add_message(request, messages.ERROR, _('Wrong product.'))
    else:
        result = False
        if not variation_quantities:
            product.select_variation(variation_id)
            try:
                if cart.add(product, quantity):
                    result = True
            except ItemTooMany, e:
                messages.add_message(request, messages.WARNING, _(u'Can\'t add product "%s" due to lack in stock. Try to decrease quantity.') % e.product)
        else:
            for k, v in variation_quantities.items():
                product.select_variation(k)
                try:
                    if cart.add(product, v):
                        result = True
                except ItemTooMany, e:
                    messages.add_message(request, messages.WARNING, _(u'Can\'t add product "%s" due to lack in stock. Try to decrease quantity.') % e.product)

        if result:
            messages.add_message(request, messages.INFO, _(u'Product added to <a href="%s">cart</a>.') % reverse('cart'))

    return_url = request.GET.get('return_url', None)

    request._server_cache = {'set_cookie': True}
    if return_url:
        return HttpResponseRedirect(return_url)
    return HttpResponseRedirect(reverse('cart'))


def remove_from_cart(request, item_id):
    cart = Cart(request)
    cart.remove(item_id)

    request._server_cache = {'set_cookie': True}
    return HttpResponseRedirect(reverse('cart'))


def update_cart(request):
    cart = Cart(request)
    for (key, quantity) in request.POST.items():
        if not key.startswith('quantity.'):
            continue
        try:
            item_id = int(key.replace('quantity.', ''))
        except:
            continue

        try:
            quantity = int(quantity)
            cart.update(item_id, quantity)
        except ItemTooMany, e:
            messages.add_message(request, messages.WARNING, _(u'Quantity for product "%s" not set due to lack in stock.' % e.product))

    request._server_cache = {'set_cookie': True}
    return HttpResponseRedirect(reverse('cart'))


def show_cart(request):
    cart = Cart(request)
    return render_to_response('qshop/cart/cart.html', {
        'cart': cart,
    }, context_instance=RequestContext(request))


def order_cart(request):
    if CART_ORDER_VIEW:
        return qshop_order_view(request)

    cart = Cart(request)

    order_form = OrderForm()

    if request.method == 'POST':
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            try:
                order = order_form.save(cart)
                request.session['order_pk'] = order.pk
                cart.checkout()
                order.finish_order(request)
                return order.get_redirect_response()
            except ItemTooMany:
                messages.add_message(request, messages.WARNING, _('Someone already bought product that you are trying to buy.'))

    if cart.total_products() < 1:
        return HttpResponseRedirect(reverse('cart'))

    return render_to_response('qshop/cart/order.html', {
        'cart': cart,
        'order_form': order_form,
    }, context_instance=RequestContext(request))


def cart_order_success(request):
    order_pk = request.session.get('order_pk', None)
    try:
        del request.session['order_pk']
    except:
        pass
    try:
        order = Order.objects.get(pk=order_pk)
    except:
        return HttpResponseRedirect('/')
    return render_to_response('qshop/cart/order_success.html', {
        'order': order,
    }, context_instance=RequestContext(request))

@csrf_exempt
def cart_order_cancelled(request, order_id=None):
    if order_id:
        order = get_object_or_404(Order, pk=order_id, payed=False)
        order.status = 4
        order.add_log_message('Order canceled!')
        order.save()
    return render_to_response('qshop/cart/order_cancelled.html', {
    }, context_instance=RequestContext(request))


def cart_order_error(request):
    return render_to_response('qshop/cart/order_error.html', {
    }, context_instance=RequestContext(request))
