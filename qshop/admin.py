from django.contrib import admin
from .models import Product, ProductVariation, ProductImage, ParametersSet, Parameter, ProductToParameter, ParameterValue
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
    list_display = ('articul', 'name', 'order')
    list_editable = ('order',)
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
            has_variations = bool(obj.productvariation_set.all())
            if obj.has_variations != has_variations:
                obj.has_variations = has_variations
                obj.save()

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
