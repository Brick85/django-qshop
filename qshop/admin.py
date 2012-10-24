from django.contrib import admin
from .models import Product, ProductImage, ProductVariation, ProductType, ProductTypeField, ProductToTypeField
from django.db import models

from .admin_forms import ProductToTypeFieldFormset

from .admin_filters import ProductCategoryListFilter

from django.conf import settings


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1


class ProductToTypeFieldInline(admin.TabularInline):
    model = ProductToTypeField
    formset = ProductToTypeFieldFormset
    extra = 0
    can_delete = False
    def has_add_permission(self, request):
        return False


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductVariationInline, ProductImageInline, ProductToTypeFieldInline]
    prepopulated_fields = {"articul": ("name",)}
    list_display = ('articul', 'name', 'order')
    list_editable = ('order',)
    list_filter = ('product_specs_type', ProductCategoryListFilter)


    filter_horizontal = ('category',)

    class Media:
        js = (
            settings.STATIC_URL + 'admin/qshop/js/products.js',
            settings.STATIC_URL + 'admin/sitemenu/js/images.js',
        )
        css = {
            'screen': (settings.STATIC_URL + 'admin/qshop/css/products.css', settings.STATIC_URL + 'admin/sitemenu/css/images.css',),
        }

admin.site.register(Product, ProductAdmin)


class ProductTypeFieldInline(admin.TabularInline):
    model = ProductTypeField


class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductTypeFieldInline]


admin.site.register(ProductType, ProductTypeAdmin)

