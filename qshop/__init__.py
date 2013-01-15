from sitemenu import sitemenu_settings

sitemenu_settings.PAGES += (
    ('', '---------', ''),
#    ('pcat', 'Category page', 'qshop.views.render_categorypage'),
#    ('prod', 'Products page', 'qshop.views.render_productspage'),
)
from qshop import qshop_settings

sitemenu_settings.PAGES += qshop_settings.PAGES
