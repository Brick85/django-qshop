from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

from sitemenu.sitemenu_settings import MENUCLASS
from sitemenu import import_item

Menu = import_item(MENUCLASS)


class ProductCategoryListFilter(SimpleListFilter):
    title = _('product category')
    parameter_name = 'listcategory'

    def lookups(self, request, model_admin):
        for menu in Menu.objects.exclude(product__id=None):
            yield (str(menu.pk), menu.__unicode__())

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category=self.value())
        return queryset
