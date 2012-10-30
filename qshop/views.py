from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from .functions import get_catalogue_root, CategoryData
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
    if not url_add or (url_add[0] == 'filter'):
        # render products page

        productdata = CategoryData(request, url_add, menu)

        if productdata.need_return:
            return productdata.return_data

        return render_to_response('qshop/productspage.html', {
                'menu': menu,
                'url_add': url_add,
                'catalogue_root': get_catalogue_root(menu),
                'productdata': productdata,
            }, context_instance=RequestContext(request))

    else:
        # render single product page

        product = get_object_or_404(Product, articul=url_add[0])

        menu._page_title = product.name

        return render_to_response('qshop/productpage.html', {
                'menu': menu,
                'url_add': url_add,
                'catalogue_root': get_catalogue_root(menu),
                'product': product,
            }, context_instance=RequestContext(request))
