from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404
from .functions import get_catalogue_root, get_filter_and_page_from_url
from .classes import CategoryData
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
    filter_string, page_num, show_product = get_filter_and_page_from_url(url_add)

    if not show_product:
        # render products page

        productdata = CategoryData(request, filter_string, menu, page_num)

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
