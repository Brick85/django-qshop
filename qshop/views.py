from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404  #, HttpResponseRedirect, HttpResponsePermanentRedirect
from . import get_catalogue_root
from .models import Product


def render_categorypage(request, menu, url_add):
    if url_add:
        raise Http404

    return render_to_response('qshop/categorypage.html', {
            'menu': menu,
            'url_add': url_add,
            'catalogue_root': get_catalogue_root(menu),
        }, context_instance=RequestContext(request))


def render_productspage(request, menu, url_add):

    if not url_add:
        # render products page

        products = Product.objects.filter(category=menu)

        for product in products:
            product._current_category = menu

        return render_to_response('qshop/productspage.html', {
                'menu': menu,
                'url_add': url_add,
                'catalogue_root': get_catalogue_root(menu),
                'products': products,
            }, context_instance=RequestContext(request))

    else:
        # render product page

        product = get_object_or_404(Product, articul=url_add[0])

        return render_to_response('qshop/productpage.html', {
                'menu': menu,
                'url_add': url_add,
                'catalogue_root': get_catalogue_root(menu),
                'product': product,
            }, context_instance=RequestContext(request))
