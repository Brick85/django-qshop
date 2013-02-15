from django import template
from ..models import Currency
from ..cart import Cart
from ..functions import get_catalogue_root

register = template.Library()


@register.simple_tag(takes_context=True)
def qshop_items_in_cart_with_qty(context, as_var=None):
    cart = Cart(context['request'])
    if as_var:
        context[as_var] = cart.total_products_with_qty()
        return ''
    return cart.total_products_with_qty()


@register.simple_tag(takes_context=True)
def qshop_items_in_cart(context, as_var=None):
    cart = Cart(context['request'])
    if as_var:
        context[as_var] = cart.total_products()
        return ''
    return cart.total_products()


@register.simple_tag(takes_context=True)
def set_catalogue_root(context):
    if 'menu' in context:
        context['catalogue_root'] = get_catalogue_root(context['menu'])
    else:
        context['catalogue_root'] = None
    return ''


@register.simple_tag(takes_context=True)
def set_currencies_list(context):
    context['current_currency'] = Currency.get_default_currency()
    context['currencies_list'] = Currency.objects.all()
    return ''
