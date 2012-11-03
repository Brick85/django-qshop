from django import template
from ..cart import Cart

register = template.Library()

def qshop_items_in_cart_with_qty(context):
    cart = Cart(context['request'])
    return cart.total_products_with_qty()
register.simple_tag(takes_context=True)(qshop_items_in_cart_with_qty)

def qshop_items_in_cart(context):
    cart = Cart(context['request'])
    return cart.total_products()
register.simple_tag(takes_context=True)(qshop_items_in_cart)
