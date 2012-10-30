

def get_catalogue_root(menu):
    items = menu.__class__.objects.filter(pk__in=menu.get_parents_ids_list() + [menu.pk])
    for item in items:
        if item.page_type == 'pcat':
            return item
    return menu


def get_filter_and_page_from_url(url_add):
    filter_string = ''
    page_num = 1
    show_product = True
    if url_add and url_add[0] == 'filter':
        filter_string = url_add[1]
        show_product = False
    if url_add and url_add[0] == 'page':
        page_num = url_add[1]
        show_product = False
    if len(url_add) >= 4 and url_add[2] == 'page':
        page_num = url_add[3]
    if not url_add:
        show_product = False
    return (filter_string, page_num, show_product)
