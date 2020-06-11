from django.contrib import admin
from .models import (
    Product, ProductVariationValue, ProductVariation, ProductImage, ParametersSet,
    Parameter, ProductToParameter, ParameterValue
)

from .admin_forms import ProductToParameterFormset, CategoryForm, PriceForm, ProductAdminForm, ProductToParameterForm
from .admin_filters import ProductCategoryListFilter

from django.conf import settings
from django.shortcuts import render
from django.contrib.admin import helpers
from django.http import HttpResponseRedirect
from sitemenu import import_item
from sitemenu.sitemenu_settings import MENUCLASS
from decimal import Decimal
from django.utils.translation import ugettext_lazy as _

from qshop.qshop_settings import ENABLE_PROMO_CODES


Menu = import_item(MENUCLASS)


parent_classes = {
    'ModelAdmin': admin.ModelAdmin,
    'TabularInline': admin.TabularInline,
    'StackedInline': admin.StackedInline,
}
if 'modeltranslation' in settings.INSTALLED_APPS:
    from modeltranslation.admin import TranslationAdmin, TranslationTabularInline, TranslationStackedInline
    USE_TRANSLATION = True
    parent_classes_translation = {
        'ModelAdmin': TranslationAdmin,
        'TabularInline': TranslationTabularInline,
        'StackedInline': TranslationStackedInline,
    }
else:
    USE_TRANSLATION = False

if 'tinymce' in settings.INSTALLED_APPS:
    from django.db import models
    from tinymce.widgets import AdminTinyMCE
    qshop_formfield_overrides = {
        models.TextField: {'widget': AdminTinyMCE},
    }
elif 'ckeditor_uploader' in settings.INSTALLED_APPS:
    from django.db import models
    from ckeditor_uploader.widgets import CKEditorUploadingWidget
    qshop_formfield_overrides = {
        models.TextField: {'widget': CKEditorUploadingWidget},
    }
elif 'ckeditor' in settings.INSTALLED_APPS:
    from django.db import models
    from ckeditor.widgets import CKEditorWidget
    qshop_formfield_overrides = {
        models.TextField: {'widget': CKEditorWidget},
    }
else:
    qshop_formfield_overrides = {}


def getParentClass(class_type, main_class):
    if USE_TRANSLATION and hasattr(main_class, '_translation_fields'):
        use_parent_classes = parent_classes_translation
    else:
        use_parent_classes = parent_classes
    return use_parent_classes[class_type]


class ProductVariationInline(getParentClass('TabularInline', ProductVariation)):
    model = ProductVariation
    extra = 1


class ProductImageInline(getParentClass('TabularInline', ProductImage)):
    model = ProductImage
    extra = 1


class ProductToParameterInline(getParentClass('TabularInline', ProductToParameter)):
    model = ProductToParameter
    extra = 0
    can_delete = False
    form = ProductToParameterForm
    formset = ProductToParameterFormset
    readonly_fields = ('get_parameter_name',)
    fieldsets = (
        (None, {
            'fields': ('get_parameter_name', 'parameter', 'value'),
        }),
    )

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        # TODO: move to Python 3.x syntax super()
        return super(ProductToParameterInline, self).get_queryset(request).select_related('parameter')

    def get_parameter_name(self, obj=None):
        if obj:
            return obj.parameter
    get_parameter_name.short_description = 'Parameter'


