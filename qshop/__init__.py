from sitemenu import sitemenu_settings

sitemenu_settings.PAGES += (
    ('', '---------', ''),
    ('pcat', 'Category page', 'qshop.views.render_categorypage'),
    ('prod', 'Products page', 'qshop.views.render_productspage'),
)


def get_catalogue_root(menu):
    items = menu.__class__.objects.filter(pk__in=menu.get_parents_ids_list() + [menu.pk])
    for item in items:
        if item.page_type == 'pcat':
            return item
    return menu
