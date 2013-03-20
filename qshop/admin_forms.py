from django.forms.models import BaseInlineFormSet
from .models import ParameterValue, Parameter, Product
from sitemenu.sitemenu_settings import MENUCLASS
from sitemenu import import_item
from django import forms

Menu = import_item(MENUCLASS)


class ProductToParameterFormset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(ProductToParameterFormset, self).add_fields(form, index)

        values = ParameterValue.objects.none()
        if form.instance.pk:
            try:
                parameter = form.instance.parameter
            except Parameter.DoesNotExist:
                pass
            else:
                values = ParameterValue.objects.filter(parameter=parameter)
        else:
            try:
                value_key = 'producttoparameter_set-{0}-parameter'.format(index)
                values = ParameterValue.objects.filter(parameter_id=form.data[value_key])
            except:
                pass
        form.fields['value'].queryset = values


class CategoryForm(forms.Form):
    category = forms.ModelChoiceField(Menu.objects)

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('qs', None)
        super(CategoryForm, self).__init__(*args, **kwargs)
        if qs:
            self.fields['category'].queryset = qs


class PriceForm(forms.Form):
    percent = forms.IntegerField()


# class ProductAdminForm(forms.ModelForm):
#     class Meta:
#         model = Product
