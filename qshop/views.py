from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
#from django.http import Http404
from .functions import get_products_page_data
from .classes import CategoryData
from .models import Product
from django.http import HttpResponsePermanentRedirect


# def render_categorypage(request, menu, url_add):
#     if url_add:
#         raise Http404

#     return render_to_response('qshop/categorypage.html', {
#             'menu': menu,
#             'url_add': url_add,
#             'catalogue_root': get_catalogue_root(menu),
#         }, context_instance=RequestContext(request))


def render_shopspage(request, menu, url_add):
    filter_string, page_num, sort, show_product = get_products_page_data(url_add)

    if not show_product:
        # render products page

        productdata = CategoryData(request, filter_string, menu, sort, page_num)

        if productdata.need_return:
            return productdata.return_data

        return render_to_response('qshop/productspage.html', {
                'menu': menu,
                'url_add': url_add,
                'productdata': productdata,
            }, context_instance=RequestContext(request))

    else:
        # render single product page

        product = get_object_or_404(Product, articul=url_add[0], category=menu)

        menu._page_title = product.name

        return render_to_response('qshop/productpage.html', {
                'menu': menu,
                'url_add': url_add,
                'product': product,
            }, context_instance=RequestContext(request))


def redirect_to_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return HttpResponsePermanentRedirect(product.get_absolute_url())
