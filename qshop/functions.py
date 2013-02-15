from .models import Product


def get_catalogue_root(menu):
    items = menu.__class__.objects.filter(pk__in=menu.get_parents_ids_list() + [menu.pk])
    for item in items:
        if item.page_type == 'prod':
            return item
    return menu


def get_products_page_data(url_add):
    filter_string = ''
    page_num = 1
    show_product = True
    sort = Product.SORT_VARIANTS[0][0]
    if not url_add:
        show_product = False
    if url_add and url_add[0].startswith('sort-'):
        sort = url_add[0].replace('sort-', '')
        show_product = False
        del url_add[0]
    if url_add and url_add[0].startswith('filter-'):
        filter_string = url_add[0].replace('filter-', '')
        show_product = False
        del url_add[0]
    if url_add and url_add[0].startswith('page-'):
        page_num = url_add[0].replace('page-', '')
        show_product = False
        del url_add[0]
    return (filter_string, page_num, sort, show_product)

