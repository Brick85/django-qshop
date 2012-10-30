from sitemenu import sitemenu_settings

sitemenu_settings.PAGES += (
    ('', '---------', ''),
    ('pcat', 'Category page', 'qshop.views.render_categorypage'),
    ('prod', 'Products page', 'qshop.views.render_productspage'),
)


