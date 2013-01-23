from django import template
from ..cart import Cart
from ..functions import get_catalogue_root

register = template.Library()


@register.simple_tag(takes_context=True)
def qshop_items_in_cart_with_qty(context):
    cart = Cart(context['request'])
    return cart.total_products_with_qty()


@register.simple_tag(takes_context=True)
def qshop_items_in_cart(context):
    cart = Cart(context['request'])
    return cart.total_products()


@register.simple_tag(takes_context=True)
def set_catalogue_root(context):
    if 'menu' in context:
        context['catalogue_root'] = get_catalogue_root(context['menu'])
    else:
        context['catalogue_root'] = None
    return ''