class ProductAdmin(getParentClass('ModelAdmin', Product)):
    inlines = [ProductImageInline, ProductVariationInline, ProductToParameterInline]
    prepopulated_fields = {"articul": ("name",)}
    list_display = ('articul', 'name', 'has_variations', 'admin_price_display', 'sort')
    list_editable = ('sort',)
    list_filter = ('parameters_set', ProductCategoryListFilter)
    actions = ['link_to_category', 'unlink_from_category', 'change_price', 'set_discount']

    search_fields = ['articul','name']
    # filter_horizontal = ('category',)

    formfield_overrides = qshop_formfield_overrides

    form = ProductAdminForm

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
                    if 'producttoparameter_set-TOTAL_FORMS' in request.POST:
                        for i in range(0, int(request.POST['producttoparameter_set-TOTAL_FORMS'])):
                            try:
                                if int(request.POST['producttoparameter_set-{0}-parameter'.format(i)]) == parameter.pk:
                                    ptp.value_id = int(request.POST['producttoparameter_set-{0}-value'.format(i)])
                            except ValueError:
                                pass
                    ptp.save()

        if formset.model == ProductVariation:
            obj = formset.instance
            variations = obj.productvariation_set.all()
            price = None
            discount_price = None
            for variation in variations:
                # if not price or variation.price < price or variation.discount_price < discount_price:
                    if variation.price and (not price or variation.price < price):
                        price = variation.price
                    if variation.discount_price and (not discount_price or variation.discount_price < discount_price):
                        discount_price = variation.discount_price

            obj.has_variations = bool(variations)
            if price:
                obj.price = price
                obj.discount_price = discount_price
            obj.save()

    def __init__(self, *args, **kwargs):
        super(ProductAdmin, self).__init__(*args, **kwargs)

    def save_model(self, request, obj, form, change):
        super(ProductAdmin, self).save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if (('productvariation_set-0-variation' in request.POST and
                request.POST['productvariation_set-0-variation']) or (obj and obj.has_variations)):
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

    def link_to_category(self, request, queryset):

        if 'apply' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                cat = form.cleaned_data.get('category')

                for obj in queryset:
                    obj.category.add(cat)

                self.message_user(request, _(u"Successfully linked products to '{0}'.").format(cat))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = CategoryForm()

        return render(request, 'qshop/admin/actions/link_to_category.html', {
            'form': form,
            'queryset': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        })
    link_to_category.short_description = _("Link to category")

    def unlink_from_category(self, request, queryset):
        cats = Menu.objects.filter(product__in=queryset).distinct()

        if 'apply' in request.POST:
            form = CategoryForm(request.POST, qs=cats)
            if form.is_valid():
                cat = form.cleaned_data.get('category')

                for obj in queryset:
                    obj.category.remove(cat)

                self.message_user(request, _(u"Successfully unlinked products from '{0}'.").format(cat))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = CategoryForm(qs=cats)

        return render(request, 'qshop/admin/actions/unlink_from_category.html', {
            'form': form,
            'queryset': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        })
    unlink_from_category.short_description = _(u"Unlink from category")

    def change_price(self, request, queryset):
        if 'apply' in request.POST:
            form = PriceForm(request.POST)
            if form.is_valid():
                percent = form.cleaned_data.get('percent')
                percent_multiplier = Decimal(percent / Decimal(100) + Decimal(1))
                for obj in queryset:
                    obj.price = obj.price * percent_multiplier
                    if obj.discount_price:
                        obj.discount_price = obj.discount_price * percent_multiplier
                    if obj.has_variations:
                        for variation in obj.get_variations():
                            variation.price = variation.price * percent_multiplier
                            if variation.discount_price:
                                variation.discount_price = variation.discount_price * percent_multiplier
                            variation.save()
                    obj.save()

                self.message_user(request, _(u"Successfully changed prices."))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = PriceForm()

        return render(request, 'qshop/admin/actions/change_price.html', {
            'form': form,
            'queryset': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        })
    change_price.short_description = _(u"Change price by percent")

    def set_discount(self, request, queryset):
        if 'apply' in request.POST:
            form = PriceForm(request.POST)
            if form.is_valid():
                percent = form.cleaned_data.get('percent')
                if percent == 0:
                    get_price = lambda x: None
                else:
                    get_price = lambda x: x * Decimal(-percent / Decimal(100) + Decimal(1))
                for obj in queryset:
                    obj.discount_price = get_price(obj.price)
                    if obj.has_variations:
                        for variation in obj.get_variations():
                            variation.discount_price = get_price(variation.price)
                            variation.save()
                    obj.save()

                self.message_user(request, _(u"Successfully set discounts."))
                return HttpResponseRedirect(request.get_full_path())
        else:
            form = PriceForm()

        return render(request, 'qshop/admin/actions/set_discount.html', {
            'form': form,
            'queryset': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        })
    set_discount.short_description = _(u"Set discount by percent")


admin.site.register(Product, ProductAdmin)


class ParameterInline(getParentClass('TabularInline', Parameter)):
    model = Parameter


class ParametersSetAdmin(getParentClass('ModelAdmin', ParametersSet)):
    inlines = [ParameterInline]


admin.site.register(ParametersSet, ParametersSetAdmin)


class ParameterValueAdmin(getParentClass('ModelAdmin', ParameterValue)):
    list_display = ('value', 'parameter')

    class Media:
        js = (
            settings.STATIC_URL + 'admin/qshop/js/products_parametervalues.js',
        )


admin.site.register(ParameterValue, ParameterValueAdmin)


class ProductVariationValueAdmin(getParentClass('ModelAdmin', ProductVariationValue)):
    list_display = ('value',)


admin.site.register(ProductVariationValue, ProductVariationValueAdmin)


if ENABLE_PROMO_CODES:
    from .models import PromoCode

    class PromoCodeAdmin(getParentClass('ModelAdmin', PromoCode)):
        list_display = ('code', 'discount', 'discount_type', 'is_active')
        search_fields = ('code',)
    admin.site.register(PromoCode, PromoCodeAdmin)
