from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.utils.datastructures import DotExpandedDict
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import logout

from . import Cart, ItemAlreadyExists, ItemDoesNotExist
from ..models import Product
#from .forms import OrderForm, OrderPaymentForm
#from .models import Order, DelayedPaymentOption


def add_to_cart(request, product_id):
    cart = Cart(request)

    quantity = request.GET.get('quantity', 1)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.add_message(request, messages.ERROR, _('Wrong product.'))
    else:
        cart.add(product, product.get_price(), quantity)

        messages.add_message(request, messages.INFO, _('Product added to <a href="%s">cart</a>.') % reverse('cart'))

    return_url = request.GET.get('return_url', None)
    if return_url:
        return HttpResponseRedirect(return_url)
    return HttpResponseRedirect(reverse('cart'))


def remove_from_cart(request, product_id):
    cart = Cart(request)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.add_message(request, messages.ERROR, _('Wrong product.'))
    else:
        cart.remove(product)
    return HttpResponseRedirect(reverse('cart'))


def update_cart(request):
    cart = Cart(request)
    data = DotExpandedDict(request.POST)
    for (product_id, quantity) in data['quantity'].items():
        try:
            product = Product.objects.get(pk=product_id)
            quantity = int(quantity)
            if quantity < 1:
                cart.remove(product)
            else:
                cart.update(product, quantity)
        except:
            pass
    return HttpResponseRedirect(reverse('cart'))


def show_cart(request):
    cart = Cart(request)
    return render_to_response('qshop/cart/show.html', {
        'cart': cart,
    }, context_instance=RequestContext(request))


# def order_cart(request):
#     cart = Cart(request)
#     if cart.total_products() < 1:
#         return HttpResponseRedirect(reverse('cart'))

#     if 'logout' in request.GET:
#         cart_id = cart.get_session_id(request)
#         logout(request)
#         cart.set_session_id(request, cart_id)
#         return HttpResponseRedirect(reverse('order_cart'))

#     show_exists_message = False
#     login_message = ''
#     username = ''
#     payment_error = ''

# #    delayed_payment_options = DelayedPaymentOption.objects.all()
#     paymentform = OrderPaymentForm()

#     if request.user.is_authenticated():
#         try:
#             instance_profile = request.user.get_profile()
#         except:
#             return HttpResponseRedirect(reverse('order_cart') + '?logout')
#         form = OrderForm(instance=instance_profile)
#         del form.fields['firstname']
#         del form.fields['lastname']
#         del form.fields['email']
#     else:
#         form = OrderForm()

#     if request.method == 'POST' and request.POST.get('gender', None):
#         if request.user.is_authenticated():
#             form = OrderForm(request.POST, instance=request.user.get_profile())
#             del form.fields['firstname']
#             del form.fields['lastname']
#             del form.fields['email']
#         else:
#             form = OrderForm(request.POST)

#         paymentform = OrderPaymentForm(request.POST)

#         # if payment_method not in Order.PAYMENT_METHODS_KEYS:
#         #     payment_error = _('Choose payment method!')
#         f_is_valid = form.is_valid()
#         pf_is_valid = paymentform.is_valid()

#         delivery_error = False

#         if f_is_valid:
#             if form.cleaned_data['other_address']:
#                 country = form.cleaned_data['delivery_country']
#             else:
#                 country = form.cleaned_data['country']

#             if country.get_delivery_price(cart.total_weight()) == None:
#                 delivery_error = True

#         if not delivery_error and f_is_valid and pf_is_valid:
#             user = None

#             if not request.user.is_authenticated():
#                 if User.objects.filter(email=form.cleaned_data['email']):
#                     show_exists_message = True
#                 else:

#                     password = UserManager().make_random_password()

#                     user = User.objects.create_user(form.cleaned_data['email'], form.cleaned_data['email'], password)
#                     user.first_name = form.cleaned_data['firstname']
#                     user.last_name = form.cleaned_data['lastname']
#                     user.save()
#                     is_new_user = True
#             else:
#                 user = request.user
#                 is_new_user = False
#                 password = ''

#             if user:
#                 form.save(user)
#                 del user._profile_cache

#                 cart._user = user

#                 order = Order()

#                 order.user = user
#                 order.cart = cart.cart
#                 order.cart_text = cart.as_table(order)

#                 order.payment_method = paymentform.cleaned_data['payment_method']
#                 order.delayed_option = paymentform.cleaned_data['delayed_option']

#                 cart.check_out()
#                 order.save()

#                 opts = {
#                     'user': user,
#                     'user_password': password,
#                 }

#                 from misc.functions import sendMailFromShop
#                 from options.models import Option

#                 sendMailFromShop(Option.getValues('mail_order'), _('[PSYREAL] New order %d') % order.pk, 'mails/order_to_admin.html', {
#                     'cart_text': order.cart_text,
#                     'order': order,
#                     'user': user,
#                 })

#                 if is_new_user:
#                     sendMailFromShop([user.email], _('Psyreal registration'), 'mails/user_registred.html', opts)

#                 if order.payment_method == 'delayed':
#                     sendMailFromShop([user.email], _('Psyreal payment'), 'mails/delayed_mail.html', {
#                     'order': order,
#                     'user': user,
#                 })

#                 order.pay()

#                 return HttpResponseRedirect(order.get_redirect())

#                 # from psyreal.settings import ORDER_MAILS
#                 # sendMailFromShop(ORDER_MAILS, _('[PsyReal] New order - %s')%order.pk, 'cart/_mail_order_to_admin.html', opts)

#                 #sendCartMail(form.cleaned_data['email'], order.cart_text, order)

#     elif request.method == 'POST' and request.POST.get('username', None):
#         username = request.POST.get('username', '')
#         password = request.POST.get('password', '')

#         from django.contrib.auth import authenticate, login

#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 cart_id = cart.get_session_id(request)
#                 login(request, user)
#                 cart.set_session_id(request, cart_id)
#                 return HttpResponseRedirect(reverse('order_cart'))
#             else:
#                 login_message = _('This account is disabled!')
#         else:
#             login_message = _('Wrong password!')

#     return render_to_response('cart/order.html', {
#         'login_message': login_message,
#         'username': username,
#         'cart': cart,
#         'form': form,
#         'show_exists_message': show_exists_message,
#         'payment_methods': Order.PAYMENT_METHODS,
#         'payment_error': payment_error,
#         #'payment_method': payment_method,
#         'paymentform': paymentform,
#     }, context_instance=RequestContext(request))


# def cart_order_success(request):
#     order_pk = request.session.get('order_pk', None)
#     try:
#         del request.session['order_pk']
#     except:
#         pass
#     order = get_object_or_404(Order, pk=order_pk)
#     return render_to_response('cart/order_success.html', {
#         'order': order,
#     }, context_instance=RequestContext(request))


# def cart_order_cancelled(request):
#     return render_to_response('cart/order_cancelled.html', {
#     }, context_instance=RequestContext(request))


# def cart_order_error(request):
#     return render_to_response('cart/order_error.html', {
#     }, context_instance=RequestContext(request))
