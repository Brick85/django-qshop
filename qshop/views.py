from django.shortcuts import render, get_object_or_404
from .functions import get_products_page_data
from .classes import CategoryData
from .models import Product, Currency
from django.http import HttpResponseRedirect, Http404


def render_shopspage(request, menu, url_add, products=None):
    filter_string, page_num, sort, show_product = get_products_page_data(url_add)

    if not show_product:
        # render products page

        productdata = CategoryData(request, filter_string, menu, sort, page_num, products)

        if productdata.need_return:
            return productdata.return_data

        return render(request, 'qshop/productspage.html', {
                'menu': menu,
                'url_add': url_add,
                'productdata': productdata,
            })

    else:
        # render single product page

        if len(url_add) != 1:
            raise Http404('wrong url_add')

        product = get_object_or_404(Product, articul=url_add[0], category=menu, hidden=False)

        menu._page_title = product.name

        return render(request, 'qshop/productpage.html', {
                'menu': menu,
                'url_add': url_add,
                'product': product,
            })


def redirect_to_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return HttpResponseRedirect(product.get_absolute_url_slow())


def set_currency(request, currency_code=None):
    if not currency_code:
        currency_code = request.POST.get('currency_code', None)
    redirect_url = request.GET.get('redirect_url', request.POST.get('redirect_url', '/'))

    currency = get_object_or_404(Currency, code=currency_code)

    Currency.set_default_currency(currency)

    return HttpResponseRedirect(redirect_url)
