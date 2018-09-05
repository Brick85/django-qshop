import re
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, get_object_or_404
from django.views.generic import CreateView, TemplateView
from .cart import Cart, ItemTooMany
from ..models import Product
from .forms import OrderForm
from .models import Order



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
            except ItemTooMany as e:
                messages.add_message(
                    request, messages.WARNING, _(u'Can\'t add product "%s" due to lack in stock. Try to decrease quantity.') % e.product
                )
        else:
            for k, v in variation_quantities.items():
                product.select_variation(k)
                try:
                    if cart.add(product, v):
                        result = True
                except ItemTooMany as e:
                    messages.add_message(
                        request, messages.WARNING, _(u'Can\'t add product "%s" due to lack in stock. Try to decrease quantity.') % e.product
                    )

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
        except ItemTooMany as e:
            messages.add_message(
                request, messages.WARNING, _(u'Can\'t add product "%s" due to lack in stock. Try to decrease quantity.') % e.product
            )

    request._server_cache = {'set_cookie': True}
    return HttpResponseRedirect(reverse('cart'))



class CartDetailView(TemplateView):
    template_name = "qshop/cart/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        return context



class OrderDetailView(CreateView):
    form_class = OrderForm
    template_name = 'qshop/cart/order_extended.html'

    @property
    def cart(self):
        cart = Cart(self.request)
        return cart

    def get(self, request, *args, **kwargs):
        if self.cart.total_products() < 1:
            return HttpResponseRedirect(reverse('cart'))
        return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(OrderDetailView, self).get_form_kwargs()
        kwargs['cart'] = self.cart
        return kwargs

    def form_valid(self, form):
        try:
            order = form.save()
            order.finish_order(self.request)
            self.request.session['order_pk'] = order.pk
            return order.get_redirect_response()
        except ItemTooMany:
            messages.add_message(self.request, messages.WARNING, _('Someone already bought product that you are trying to buy.'))

        return super(OrderDetailView, self).form_valid(form)


class AjaxOrderDetailView(OrderDetailView):
    def form_valid(self, form):
        import ipdb; ipdb.set_trace()


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
    return render(request, 'qshop/cart/order_success.html', {
        'order': order,
    })

@csrf_exempt
def cart_order_cancelled(request, order_id=None):
    if order_id:
        order = get_object_or_404(Order, pk=order_id, paid=False)
        order.status = 4
        order.add_log_message('Order canceled!')
        order.save()
    return render(request, 'qshop/cart/order_cancelled.html', {
    })


def cart_order_error(request):
    return render(request, 'qshop/cart/order_error.html', {
    })

from qshop.qshop_settings import CART_ORDER_VIEW

if CART_ORDER_VIEW:
    from sitemenu import import_item
    qshop_order_view = import_item(CART_ORDER_VIEW)

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

    return render(request, 'qshop/cart/order.html', {
        'cart': cart,
        'order_form': order_form,
    })
