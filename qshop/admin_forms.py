from django.forms.models import BaseInlineFormSet
from .models import ParameterValue, Parameter, Product
from qshop.admin_widgets import CategoryCheckboxSelectMultiple
from sitemenu.sitemenu_settings import MENUCLASS
from sitemenu import import_item
from django import forms
import re
from django.utils.translation import ugettext_lazy as _
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
    percent = forms.IntegerField(label=_(u"Percents"))


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'category': CategoryCheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        if 'weight' in self.fields:
            self.fields['weight'].help_text = 'in gramms'
        if 'category' in self.fields:
            self.fields['category'].help_text = ''
            self.fields['category'].widget.can_add_related = False

    def clean_articul(self):
        data = self.cleaned_data['articul']
        try:
            data = re.match("(.*)-copy-\d+", data).groups()[0]
        except:
            pass
        orig_data = data
        i = 1
        check = True
        while check:
            try:
                if Product.objects.exclude(pk=self.instance.pk).get(articul=data):
                    data = "{0}-copy-{1}".format(orig_data, i)
                    i += 1
            except Product.DoesNotExist:
                check = False

        return data
