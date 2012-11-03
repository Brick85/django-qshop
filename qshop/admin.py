from django.contrib import admin
from .models import Product, ProductVariationValue, ProductVariation, ProductImage, ParametersSet, Parameter, ProductToParameter, ParameterValue
#from django.db import models

from .admin_forms import ProductToParameterFormset

from .admin_filters import ProductCategoryListFilter

from django.conf import settings


class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductToParameterInline(admin.TabularInline):
    model = ProductToParameter
    #formset = ProductToTypeFieldFormset
    extra = 0
    can_delete = False
    #readonly_fields = ('parameter',)
    formset = ProductToParameterFormset
    fieldsets = (
        (None, {
            'fields': ('parameter', 'value'),
        }),
    )

    def has_add_permission(self, request):
        return False


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariationInline, ProductImageInline, ProductToParameterInline]
    prepopulated_fields = {"articul": ("name",)}
    list_display = ('articul', 'name', 'sort')
    list_editable = ('sort',)
    list_filter = ('parameters_set', ProductCategoryListFilter)

    filter_horizontal = ('category',)

    def save_formset(self, request, form, formset, change):
        super(ProductAdmin, self).save_formset(request, form, formset, change)

        if formset.model == ProductToParameter:
            obj = formset.instance
            if obj.is_parametrs_set_changed():
                for current_ptp in ProductToParameter.objects.filter(product=obj):
                    current_ptp.delete()
                for parameter in obj.parameters_set.parameter_set.all():
                    ptp = ProductToParameter()
                    ptp.parameter = parameter
                    ptp.product = obj
                    ptp.save()

        if formset.model == ProductVariation:
            obj = formset.instance
            variations = obj.productvariation_set.all()
            price = None
            discount_price = None
            for variation in variations:
                if not price or variation.get_price() < price:
                    price = variation.get_price_real()
                    discount_price = variation.get_price_discount()

            obj.has_variations = bool(variations)
            if price:
                obj.price = price
                obj.discount_price = discount_price
            obj.save()

    def get_readonly_fields(self, request, obj=None):
        if obj.has_variations:
            readonly_fields = list(self.readonly_fields) + ['price', 'discount_price']
        else:
            readonly_fields = self.readonly_fields
        return readonly_fields

    class Media:
        js = (
            settings.STATIC_URL + 'admin/qshop/js/products.js',
            settings.STATIC_URL + 'admin/sitemenu/js/images.js',
        )
        css = {
            'screen': (settings.STATIC_URL + 'admin/qshop/css/products.css', settings.STATIC_URL + 'admin/sitemenu/css/images.css',),
        }

admin.site.register(Product, ProductAdmin)


class ParameterInline(admin.TabularInline):
    model = Parameter


class ParametersSetAdmin(admin.ModelAdmin):
    inlines = [ParameterInline]


admin.site.register(ParametersSet, ParametersSetAdmin)


class ParameterValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'parameter')

    class Media:
        js = (
            settings.STATIC_URL + 'admin/qshop/js/products_parametervalues.js',
        )

admin.site.register(ParameterValue, ParameterValueAdmin)


class ProductVariationValueAdmin(admin.ModelAdmin):
    list_display = ('value',)

admin.site.register(ProductVariationValue, ProductVariationValueAdmin)
